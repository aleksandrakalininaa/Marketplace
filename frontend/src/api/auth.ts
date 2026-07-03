import api from './client';

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface VkData {
  code: string;
  redirect_uri: string;
}

export const authApi = {
  register(data: RegisterData) {
    return api.post('/auth/register', data);
  },

  login(data: LoginData) {
    return api.post('/auth/login', data);
  },

  refresh(refreshToken: string) {
    return api.post('/auth/refresh', { refresh_token: refreshToken });
  },

  vkAuth(data: VkData) {
    return api.post('/auth/vk', data);
  },

  forgotPassword(email: string) {
    return api.post('/auth/forgot-password', { email });
  },

  resetPassword(token: string, newPassword: string) {
    return api.post('/auth/reset-password', { token, new_password: newPassword });
  },

  linkVk(data: VkData) {
    return api.post('/auth/link-vk', data);
  },

  getMe() {
    return api.get('/auth/me');
  },
};