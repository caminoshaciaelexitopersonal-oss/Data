'use client';

import React, { useState, useEffect } from 'react';
import { DefaultService } from '@/lib/api-client';

// Basic Toast component for notifications
const ToastContainer = ({ toasts }: { toasts: { id: number; message: string; type: string }[] }) => (
  <div className="fixed bottom-4 right-4 space-y-2">
    {toasts.map(toast => (
      <div key={toast.id} className={`p-4 rounded-md shadow-lg text-white ${toast.type === 'error' ? 'bg-red-600' : 'bg-blue-600'}`}>
        {toast.message}
      </div>
    ))}
  </div>
);

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [toasts, setToasts] = useState<{ id: number; message: string; type: string }[]>([]);

  const addToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToasts(prev => [...prev, { id: Date.now(), message, type }]);
    setTimeout(() => setToasts(prev => prev.slice(1)), 5000); // Auto-dismiss after 5s
  };

  useEffect(() => {
    const createSession = async () => {
      try {
        const session = await DefaultService.createSession();
        setSessionId(session.session_id ?? null);
        addToast(`Sesión iniciada: ${session.session_id ?? 'N/A'}`, 'info');
      } catch (error) {
        addToast(`Error al iniciar sesión: ${(error as Error).message}`, 'error');
      }
    };
    createSession();
  }, []);

  return (
    <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center">
        <h1 className="text-xl font-bold">Sistema de Analítica de Datos Inteligente (SADI)</h1>
      </header>
      <main className="flex-1 overflow-y-auto p-8">
        <h2 className="text-2xl mb-4">Modernización del Frontend en Progreso</h2>
        <p>El esqueleto de la aplicación Next.js está funcionando.</p>
        <p className="mt-4">ID de Sesión: <span className="font-mono text-green-400">{sessionId || 'Creando...'}</span></p>
      </main>
      <ToastContainer toasts={toasts} />
    </div>
  );
}
