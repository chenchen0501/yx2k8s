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

# 任务状态管理 - 统一管理
task_lock = Lock()

task_status = {
    'running': False,
    'current_step': '',
    'logs': [],
    'result': None,
    'start_time': None,
    'end_time': None,
    'tasks': []
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

        # 创建 logger
        project_logger = WebLogger()
        project_logger.log(f"开始执行部署任务 (共 {len(selected_tasks)} 个)", "INFO")

        # 创建任务调度器
        scheduler = TaskScheduler(log_callback=project_logger.log)

        # 根据选中的任务创建 DeployTask
        task_map = {
            'frontend-build': ('前端云效构建', 'frontend', 'build'),
            'frontend-test': ('前端测试环境', 'frontend', 'test'),
            'backend-build': ('后端云效构建', 'backend', 'build'),
            'backend-test': ('后端测试环境', 'backend', 'test'),
        }

        for task_info in selected_tasks:
            task_id = task_info['task_id']
            run_build = task_info['run_build']

            if task_id in task_map:
                name, proj, env = task_map[task_id]
                mode = '触发构建' if run_build else '使用最近构建'
                project_logger.log(f"添加任务: {name} [{mode}]", "INFO")

                task = DeployTask(task_id, name, proj, env, run_build=run_build)
                scheduler.add_task(task)

                # 更新任务状态
                with task_lock:
                    task_status['tasks'].append({
                        'id': task_id,
                        'name': name,
                        'run_build': run_build,
                        'status': 'pending'
                    })
            else:
                project_logger.log(f"⚠️ 未知的任务ID: {task_id}，已跳过", "WARNING")

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
            project_logger.log(f"✅ 所有任务执行成功! 成功 {success_count} 个", "SUCCESS")
            socketio.emit('task_status', {'status': 'success', 'summary': f'成功完成 {success_count} 个任务'})
        else:
            with task_lock:
                task_status['result'] = 'partial'
                task_status['current_step'] = f'部分任务失败: 成功 {success_count} 个, 失败 {error_count} 个'
            project_logger.log(f"⚠️ 部分任务失败: 成功 {success_count} 个, 失败 {error_count} 个", "WARNING")
            socketio.emit('task_status', {'status': 'partial', 'summary': f'成功 {success_count} 个, 失败 {error_count} 个'})

    except Exception as e:
        with task_lock:
            task_status['result'] = 'error'
            task_status['current_step'] = f'部署失败: {str(e)}'

        project_logger = WebLogger()
        project_logger.log(f"部署任务执行失败: {str(e)}", "ERROR")
        socketio.emit('task_status', {'status': 'error', 'error': str(e), 'summary': str(e)})

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
    except Exception as e:
        # 创建 logger 来记录错误
        project_logger = WebLogger()
        project_logger.log(f"部署任务执行异常: {str(e)}", "ERROR")
        import traceback
        project_logger.log(f"异常堆栈: {traceback.format_exc()}", "ERROR")

        # 更新任务状态
        with task_lock:
            task_status['running'] = False
            task_status['result'] = 'error'
            task_status['end_time'] = datetime.now().isoformat()

        # 发送错误状态
        socketio.emit('task_status', {
            'status': 'error',
            'summary': f'任务执行异常: {str(e)}'
        })
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
        status_data = task_status.copy()

    return jsonify(status_data)


@app.route('/api/deploy', methods=['POST'])
def trigger_deploy():
    """触发部署任务"""
    # 获取选中的任务
    data = request.get_json()
    selected_tasks = data.get('tasks', [])
    mode = data.get('mode', 'all')

    # 检查是否正在运行
    with task_lock:
        if task_status['running']:
            return jsonify({
                'success': False,
                'message': '任务正在执行中,请稍后再试'
            }), 400

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

    # 根据模式返回消息
    mode_desc = {
        'yunxiao': '云效构建',
        'k8s': 'K8s发布',
        'all': '完整部署'
    }.get(mode, '部署')

    return jsonify({
        'success': True,
        'message': f'{mode_desc}任务已启动 (共 {len(selected_tasks)} 个任务)'
    })


@socketio.on('connect')
def handle_connect():
    """WebSocket 连接建立"""
    emit('connected', {'data': '连接成功'})

    # 发送当前状态
    with task_lock:
        if task_status['running']:
            emit('task_status', {'status': 'running'})


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
