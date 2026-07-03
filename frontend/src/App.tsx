import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { HomePage } from './pages/HomePage';
import { VkCallbackPage } from './pages/VkCallbackPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { ProductPage } from './pages/ProductPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth/vk-callback" element={<VkCallbackPage />} />
          <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
          <Route path="/products/:id" element={<ProductPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;