import React, { useState, useEffect } from 'react';
import { chatService, Message } from '../../services/chatService';

interface NodeChatProps {
  nodeId: number;
  canvasId: number;
  nodeTitle: string;
}

const NodeChat: React.FC<NodeChatProps> = ({ nodeId, canvasId, nodeTitle }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [chatId, setChatId] = useState<number | null>(null);
  const [includeCanvasContext, setIncludeCanvasContext] = useState(true);

  useEffect(() => {
    loadOrCreateChat();
  }, [nodeId]);

  const loadOrCreateChat = async () => {
    try {
      setLoading(true);
      // Try to find existing chat for this node
      const chats = await chatService.listNodeChats(nodeId);

      if (chats.length > 0) {
        // Use the first chat
        const chat = chats[0];
        setChatId(chat.id);
        const msgs = await chatService.getMessages(chat.id);
        setMessages(msgs);
      } else {
        // Create a new node chat
        const newChat = await chatService.createChat({
          canvas_id: canvasId,
          name: `${nodeTitle} Discussion`,
          chat_type: 'sales_assistant',
          node_id: nodeId,
        });
        setChatId(newChat.id);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to load/create node chat:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !chatId || sending) return;

    const userMessage = inputValue;
    setInputValue('');
    setSending(true);

    // Optimistic update
    const tempUserMessage: Message = {
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const response = await chatService.sendMessage(chatId, {
        content: userMessage,
        include_canvas_context: includeCanvasContext,
      });

      // Update with actual messages
      setMessages(prev => {
        const withoutTemp = prev.slice(0, -1);
        return [...withoutTemp, tempUserMessage, response];
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => prev.slice(0, -1));
      setInputValue(userMessage);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <div className="node-chat-loading">Loading chat...</div>;
  }

  return (
    <div className="node-chat">
      <div className="node-chat-context-toggle">
        <label>
          <input
            type="checkbox"
            checked={includeCanvasContext}
            onChange={(e) => setIncludeCanvasContext(e.target.checked)}
          />
          <span>Include full canvas context</span>
        </label>
        <p className="context-hint">
          {includeCanvasContext
            ? 'AI will see all nodes on this canvas'
            : 'AI will only see this node\'s information'}
        </p>
      </div>

      <div className="node-chat-messages">
        {messages.length === 0 ? (
          <div className="node-chat-empty">
            <p>Start a conversation about this {nodeTitle.toLowerCase()}</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`node-chat-message ${msg.role}`}>
              <div className="message-role">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line || '\u00A0'}</p>
                ))}
              </div>
            </div>
          ))
        )}
        {sending && (
          <div className="node-chat-message assistant">
            <div className="message-role">🤖</div>
            <div className="message-content typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>

      <form className="node-chat-input" onSubmit={handleSendMessage}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage(e);
            }
          }}
          placeholder="Ask about this node..."
          rows={2}
          disabled={sending}
        />
        <button
          type="submit"
          className="btn-send-node-chat"
          disabled={!inputValue.trim() || sending}
        >
          {sending ? '...' : '→'}
        </button>
      </form>
    </div>
  );
};

export default NodeChat;
