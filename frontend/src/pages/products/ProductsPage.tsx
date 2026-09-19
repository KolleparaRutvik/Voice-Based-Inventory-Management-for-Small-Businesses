import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Package, Filter, Loader2, AlertCircle } from 'lucide-react';
import { productsService } from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import type { Product } from '../../types';
import { CATEGORIES } from '../../types';

export default function ProductsPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadProducts();
  }, [search, categoryFilter]);

  const loadProducts = async () => {
    try {
      const result = await productsService.getAll({ search, category: categoryFilter });
      if (result.success && result.data) {
        setProducts((result.data as { items: Product[] }).items || result.data as Product[]);
      }
    } catch {
      // Fallback demo data
      setProducts([
        { id: '1', shop_id: '', name: 'Rice (Biyyam)', local_name: 'Biyyam', category: 'Grains & Rice', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 25, purchase_price: 1450, selling_price: 65, minimum_stock: 5, recommended_stock: 20, reorder_quantity: 10, is_active: true, created_at: '', updated_at: '', current_stock: 450, stock_value: 26100 },
        { id: '2', shop_id: '', name: 'Sugar (Chakkera)', local_name: 'Chakkera', category: 'Sugar & Jaggery', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 50, purchase_price: 2100, selling_price: 48, minimum_stock: 10, recommended_stock: 50, reorder_quantity: 25, is_active: true, created_at: '', updated_at: '', current_stock: 180, stock_value: 7560 },
        { id: '3', shop_id: '', name: 'Sunflower Oil', local_name: 'Nune', category: 'Oils & Ghee', base_unit: 'litre', purchase_unit: 'can', selling_unit: 'litre', conversion_factor: 15, purchase_price: 2250, selling_price: 165, minimum_stock: 5, recommended_stock: 30, reorder_quantity: 15, is_active: true, created_at: '', updated_at: '', current_stock: 35, stock_value: 5250 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.local_name && p.local_name.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory = !categoryFilter || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-surface-900">{t('navProducts')}</h2>
          <p className="text-sm text-surface-500">{filteredProducts.length} {t('totalProducts').toLowerCase()}</p>
        </div>
        <button
          onClick={() => navigate('/products/new')}
          className="touch-btn gradient-primary text-white px-4 gap-2 text-sm shadow-md"
        >
          <Plus className="w-4 h-4" />
          <span>{t('addProduct')}</span>
        </button>
      </div>

      {/* Search & Filter bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('search')}
            className="input-field pl-10"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`touch-btn border px-3 ${showFilters ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-surface-200 text-surface-600'}`}
        >
          <Filter className="w-4 h-4" />
        </button>
      </div>

      {/* Category Filters */}
      {showFilters && (
        <div className="flex flex-wrap gap-2 animate-slide-down">
          <button
            onClick={() => setCategoryFilter('')}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              !categoryFilter ? 'bg-primary-500 text-white shadow-sm' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
            }`}
          >
            {t('all')}
          </button>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                categoryFilter === cat ? 'bg-primary-500 text-white shadow-sm' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Product List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-12 rounded-2xl bg-white border border-surface-100">
          <Package className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-surface-600 font-medium">No products found</p>
          <p className="text-surface-400 text-sm mt-1">Add your first product to get started</p>
          <button
            onClick={() => navigate('/products/new')}
            className="touch-btn gradient-primary text-white px-6 gap-2 text-sm mt-4 mx-auto"
          >
            <Plus className="w-4 h-4" />
            <span>{t('addProduct')}</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredProducts.map((product) => {
            const isLow = (product.current_stock || 0) <= product.minimum_stock;
            return (
              <button
                key={product.id}
                onClick={() => navigate(`/products/${product.id}`)}
                className="w-full flex items-center gap-3.5 p-4 rounded-2xl bg-white border border-surface-200/80 hover:border-primary-300 hover:shadow-md transition-all active:scale-[0.99] text-left group"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-50 to-accent-50 border border-primary-100 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                  <Package className="w-6 h-6 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-surface-900 truncate">{product.name}</p>
                    {product.local_name && (
                      <span className="px-2 py-0.2 rounded-md text-[11px] font-semibold bg-primary-50 text-primary-700 border border-primary-100">
                        {product.local_name}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-surface-500 mt-0.5">
                    {product.category || 'General'} • {product.purchase_unit !== product.base_unit ? `1 ${product.purchase_unit} = ${product.conversion_factor} ${product.base_unit}` : product.base_unit}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
                      isLow
                        ? 'bg-red-50 text-red-700 border border-red-200'
                        : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {isLow && <AlertCircle className="w-3 h-3" />}
                      {t('currentStock')}: {product.current_stock || 0} {product.base_unit}
                    </span>
                    <span className="text-xs text-surface-500">
                      ₹{product.selling_price}/{product.selling_unit}
                    </span>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold text-surface-900">
                    {formatCurrency(product.stock_value || 0)}
                  </p>
                  <p className="text-[10px] text-surface-400 mt-0.5">Value</p>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
