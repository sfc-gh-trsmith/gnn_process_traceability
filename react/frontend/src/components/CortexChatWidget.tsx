import { useState, useRef, useEffect, KeyboardEvent, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Trash2, Loader2, Bot, User, ChevronDown, Wrench, Maximize2, Minimize2, BarChart3 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import { VegaEmbed } from 'react-vega';
import type { VisualizationSpec } from 'vega-embed';
import { useCortexAgent } from '../hooks/useCortexAgent';
import type { CortexMessage, ToolCall } from '../types/cortex';

const suggestions = [
  'What defect patterns should I investigate?',
  'Show me the highest risk components',
  'Explain the root cause analysis for welding defects',
  'Which suppliers have quality issues?',
];

function VegaChart({ spec }: { spec: string }) {
  const parsedSpec = useMemo(() => {
    try {
      const parsed = JSON.parse(spec) as VisualizationSpec;
      return {
        ...parsed,
        width: 350,
        height: 200,
        autosize: { type: 'fit', contains: 'padding' },
        background: 'transparent',
        config: {
          axis: { labelColor: '#94a3b8', titleColor: '#94a3b8', gridColor: '#334155' },
          legend: { labelColor: '#94a3b8', titleColor: '#94a3b8' },
          title: { color: '#e2e8f0' },
          view: { stroke: 'transparent' },
        },
      } as VisualizationSpec;
    } catch {
      return null;
    }
  }, [spec]);

  if (!parsedSpec) return <div className="text-xs text-critical">Invalid chart spec</div>;

  return (
    <div className="w-full min-h-[220px]">
      <VegaEmbed spec={parsedSpec} />
    </div>
  );
}

function ToolCallDisplay({ tool }: { tool: ToolCall }) {
  const [expanded, setExpanded] = useState(false);

  const charts = useMemo(() => {
    if (tool.tool_name !== 'data_to_chart' || !tool.result) return [];
    try {
      const result = typeof tool.result === 'string' ? JSON.parse(tool.result) : tool.result;
      console.log('data_to_chart result:', result);
      if (result?.charts && Array.isArray(result.charts)) {
        return result.charts as string[];
      }
    } catch (e) {
      console.error('Error parsing chart result:', e);
    }
    return [];
  }, [tool]);

  const hasCharts = charts.length > 0;

  return (
    <div className="mt-2 rounded-lg bg-slate-800/50 border border-slate-700/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-slate-700/30 transition-colors"
      >
        {hasCharts ? (
          <BarChart3 className="w-3 h-3 text-purple" />
        ) : (
          <Wrench className="w-3 h-3 text-primary" />
        )}
        <span className="text-slate-300 font-medium">{tool.tool_name}</span>
        <span className={clsx(
          'ml-auto px-1.5 py-0.5 rounded text-[10px] font-medium',
          tool.status === 'complete' ? 'bg-success/20 text-success' :
          tool.status === 'error' ? 'bg-critical/20 text-critical' :
          'bg-warning/20 text-warning'
        )}>
          {tool.status || 'pending'}
        </span>
        <ChevronDown className={clsx('w-3 h-3 transition-transform', expanded && 'rotate-180')} />
      </button>
      
      {hasCharts && (
        <div className="px-3 py-3 border-t border-slate-700/50">
          {charts.map((chartSpec, i) => (
            <VegaChart key={i} spec={chartSpec} />
          ))}
        </div>
      )}
      
      {expanded && (
        <div className={clsx('px-3 py-2 text-[10px]', hasCharts && 'border-t border-slate-700/50')}>
          {tool.sql && (
            <div className="mb-2">
              <div className="text-slate-500 mb-1">SQL:</div>
              <pre className="bg-slate-900/50 p-2 rounded overflow-x-auto text-slate-300">{tool.sql}</pre>
            </div>
          )}
          {tool.result && (
            <div>
              <div className="text-slate-500 mb-1">Result:</div>
              <pre className="bg-slate-900/50 p-2 rounded overflow-x-auto text-slate-300 max-h-32">
                {typeof tool.result === 'string' ? tool.result : JSON.stringify(tool.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message, reasoningStage }: { message: CortexMessage; reasoningStage?: string }) {
  const isUser = message.role === 'user';

  return (
    <div className={clsx('flex gap-2', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div className={clsx(
        'flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center',
        isUser ? 'bg-primary/20' : 'bg-purple/20'
      )}>
        {isUser ? <User className="w-4 h-4 text-primary" /> : <Bot className="w-4 h-4 text-purple" />}
      </div>
      
      <div className={clsx(
        'flex-1 min-w-0',
        isUser ? 'text-right' : 'text-left'
      )}>
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mb-2 max-w-[85%]">
            {message.toolCalls.map((tool, i) => (
              <ToolCallDisplay key={i} tool={tool} />
            ))}
          </div>
        )}
        
        <div className={clsx(
          'inline-block max-w-[85%] rounded-2xl px-3 py-2 text-sm',
          isUser ? 'bg-primary text-white rounded-tr-sm' : 'bg-slate-800 text-slate-100 rounded-tl-sm'
        )}>
          {message.isStreaming && !message.content && reasoningStage ? (
            <div className="flex items-center gap-2 text-slate-400">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span className="text-xs">{reasoningStage}</span>
            </div>
          ) : (
            <div className="prose prose-sm prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-1.5 [&_p]:text-sm [&_li]:text-sm">
              <ReactMarkdown>{message.content || ''}</ReactMarkdown>
            </div>
          )}
        </div>
        
        {message.error && (
          <div className="mt-1 text-xs text-critical">{message.error}</div>
        )}
      </div>
    </div>
  );
}

export default function CortexChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { messages, isStreaming, error, reasoningStage, sendMessage, clearMessages } = useCortexAgent({
    endpoint: '/api/agent/run',
  });

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, reasoningStage]);

  useEffect(() => {
    if (isOpen && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = () => {
    if (input.trim() && !isStreaming) {
      sendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  return (
    <>
      <motion.button
        onClick={() => setIsOpen(true)}
        className={clsx(
          'fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center',
          'bg-gradient-to-br from-primary to-secondary hover:shadow-primary/30 hover:shadow-xl transition-shadow',
          isOpen && 'hidden'
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Open chat with Quality Engineer Agent"
      >
        <MessageCircle className="w-6 h-6 text-white" />
        {messages.length > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-accent rounded-full text-xs font-bold flex items-center justify-center text-background">
            {messages.filter(m => m.role === 'assistant').length}
          </span>
        )}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => !isFullScreen && setIsOpen(false)}
              className={clsx(
                'fixed inset-0 z-50',
                isFullScreen ? 'bg-black/60' : 'bg-black/40 backdrop-blur-sm'
              )}
            />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className={clsx(
                'fixed z-50 bg-card shadow-2xl border border-border flex flex-col overflow-hidden transition-all duration-300',
                isFullScreen
                  ? 'inset-4 rounded-xl'
                  : 'bottom-6 right-6 w-[420px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-3rem)] rounded-2xl'
              )}
            >
              <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-gradient-to-r from-primary/10 to-purple/10">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text text-sm">Quality Engineer Agent</h3>
                    <p className="text-xs text-text-secondary">Ask about defects, risks & patterns</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {messages.length > 0 && (
                    <button
                      onClick={(e) => { e.stopPropagation(); clearMessages(); }}
                      className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                      title="Clear chat"
                      aria-label="Clear chat history"
                    >
                      <Trash2 className="w-4 h-4 text-text-secondary" />
                    </button>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); setIsFullScreen(!isFullScreen); }}
                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                    title={isFullScreen ? 'Exit fullscreen' : 'Fullscreen'}
                    aria-label={isFullScreen ? 'Exit fullscreen' : 'Fullscreen'}
                  >
                    {isFullScreen ? (
                      <Minimize2 className="w-4 h-4 text-text-secondary" />
                    ) : (
                      <Maximize2 className="w-4 h-4 text-text-secondary" />
                    )}
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                    aria-label="Close chat"
                  >
                    <X className="w-4 h-4 text-text-secondary" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center px-4">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-purple/20 flex items-center justify-center mb-4">
                      <Bot className="w-8 h-8 text-primary" />
                    </div>
                    <h4 className="font-semibold text-text mb-1">Quality Engineer Agent</h4>
                    <p className="text-sm text-text-secondary mb-6">
                      I can help you analyze defects, trace root causes, and identify quality risks in your process data.
                    </p>
                    <div className="space-y-2 w-full">
                      <p className="text-xs text-text-secondary mb-2">Try asking:</p>
                      {suggestions.map((s, i) => (
                        <button
                          key={i}
                          onClick={() => handleSuggestionClick(s)}
                          className="w-full text-left px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 text-sm text-slate-300 transition-colors"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((msg) => (
                      <MessageBubble
                        key={msg.id}
                        message={msg}
                        reasoningStage={msg.isStreaming ? reasoningStage : undefined}
                      />
                    ))}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {error && (
                <div className="px-4 py-2 bg-critical/10 border-t border-critical/20 text-critical text-xs">
                  {error}
                </div>
              )}

              <div className="p-3 border-t border-border">
                <div className="flex gap-2">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about quality issues..."
                    rows={1}
                    className="flex-1 resize-none bg-background border border-border rounded-xl px-3 py-2 text-sm text-text placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    disabled={isStreaming}
                  />
                  <button
                    onClick={handleSubmit}
                    disabled={!input.trim() || isStreaming}
                    className={clsx(
                      'px-4 rounded-xl transition-all flex items-center justify-center',
                      input.trim() && !isStreaming
                        ? 'bg-primary hover:bg-primary/80 text-white'
                        : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    )}
                    aria-label="Send message"
                  >
                    {isStreaming ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
