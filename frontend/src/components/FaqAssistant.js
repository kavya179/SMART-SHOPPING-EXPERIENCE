import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { askFaqAssistant } from '../services/api';
import './FaqAssistant.css';

const DEFAULT_PROMPTS = [
  '👋 Hi! What can you do?',
  'Which products contain Vitamin C or Niacinamide?',
  'What products are best for oily skin?',
  'Show products under ₹500',
  'How do I perform a patch test?',
  'What is the shipping and return policy?',
];

function formatMessageText(text) {
  if (!text) return null;

  // Split by line breaks
  const lines = text.split('\n');
  return lines.map((line, lineIdx) => {
    if (!line.trim()) {
      return <div key={lineIdx} className="faq-line-spacer" />;
    }

    // Replace **bold** with <strong> and *italic* with <em>
    const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    const formattedLine = parts.map((part, partIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={partIdx}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={partIdx}>{part.slice(1, -1)}</em>;
      }
      return part;
    });

    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
      return (
        <div key={lineIdx} className="faq-bullet-item">
          {formattedLine}
        </div>
      );
    }

    if (line.trim().startsWith('|')) {
      return (
        <div key={lineIdx} className="faq-table-row-text">
          {formattedLine}
        </div>
      );
    }

    return (
      <p key={lineIdx} className="faq-text-para">
        {formattedLine}
      </p>
    );
  });
}

