import { Link } from 'react-router-dom';
import type { ProductShort } from '../api/catalog';

interface ProductCardProps {
  product: ProductShort;
}

/** Карточка товара: изображение, название, цена, кнопка + ссылка на страницу товара */
export function ProductCard({ product }: ProductCardProps) {
  const imageUrl = product.image_urls.length > 0 ? product.image_urls[0] : null;
  const inStock = product.quantity > 0;

  return (
    <Link to={`/products/${product.id}`} className="product-card-link">
      <div className="product-card">
        <div className="product-card-image">
          {imageUrl ? (
            <img src={imageUrl} alt={product.name} referrerPolicy="no-referrer" />
          ) : (
            <div className="product-card-no-image">Нет фото</div>
          )}
        </div>
        <div className="product-card-body">
          <h3 className="product-card-name">{product.name}</h3>
          {product.category && (
            <span className="product-card-category">{product.category.name}</span>
          )}
          <div className="product-card-footer">
            <span className="product-card-price">{product.price.toFixed(2)} ₽</span>
            <button
              className={`btn-add-cart ${!inStock ? 'disabled' : ''}`}
              disabled={!inStock}
              onClick={(e) => {
                e.preventDefault(); // не переходить по ссылке карточки
                alert('Добавлено в корзину');
              }}
            >
              {inStock ? 'В корзину' : 'Нет в наличии'}
            </button>
          </div>
        </div>
      </div>
    </Link>
  );
}