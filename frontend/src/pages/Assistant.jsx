import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Loader2, Sparkles, BrainCircuit, LayoutGrid, Receipt, Wallet, Target } from 'lucide-react';
import assistantApi from '../api/assistantApi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';

const quickLinks = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutGrid },
    { label: 'Transactions', path: '/transactions', icon: Receipt },
    { label: 'Accounts', path: '/accounts', icon: Wallet },
    { label: 'Goals', path: '/goals', icon: Target }
];

const suggestedQuestions = [
    "Analyze my spending this month",
    "Show my biggest expenses",
    "How is my portfolio performing?",
    "Explain SIP"
];

const Assistant = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const endOfMessagesRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    // Auto focus input on load
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, []);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        setInput('');
        
        // Add user message
        const newMsgId = Date.now();
        setMessages(prev => [...prev, { id: newMsgId, type: 'user', text: userMsg }]);
        setIsLoading(true);

        try {
            const response = await assistantApi.queryAssistant(userMsg);
            setMessages(prev => [...prev, { 
                id: Date.now() + 1, 
                type: 'bot', 
                text: response.answer,
                mode: response.mode_used
            }]);
        } catch (error) {
            console.error("Failed to fetch response:", error);
            setMessages(prev => [...prev, { 
                id: Date.now() + 1, 
                type: 'bot', 
                text: "I'm sorry, I encountered an error while processing your request. Please try again later."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AppShell>
            <div className="flex flex-col h-[calc(100vh-64px)] bg-white overflow-hidden relative font-sans text-gray-800 rounded-2xl shadow-sm border border-slate-200">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto pt-24 pb-48 w-full flex flex-col items-center">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center flex-1 h-full w-full max-w-3xl px-6 animate-fade-in-up">
                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl mb-8">
                            <Bot size={40} className="text-white" />
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-4 text-center">How can I help with your finances today?</h2>
                        <p className="text-gray-500 text-center mb-10 max-w-lg">
                            I can analyze your spending, check your goals, or explain complex financial concepts.
                        </p>
                        
                        {/* Empty State Suggested Questions */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                            {suggestedQuestions.map((q, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => { setInput(q); inputRef.current?.focus(); }}
                                    className="flex items-center p-4 rounded-2xl border border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-300 hover:shadow-sm transition-all text-left group"
                                >
                                    <Sparkles className="text-indigo-400 group-hover:text-indigo-600 mr-3 shrink-0 transition-colors" size={20} />
                                    <span className="text-sm font-medium text-gray-700">{q}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="w-full max-w-4xl px-4 md:px-8 space-y-8">
                        {messages.map((msg) => (
                            <div key={msg.id} className="w-full animate-fade-in">
                                {msg.type === 'user' ? (
                                    <div className="flex justify-end w-full">
                                        <div className="bg-indigo-600 text-white px-6 py-4 rounded-3xl rounded-tr-sm max-w-[85%] md:max-w-[75%] shadow-sm">
                                            <p className="whitespace-pre-wrap text-base font-medium">{msg.text}</p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex gap-4 md:gap-6 w-full">
                                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md">
                                            <Bot size={22} className="text-white" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="prose prose-base prose-indigo prose-a:text-indigo-600 max-w-none text-gray-800">
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {msg.text}
                                                </ReactMarkdown>
                                            </div>
                                            {msg.mode && (
                                                <div className="mt-2 text-xs font-semibold text-gray-400 flex items-center gap-1">
                                                    {msg.mode === 'personal' ? (
                                                        <><BrainCircuit size={12}/> Analyzed from your financial data</>
                                                    ) : (
                                                        <><Sparkles size={12}/> General knowledge base</>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                        
                        {isLoading && (
                            <div className="flex gap-4 md:gap-6 w-full animate-pulse">
                                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md">
                                    <Bot size={22} className="text-white" />
                                </div>
                                <div className="flex-1 flex items-center">
                                    <div className="flex gap-1.5 p-3 rounded-full bg-gray-100">
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{animationDelay: '0ms'}}></div>
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{animationDelay: '150ms'}}></div>
                                        <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{animationDelay: '300ms'}}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={endOfMessagesRef} />
                    </div>
                )}
            </div>

            {/* Input Area (Sticky Bottom) */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-transparent pt-12 pb-6 px-4">
                <div className="max-w-4xl mx-auto">
                    {/* Quick Links above input if chatting */}
                    {messages.length > 0 && (
                        <div className="flex justify-center gap-2 mb-4 overflow-x-auto pb-2 scrollbar-hide">
                            {quickLinks.map((link) => (
                                <button
                                    key={link.label}
                                    onClick={() => navigate(link.path)}
                                    className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-indigo-600 transition-colors shadow-sm whitespace-nowrap"
                                >
                                    <link.icon size={14} />
                                    {link.label}
                                </button>
                            ))}
                        </div>
                    )}
                    
                    <form onSubmit={handleSend} className="relative shadow-2xl rounded-2xl bg-white border border-gray-200 overflow-hidden">
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend(e);
                                }
                            }}
                            placeholder="Message Finance Analytics Assistant..."
                            className="w-full pl-5 pr-14 py-4 bg-transparent border-none focus:outline-none focus:ring-0 resize-none max-h-32 min-h-[56px] text-gray-700"
                            rows={1}
                            disabled={isLoading}
                            style={{ height: 'auto' }}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !input.trim()}
                            className={`absolute right-3 bottom-3 p-2 rounded-lg flex items-center justify-center transition-all ${
                                input.trim() && !isLoading
                                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            }`}
                        >
                            <Send size={18} className={isLoading ? "animate-pulse" : ""} />
                        </button>
                    </form>
                    <p className="text-center text-[10px] text-gray-400 mt-3 font-medium">
                        AI can make mistakes. Consider verifying important financial information.
                    </p>
                </div>
            </div>
            
            {/* CSS for custom animations */}
            <style>{`
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in-up {
                    animation: fadeInUp 0.5s ease-out forwards;
                }
                .animate-fade-in {
                    animation: fadeInUp 0.3s ease-out forwards;
                }
                .scrollbar-hide::-webkit-scrollbar {
                    display: none;
                }
                .scrollbar-hide {
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }
            `}</style>
            </div>
        </AppShell>
    );
};

export default Assistant;