export default function FaqAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationContextProductId, setConversationContextProductId] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState(DEFAULT_PROMPTS);

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: "👋 Hi! I'm the **Joyory Catalog & AI Assistant**.\n\nAsk me about **specific products**, **prices**, **active ingredients**, **routine steps**, **budget filters** (e.g. *'under ₹500'*), or compare two products from our live catalog.",
      intentLabel: '👋 Welcome Assistant',
      disclaimer: "⚠️ Demo Catalog Assistant: Grounded in SQLite catalog specifications. Not medical advice.",
      referencedProducts: [],
      suggestedQuestions: DEFAULT_PROMPTS,
    },
  ]);

  const location = useLocation();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Detect if user is currently on a product detail page (e.g., /products/14)
  const productMatch = location.pathname.match(/\/products\/(\d+)/);
  const activeProductId = productMatch ? parseInt(productMatch[1], 10) : null;

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  }, [isOpen, messages]);

  const handleSendMessage = async (queryText = null) => {
    const query = (queryText || inputQuery).trim();
    if (!query || loading) return;

    const userMessageId = Date.now();
    const newUserMessage = {
      id: userMessageId,
      sender: 'user',
      text: query,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const response = await askFaqAssistant(query, activeProductId, conversationContextProductId);

      // Update conversation context if returned by backend
      if (response.context_product_id) {
        setConversationContextProductId(response.context_product_id);
      }

      if (response.suggested_questions && response.suggested_questions.length > 0) {
        setSuggestedQuestions(response.suggested_questions);
      }

      const assistantMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: response.answer || "I couldn't find specific catalog data for that query.",
        intentLabel: response.intent_label,
        disclaimer: response.disclaimer,
        referencedProducts: response.referenced_products || [],
        found: response.found,
        suggestedQuestions: response.suggested_questions || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: "Sorry, I encountered an issue connecting to the catalog database. Please ensure the backend server is running and try again.",
        disclaimer: "⚠️ Connection error. No medical advice provided.",
        referencedProducts: [],
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const clearChat = () => {
    setConversationContextProductId(null);
    setSuggestedQuestions(DEFAULT_PROMPTS);
    setMessages([
      {
        id: Date.now(),
        sender: 'assistant',
        text: "✨ Conversation cleared. What else can I help you find or understand in our catalog?",
        disclaimer: "⚠️ Demo Catalog Assistant: Not medical advice.",
        referencedProducts: [],
        suggestedQuestions: DEFAULT_PROMPTS,
      },
    ]);
  };

  return (
    <div className="faq-assistant-wrapper">
      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          className="faq-launcher-btn"
          onClick={() => setIsOpen(true)}
          aria-label="Open Beauty FAQ Assistant"
          id="open-faq-assistant-btn"
        >
          <span className="faq-launcher-icon">✨</span>
          <span className="faq-launcher-text">Beauty AI & FAQ</span>
          <span className="faq-launcher-pulse"></span>
        </button>
      )}

      {/* Floating Chat Drawer Window */}
      {isOpen && (
        <div className="faq-chat-window animate-slide-up" id="faq-assistant-modal">
          {/* Header */}
          <div className="faq-header">
            <div className="faq-header-info">
              <div className="faq-avatar">
                <span>🌸</span>
              </div>
              <div>
                <h6 className="faq-title">Joyory Catalog Assistant</h6>
                <div className="faq-subtitle">
                  <span className="faq-status-dot"></span>
                  <span>Conversational & Live SQLite Grounded</span>
                </div>
              </div>
            </div>
            <div className="faq-header-actions">
              <button
                className="faq-action-btn"
                onClick={clearChat}
                title="Clear Conversation Context"
                aria-label="Clear Conversation"
              >
                🔄
              </button>
              <button
                className="faq-action-btn"
                onClick={() => setIsOpen(false)}
                title="Close Assistant"
                aria-label="Close Assistant"
                id="close-faq-assistant-btn"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Non-Medical Notice Banner */}
          <div className="faq-notice-bar">
            <span className="faq-notice-icon">🛡️</span>
            <span>Demo Assistant &middot; Catalog specifications only &middot; Not medical advice</span>
          </div>

          {/* Quick Suggestion Chips */}
          <div className="faq-suggestions-rail">
            {activeProductId && (
              <button
                className="faq-chip faq-chip-contextual"
                onClick={() => handleSendMessage('How do I use this product and what are the directions?')}
              >
                📋 How to use this product?
              </button>
            )}
            {activeProductId && (
              <button
                className="faq-chip faq-chip-contextual"
                onClick={() => handleSendMessage('What are the key ingredients and full INCI in this?')}
              >
                🔬 Show ingredients
              </button>
            )}
            {suggestedQuestions.map((prompt, idx) => (
              <button
                key={idx}
                className="faq-chip"
                onClick={() => handleSendMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Messages Stream */}
          <div className="faq-messages-container">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`faq-message-row ${msg.sender === 'user' ? 'faq-msg-user' : 'faq-msg-assistant'}`}
              >
                {msg.sender === 'assistant' && (
                  <div className="faq-msg-avatar">🌿</div>
                )}
                <div className="faq-bubble">
                  {/* Intent Badge */}
                  {msg.intentLabel && msg.sender === 'assistant' && (
                    <div className="faq-intent-tag">{msg.intentLabel}</div>
                  )}

                  <div className="faq-bubble-content">
                    {formatMessageText(msg.text)}
                  </div>

                  {/* Referenced Products List */}
                  {msg.referencedProducts && msg.referencedProducts.length > 0 && (
                    <div className="faq-referenced-products">
                      <div className="faq-ref-title">Referenced Catalog Products:</div>
                      <div className="faq-ref-list">
                        {msg.referencedProducts.map((p) => (
                          <div
                            key={p.id}
                            className="faq-ref-card"
                            onClick={() => handleProductClick(p.id)}
                            role="button"
                            tabIndex={0}
                          >
                            <div className="faq-ref-info">
                              <span className="faq-ref-name">{p.name}</span>
                              <span className="faq-ref-brand">{p.brand} &middot; ₹{p.price}</span>
                            </div>
                            <span className="faq-ref-arrow">View Product →</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Medical / Demo Disclaimer Footer on assistant bubbles */}
                  {msg.disclaimer && (
                    <div className="faq-bubble-disclaimer">
                      {msg.disclaimer}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Loading / Typing Animation */}
            {loading && (
              <div className="faq-message-row faq-msg-assistant">
                <div className="faq-msg-avatar">🌿</div>
                <div className="faq-bubble faq-bubble-typing">
                  <span className="faq-dot"></span>
                  <span className="faq-dot"></span>
                  <span className="faq-dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <div className="faq-input-area">
            <input
              ref={inputRef}
              type="text"
              className="faq-input-field"
              placeholder="Ask about products, ingredients, prices, routine..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              id="faq-query-input"
            />
            <button
              className="faq-send-btn"
              onClick={() => handleSendMessage()}
              disabled={!inputQuery.trim() || loading}
              aria-label="Send query"
              id="faq-send-btn"
            >
              <span>➤</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
