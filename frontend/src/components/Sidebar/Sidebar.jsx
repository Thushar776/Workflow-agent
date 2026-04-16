import React from 'react';
import './Sidebar.css';

const TOOLS = [
  { name: 'Gmail', status: 'Ready', colorClass: 'icon-purple', url: 'https://mail.google.com', svg: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
  )},
  { name: 'Calendar', status: 'Active', colorClass: 'icon-teal', url: 'https://calendar.google.com', svg: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
  )},
  { name: 'CSV Tool', status: 'Ready', colorClass: 'icon-blue', url: '', svg: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
  )},
];

const COMMANDS = [
  "Summarize my emails",
  "Schedule a meeting",
  "Analyze sales data",
  "Clear chat history"
];

export default function Sidebar({ user, onLogout, onCommandClick }) {
  const userName = user?.full_name || 'Workflow User';
  const initial = userName.charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      {/* Profile Header */}
      <div className="side-profile">
        <div className="profile-avatar-wrap">
          <div className="profile-avatar">{initial}</div>
        </div>
        <div className="profile-info">
          <div className="profile-name">{userName}</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="side-scroll-area">
        {/* Tools */}
        <div className="side-section">
          <div className="side-header">AUTOMATION TOOLS</div>
          <div className="side-tools-list">
            {TOOLS.map((tool, i) => (
              <div 
                key={i} 
                className="premium-tool-card" 
                onClick={() => tool.url && window.open(tool.url, '_blank')}
              >
                <div className={`tool-icon-bg ${tool.colorClass}`}>
                  {tool.svg}
                  <span className={`tool-badge ${tool.status === 'Active' ? 'badge-active' : 'badge-ready'}`}></span>
                </div>
                <div className="tool-meta">
                  <div className="tool-name">{tool.name}</div>
                  <div className="tool-status-text">{tool.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Commands */}
        <div className="side-section">
          <div className="side-header">QUICK COMMANDS</div>
          <div className="quick-commands-grid">
            {COMMANDS.map((cmd, i) => (
              <button 
                key={i} 
                className="command-chip"
                onClick={() => onCommandClick?.(cmd)}
              >
                {cmd}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Stats */}
      <div className="side-footer">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-value">24</span>
            <span className="stat-label">Workflows</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">142</span>
            <span className="stat-label">Tool Calls</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
