import React from 'react';
import './TaskCard.css';

interface TaskCardProps {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  status?: 'running' | 'success' | 'error';
  disabled: boolean;
  logs: string[];
  onAction: (mode: 'yunxiao' | 'k8s' | 'all') => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  id,
  icon,
  title,
  description,
  status,
  disabled,
  logs,
  onAction
}) => {
  const [showLogs, setShowLogs] = React.useState(false);
  const logEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (showLogs) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, showLogs]);

  const statusLabel = status === 'running' ? '运行中' : status === 'success' ? '成功' : status === 'error' ? '失败' : '待机';

  return (
    <div className={`task-card ${status || ''}`} id={`card-${id}`}>
      <div className="task-info">
        <div className="task-icon">{icon}</div>
        <div className="task-details">
          <div className="task-title">{title}</div>
          <div className="task-desc">{description}</div>
        </div>
        <div className={`task-status ${status || 'idle'}`}>{statusLabel}</div>
      </div>
      <div className="task-actions">
        <button
          className="task-btn btn-yunxiao"
          disabled={disabled}
          onClick={() => onAction('yunxiao')}
        >
          <span className="btn-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                d="M5 12.5a7 7 0 0 1 13.69-2.41.75.75 0 0 1-1.44.44A5.5 5.5 0 0 0 6.5 12.5c0 3.04 2.46 5.5 5.5 5.5 1.77 0 3.35-.83 4.36-2.12a.75.75 0 1 1 1.2.9A6.97 6.97 0 0 1 12 19.5c-3.87 0-7-3.13-7-7Zm11.22-6.6 3.03.83a.75.75 0 0 1 .52.92l-1.21 4.52a.75.75 0 0 1-1.45-.39l.66-2.47-5.1 5.1a.75.75 0 0 1-1.06-1.06l5.1-5.1-2.49-.68a.75.75 0 1 1 .38-1.45Z"
                fill="currentColor"
              />
            </svg>
          </span>
          云效执行
        </button>
        <button
          className="task-btn btn-k8s"
          disabled={disabled}
          onClick={() => onAction('k8s')}
        >
          <span className="btn-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                d="M12 3.5 4.5 7.75v8.5L12 20.5l7.5-4.25v-8.5L12 3.5Zm0 1.72 5.75 3.25-5.75 3.25-5.75-3.25L12 5.22Zm-6 10.02v-5.3l5.25 2.97v5.3L6 15.24Zm12 0-5.25 2.97v-5.3l5.25-2.97v5.3Z"
                fill="currentColor"
              />
            </svg>
          </span>
          K8s 发布
        </button>
        <button
          className="task-btn btn-all"
          disabled={disabled}
          onClick={() => onAction('all')}
        >
          <span className="btn-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                d="M12.75 2.5a.75.75 0 0 1 .7.98l-1.4 4.2h5.2a.75.75 0 0 1 .57 1.24l-8.5 10a.75.75 0 0 1-1.29-.68l1.45-4.77H6.25a.75.75 0 0 1-.57-1.24l6.5-7.5a.75.75 0 0 1 .57-.23Z"
                fill="currentColor"
              />
            </svg>
          </span>
          全部流程
        </button>
        <button
          className="task-btn btn-logs"
          onClick={() => setShowLogs(!showLogs)}
        >
          <span className="btn-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                d="M6 4.75A1.75 1.75 0 0 1 7.75 3h8.5A1.75 1.75 0 0 1 18 4.75v14.5A1.75 1.75 0 0 1 16.25 21h-8.5A1.75 1.75 0 0 1 6 19.25V4.75Zm1.75-.25a.25.25 0 0 0-.25.25v14.5c0 .14.11.25.25.25h8.5a.25.25 0 0 0 .25-.25V4.75a.25.25 0 0 0-.25-.25h-8.5Zm1.75 4h5a.75.75 0 0 1 0 1.5h-5a.75.75 0 0 1 0-1.5Zm0 4h6.5a.75.75 0 0 1 0 1.5H9.5a.75.75 0 0 1 0-1.5Zm0 4h6.5a.75.75 0 0 1 0 1.5H9.5a.75.75 0 0 1 0-1.5Z"
                fill="currentColor"
              />
            </svg>
          </span>
          日志
          <span className="btn-caret" aria-hidden="true">
            {showLogs ? '▴' : '▾'}
          </span>
        </button>
      </div>
      {showLogs && (
        <div className="task-logs">
          {logs.length === 0 ? (
            <div className="log-empty">暂无日志</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="log-line">
                {log}
              </div>
            ))
          )}
          <div ref={logEndRef} />
        </div>
      )}
    </div>
  );
};

export default TaskCard;
