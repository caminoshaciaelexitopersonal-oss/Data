import React, { useState, useRef, useEffect } from 'react';
import { UserIcon, BotIcon, MicIcon, StopIcon } from './icons';

// Hook para el reconocimiento de voz
const useSpeechRecognition = (onResult: (text: string) => void) => {
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech recognition not supported in this browser.");
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'es-ES';
        recognition.interimResults = false;

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            onResult(transcript);
            setIsListening(false);
        };
        recognition.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setIsListening(false);
        };
        recognition.onend = () => {
            setIsListening(false);
        };
        recognitionRef.current = recognition;
    }, [onResult]);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
        }
        setIsListening(!isListening);
    };

    return { isListening, toggleListening };
};


interface Message {
    sender: 'user' | 'bot';
    text: string;
    imageBase64?: string;
}

interface ChatViewProps {
    onSendMessage: (message: string) => Promise<any>;
}

export const ChatView: React.FC<ChatViewProps> = ({ onSendMessage }) => {
    const [messages, setMessages] = useState<Message[]>([
        { sender: 'bot', text: "¡Hola! Soy tu asistente de análisis de datos. ¿Qué te gustaría hacer hoy? Puedes decirme 'carga un archivo' o 'ejecuta un clustering con 3 grupos'." }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);

    const { isListening, toggleListening } = useSpeechRecognition((transcript) => {
        setInputValue(transcript);
        handleSendMessage(transcript);
    });

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    useEffect(scrollToBottom, [messages]);

    const handleSendMessage = async (messageText = inputValue) => {
        if (!messageText.trim()) return;

        const userMessage: Message = { sender: 'user', text: messageText };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const agentResponse = await onSendMessage(messageText);
            let botResponse: Message;

            if (typeof agentResponse.output === 'object' && agentResponse.output.image_base64) {
                botResponse = {
                    sender: 'bot',
                    text: agentResponse.output.description || "Aquí está la visualización que pediste.",
                    imageBase64: agentResponse.output.image_base64
                };
            } else {
                botResponse = { sender: 'bot', text: agentResponse.output || "No estoy seguro de cómo responder a eso." };
            }
            setMessages(prev => [...prev, botResponse]);

        } catch (error) {
            const err = error as Error;
            const errorMessage: Message = { sender: 'bot', text: `Lo siento, hubo un error: ${err.message}` };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-800/30">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                        {msg.sender === 'bot' && <div className="bg-gray-700 p-2 rounded-full"><BotIcon className="w-6 h-6 text-cyan-400" /></div>}
                        <div className={`px-4 py-2 rounded-lg max-w-lg ${msg.sender === 'user' ? 'bg-cyan-600 text-white' : 'bg-gray-700 text-slate-200'}`}>
                            <p className="text-sm" dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br />') }} />
                            {msg.imageBase64 && (
                                <img src={`data:image/png;base64,${msg.imageBase64}`} alt="Generated chart" className="mt-2 rounded-lg"/>
                            )}
                        </div>
                        {msg.sender === 'user' && <div className="bg-gray-700 p-2 rounded-full"><UserIcon className="w-6 h-6 text-slate-300" /></div>}
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-start gap-3">
                        <div className="bg-gray-700 p-2 rounded-full"><BotIcon className="w-6 h-6 text-cyan-400" /></div>
                        <div className="px-4 py-2 rounded-lg bg-gray-700 text-slate-200">
                            <div className="flex items-center space-x-1">
                                <span className="h-2 w-2 bg-cyan-400 rounded-full animate-pulse [animation-delay:-0.3s]"></span>
                                <span className="h-2 w-2 bg-cyan-400 rounded-full animate-pulse [animation-delay:-0.15s]"></span>
                                <span className="h-2 w-2 bg-cyan-400 rounded-full animate-pulse"></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div className="p-4 bg-gray-800 border-t border-gray-700">
                <div className="flex items-center bg-gray-700 rounded-lg p-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                        placeholder="Escribe o usa el micrófono..."
                        className="flex-1 bg-transparent text-white focus:outline-none px-2"
                        disabled={isLoading}
                    />
                    <button onClick={toggleListening} className="p-2 text-gray-400 hover:text-white" disabled={isLoading}>
                        {isListening ? <StopIcon className="w-6 h-6 text-red-500"/> : <MicIcon className="w-6 h-6"/>}
                    </button>
                    <button
                        onClick={() => handleSendMessage()}
                        disabled={isLoading || !inputValue.trim()}
                        className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-md disabled:opacity-50"
                    >
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
};
