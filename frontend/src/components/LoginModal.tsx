import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';

interface LoginModalProps {
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export function LoginModal({ onClose, onSwitchToRegister }: LoginModalProps) {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authApi.login(form);
      await login(res.data.access_token, res.data.refresh_token);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Неверные учетные данные');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Вход</h2>
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
        <p className="auth-link">
          Нет аккаунта?{' '}
          <button className="link-btn" onClick={onSwitchToRegister}>
            Зарегистрироваться
          </button>
        </p>
      </div>
    </div>
  );
}