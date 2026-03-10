import React, { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import './App.css';
import TaskCard from './components/TaskCard';
import Notification from './components/Notification';

interface TaskStatus {
  [key: string]: 'running' | 'success' | 'error' | undefined;
}

interface NotificationState {
  message: string;
  type: 'success' | 'error' | 'info';
}

interface ProjectLogs {
  [key: string]: string[];
}

function App() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [projectLogs, setProjectLogs] = useState<ProjectLogs>({
    'spms-web': [],
    'spms-server': []
  });
  const [runningTasks, setRunningTasks] = useState<Set<string>>(new Set());
  const [notification, setNotification] = useState<NotificationState | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>({});

  const projectMap: { [key: string]: any } = {
    'spms-web': {
      name: 'spms-web (前端)',
      buildTask: 'frontend-build',
      deployTask: 'frontend-test'
    },
    'spms-server': {
      name: 'spms-server (后端)',
      buildTask: 'backend-build',
      deployTask: 'backend-test'
    }
  };

  useEffect(() => {
    const newSocket = io('http://localhost:5001');
    setSocket(newSocket);

    newSocket.on('connected', (data: any) => {
      console.log('WebSocket 已连接:', data);
      setNotification({ message: 'WebSocket 连接成功', type: 'success' });
    });

    newSocket.on('task_status', (data: any) => {
      console.log('任务状态更新:', data);
      const { task, status } = data;

      setTaskStatus(prev => ({ ...prev, [task]: status }));

      if (status === 'running') {
        setRunningTasks(prev => new Set(prev).add(task));
      } else {
        setRunningTasks(prev => {
          const newSet = new Set(prev);
          newSet.delete(task);
          return newSet;
        });
      }
    });

    newSocket.on('log', (data: any) => {
      const message = data.message;

      // 根据任务类型分配日志到对应项目
      let projectId = '';
      if (message.includes('frontend') || message.includes('前端')) {
        projectId = 'spms-web';
      } else if (message.includes('backend') || message.includes('后端')) {
        projectId = 'spms-server';
      }

      if (projectId) {
        setProjectLogs(prev => ({
          ...prev,
          [projectId]: [...prev[projectId], message]
        }));
      }
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const handleStartTask = async (projectId: string, mode: 'yunxiao' | 'k8s' | 'all') => {
    const project = projectMap[projectId];
    if (!project) return;

    let tasks: string[] = [];
    if (mode === 'yunxiao') {
      tasks = [project.buildTask];
    } else if (mode === 'k8s') {
      tasks = [project.deployTask];
    } else {
      tasks = [project.buildTask, project.deployTask];
    }

    // 清空该项目的日志
    setProjectLogs(prev => ({
      ...prev,
      [projectId]: []
    }));

    setNotification({ message: `开始执行 ${project.name} - ${mode}`, type: 'info' });

    try {
      const response = await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tasks })
      });

      const result = await response.json();
      if (result.status === 'started') {
        setNotification({ message: '任务已启动', type: 'success' });
      } else {
        setNotification({ message: result.message || '启动失败', type: 'error' });
      }
    } catch (error) {
      console.error('启动任务失败:', error);
      setNotification({ message: '启动任务失败', type: 'error' });
    }
  };

  const isProjectRunning = (projectId: string): boolean => {
    const project = projectMap[projectId];
    return runningTasks.has(project.buildTask) || runningTasks.has(project.deployTask);
  };

  const getProjectStatus = (projectId: string): 'running' | 'success' | 'error' | undefined => {
    const project = projectMap[projectId];
    const buildStatus = taskStatus[project.buildTask];
    const deployStatus = taskStatus[project.deployTask];

    if (buildStatus === 'running' || deployStatus === 'running') return 'running';
    if (buildStatus === 'error' || deployStatus === 'error') return 'error';
    if (buildStatus === 'success' || deployStatus === 'success') return 'success';
    return undefined;
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-brand">
            <div className="app-mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path
                  d="M4 6.5C4 5.12 5.12 4 6.5 4h11c1.38 0 2.5 1.12 2.5 2.5v6.25c0 1.38-1.12 2.5-2.5 2.5h-3.25l-2.5 3-2.5-3H6.5C5.12 15.25 4 14.13 4 12.75V6.5Zm2.5-.5a.75.75 0 0 0-.75.75v6.25c0 .41.34.75.75.75h11a.75.75 0 0 0 .75-.75V6.75a.75.75 0 0 0-.75-.75h-11Zm2.75 2.5h7.5a.75.75 0 0 1 0 1.5h-7.5a.75.75 0 0 1 0-1.5Zm0 3h4.5a.75.75 0 0 1 0 1.5h-4.5a.75.75 0 0 1 0-1.5Z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div>
              <h1>云效 · K8s 部署平台</h1>
              <p>基于浏览器自动化的 CI/CD 控制台，专注构建与测试环境发布</p>
            </div>
          </div>
          <div className="app-env" aria-label="环境状态">
            <span className="env-dot" />
            Local
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="task-list">
          <TaskCard
            id="spms-web"
            icon={
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path
                  d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm6.7 8.25h-3.3a12.78 12.78 0 0 0-1.02-5.02 7.52 7.52 0 0 1 4.32 5.02ZM12 4.5c.82 1.07 1.5 2.8 1.8 4.75H10.2c.3-1.95.98-3.68 1.8-4.75ZM9.62 6.23A12.78 12.78 0 0 0 8.6 11.25H5.3a7.52 7.52 0 0 1 4.32-5.02Zm-4.32 6.52h3.3c.13 1.76.5 3.43 1.02 5.02a7.52 7.52 0 0 1-4.32-5.02Zm6.7 6.75c-.82-1.07-1.5-2.8-1.8-4.75h3.6c-.3 1.95-.98 3.68-1.8 4.75Zm2.38-1.73c.52-1.59.9-3.26 1.02-5.02h3.3a7.52 7.52 0 0 1-4.32 5.02Z"
                  fill="currentColor"
                />
              </svg>
            }
            title="spms-web"
            description="前端项目"
            status={getProjectStatus('spms-web')}
            disabled={isProjectRunning('spms-web')}
            logs={projectLogs['spms-web']}
            onAction={(mode) => handleStartTask('spms-web', mode)}
          />
          <TaskCard
            id="spms-server"
            icon={
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path
                  d="M5.5 4.5A2.5 2.5 0 0 1 8 2h8a2.5 2.5 0 0 1 2.5 2.5v2A2.5 2.5 0 0 1 16 9H8A2.5 2.5 0 0 1 5.5 6.5v-2ZM8 3.5a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H8Zm-2.5 12A2.5 2.5 0 0 1 8 13h8a2.5 2.5 0 0 1 2.5 2.5v2A2.5 2.5 0 0 1 16 20H8a2.5 2.5 0 0 1-2.5-2.5v-2ZM8 14.5a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H8Zm2.25 2a.75.75 0 0 1 .75-.75h2a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1-.75-.75Z"
                  fill="currentColor"
                />
              </svg>
            }
            title="spms-server"
            description="后端项目"
            status={getProjectStatus('spms-server')}
            disabled={isProjectRunning('spms-server')}
            logs={projectLogs['spms-server']}
            onAction={(mode) => handleStartTask('spms-server', mode)}
          />
        </div>
      </main>

      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
}

export default App;
