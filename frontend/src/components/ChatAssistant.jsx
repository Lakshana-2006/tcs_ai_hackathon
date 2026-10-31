import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  RotateCcw, 
  Minimize2, 
  Maximize2,
  AlertCircle, 
  CheckCircle2, 
  Terminal, 
  HelpCircle,
  ChevronDown,
  Layers,
  Thermometer,
  ShieldAlert
} from 'lucide-react';
import { sendChatMessage } from '../api';

export default function ChatAssistant({
  city,
  weather,
  zones = [],
  selectedZone,
  selectedInterventions = {},
  simulationResult
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }, [messages, isOpen, isMinimized, loading]);

  // Focus textarea when panel opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      textareaRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  // Suggested starter queries
  const starterQuestions = [
    "Which zone has the highest heat risk?",
    `Why is ${selectedZone?.short_name || selectedZone?.name || 'this zone'} vulnerable?`,
    "Explain current simulation results",
    "Cooling centers vs tree planting: what is the difference?"
  ];

  // Prepare active dashboard context payload
  const buildContextPayload = () => {
    return {
      city: city || null,
      weather: weather || null,
      zones: zones || [],
      selected_zone: selectedZone || (zones.length > 0 ? zones[0] : null),
      selected_interventions: selectedInterventions || {},
      simulation_result: simulationResult || null
    };
  };

  const handleSend = async (textToSend = null) => {
    const query = (textToSend !== null ? textToSend : input).trim();
    if (!query || loading) return;

    setError(null);
    setInput('');
    setHasInteracted(true);

    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setLoading(true);

    try {
      // Pass previous turns for conversational continuity
      const historyPayload = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const contextPayload = buildContextPayload();
      const res = await sendChatMessage(query, historyPayload, contextPayload);

      const assistantMessage = {
        role: 'assistant',
        content: res.reply,
        isConfigured: res.is_configured,
        provider: res.provider,
        setupInstructions: res.setup_instructions,
        contextUsed: res.context_used,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages([...updatedHistory, assistantMessage]);
    } catch (err) {
      console.error('Chat Assistant error:', err);
      setError(err.message || 'Unable to reach the AI Assistant backend.');
      const errorMessage = {
        role: 'assistant',
        content: `⚠️ Communication Error: ${err.message || 'Could not connect to the assistant server.'}. Please verify that the backend is running.`,
        isError: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages([...updatedHistory, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleResetChat = () => {
    setMessages([]);
    setError(null);
  };

  // Helper to format basic markdown-style text (bold, headers, bullets, code)
  const renderFormattedContent = (content) => {
    if (!content) return null;

    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Code blocks start or end
      if (line.trim().startsWith('```')) {
        return (
          <div key={idx} className="my-1 border-t border-slate-700/60 font-mono text-[10px] text-emerald-400">
            {line.replace(/```[a-z]*/g, '')}
          </div>
        );
      }

      // Headers (### or ####)
      if (line.startsWith('#### ')) {
        return <h5 key={idx} className="font-bold text-slate-200 text-xs mt-2 mb-1">{line.replace('#### ', '')}</h5>;
      }
      if (line.startsWith('### ')) {
        return <h4 key={idx} className="font-bold text-emerald-300 text-xs mt-2.5 mb-1 flex items-center gap-1.5">{line.replace('### ', '')}</h4>;
      }

      // Bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*')) {
        const bulletText = line.trim().replace(/^[-*•]\s*/, '');
        return (
          <li key={idx} className="ml-3 list-disc my-0.5 text-slate-300">
            {renderInlineMarkdown(bulletText)}
          </li>
        );
      }

      // Standard line
      if (line.trim().length === 0) {
        return <div key={idx} className="h-1.5" />;
      }

      return (
        <p key={idx} className="my-0.5 leading-relaxed text-slate-300">
          {renderInlineMarkdown(line)}
        </p>
      );
    });
  };

  // Inline markdown (bold **text**, inline `code`)
  const renderInlineMarkdown = (text) => {
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="bg-slate-800 text-emerald-300 px-1 py-0.2 rounded text-[11px] font-mono border border-slate-700">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  const activeZoneName = selectedZone?.short_name || selectedZone?.name || 'Zone Profile';

  return (
    <>
      {/* 1. Floating Toggle Button (Bottom-Right) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-xl shadow-emerald-950/50 hover:shadow-emerald-500/30 border border-emerald-400/30 transition-all duration-300 hover:scale-105 active:scale-95 group"
          aria-label="Open HEATSHIELD AI Assistant"
        >
          <div className="relative">
            <Bot className="w-5 h-5 text-white animate-pulse" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-300 ring-2 ring-slate-950"></span>
          </div>
          <span className="text-xs font-bold tracking-wide uppercase font-mono">
            AI Assistant
          </span>
          <span className="text-[10px] bg-emerald-900/80 px-2 py-0.5 rounded-full text-emerald-200 border border-emerald-500/40 hidden sm:inline-block">
            {city?.name || 'Digital Twin'}
          </span>
        </button>
      )}

      {/* 2. Floating AI Chat Panel */}
      {isOpen && (
        <div 
          className={`fixed bottom-6 right-6 z-50 flex flex-col bg-slate-900/95 backdrop-blur-xl border border-slate-800 shadow-2xl shadow-black/80 rounded-2xl overflow-hidden transition-all duration-300 font-sans ${
            isMinimized 
              ? 'w-72 h-14' 
              : 'w-[calc(100vw-2rem)] sm:w-[460px] h-[600px] max-h-[85vh]'
          }`}
        >
          {/* Header */}
          <div className="bg-slate-950/80 border-b border-slate-800 px-4 py-3 flex items-center justify-between shrink-0 select-none">
            <div className="flex items-center gap-2.5">
              <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
                <Bot className="w-4 h-4" />
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-white tracking-wide">
                    HEATSHIELD AI Assistant
                  </h3>
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                    Live
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono mt-0.5 truncate max-w-[240px]">
                  <span>{city?.name || 'Metro'}</span>
                  <span>•</span>
                  <span className="truncate">{activeZoneName}</span>
                </div>
              </div>
            </div>

            {/* Window Controls */}
            <div className="flex items-center gap-1 text-slate-400">
              <button
                type="button"
                onClick={handleResetChat}
                className="p-1 rounded hover:bg-slate-800 hover:text-slate-200 transition"
                title="Clear conversation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 rounded hover:bg-slate-800 hover:text-slate-200 transition"
                title={isMinimized ? "Expand" : "Minimize"}
              >
                {isMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
              </button>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1 rounded hover:bg-slate-800 hover:text-rose-400 transition"
                title="Close Assistant"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Panel Body (Hidden when minimized) */}
          {!isMinimized && (
            <>
              {/* Context Telemetry Pill Bar */}
              <div className="bg-slate-950/60 border-b border-slate-800/80 px-4 py-1.5 flex items-center justify-between text-[10px] text-slate-400 font-mono shrink-0">
                <span className="flex items-center gap-1">
                  <Thermometer className="w-3 h-3 text-cyan-400" />
                  {weather ? `${weather.air_temperature_c}°C air • ${weather.apparent_temperature_c}°C heat index` : 'Telemetry synced'}
                </span>
                <span className="text-emerald-400 truncate max-w-[170px]">
                  {selectedZone ? `Risk: ${selectedZone.baseline_risk}/100` : 'Zone active'}
                </span>
              </div>

              {/* Chat Message History */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
                {/* Initial Welcome Message */}
                <div className="flex items-start gap-2.5">
                  <div className="w-6 h-6 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                  <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-slate-300 leading-relaxed max-w-[90%] space-y-2">
                    <p>
                      Hello! I am your <strong>HEATSHIELD AI Assistant</strong>.
                    </p>
                    <p className="text-[11px] text-slate-400">
                      I have real-time access to the active digital twin for <strong>{city?.name || 'your city'}</strong>, its 5 analysis zones, current weather telemetry, and your What-If intervention model.
                    </p>
                  </div>
                </div>

                {/* Starter Questions (show if conversation is fresh) */}
                {messages.length === 0 && (
                  <div className="pt-1 pb-1 space-y-1.5">
                    <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block pl-1">
                      Suggested Inquiries:
                    </span>
                    <div className="flex flex-col gap-1.5">
                      {starterQuestions.map((q, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => handleSend(q)}
                          className="text-left text-xs px-3 py-2 rounded-lg bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-emerald-500/40 text-slate-300 transition flex items-center justify-between group"
                        >
                          <span className="truncate mr-2">{q}</span>
                          <span className="text-emerald-400 opacity-0 group-hover:opacity-100 transition shrink-0 font-mono text-[10px]">
                            Ask ↵
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Conversation Turns */}
                {messages.map((msg, index) => {
                  const isUser = msg.role === 'user';

                  return (
                    <div 
                      key={index} 
                      className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      <div 
                        className={`w-6 h-6 rounded flex items-center justify-center shrink-0 mt-0.5 text-xs font-mono font-bold ${
                          isUser 
                            ? 'bg-slate-700 text-slate-200 border border-slate-600' 
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {isUser ? 'U' : <Bot className="w-3.5 h-3.5" />}
                      </div>

                      <div 
                        className={`rounded-xl p-3 leading-relaxed max-w-[85%] ${
                          isUser 
                            ? 'bg-emerald-600/20 border border-emerald-500/30 text-white' 
                            : msg.isError
                              ? 'bg-rose-950/40 border border-rose-500/30 text-rose-200'
                              : 'bg-slate-950/80 border border-slate-800 text-slate-300'
                        }`}
                      >
                        <div className="text-[11.5px]">
                          {renderFormattedContent(msg.content)}
                        </div>
                        <div className={`text-[9px] font-mono mt-1 text-right ${isUser ? 'text-emerald-400/70' : 'text-slate-500'}`}>
                          {msg.timestamp}
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Loading / Thinking Indicator */}
                {loading && (
                  <div className="flex items-start gap-2.5">
                    <div className="w-6 h-6 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="w-3.5 h-3.5 animate-spin" />
                    </div>
                    <div className="bg-slate-950/70 border border-slate-800 rounded-xl px-3 py-2 text-slate-400 text-xs flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                      <span>Analyzing digital twin telemetry...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Message Input Footer */}
              <div className="bg-slate-950/90 border-t border-slate-800 p-3 shrink-0">
                <form 
                  onSubmit={(e) => { e.preventDefault(); handleSend(); }} 
                  className="space-y-1.5"
                >
                  <div className="relative flex items-center">
                    <textarea
                      ref={textareaRef}
                      rows={1}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={`Ask about ${city?.name || 'the city'}, heat risk, or interventions...`}
                      className="w-full resize-none rounded-xl bg-slate-900 border border-slate-700/80 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none transition pr-10 min-h-[40px] max-h-[100px]"
                      disabled={loading}
                    />

                    <button
                      type="submit"
                      disabled={!input.trim() || loading}
                      className="absolute right-1.5 p-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-800 text-slate-950 disabled:text-slate-600 transition disabled:opacity-40"
                      title="Send message (Enter)"
                    >
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono px-1">
                    <span>Press <kbd className="text-slate-400 font-semibold">Enter ↵</kbd> to send</span>
                    <span><kbd className="text-slate-400 font-semibold">Shift + Enter</kbd> for new line</span>
                  </div>
                </form>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}

