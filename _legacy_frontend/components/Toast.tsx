import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// import { CheckCircleIcon, XCircleIcon, InformationCircleIcon } from './icons'; // Suponiendo que tienes estos iconos

export interface ToastMessage {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

interface ToastProps {
  toast: ToastMessage;
  onDismiss: (id: number) => void;
}

const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, toast.duration || 5000);

    return () => {
      clearTimeout(timer);
    };
  }, [toast, onDismiss]);

  // const icons = {
  //   success: <CheckCircleIcon className="w-6 h-6 text-green-500" />,
  //   error: <XCircleIcon className="w-6 h-6 text-red-500" />,
  //   info: <InformationCircleIcon className="w-6 h-6 text-blue-500" />,
  // };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.3 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
      className={`flex items-center p-4 mb-4 text-white rounded-lg shadow-lg bg-gray-800 border border-gray-700`}
    >
      {/* <div className="mr-3">{icons[toast.type]}</div> */}
      <div className="text-sm font-medium">{toast.message}</div>
      <button onClick={() => onDismiss(toast.id)} className="ml-auto -mx-1.5 -my-1.5 p-1.5 rounded-lg hover:bg-gray-700">
        <span className="sr-only">Dismiss</span>
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path></svg>
      </button>
    </motion.div>
  );
};


interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: number) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed bottom-0 right-0 p-8 z-50">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
};
