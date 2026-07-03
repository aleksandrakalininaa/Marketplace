import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';

const VK_REDIRECT_URI = import.meta.env.VITE_VK_REDIRECT_URI || 'http://localhost:3000/auth/vk-callback';

export function VkCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setError('Не получен код авторизации VK');
      return;
    }

    authApi.vkAuth({ code, redirect_uri: VK_REDIRECT_URI })
      .then(async (res) => {
        await login(res.data.access_token, res.data.refresh_token);
        navigate('/dashboard');
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Ошибка входа через VK');
      });
  }, [searchParams, navigate, login]);

  if (error) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1>Ошибка</h1>
          <p className="error">{error}</p>
          <button onClick={() => navigate('/login')}>Назад к входу</button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Вход через VK...</h1>
        <p>Пожалуйста, подождите</p>
      </div>
    </div>
  );
}