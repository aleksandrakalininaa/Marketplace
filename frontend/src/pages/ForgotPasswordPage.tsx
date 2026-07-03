import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../api/auth';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      await authApi.forgotPassword(email);
      setMessage('Если такой email существует, ссылка для сброса пароля отправлена.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Восстановление пароля</h1>
        {message && <p className="success">{message}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Отправка...' : 'Отправить ссылку'}
          </button>
        </form>
        <p className="auth-link">
          <Link to="/login">Назад к входу</Link>
        </p>
      </div>
    </div>
  );
}