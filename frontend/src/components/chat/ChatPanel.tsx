import React, { useState, useEffect } from 'react';
import { chatService, Chat, Message } from '../../services/chatService';
import './ChatPanel.css';

interface ChatPanelProps {
  canvasId: number;
  onClose: () => void;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ canvasId, onClose }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [showNewChatModal, setShowNewChatModal] = useState(false);

  useEffect(() => {
    loadChats();
  }, [canvasId]);

  const loadChats = async () => {
    try {
      const data = await chatService.listChats(canvasId);
      setChats(data);
    } catch (error) {
      console.error('Failed to load chats:', error);
    }
  };

  const loadMessages = async (chatId: number) => {
    setLoading(true);
    try {
      const data = await chatService.getMessages(chatId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChat = (chat: Chat) => {
    setSelectedChat(chat);
    loadMessages(chat.id);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !selectedChat || sending) return;

    const userMessage = inputValue;
    setInputValue('');
    setSending(true);

    // Optimistically add user message
    const tempUserMessage: Message = {
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await chatService.sendMessage(selectedChat.id, {
        content: userMessage,
      });

      // Replace temp message and add assistant response
      setMessages(prev => {
        const withoutTemp = prev.slice(0, -1);
        return [...withoutTemp, tempUserMessage, response];
      });

      // Reload chat list to update message count
      loadChats();
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic message on error
      setMessages(prev => prev.slice(0, -1));
      setInputValue(userMessage); // Restore input
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const handleCreateChat = async (name: string, chatType: 'sales_assistant' | 'whats_next') => {
    try {
      const newChat = await chatService.createChat({
        canvas_id: canvasId,
        name,
        chat_type: chatType,
      });
      setChats(prev => [...prev, newChat]);
      setShowNewChatModal(false);
      handleSelectChat(newChat);
    } catch (error) {
      console.error('Failed to create chat:', error);
      alert('Failed to create chat. Please try again.');
    }
  };

  const handleDeleteChat = async (chatId: number) => {
    if (!confirm('Delete this chat? This cannot be undone.')) return;

    try {
      await chatService.deleteChat(chatId);
      setChats(prev => prev.filter(c => c.id !== chatId));
      if (selectedChat?.id === chatId) {
        setSelectedChat(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
      alert('Failed to delete chat.');
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-panel-header">
        <h2>AI Assistant</h2>
        <button className="btn-close-chat" onClick={onClose}>✕</button>
      </div>

      <div className="chat-panel-content">
        {/* Chat List Sidebar */}
        <div className="chat-list-sidebar">
          <button
            className="btn btn-primary btn-new-chat"
            onClick={() => setShowNewChatModal(true)}
          >
            + New Chat
          </button>

          <div className="chat-list">
            {chats.length === 0 ? (
              <p className="empty-chats">No chats yet. Create one to get started.</p>
            ) : (
              chats.map(chat => (
                <div
                  key={chat.id}
                  className={`chat-list-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
                  onClick={() => handleSelectChat(chat)}
                >
                  <div className="chat-list-item-header">
                    <span className="chat-name">{chat.name}</span>
                    <button
                      className="btn-delete-chat"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteChat(chat.id);
                      }}
                    >
                      🗑
                    </button>
                  </div>
                  <div className="chat-list-item-meta">
                    <span className={`chat-type-badge ${chat.chat_type}`}>
                      {chat.chat_type === 'sales_assistant' ? 'Sales Assistant' : "What's Next"}
                    </span>
                    <span className="message-count">{chat.message_count} messages</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Messages Area */}
        <div className="chat-messages-area">
          {!selectedChat ? (
            <div className="no-chat-selected">
              <p>Select a chat or create a new one to start</p>
            </div>
          ) : (
            <>
              <div className="chat-messages">
                {loading ? (
                  <div className="loading-messages">Loading messages...</div>
                ) : messages.length === 0 ? (
                  <div className="empty-messages">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                      <div className="message-role">
                        {msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                      </div>
                      <div className="message-content">
                        {msg.content.split('\n').map((line, i) => (
                          <p key={i}>{line || '\u00A0'}</p>
                        ))}
                      </div>
                      {msg.token_count && (
                        <div className="message-meta">
                          {msg.token_count} tokens
                        </div>
                      )}
                    </div>
                  ))
                )}
                {sending && (
                  <div className="message assistant">
                    <div className="message-role">🤖 AI Assistant</div>
                    <div className="message-content typing">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
              </div>

              <form className="chat-input-form" onSubmit={handleSendMessage}>
                <textarea
                  className="chat-input"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(e);
                    }
                  }}
                  placeholder="Ask for advice, next steps, competitive analysis..."
                  rows={3}
                  disabled={sending}
                />
                <button
                  type="submit"
                  className="btn btn-primary btn-send"
                  disabled={!inputValue.trim() || sending}
                >
                  {sending ? 'Sending...' : 'Send'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>

      {/* New Chat Modal */}
      {showNewChatModal && (
        <NewChatModal
          onClose={() => setShowNewChatModal(false)}
          onCreate={handleCreateChat}
        />
      )}
    </div>
  );
};

interface NewChatModalProps {
  onClose: () => void;
  onCreate: (name: string, chatType: 'sales_assistant' | 'whats_next') => void;
}

const NewChatModal: React.FC<NewChatModalProps> = ({ onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [chatType, setChatType] = useState<'sales_assistant' | 'whats_next'>('sales_assistant');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    onCreate(name, chatType);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>New Chat</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Chat Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Deal Strategy Discussion"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Chat Type</label>
            <select value={chatType} onChange={(e) => setChatType(e.target.value as any)}>
              <option value="sales_assistant">Sales Assistant - Ongoing conversation & advice</option>
              <option value="whats_next">What's Next - Quick deal analysis</option>
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={!name.trim()}>
              Create Chat
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;
