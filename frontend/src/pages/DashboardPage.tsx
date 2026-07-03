import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';

const VK_APP_ID = import.meta.env.VITE_VK_APP_ID || '';
const VK_REDIRECT_URI = import.meta.env.VITE_VK_REDIRECT_URI || 'http://localhost:3000/auth/vk-callback';

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [linkError, setLinkError] = useState('');
  const [linkSuccess, setLinkSuccess] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLinkVk = () => {
    if (!VK_APP_ID) {
      setLinkError('VK App ID не настроен');
      return;
    }
    // Use a different redirect URI for linking
    const vkAuthUrl = `https://oauth.vk.com/authorize?client_id=${VK_APP_ID}&redirect_uri=${encodeURIComponent(VK_REDIRECT_URI)}&display=page&scope=email&response_type=code&v=5.199&state=link`;
    sessionStorage.setItem('vk_action', 'link');
    window.location.href = vkAuthUrl;
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Маркетплейс</h1>
        <nav>
          <span>Привет, {user?.name}</span>
          <button onClick={handleLogout}>Выйти</button>
        </nav>
      </header>
      <main className="dashboard-content">
        <h2>Личный кабинет</h2>
        <div className="profile-card">
          <p><strong>ID:</strong> {user?.id}</p>
          <p><strong>Имя:</strong> {user?.name}</p>
          <p><strong>Email:</strong> {user?.email || 'не указан'}</p>
          <p><strong>VK привязан:</strong> {user?.vk_linked ? 'Да' : 'Нет'}</p>

          {!user?.vk_linked && (
            <div className="vk-link-section">
              <button className="vk-btn" onClick={handleLinkVk}>
                Привязать VK
              </button>
              {linkError && <p className="error">{linkError}</p>}
              {linkSuccess && <p className="success">{linkSuccess}</p>}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}