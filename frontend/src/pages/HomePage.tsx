import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';
import { CatalogPage } from './CatalogPage';

/** Единая главная страница: без авторизации — формы, после входа — каталог */
export function HomePage() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // Режим: 'login' | 'register' | 'forgot'
  const [mode, setMode] = useState<'login' | 'register' | 'forgot'>('login');

  // Поля форм
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // VK
  const VK_APP_ID = import.meta.env.VITE_VK_APP_ID || '54663805';
  const VK_REDIRECT_URI =
    import.meta.env.VITE_VK_REDIRECT_URI || 'http://localhost:3000/auth/vk-callback';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authApi.login({ email, password });
      await login(res.data.access_token, res.data.refresh_token);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Неверные данные');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.register({ email, password, name });
      setSuccess('Регистрация успешна! Теперь войдите.');
      setMode('login');
      setPassword('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await authApi.forgotPassword(email);
      setSuccess('Если email существует, ссылка отправлена.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const handleVkLogin = () => {
    const vkAuthUrl = `https://oauth.vk.com/authorize?client_id=${VK_APP_ID}&redirect_uri=${encodeURIComponent(VK_REDIRECT_URI)}&display=page&scope=email&response_type=code&v=5.199`;
    window.location.href = vkAuthUrl;
  };

  // === НЕ АВТОРИЗОВАН — показываем формы ===
  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1>Маркетплейс</h1>

          {/* Табы */}
          <div className="auth-tabs">
            <button
              className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
              onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
            >
              Вход
            </button>
            <button
              className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
              onClick={() => { setMode('register'); setError(''); setSuccess(''); }}
            >
              Регистрация
            </button>
          </div>

          {success && <p className="success">{success}</p>}
          {error && <p className="error">{error}</p>}

          {/* Форма входа */}
          {mode === 'login' && (
            <form onSubmit={handleLogin}>
              <input
                type="email" placeholder="Email" value={email}
                onChange={(e) => setEmail(e.target.value)} required
              />
              <input
                type="password" placeholder="Пароль" value={password}
                onChange={(e) => setPassword(e.target.value)} required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Загрузка...' : 'Войти'}
              </button>
              <div className="auth-divider"><span>или</span></div>
              <button type="button" className="vk-btn" onClick={handleVkLogin}>
                Войти через VK
              </button>
              <p className="auth-link">
                <button type="button" className="link-btn" onClick={() => setMode('forgot')}>
                  Забыли пароль?
                </button>
              </p>
            </form>
          )}

          {/* Форма регистрации */}
          {mode === 'register' && (
            <form onSubmit={handleRegister}>
              <input
                type="text" placeholder="Имя" value={name}
                onChange={(e) => setName(e.target.value)} required
              />
              <input
                type="email" placeholder="Email" value={email}
                onChange={(e) => setEmail(e.target.value)} required
              />
              <input
                type="password" placeholder="Пароль" value={password}
                onChange={(e) => setPassword(e.target.value)} required minLength={6}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Загрузка...' : 'Зарегистрироваться'}
              </button>
            </form>
          )}

          {/* Форма восстановления пароля */}
          {mode === 'forgot' && (
            <form onSubmit={handleForgot}>
              <input
                type="email" placeholder="Email" value={email}
                onChange={(e) => setEmail(e.target.value)} required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Отправка...' : 'Отправить ссылку'}
              </button>
              <p className="auth-link">
                <button type="button" className="link-btn" onClick={() => setMode('login')}>
                  Назад к входу
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  // === АВТОРИЗОВАН — каталог ===
  return (
    <div>
      <header className="catalog-header">
        <div className="catalog-header-left">
          <h1>Маркетплейс</h1>
          <span className="header-greeting">Привет, {user?.name}</span>
        </div>
        <div className="catalog-header-right">
          <button className="header-btn" onClick={logout}>Выйти</button>
        </div>
      </header>
      <CatalogPage />
    </div>
  );
}