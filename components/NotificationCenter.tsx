import React, { useEffect } from 'react';
import { Notification } from '../types';
import { CheckCircleIcon, XCircleIcon, InfoIcon } from './icons';

interface NotificationCenterProps {
  notifications: Notification[];
  onRemove: (id: number) => void;
}

const icons = {
  success: <CheckCircleIcon className="w-6 h-6 text-emerald-400" />,
  error: <XCircleIcon className="w-6 h-6 text-rose-400" />,
  info: <InfoIcon className="w-6 h-6 text-sky-400" />,
};

const bgColor = {
    success: 'bg-emerald-500/10 border-emerald-500/30',
    error: 'bg-rose-500/10 border-rose-500/30',
    info: 'bg-sky-500/10 border-sky-500/30'
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ notifications, onRemove }) => {
  return (
    <div className="fixed top-5 right-5 z-50 w-full max-w-sm pointer-events-none">
      <div className="flex flex-col-reverse gap-3 pointer-events-auto">
        {notifications.map(notification => (
          <Toast key={notification.id} notification={notification} onRemove={onRemove} />
        ))}
      </div>
    </div>
  );
};

const Toast: React.FC<{ notification: Notification; onRemove: (id: number) => void }> = ({ notification, onRemove }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onRemove(notification.id);
    }, 5000); // Remove after 5 seconds

    return () => {
      clearTimeout(timer);
    };
  }, [notification.id, onRemove]);

  return (
    <div
      className={`flex items-start p-4 rounded-lg shadow-lg border text-white ${bgColor[notification.type]} animate-fade-in-right backdrop-blur-sm`}
    >
      <div className="flex-shrink-0">{icons[notification.type]}</div>
      <div className="ml-3 flex-1">
        <p className="text-sm font-medium">{notification.message}</p>
      </div>
       <button onClick={() => onRemove(notification.id)} className="ml-4 -mt-1 -mr-1 p-1 rounded-md hover:bg-white/10 focus:outline-none">
           <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
           </svg>
       </button>
    </div>
  );
};