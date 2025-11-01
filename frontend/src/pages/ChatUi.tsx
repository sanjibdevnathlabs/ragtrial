import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, DocumentArrowUpIcon, TrashIcon, ArrowPathIcon } from '@heroicons/react/24/solid';
import SourcesAccordion from '../components/SourcesAccordion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

interface Source {
  filename: string;
  chunk_index: number;
  content: string;
}

interface FileInfo {
  file_id: string;
  filename: string;
  file_size: number;
  indexed: boolean;
}

/**
 * Chat UI page component
 * 
 * Native React chat interface for RAG queries.
 * Replaces Streamlit iframe with a modern, responsive chat UI.
 */
export default function ChatUi() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load files on mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const response = await fetch('/api/v1/files');
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await loadFiles();
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.answer || 'No answer provided.',
          sources: data.sources || [],
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const error = await response.json();
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Error: ${error.error || 'Failed to get response'}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Query error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Error: Failed to connect to the server.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 pt-16">
      {/* Hero Section */}
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">
            <span className="gradient-text">RAG Document Chat</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Upload documents, ask questions, and get AI-powered answers with source attribution
          </p>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="glass rounded-xl p-6 sticky top-24">
              {/* File Upload */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">Upload Documents</h3>
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileUpload}
                  accept=".pdf,.txt,.md,.docx,.csv,.json"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg cursor-pointer transition-all ${
                    isUploading
                      ? 'bg-slate-600 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'
                  }`}
                >
                  {isUploading ? (
                    <>
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <DocumentArrowUpIcon className="w-5 h-5" />
                      <span>Upload File</span>
                    </>
                  )}
                </label>
                <p className="text-xs text-slate-400 mt-2">
                  PDF, TXT, MD, DOCX, CSV, JSON
                </p>
              </div>

              {/* Indexed Documents */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-3">
                  Indexed Documents ({files.filter(f => f.indexed).length})
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {files.filter(f => f.indexed).map((file) => (
                    <div
                      key={file.file_id}
                      className="bg-slate-700/50 rounded-lg p-3 text-sm"
                    >
                      <p className="text-white font-medium truncate" title={file.filename}>
                        {file.filename}
                      </p>
                      <p className="text-slate-400 text-xs">
                        {(file.file_size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  ))}
                  {files.filter(f => f.indexed).length === 0 && (
                    <p className="text-slate-400 text-sm">No documents indexed yet</p>
                  )}
                </div>
              </div>

              {/* Actions */}
              <button
                onClick={handleClearChat}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 transition-all"
              >
                <TrashIcon className="w-5 h-5" />
                <span>Clear Chat</span>
              </button>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="glass rounded-xl overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 20rem)' }}>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-slate-400 mt-20">
                    <p className="text-xl mb-2">👋 Welcome to RAG Chat!</p>
                    <p>Upload documents and start asking questions.</p>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-3xl rounded-2xl px-6 py-4 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                          : 'bg-slate-700/50 text-slate-100'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      
                      {/* Sources - Collapsible Accordion */}
                      {message.sources && message.sources.length > 0 && (
                        <SourcesAccordion 
                          sources={message.sources} 
                          defaultExpanded={false}
                        />
                      )}

                      <p className="text-xs opacity-60 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-700/50 rounded-2xl px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-white/10 p-6">
                <div className="flex gap-3">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Ask a question about your documents..."
                    className="flex-1 bg-slate-700/50 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                    rows={2}
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!input.trim() || isLoading}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    <PaperAirplaneIcon className="w-6 h-6" />
                  </button>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Press Enter to send, Shift+Enter for new line
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
