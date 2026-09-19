import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Check, PackageMinus } from 'lucide-react';
import { inventoryService, productsService } from '../../services/api';
import { UNITS } from '../../types';
import type { Product } from '../../types';

export default function StockOutPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    product_id: '',
    quantity: 0,
    unit: 'kg',
    transaction_type: 'SALE',
    price: 0,
    notes: '',
  });

  useEffect(() => { loadProducts(); }, []);

  const loadProducts = async () => {
    try {
      const result = await productsService.getAll();
      if (result.success && result.data) {
        setProducts((result.data as { items: Product[] }).items || result.data as Product[]);
      }
    } catch {
      setProducts([
        { id: '1', shop_id: '', name: 'Rice (Biyyam)', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 25, purchase_price: 1450, selling_price: 65, minimum_stock: 5, recommended_stock: 20, reorder_quantity: 10, is_active: true, created_at: '', updated_at: '', current_stock: 450 },
        { id: '2', shop_id: '', name: 'Sugar (Chakkera)', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 50, purchase_price: 2100, selling_price: 48, minimum_stock: 10, recommended_stock: 50, reorder_quantity: 25, is_active: true, created_at: '', updated_at: '', current_stock: 8 },
      ]);
    }
  };

  const selectedProduct = products.find(p => p.id === form.product_id);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await inventoryService.stockOut(form);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => navigate('/inventory'), 2000);
      } else {
        setError(result.error?.message || 'Failed to remove stock');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove stock');
    } finally {
      setLoading(false);
    }
  };

  const transactionTypes = [
    { value: 'SALE', label: 'Sale' },
    { value: 'STOCK_OUT', label: 'Stock Out' },
    { value: 'DAMAGE', label: 'Damage / Waste' },
    { value: 'RETURN', label: 'Return to Supplier' },
  ];

  if (success) {
    return (
      <div className="page-container pt-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-rose-100 flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-rose-600" />
          </div>
          <p className="text-lg font-semibold text-surface-900">Stock Removed!</p>
          <p className="text-sm text-surface-500 mt-1">
            {form.quantity} {form.unit} of {selectedProduct?.name} removed
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
          <ArrowLeft className="w-5 h-5 text-surface-600" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
            <PackageMinus className="w-5 h-5 text-rose-500" /> Stock Out
          </h2>
          <p className="text-sm text-surface-500">Remove stock from inventory</p>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-type">Reason *</label>
            <div className="grid grid-cols-2 gap-2">
              {transactionTypes.map(t => (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => setForm(prev => ({ ...prev, transaction_type: t.value }))}
                  className={`px-3 py-2.5 rounded-xl text-sm font-medium border transition-all ${
                    form.transaction_type === t.value
                      ? 'border-rose-300 bg-rose-50 text-rose-700'
                      : 'border-surface-200 text-surface-600 hover:bg-surface-50'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-product">Product *</label>
            <select
              id="so-product"
              value={form.product_id}
              onChange={(e) => {
                const prod = products.find(p => p.id === e.target.value);
                setForm(prev => ({
                  ...prev,
                  product_id: e.target.value,
                  unit: prod?.selling_unit || 'kg',
                  price: prod?.selling_price || 0,
                }));
              }}
              className="input-field"
              required
            >
              <option value="">Select Product</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} (Stock: {p.current_stock || '?'} {p.base_unit})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-qty">Quantity *</label>
              <input id="so-qty" type="number" step="0.01" min="0.01" value={form.quantity || ''} onChange={(e) => setForm(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 0 }))} className="input-field" placeholder="5" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-unit">Unit</label>
              <select id="so-unit" value={form.unit} onChange={(e) => setForm(prev => ({ ...prev, unit: e.target.value }))} className="input-field">
                {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
              </select>
            </div>
          </div>

          {form.transaction_type === 'SALE' && (
            <div>
              <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-price">Selling Price per {form.unit} (₹)</label>
              <input id="so-price" type="number" step="0.01" min="0" value={form.price || ''} onChange={(e) => setForm(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))} className="input-field" />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="so-notes">Notes</label>
            <input id="so-notes" type="text" value={form.notes} onChange={(e) => setForm(prev => ({ ...prev, notes: e.target.value }))} className="input-field" placeholder="Optional notes" />
          </div>
        </div>

        {form.product_id && form.quantity > 0 && (
          <div className="bg-rose-50 rounded-2xl border border-rose-200 p-4 animate-slide-up">
            <h4 className="text-sm font-semibold text-rose-800 mb-2">Summary</h4>
            <div className="space-y-1 text-sm text-rose-700">
              <p>Product: <strong>{selectedProduct?.name}</strong></p>
              <p>Remove: <strong>{form.quantity} {form.unit}</strong></p>
              <p>Reason: <strong>{transactionTypes.find(t => t.value === form.transaction_type)?.label}</strong></p>
              {form.transaction_type === 'SALE' && form.price > 0 && (
                <p>Total: <strong>₹{(form.quantity * form.price).toLocaleString('en-IN')}</strong></p>
              )}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !form.product_id || form.quantity <= 0}
          className="w-full touch-btn bg-rose-500 hover:bg-rose-600 text-white font-semibold text-sm py-3.5 disabled:opacity-50"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Removing Stock...</>
          ) : (
            <><PackageMinus className="w-4 h-4" /> Remove Stock</>
          )}
        </button>
      </form>
    </div>
  );
}
