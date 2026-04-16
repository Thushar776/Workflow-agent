import React from 'react';
import './Sidebar.css';

const TOOLS = [
  { name: 'Gmail', status: 'Active', colorClass: 'icon-red', url: 'https://mail.google.com/', svg: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
  )},
  { name: 'Calendar', status: 'Active', colorClass: 'icon-blue', url: 'https://calendar.google.com/', svg: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
  )},
  { name: 'CSV Analyzer', status: 'Active', colorClass: 'icon-yellow', url: 'https://docs.google.com/spreadsheets/', svg: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
  )},
];

export default function Sidebar({ user, onLogout }) {
  // Use image if possible, otherwise initial
  const userName = user?.full_name || 'Thushar S';
  const initial = userName.charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="side-brand">
        <div className="brand-icon-box">
          <span className="brand-w">W</span>
        </div>
        <span className="brand-text">Workflow Agent</span>
      </div>

      {/* Tools Section */}
      <div className="side-tools-container">
        <div className="side-header">TOOLS</div>
        <div className="side-tools-list">
          {TOOLS.map((tool, i) => (
            <div 
              key={i} 
              className="side-tool" 
              onClick={() => window.open(tool.url, '_blank')}
              style={{ cursor: 'pointer' }}
            >
              <div className={`tool-icon-box ${tool.colorClass}`}>
                {tool.svg}
              </div>
              <div className="tool-content">
                <div className="tool-title">{tool.name}</div>
                <div className="tool-subtitle">{tool.status}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Profile Section */}
      <div className="side-profile">
        <div className="profile-top">
          <div className="profile-avatar-wrap">
            <div className="profile-avatar">{initial}</div>
            <button className="profile-add-btn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            </button>
          </div>
        </div>
        <div className="profile-info">
          <div className="profile-name">{userName}</div>
          <div className="profile-role">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: 4}}><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>
            {user?.role === 'admin' ? 'Admin' : 'User'}
          </div>
        </div>
      </div>
    </aside>
  );
}
