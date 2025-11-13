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

# 导入任务调度器
from task_scheduler import TaskScheduler, DeployTask

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
    'end_time': None,
    'tasks': []  # 当前执行的任务列表
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


async def run_deployment(selected_tasks):
    """
    异步执行部署任务

    Args:
        selected_tasks: 选中的任务列表,每个任务是字典 {'task_id': 'frontend-test', 'run_build': True}
    """
    global task_status

    try:
        with task_lock:
            task_status['running'] = True
            task_status['logs'] = []
            task_status['result'] = None
            task_status['start_time'] = datetime.now().isoformat()
            task_status['end_time'] = None
            task_status['current_step'] = '初始化...'
            task_status['tasks'] = []

        socketio.emit('task_status', {'status': 'running'})

        web_logger.log(f"开始执行部署任务 (共 {len(selected_tasks)} 个)", "INFO")

        # 创建任务调度器
        scheduler = TaskScheduler(log_callback=web_logger.log)

        # 根据选中的任务创建 DeployTask
        task_map = {
            'frontend-test': ('前端测试环境', 'frontend', 'test'),
            'frontend-prod': ('前端生产环境', 'frontend', 'prod'),
            'backend-test': ('后端测试环境', 'backend', 'test'),
            'backend-prod': ('后端生产环境', 'backend', 'prod'),
        }

        for task_info in selected_tasks:
            task_id = task_info['task_id']
            run_build = task_info['run_build']

            if task_id in task_map:
                name, project, env = task_map[task_id]
                mode = '触发构建' if run_build else '使用最近构建'
                web_logger.log(f"添加任务: {name} [{mode}]", "INFO")

                task = DeployTask(task_id, name, project, env, run_build=run_build)
                scheduler.add_task(task)

                # 更新任务状态
                with task_lock:
                    task_status['tasks'].append({
                        'id': task_id,
                        'name': name,
                        'run_build': run_build,
                        'status': 'pending'
                    })

        # 执行所有任务
        await scheduler.execute_all()

        # 检查执行结果
        success_count = sum(1 for t in scheduler.tasks if t.status == 'success')
        error_count = sum(1 for t in scheduler.tasks if t.status == 'error')

        # 更新任务状态
        with task_lock:
            for task in scheduler.tasks:
                # 查找对应的任务状态并更新
                for ts in task_status['tasks']:
                    if ts['id'] == task.task_id:
                        ts['status'] = task.status
                        ts['tag'] = task.tag
                        if task.error_message:
                            ts['error'] = task.error_message
                        break

        if error_count == 0:
            with task_lock:
                task_status['result'] = 'success'
                task_status['current_step'] = '所有任务执行完成'
            web_logger.log(f"✅ 所有任务执行成功! 成功 {success_count} 个", "SUCCESS")
            socketio.emit('task_status', {'status': 'success'})
        else:
            with task_lock:
                task_status['result'] = 'partial'
                task_status['current_step'] = f'部分任务失败: 成功 {success_count} 个, 失败 {error_count} 个'
            web_logger.log(f"⚠️ 部分任务失败: 成功 {success_count} 个, 失败 {error_count} 个", "WARNING")
            socketio.emit('task_status', {'status': 'partial'})

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


def start_deployment_task(selected_tasks):
    """在新的事件循环中启动部署任务"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_deployment(selected_tasks))
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

    # 获取选中的任务
    data = request.get_json()
    selected_tasks = data.get('tasks', [])

    if not selected_tasks:
        return jsonify({
            'success': False,
            'message': '请至少选择一个任务'
        }), 400

    # 在新线程中启动异步任务
    import threading
    thread = threading.Thread(
        target=start_deployment_task,
        args=(selected_tasks,)
    )
    thread.daemon = True
    thread.start()

    # 统计触发构建和使用最近构建的数量
    build_count = sum(1 for t in selected_tasks if t.get('run_build', True))
    skip_count = len(selected_tasks) - build_count

    if skip_count == 0:
        mode_desc = '全部触发新构建'
    elif build_count == 0:
        mode_desc = '全部使用最近构建'
    else:
        mode_desc = f'{build_count}个触发构建, {skip_count}个使用最近构建'

    return jsonify({
        'success': True,
        'message': f'部署任务已启动 (共 {len(selected_tasks)} 个任务, {mode_desc})'
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
