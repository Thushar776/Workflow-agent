import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Sidebar from './components/Sidebar/Sidebar';
import ChatBox from './components/Chat/ChatBox';
import ExecutionPanel from './components/Logs/ExecutionPanel';
import './App.css';

function AgentDashboard() {
  const { user, token, logout } = useAuth();
  const [history, setHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSendMessage = async (message) => {
    const newUserMsg = { role: "user", parts: [{ text: message }] };
    setHistory(prev => [...prev, newUserMsg]);
    setIsProcessing(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message, history }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        const taskId = data.task_id;
        
        // Polling loop
        const pollInterval = setInterval(async () => {
          try {
            const statusRes = await fetch(`http://127.0.0.1:8000/api/chat/status/${taskId}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            const statusData = await statusRes.json();

            if (statusData.status === 'completed') {
              clearInterval(pollInterval);
              setHistory(statusData.history);
              if (statusData.logs && statusData.logs.length > 0) {
                setLogs(prev => [...prev, ...statusData.logs]);
              }
              setIsProcessing(false);
            } else if (statusData.status === 'error') {
              clearInterval(pollInterval);
              throw new Error(statusData.detail || 'Background task failed');
            }
          } catch (err) {
            clearInterval(pollInterval);
            console.error(err);
            const errorMsg = { role: "model", parts: [{ text: "Error fetching task status." }] };
            setHistory(prev => [...prev, errorMsg]);
            setIsProcessing(false);
          }
        }, 1000);

      } else {
        throw new Error(data.detail || 'Server error');
      }
    } catch (error) {
      console.error(error);
      const errorMsg = { role: "model", parts: [{ text: "Error connecting to AI service." }] };
      setHistory(prev => [...prev, errorMsg]);
      setIsProcessing(false);
    } 
  };

  return (
    <div className="app-layout">
      <Sidebar user={user} onLogout={logout} />
      <main className="chat-main">
        <ChatBox
          history={history}
          onSendMessage={handleSendMessage}
          isProcessing={isProcessing}
        />
      </main>
      <aside className="log-aside">
        <ExecutionPanel logs={logs} />
      </aside>
    </div>
  );
}

function AppContent() {
  const { user, loading } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!user) {
    return authView === 'login'
      ? <LoginPage onSwitch={() => setAuthView('register')} />
      : <RegisterPage onSwitch={() => setAuthView('login')} />;
  }

  return <AgentDashboard />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
