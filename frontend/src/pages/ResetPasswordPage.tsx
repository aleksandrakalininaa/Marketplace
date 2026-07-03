import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token') || '';

  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    if (!token) {
      setError('Отсутствует токен сброса пароля');
      return;
    }
    setLoading(true);
    try {
      const res = await authApi.resetPassword(token, newPassword);
      setMessage(res.data.message || 'Пароль обновлён');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сброса пароля');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Сброс пароля</h1>
        {message && <p className="success">{message}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            placeholder="Новый пароль"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={6}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading || !token}>
            {loading ? 'Сохранение...' : 'Сменить пароль'}
          </button>
        </form>
        <p className="auth-link">
          <Link to="/login">Назад к входу</Link>
        </p>
      </div>
    </div>
  );
}