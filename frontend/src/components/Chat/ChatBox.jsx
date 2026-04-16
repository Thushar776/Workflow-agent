import React, { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

export default function ChatBox({ history, onSendMessage, isProcessing, pendingCommand, onClearPending }) {
  const [input, setInput] = useState('');
  const [file, setFile] = useState(null);
  const endRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (pendingCommand) {
      setInput(pendingCommand);
      onClearPending();
    }
  }, [pendingCommand, onClearPending]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const send = async (e) => {
    e.preventDefault();
    if ((!input.trim() && !file) || isProcessing) return;
    
    let finalMessage = input;
    if (file) {
      const text = await file.text();
      finalMessage = `I have attached a file named ${file.name} with the following content:\n\n${text}\n\nMy request is: ${input}`;
    }
    
    onSendMessage(finalMessage);
    setInput('');
    setFile(null);
  };

  const empty = history.length === 0;

  return (
    <div className="chat">
      <div className="chat-scroll">
        {empty ? (
          <div className="chat-welcome animate-fade-up">
            <div className="hero-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            </div>
            <h1>FlowMind</h1>
            <p>Intelligence at your fingertips. Automate your Gmail, Calendar, and CSV workflows with natural language.</p>
          </div>
        ) : (
          history.map((msg, i) => {
            if (msg.role === "user" && msg.parts[0]?.text) {
              return (
                <div key={i} className="msg-row user-row animate-fade-up">
                  <div className="user-bubble">
                    <p>{msg.parts[0].text}</p>
                  </div>
                </div>
              );
            }
            if (msg.role === "model" && msg.parts[0]?.text) {
              return (
                <div key={i} className="msg-row bot-row animate-fade-up">
                  <div className="bot-card">
                    <div className="bot-surface">
                      <p>{msg.parts[0].text}</p>
                    </div>
                    {/* Execution trace would go here if we had per-message logs */}
                  </div>
                </div>
              );
            }
            return null;
          })
        )}
        {isProcessing && (
          <div className="msg-row bot-row animate-fade-up">
            <div className="bot-card">
              <div className="bot-surface">
                <div className="typing-indicator">
                  <span className="dot"></span><span className="dot"></span><span className="dot"></span>
                </div>
              </div>
              <div className="execution-trace">
                <div className="trace-step">
                  <div className="step-icon-box running">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                  </div>
                  <span className="step-label">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="chat-input-area">
        {file && (
          <div className="file-indicator animate-fade-in">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
            <span className="file-name">Input: {file.name}</span>
            <button type="button" className="file-remove" onClick={() => setFile(null)}>×</button>
          </div>
        )}
        <form onSubmit={send} className="pill-input-container">
          <input
            type="file"
            accept=".csv,.txt,.md,.json"
            style={{ display: 'none' }}
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          <button 
            type="button" 
            className="action-btn" 
            onClick={() => fileInputRef.current?.click()}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a workflow task..."
            disabled={isProcessing}
            className="input-field"
          />
          <button type="submit" disabled={isProcessing || (!input.trim() && !file)} className="send-btn-circle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" /></svg>
          </button>
        </form>
        <div className="input-hint">
          Press <strong>Enter</strong> to send · <strong>Shift+Enter</strong> for new line
        </div>
      </div>
    </div>
  );
}
