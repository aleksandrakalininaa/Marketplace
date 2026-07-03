import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import type { ProductDetail } from '../api/catalog';

/** Страница товара: галерея, описание, характеристики, кнопка в корзину */
export function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ status: number; message: string } | null>(null);
  const [activeImage, setActiveImage] = useState(0);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    catalogApi
      .getProduct(id)
      .then((res) => {
        setProduct(res.data);
        document.title = `${res.data.name} — Маркетплейс`;
      })
      .catch((err) => {
        const status = err.response?.status || 500;
        setError({
          status,
          message: status === 404 ? 'Товар не найден' : 'Произошла ошибка при загрузке товара',
        });
      })
      .finally(() => setLoading(false));

    return () => {
      document.title = 'Маркетплейс';
    };
  }, [id]);

  if (loading) {
    return (
      <div className="product-page">
        <div className="product-skeleton">
          <div className="skeleton-gallery" />
          <div className="skeleton-info">
            <div className="skeleton-line skeleton-title" />
            <div className="skeleton-line skeleton-price" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="product-page">
        <div className="product-error">
          <h2>{error.message}</h2>
          {error.status === 404 ? (
            <Link to="/" className="back-link">Вернуться в каталог</Link>
          ) : (
            <button onClick={() => window.location.reload()} className="btn-retry">
              Повторить
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!product) return null;

  const images = product.image_urls.length > 0 ? product.image_urls : [];
  const attrs = Object.entries(product.attributes || {});
  const inStock = product.quantity > 0;

  return (
    <div className="product-page">
      <Link to="/" className="back-link product-back">← В каталог</Link>

      <div className="product-detail">
        {/* Галерея изображений */}
        <div className="product-gallery">
          <div className="gallery-main">
            {images.length > 0 ? (
              <img src={images[activeImage]} alt={product.name} />
            ) : (
              <div className="gallery-no-image">Нет фото</div>
            )}
          </div>
          {images.length > 1 && (
            <div className="gallery-thumbnails">
              {images.map((url, i) => (
                <button
                  key={i}
                  className={`gallery-thumb ${i === activeImage ? 'active' : ''}`}
                  onClick={() => setActiveImage(i)}
                >
                  <img src={url} alt={`${product.name} ${i + 1}`} />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Информация о товаре */}
        <div className="product-info">
          <h1 className="product-title">{product.name}</h1>
          <p className="product-price-detail">{product.price.toFixed(2)} ₽</p>

          <p className={`product-stock ${inStock ? 'in-stock' : 'out-of-stock'}`}>
            {inStock ? `В наличии (${product.quantity} шт.)` : 'Нет в наличии'}
          </p>

          <button
            className="btn-add-cart-detail"
            disabled={!inStock}
            onClick={() => alert('Добавлено в корзину')}
          >
            {inStock ? 'Добавить в корзину' : 'Нет в наличии'}
          </button>

          {/* Характеристики */}
          {attrs.length > 0 && (
            <div className="product-attributes">
              <h3>Характеристики</h3>
              <table>
                <tbody>
                  {attrs.map(([key, value]) => (
                    <tr key={key}>
                      <td className="attr-key">{key}</td>
                      <td className="attr-value">{String(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Описание */}
          {product.description && (
            <div className="product-description">
              <h3>Описание</h3>
              <p>{product.description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}