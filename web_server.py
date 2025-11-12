#!/usr/bin/env python3
"""
Web 服务 - 提供界面触发云效到 K8s 自动部署

启动方式:
    python web_server.py

访问地址:
    http://localhost:5000
    或局域网内其他设备访问: http://<本机IP>:5000
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Lock

# 导入原有的主流程
from main import main as deploy_main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yunxiao-k8s-deployer-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 任务状态管理
task_lock = Lock()
task_status = {
    'running': False,
    'current_step': '',
    'logs': [],
    'result': None,
    'start_time': None,
    'end_time': None
}


class WebLogger:
    """Web 日志输出类,用于捕获日志并通过 WebSocket 发送"""

    def __init__(self):
        self.logs = []

    def log(self, message, level="INFO"):
        """记录日志并发送到前端"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)

        # 通过 WebSocket 实时发送日志
        socketio.emit('log', log_entry)

        # 同时输出到控制台
        print(f"[{timestamp}] [{level}] {message}")


# 全局 logger 实例
web_logger = WebLogger()


async def run_deployment():
    """异步执行部署任务"""
    global task_status

    try:
        with task_lock:
            task_status['running'] = True
            task_status['logs'] = []
            task_status['result'] = None
            task_status['start_time'] = datetime.now().isoformat()
            task_status['end_time'] = None
            task_status['current_step'] = '初始化...'

        socketio.emit('task_status', {'status': 'running'})
        web_logger.log("开始执行部署任务", "INFO")

        # 执行主流程
        # 由于 main() 函数使用了 sys.exit,我们需要捕获它
        try:
            await deploy_main()

            with task_lock:
                task_status['result'] = 'success'
                task_status['current_step'] = '部署完成'

            web_logger.log("部署任务执行成功!", "SUCCESS")
            socketio.emit('task_status', {'status': 'success'})

        except SystemExit as e:
            if e.code == 0:
                # 正常退出
                with task_lock:
                    task_status['result'] = 'success'
                    task_status['current_step'] = '部署完成'
                web_logger.log("部署任务执行成功!", "SUCCESS")
                socketio.emit('task_status', {'status': 'success'})
            else:
                # 异常退出
                raise

    except Exception as e:
        with task_lock:
            task_status['result'] = 'error'
            task_status['current_step'] = f'部署失败: {str(e)}'

        web_logger.log(f"部署任务执行失败: {str(e)}", "ERROR")
        socketio.emit('task_status', {'status': 'error', 'error': str(e)})

    finally:
        with task_lock:
            task_status['running'] = False
            task_status['end_time'] = datetime.now().isoformat()


def start_deployment_task():
    """在新的事件循环中启动部署任务"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_deployment())
    finally:
        loop.close()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取当前任务状态"""
    with task_lock:
        return jsonify(task_status)


@app.route('/api/deploy', methods=['POST'])
def trigger_deploy():
    """触发部署任务"""
    with task_lock:
        if task_status['running']:
            return jsonify({
                'success': False,
                'message': '已有任务正在执行中,请稍后再试'
            }), 400

    # 在新线程中启动异步任务
    import threading
    thread = threading.Thread(target=start_deployment_task)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '部署任务已启动'
    })


@socketio.on('connect')
def handle_connect():
    """WebSocket 连接建立"""
    emit('connected', {'data': '连接成功'})

    # 发送当前状态
    with task_lock:
        emit('task_status', {
            'status': 'running' if task_status['running'] else 'idle'
        })


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket 连接断开"""
    print('客户端断开连接')


# 替换原有的 log 函数,使其通过 WebSocket 发送
import utils
original_log = utils.log

def web_log(message, level="INFO"):
    """替换的日志函数"""
    web_logger.log(message, level)

# 替换全局 log 函数
utils.log = web_log


if __name__ == '__main__':
    # 使用端口 5001 (避免与 macOS AirPlay Receiver 冲突)
    PORT = 5001

    print("=" * 60)
    print("云效 K8s 自动部署 Web 服务")
    print("=" * 60)
    print(f"本地访问: http://localhost:{PORT}")
    print(f"局域网访问: http://<本机IP>:{PORT}")
    print("=" * 60)

    # 启动 Flask 应用
    # 使用 0.0.0.0 允许局域网访问
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)
