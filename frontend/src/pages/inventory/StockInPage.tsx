import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Check, PackagePlus } from 'lucide-react';
import { inventoryService, productsService } from '../../services/api';
import { UNITS } from '../../types';
import type { Product } from '../../types';

export default function StockInPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    product_id: '',
    quantity: 0,
    unit: 'bag',
    price: 0,
    notes: '',
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const result = await productsService.getAll();
      if (result.success && result.data) {
        setProducts((result.data as { items: Product[] }).items || result.data as Product[]);
      }
    } catch {
      setProducts([
        { id: '1', shop_id: '', name: 'Rice (Biyyam)', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 25, purchase_price: 1450, selling_price: 65, minimum_stock: 5, recommended_stock: 20, reorder_quantity: 10, is_active: true, created_at: '', updated_at: '' },
        { id: '2', shop_id: '', name: 'Sugar (Chakkera)', base_unit: 'kg', purchase_unit: 'bag', selling_unit: 'kg', conversion_factor: 50, purchase_price: 2100, selling_price: 48, minimum_stock: 10, recommended_stock: 50, reorder_quantity: 25, is_active: true, created_at: '', updated_at: '' },
        { id: '3', shop_id: '', name: 'Sunflower Oil', base_unit: 'litre', purchase_unit: 'can', selling_unit: 'litre', conversion_factor: 15, purchase_price: 2250, selling_price: 165, minimum_stock: 5, recommended_stock: 30, reorder_quantity: 15, is_active: true, created_at: '', updated_at: '' },
      ]);
    }
  };

  const selectedProduct = products.find(p => p.id === form.product_id);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await inventoryService.stockIn(form);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => navigate('/inventory'), 2000);
      } else {
        setError(result.error?.message || 'Failed to add stock');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add stock');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="page-container pt-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-emerald-600" />
          </div>
          <p className="text-lg font-semibold text-surface-900">Stock Added!</p>
          <p className="text-sm text-surface-500 mt-1">
            {form.quantity} {form.unit} of {selectedProduct?.name} added to inventory
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
            <PackagePlus className="w-5 h-5 text-emerald-500" /> Stock In
          </h2>
          <p className="text-sm text-surface-500">Add stock to inventory</p>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="si-product">Product *</label>
            <select
              id="si-product"
              value={form.product_id}
              onChange={(e) => {
                const prod = products.find(p => p.id === e.target.value);
                setForm(prev => ({
                  ...prev,
                  product_id: e.target.value,
                  unit: prod?.purchase_unit || 'bag',
                  price: prod?.purchase_price || 0,
                }));
              }}
              className="input-field"
              required
            >
              <option value="">Select Product</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="si-qty">Quantity *</label>
              <input
                id="si-qty"
                type="number"
                step="0.01"
                min="0.01"
                value={form.quantity || ''}
                onChange={(e) => setForm(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 0 }))}
                className="input-field"
                placeholder="10"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="si-unit">Unit</label>
              <select
                id="si-unit"
                value={form.unit}
                onChange={(e) => setForm(prev => ({ ...prev, unit: e.target.value }))}
                className="input-field"
              >
                {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="si-price">Price per {form.unit} (₹)</label>
            <input
              id="si-price"
              type="number"
              step="0.01"
              min="0"
              value={form.price || ''}
              onChange={(e) => setForm(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
              className="input-field"
              placeholder="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="si-notes">Notes (optional)</label>
            <input
              id="si-notes"
              type="text"
              value={form.notes}
              onChange={(e) => setForm(prev => ({ ...prev, notes: e.target.value }))}
              className="input-field"
              placeholder="e.g., From ABC Traders"
            />
          </div>
        </div>

        {/* Summary */}
        {form.product_id && form.quantity > 0 && (
          <div className="bg-emerald-50 rounded-2xl border border-emerald-200 p-4 animate-slide-up">
            <h4 className="text-sm font-semibold text-emerald-800 mb-2">Summary</h4>
            <div className="space-y-1 text-sm text-emerald-700">
              <p>Product: <strong>{selectedProduct?.name}</strong></p>
              <p>Quantity: <strong>{form.quantity} {form.unit}</strong></p>
              {selectedProduct && form.unit !== selectedProduct.base_unit && (
                <p>In base units: <strong>{(form.quantity * (selectedProduct.conversion_factor || 1)).toFixed(2)} {selectedProduct.base_unit}</strong></p>
              )}
              {form.price > 0 && (
                <p>Total: <strong>₹{(form.quantity * form.price).toLocaleString('en-IN')}</strong></p>
              )}
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !form.product_id || form.quantity <= 0}
          className="w-full touch-btn bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm py-3.5 disabled:opacity-50"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Adding Stock...</>
          ) : (
            <><PackagePlus className="w-4 h-4" /> Add Stock</>
          )}
        </button>
      </form>
    </div>
  );
}
