import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';

const VK_APP_ID = import.meta.env.VITE_VK_APP_ID || '';
const VK_REDIRECT_URI = import.meta.env.VITE_VK_REDIRECT_URI || 'http://localhost:3000/auth/vk-callback';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Show message after registration
  useEffect(() => {
    if ((location.state as any)?.registered) {
      setSuccessMsg('Регистрация успешна! Теперь войдите.');
    }
  }, [location.state]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authApi.login(form);
      await login(res.data.access_token, res.data.refresh_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Неверные учетные данные');
    } finally {
      setLoading(false);
    }
  };

  const handleVkLogin = () => {
    if (!VK_APP_ID) {
      setError('VK App ID не настроен');
      return;
    }
    const vkAuthUrl = `https://oauth.vk.com/authorize?client_id=${VK_APP_ID}&redirect_uri=${encodeURIComponent(VK_REDIRECT_URI)}&display=page&scope=email&response_type=code&v=5.199`;
    window.location.href = vkAuthUrl;
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Вход</h1>
        {successMsg && <p className="success">{successMsg}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Пароль"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Загрузка...' : 'Войти'}
          </button>
        </form>
        <div className="auth-divider">
          <span>или</span>
        </div>
        <button className="vk-btn" onClick={handleVkLogin} type="button">
          Войти через VK
        </button>
        <p className="auth-link">
          <Link to="/forgot-password">Забыли пароль?</Link>
        </p>
        <p className="auth-link">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}