'use client';
import { useState, useRef, useEffect } from 'react';

const FASTAPI_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Message = { role: 'user' | 'assistant'; content: string };
type Chat = { id: string; title: string; messages: Message[] };

function BotIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="11" width="18" height="10" rx="2"/>
      <circle cx="12" cy="5" r="2"/>
      <path d="M12 7v4"/>
      <line x1="8" y1="16" x2="8" y2="16"/>
      <line x1="16" y1="16" x2="16" y2="16"/>
    </svg>
  );
}

function UserIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <circle cx="12" cy="8" r="4"/>
      <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="3 6 5 6 21 6"/>
      <path d="M19 6l-1 14H6L5 6"/>
      <path d="M10 11v6M14 11v6"/>
      <path d="M9 6V4h6v2"/>
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
    </svg>
  );
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([
    { id: '1', title: 'New conversation', messages: [] }
  ]);
  const [activeChatId, setActiveChatId] = useState('1');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const activeChat = chats.find(c => c.id === activeChatId)!;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeChat?.messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  function showToast(msg: string, type: 'success' | 'error') {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }

  function newChat() {
    const id = Date.now().toString();
    setChats(prev => [{ id, title: 'New conversation', messages: [] }, ...prev]);
    setActiveChatId(id);
    setInput('');
  }

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: 'user', content: input.trim() };
    const updatedMessages = [...activeChat.messages, userMsg];

    setChats(prev => prev.map(c => c.id === activeChatId ? {
      ...c,
      title: c.messages.length === 0 ? input.trim().slice(0, 40) : c.title,
      messages: updatedMessages
    } : c));
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${FASTAPI_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updatedMessages }),
      });
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      const assistantMsg: Message = { role: 'assistant', content: data.reply || data.message || data.content };
      setChats(prev => prev.map(c => c.id === activeChatId ? {
        ...c, messages: [...updatedMessages, assistantMsg]
      } : c));
    } catch {
      showToast('Failed to send message. Is the backend running?', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${FASTAPI_BASE}/api/upload`, {
        method: 'POST',
        headers: { 'accept': 'application/json' },
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      showToast(`"${file.name}" uploaded — ${data.chunks} chunks indexed`, 'success');
    } catch {
      showToast('Upload failed. Check backend connection.', 'error');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  async function clearKnowledge() {
    if (!confirm('Clear all knowledge base files? This cannot be undone.')) return;
    setClearing(true);
    try {
      const res = await fetch(`${FASTAPI_BASE}/api/reset-knowledgebase`, {
        method: 'DELETE',
        headers: { 'accept': 'application/json' },
      });
      if (!res.ok) throw new Error('Clear failed');
      const data = await res.json();
      showToast(data.message || 'Knowledge base cleared', 'success');
    } catch {
      showToast('Failed to clear knowledge base.', 'error');
    } finally {
      setClearing(false);
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#212121', color: '#ececec', fontFamily: "'Inter', -apple-system, sans-serif", overflow: 'hidden' }}>

      {/* Sidebar */}
      <div style={{
        width: sidebarOpen ? 260 : 0,
        minWidth: sidebarOpen ? 260 : 0,
        background: '#171717',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.2s ease',
        overflow: 'hidden',
        borderRight: '1px solid #2a2a2a',
      }}>
        {/* Sidebar header */}
        <div style={{ padding: '12px 12px 8px', display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={newChat} style={{
            flex: 1, display: 'flex', alignItems: 'center', gap: 8,
            background: 'none', border: '1px solid #333', borderRadius: 8,
            color: '#ececec', padding: '8px 12px', cursor: 'pointer', fontSize: 13,
            transition: 'background 0.15s',
          }}
            onMouseEnter={e => (e.currentTarget.style.background = '#2a2a2a')}
            onMouseLeave={e => (e.currentTarget.style.background = 'none')}
          >
            <PlusIcon /> New chat
          </button>
        </div>

        {/* Knowledge base section */}
        <div style={{ padding: '4px 12px 8px' }}>
          <div style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6, paddingLeft: 4 }}>Knowledge Base</div>
          <div style={{ display: 'flex', gap: 6 }}>
            <button onClick={() => fileInputRef.current?.click()} disabled={uploading} style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              background: uploading ? '#1a3a2a' : '#1a2a1a', border: '1px solid #2d4a2d',
              borderRadius: 7, color: uploading ? '#4a9a5a' : '#5cb85c', padding: '7px 10px',
              cursor: uploading ? 'not-allowed' : 'pointer', fontSize: 12, transition: 'all 0.15s',
            }}
              onMouseEnter={e => !uploading && (e.currentTarget.style.background = '#223022')}
              onMouseLeave={e => !uploading && (e.currentTarget.style.background = '#1a2a1a')}
            >
              <UploadIcon />
              {uploading ? 'Uploading…' : 'Upload'}
            </button>
            <button onClick={clearKnowledge} disabled={clearing} style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              background: clearing ? '#3a1a1a' : '#2a1a1a', border: '1px solid #4a2d2d',
              borderRadius: 7, color: clearing ? '#c0504d' : '#e05555', padding: '7px 10px',
              cursor: clearing ? 'not-allowed' : 'pointer', fontSize: 12, transition: 'all 0.15s',
            }}
              onMouseEnter={e => !clearing && (e.currentTarget.style.background = '#321a1a')}
              onMouseLeave={e => !clearing && (e.currentTarget.style.background = '#2a1a1a')}
            >
              <TrashIcon />
              {clearing ? 'Clearing…' : 'Clear'}
            </button>
          </div>
          <input ref={fileInputRef} type="file" style={{ display: 'none' }} onChange={uploadFile} accept=".pdf,.txt,.md,.docx,.csv" />
        </div>

        <div style={{ height: 1, background: '#2a2a2a', margin: '0 12px 8px' }} />

        {/* Chat list */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
          <div style={{ fontSize: 10, color: '#555', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6, paddingLeft: 6 }}>Conversations</div>
          {chats.map(chat => (
            <button key={chat.id} onClick={() => setActiveChatId(chat.id)} style={{
              width: '100%', display: 'flex', alignItems: 'center', gap: 8,
              background: chat.id === activeChatId ? '#2a2a2a' : 'none',
              border: 'none', borderRadius: 7, color: chat.id === activeChatId ? '#fff' : '#999',
              padding: '8px 10px', cursor: 'pointer', fontSize: 13, textAlign: 'left',
              marginBottom: 2, transition: 'all 0.15s',
            }}
              onMouseEnter={e => chat.id !== activeChatId && (e.currentTarget.style.background = '#222')}
              onMouseLeave={e => chat.id !== activeChatId && (e.currentTarget.style.background = 'none')}
            >
              <span style={{ color: '#555', flexShrink: 0 }}><ChatIcon /></span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{chat.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>

        {/* Top bar */}
        <div style={{ display: 'flex', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid #2a2a2a', gap: 12 }}>
          <button onClick={() => setSidebarOpen(o => !o)} style={{
            background: 'none', border: 'none', color: '#666', cursor: 'pointer', padding: 6,
            borderRadius: 6, display: 'flex', alignItems: 'center',
          }}
            onMouseEnter={e => (e.currentTarget.style.background = '#2a2a2a')}
            onMouseLeave={e => (e.currentTarget.style.background = 'none')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <span style={{ fontSize: 14, color: '#888', fontWeight: 500 }}>
            {activeChat?.title || 'New conversation'}
          </span>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px 0' }}>
          {activeChat?.messages.length === 0 && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 16, color: '#555' }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: '#2a2a2a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
                <BotIcon />
              </div>
              <div style={{ fontSize: 22, fontWeight: 600, color: '#888' }}>How can I help you?</div>
              <div style={{ fontSize: 14, color: '#555' }}>Ask anything or upload files to your knowledge base</div>
            </div>
          )}

          {activeChat?.messages.map((m, i) => (
            <div key={i} style={{
              maxWidth: 780, margin: '0 auto', padding: '8px 24px',
              display: 'flex', gap: 16, alignItems: 'flex-start',
            }}>
              <div style={{
                width: 32, height: 32, borderRadius: '50%', flexShrink: 0, marginTop: 2,
                background: m.role === 'user' ? '#5b5bd6' : '#2a2a2a',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: m.role === 'user' ? '#fff' : '#999',
              }}>
                {m.role === 'user' ? <UserIcon /> : <BotIcon />}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: m.role === 'user' ? '#a8a8f8' : '#888', marginBottom: 6 }}>
                  {m.role === 'user' ? 'You' : 'Assistant'}
                </div>
                <div style={{
                  fontSize: 15, lineHeight: 1.7, color: '#ddd',
                  whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                }}>
                  {m.content}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ maxWidth: 780, margin: '0 auto', padding: '8px 24px', display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#2a2a2a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999', flexShrink: 0 }}>
                <BotIcon />
              </div>
              <div style={{ paddingTop: 10, display: 'flex', gap: 5 }}>
                {[0, 1, 2].map(i => (
                  <div key={i} style={{
                    width: 7, height: 7, borderRadius: '50%', background: '#555',
                    animation: 'pulse 1.2s ease-in-out infinite',
                    animationDelay: `${i * 0.2}s`,
                  }} />
                ))}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div style={{ padding: '16px 24px 24px', borderTop: '1px solid #2a2a2a' }}>
          <div style={{ maxWidth: 780, margin: '0 auto' }}>
            <div style={{
              display: 'flex', alignItems: 'flex-end', gap: 10,
              background: '#2a2a2a', borderRadius: 14, padding: '10px 14px',
              border: '1px solid #363636', transition: 'border-color 0.15s',
            }}
              onFocusCapture={e => (e.currentTarget.style.borderColor = '#555')}
              onBlurCapture={e => (e.currentTarget.style.borderColor = '#363636')}
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                placeholder="Message…"
                rows={1}
                style={{
                  flex: 1, background: 'none', border: 'none', outline: 'none',
                  color: '#ececec', fontSize: 15, lineHeight: 1.6, resize: 'none',
                  fontFamily: 'inherit', maxHeight: 200, overflowY: 'auto',
                }}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                style={{
                  width: 34, height: 34, borderRadius: 8, flexShrink: 0,
                  background: input.trim() && !loading ? '#5b5bd6' : '#333',
                  border: 'none', color: input.trim() && !loading ? '#fff' : '#555',
                  cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.15s',
                }}
              >
                <SendIcon />
              </button>
            </div>
            <div style={{ textAlign: 'center', fontSize: 12, color: '#444', marginTop: 10 }}>
              Press Enter to send · Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 32, left: '50%', transform: 'translateX(-50%)',
          background: toast.type === 'success' ? '#1a3a2a' : '#3a1a1a',
          border: `1px solid ${toast.type === 'success' ? '#2d5a3d' : '#5a2d2d'}`,
          color: toast.type === 'success' ? '#6fcf97' : '#eb5757',
          padding: '10px 20px', borderRadius: 10, fontSize: 13, fontWeight: 500,
          boxShadow: '0 4px 24px rgba(0,0,0,0.4)', zIndex: 1000,
          animation: 'fadeIn 0.2s ease',
        }}>
          {toast.msg}
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); } 40% { opacity: 1; transform: scale(1); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateX(-50%) translateY(8px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        body { margin: 0; }
      `}</style>
    </div>
  );
}