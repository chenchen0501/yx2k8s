import React from 'react';
import './Notification.css';

interface NotificationProps {
  message: string;
  type: 'success' | 'error' | 'info';
  onClose: () => void;
}

const Notification: React.FC<NotificationProps> = ({ message, type, onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg viewBox="0 0 24 24" role="img" focusable="false">
            <path
              d="M9.25 12.75 11 14.5l3.75-4a.75.75 0 0 1 1.1 1.02l-4.27 4.55a.75.75 0 0 1-1.08.02L8.2 13.82a.75.75 0 1 1 1.05-1.07Z"
              fill="currentColor"
            />
            <path
              d="M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17Zm0 1.5a7 7 0 1 1 0 14 7 7 0 0 1 0-14Z"
              fill="currentColor"
            />
          </svg>
        );
      case 'error':
        return (
          <svg viewBox="0 0 24 24" role="img" focusable="false">
            <path
              d="M8.47 8.47a.75.75 0 0 1 1.06 0L12 10.94l2.47-2.47a.75.75 0 0 1 1.06 1.06L13.06 12l2.47 2.47a.75.75 0 0 1-1.06 1.06L12 13.06l-2.47 2.47a.75.75 0 0 1-1.06-1.06L10.94 12 8.47 9.53a.75.75 0 0 1 0-1.06Z"
              fill="currentColor"
            />
            <path
              d="M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17Zm0 1.5a7 7 0 1 1 0 14 7 7 0 0 1 0-14Z"
              fill="currentColor"
            />
          </svg>
        );
      case 'info':
        return (
          <svg viewBox="0 0 24 24" role="img" focusable="false">
            <path
              d="M12 6.5a1 1 0 1 1 0 2 1 1 0 0 1 0-2Zm-1 4.25a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 .75.75v5a.75.75 0 0 1-1.5 0v-4.25h-.25a.75.75 0 0 1-.75-.75Z"
              fill="currentColor"
            />
            <path
              d="M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17Zm0 1.5a7 7 0 1 1 0 14 7 7 0 0 1 0-14Z"
              fill="currentColor"
            />
          </svg>
        );
      default:
        return (
          <svg viewBox="0 0 24 24" role="img" focusable="false">
            <path
              d="M12 6.5a1 1 0 1 1 0 2 1 1 0 0 1 0-2Zm-1 4.25a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 .75.75v5a.75.75 0 0 1-1.5 0v-4.25h-.25a.75.75 0 0 1-.75-.75Z"
              fill="currentColor"
            />
            <path
              d="M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17Zm0 1.5a7 7 0 1 1 0 14 7 7 0 0 1 0-14Z"
              fill="currentColor"
            />
          </svg>
        );
    }
  };

  return (
    <div className={`notification notification-${type}`}>
      <span className="notification-icon">{getIcon()}</span>
      <span className="notification-message">{message}</span>
      <button className="notification-close" onClick={onClose}>
        ×
      </button>
    </div>
  );
};

export default Notification;
