import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { catalogApi } from '../api/catalog';
import type { CategoryNode, ProductShort } from '../api/catalog';
import { CategoryTree } from '../components/CategoryTree';
import { ProductCard } from '../components/ProductCard';

/** Страница каталога: дерево категорий + поиск + сетка товаров с фильтрами */
export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [categories, setCategories] = useState<CategoryNode[]>([]);
  const [products, setProducts] = useState<ProductShort[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = searchParams.get('search') || '';
  const categoryId = searchParams.get('category_id') || '';
  const minPrice = searchParams.get('min_price') || '';
  const maxPrice = searchParams.get('max_price') || '';
  const inStock = searchParams.get('in_stock') === 'true';
  const sort = searchParams.get('sort') || 'newest';
  const page = parseInt(searchParams.get('page') || '1', 10);
  const limit = 20;

  // Загрузка категорий
  useEffect(() => {
    catalogApi
      .getCategories()
      .then((res) => setCategories(res.data))
      .catch(() => setError('Не удалось загрузить категории'));
  }, []);

  // Загрузка товаров при изменении параметров
  const fetchProducts = useCallback(async () => {
    // Нужен либо search, либо categoryId
    if (!search && !categoryId) return;
    setLoading(true);
    setError(null);
    try {
      const filters: any = { search, page, limit, sort };
      if (categoryId) filters.category_id = categoryId;
      if (minPrice) filters.min_price = parseFloat(minPrice);
      if (maxPrice) filters.max_price = parseFloat(maxPrice);
      if (inStock) filters.in_stock = true;

      const res = await catalogApi.getProducts(filters);
      setProducts(res.data.items);
      setTotal(res.data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || 'Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  }, [search, categoryId, minPrice, maxPrice, inStock, sort, page]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const updateParam = (key: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    if (key !== 'page') {
      newParams.set('page', '1');
    }
    setSearchParams(newParams);
  };

  const handleCategorySelect = (id: string) => {
    // Сохраняем search если есть, добавляем category_id
    const newParams = new URLSearchParams();
    if (search) newParams.set('search', search);
    newParams.set('category_id', id);
    setSearchParams(newParams);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="catalog-page">
      {/* Левая панель с категориями */}
      <aside className="catalog-sidebar">
        <h2 className="sidebar-title">Категории</h2>
        <CategoryTree
          categories={categories}
          activeId={categoryId}
          onSelect={handleCategorySelect}
        />
      </aside>

      {/* Основная область */}
      <main className="catalog-main">
        {/* Фильтры — показываем только когда есть результаты или выбрана категория */}
        {(search || categoryId) && (
          <div className="catalog-filters">
            <div className="filter-group">
              <label>
                Цена от:
                <input
                  type="number" min="0" value={minPrice}
                  onChange={(e) => updateParam('min_price', e.target.value)} placeholder="0"
                />
              </label>
              <label>
                до:
                <input
                  type="number" min="0" value={maxPrice}
                  onChange={(e) => updateParam('max_price', e.target.value)} placeholder="0"
                />
              </label>
            </div>
            <label className="filter-checkbox">
              <input
                type="checkbox" checked={inStock}
                onChange={(e) => updateParam('in_stock', e.target.checked ? 'true' : '')}
              />
              Только в наличии
            </label>
            <label className="filter-sort">
              Сортировка:
              <select value={sort} onChange={(e) => updateParam('sort', e.target.value)}>
                <option value="newest">Новые</option>
                <option value="price_asc">Цена ↑</option>
                <option value="price_desc">Цена ↓</option>
                <option value="name_asc">Название А-Я</option>
                <option value="name_desc">Название Я-А</option>
              </select>
            </label>
          </div>
        )}

        {/* Состояния */}
        {!search && !categoryId && (
          <div className="catalog-placeholder">
            <p>Выберите категорию слева или введите поисковый запрос</p>
          </div>
        )}

        {loading && (
          <div className="catalog-skeleton">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="skeleton-card" />
            ))}
          </div>
        )}

        {error && !loading && (
          <div className="catalog-error">
            <p>{error}</p>
            <button onClick={fetchProducts}>Повторить</button>
          </div>
        )}

        {!loading && !error && products.length === 0 && (search || categoryId) && (
          <div className="catalog-empty">
            {search
              ? `По запросу «${search}» ничего не найдено`
              : 'В этой категории пока нет товаров'}
          </div>
        )}

        {!loading && !error && products.length > 0 && (
          <>
            {search && <p className="search-count">Найдено: {total} товаров</p>}
            <div className="product-grid">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button disabled={page <= 1} onClick={() => updateParam('page', String(page - 1))}>
                  ←
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    className={`page-btn ${p === page ? 'active' : ''}`}
                    onClick={() => updateParam('page', String(p))}
                  >
                    {p}
                  </button>
                ))}
                <button
                  disabled={page >= totalPages}
                  onClick={() => updateParam('page', String(page + 1))}
                >
                  →
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}