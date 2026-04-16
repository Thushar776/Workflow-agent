import React, { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

export default function ChatBox({ history, onSendMessage, isProcessing }) {
  const [input, setInput] = useState('');
  const [file, setFile] = useState(null);
  const endRef = useRef(null);
  const fileInputRef = useRef(null);

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
          <div className="chat-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--border-light)" strokeWidth="1">
              <rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="16" x2="16" y2="16"></line>
            </svg>
            <p>Start a new workflow</p>
          </div>
        ) : (
          history.map((msg, i) => {
            if (msg.role === "user" && msg.parts[0]?.text) {
              return (
                <div key={i} className="msg-row user-row animate-fade-up">
                  <div className="user-msg-block">
                    <p>{msg.parts[0].text}</p>
                    <button className="user-msg-close">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                  </div>
                </div>
              );
            }
            if (msg.role === "model" && msg.parts[0]?.text) {
              return (
                <div key={i} className="msg-row bot-row animate-fade-up">
                  <div className="bot-msg-container">
                    <div className="bot-msg-header">
                      <div className="bot-avatar">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-2.5-9c.83 0 1.5-.67 1.5-1.5S10.33 8 9.5 8 8 8.67 8 9.5 8.83 11 9.5 11zm5 0c.83 0 1.5-.67 1.5-1.5S17.33 8 16.5 8 15 8.67 15 9.5s.67 1.5 1.5 1.5zm-2.5 4c-1.54 0-2.88-.74-3.7-1.89l1.45-1.45c.49.52 1.33.84 2.25.84s1.76-.32 2.25-.84l1.45 1.45c-.82 1.15-2.16 1.89-3.7 1.89z"/></svg>
                      </div>
                      <span className="bot-name">Workflow Agent</span>
                    </div>
                    <div className="bot-msg-body">
                      <p>{msg.parts[0].text}</p>
                    </div>
                  </div>
                </div>
              );
            }
            return null;
          })
        )}
        {isProcessing && (
          <div className="msg-row bot-row animate-fade-up">
            <div className="bot-msg-container">
              <div className="bot-msg-header">
                <div className="bot-avatar">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-2.5-9c.83 0 1.5-.67 1.5-1.5S10.33 8 9.5 8 8 8.67 8 9.5 8.83 11 9.5 11zm5 0c.83 0 1.5-.67 1.5-1.5S17.33 8 16.5 8 15 8.67 15 9.5s.67 1.5 1.5 1.5zm-2.5 4c-1.54 0-2.88-.74-3.7-1.89l1.45-1.45c.49.52 1.33.84 2.25.84s1.76-.32 2.25-.84l1.45 1.45c-.82 1.15-2.16 1.89-3.7 1.89z"/></svg>
                </div>
                <span className="bot-name">Workflow Agent</span>
              </div>
              <div className="bot-msg-body">
                <div className="typing-indicator">
                  <span className="dot"></span><span className="dot"></span><span className="dot"></span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="chat-input-area">
        {file && (
          <div className="file-indicator">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
            <span className="file-name">{file.name}</span>
            <button className="file-remove" onClick={() => setFile(null)}>×</button>
          </div>
        )}
        <form onSubmit={send} className="input-bar">
          <input
            type="file"
            accept=".csv,.txt"
            style={{ display: 'none' }}
            ref={fileInputRef}
            onChange={handleFileChange}
          />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a task..."
            disabled={isProcessing}
            className="input-field"
          />
          <div className="input-actions">
            <button type="button" className="action-btn icon-plus"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg></button>
            <button type="button" className="action-btn"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg></button>
            <button type="button" className="action-btn" onClick={() => fileInputRef.current?.click()}><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg></button>
            <button type="submit" disabled={isProcessing || (!input.trim() && !file)} className="send-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" /></svg>
            </button>
          </div>
        </form>
        <div className="input-meta">
          <div className="meta-user">
            <span className="meta-box"></span>
            User
          </div>
        </div>
      </div>
    </div>
  );
}
