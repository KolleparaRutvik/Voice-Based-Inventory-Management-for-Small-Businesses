import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Check } from 'lucide-react';
import { productsService, suppliersService } from '../../services/api';
import { UNITS, CATEGORIES } from '../../types';
import type { Supplier } from '../../types';

export default function AddProductPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  const [form, setForm] = useState({
    name: '',
    local_name: '',
    category: '',
    base_unit: 'kg',
    purchase_unit: 'bag',
    selling_unit: 'kg',
    conversion_factor: 25,
    purchase_price: 0,
    selling_price: 0,
    minimum_stock: 0,
    recommended_stock: 0,
    reorder_quantity: 0,
    supplier_id: '',
  });

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    try {
      const result = await suppliersService.getAll();
      if (result.success && result.data) {
        setSuppliers((result.data as { items: Supplier[] }).items || result.data as Supplier[]);
      }
    } catch {
      // Ignore
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await productsService.create(form);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => navigate('/products'), 1500);
      } else {
        setError(result.error?.message || 'Failed to create product');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  const unitCostDisplay = () => {
    if (form.purchase_price > 0 && form.conversion_factor > 0) {
      const unitCost = form.purchase_price / form.conversion_factor;
      return `₹${unitCost.toFixed(2)} per ${form.base_unit}`;
    }
    return null;
  };

  const marginDisplay = () => {
    if (form.purchase_price > 0 && form.selling_price > 0 && form.conversion_factor > 0) {
      const unitCost = form.purchase_price / form.conversion_factor;
      const margin = form.selling_price - unitCost;
      const marginPercent = ((margin / unitCost) * 100).toFixed(1);
      return `₹${margin.toFixed(2)} margin (${marginPercent}%)`;
    }
    return null;
  };

  if (success) {
    return (
      <div className="page-container pt-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-emerald-600" />
          </div>
          <p className="text-lg font-semibold text-surface-900">Product Added!</p>
          <p className="text-sm text-surface-500 mt-1">Redirecting to products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
          <ArrowLeft className="w-5 h-5 text-surface-600" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-surface-900">Add Product</h2>
          <p className="text-sm text-surface-500">Add a new product to your shop</p>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Basic Info */}
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <h3 className="text-sm font-semibold text-surface-700">Basic Information</h3>
          
          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="prod-name">Product Name *</label>
            <input id="prod-name" name="name" value={form.name} onChange={handleChange} className="input-field" placeholder="Rice" required />
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="prod-local">Local Name</label>
            <input id="prod-local" name="local_name" value={form.local_name} onChange={handleChange} className="input-field" placeholder="Biyyam" />
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="prod-category">Category</label>
            <select id="prod-category" name="category" value={form.category} onChange={handleChange} className="input-field">
              <option value="">Select Category</option>
              {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>
        </div>

        {/* Units */}
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <h3 className="text-sm font-semibold text-surface-700">Units & Conversion</h3>
          
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-base-unit">Base Unit</label>
              <select id="prod-base-unit" name="base_unit" value={form.base_unit} onChange={handleChange} className="input-field text-sm">
                {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-purchase-unit">Purchase Unit</label>
              <select id="prod-purchase-unit" name="purchase_unit" value={form.purchase_unit} onChange={handleChange} className="input-field text-sm">
                {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-sell-unit">Selling Unit</label>
              <select id="prod-sell-unit" name="selling_unit" value={form.selling_unit} onChange={handleChange} className="input-field text-sm">
                {UNITS.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-600 mb-1" htmlFor="prod-conv">
              Conversion: 1 {form.purchase_unit} = ? {form.base_unit}
            </label>
            <input id="prod-conv" name="conversion_factor" type="number" step="0.01" min="0" value={form.conversion_factor} onChange={handleChange} className="input-field" />
          </div>
        </div>

        {/* Pricing */}
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <h3 className="text-sm font-semibold text-surface-700">Pricing</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-pprice">Purchase Price (₹/{form.purchase_unit})</label>
              <input id="prod-pprice" name="purchase_price" type="number" step="0.01" min="0" value={form.purchase_price || ''} onChange={handleChange} className="input-field" placeholder="0" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-sprice">Selling Price (₹/{form.selling_unit})</label>
              <input id="prod-sprice" name="selling_price" type="number" step="0.01" min="0" value={form.selling_price || ''} onChange={handleChange} className="input-field" placeholder="0" />
            </div>
          </div>

          {(unitCostDisplay() || marginDisplay()) && (
            <div className="p-3 rounded-xl bg-surface-50 text-xs text-surface-600 space-y-1">
              {unitCostDisplay() && <p>Unit cost: {unitCostDisplay()}</p>}
              {marginDisplay() && <p className="text-emerald-600 font-medium">{marginDisplay()}</p>}
            </div>
          )}
        </div>

        {/* Stock Levels */}
        <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
          <h3 className="text-sm font-semibold text-surface-700">Stock Levels ({form.base_unit})</h3>
          
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-min">Minimum</label>
              <input id="prod-min" name="minimum_stock" type="number" step="0.01" min="0" value={form.minimum_stock || ''} onChange={handleChange} className="input-field" placeholder="0" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-rec">Recommended</label>
              <input id="prod-rec" name="recommended_stock" type="number" step="0.01" min="0" value={form.recommended_stock || ''} onChange={handleChange} className="input-field" placeholder="0" />
            </div>
            <div>
              <label className="block text-xs font-medium text-surface-600 mb-1" htmlFor="prod-reorder">Reorder Qty</label>
              <input id="prod-reorder" name="reorder_quantity" type="number" step="0.01" min="0" value={form.reorder_quantity || ''} onChange={handleChange} className="input-field" placeholder="0" />
            </div>
          </div>
        </div>

        {/* Supplier */}
        {suppliers.length > 0 && (
          <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
            <h3 className="text-sm font-semibold text-surface-700">Supplier</h3>
            <select name="supplier_id" value={form.supplier_id} onChange={handleChange} className="input-field">
              <option value="">Select Supplier (optional)</option>
              {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !form.name}
          className="w-full touch-btn gradient-primary text-white font-semibold text-sm py-3.5 disabled:opacity-50"
        >
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Adding Product...</>
          ) : (
            'Add Product'
          )}
        </button>
      </form>
    </div>
  );
}
