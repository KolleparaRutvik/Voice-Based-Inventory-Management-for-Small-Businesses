import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Package,
  PlusCircle,
  MinusCircle,
  TrendingUp,
  AlertTriangle,
  Scale,
  Edit2,
  Check,
  X,
  Loader2,
  Calendar,
  Layers,
} from 'lucide-react';
import { productsService, inventoryService, transactionsService } from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import type { Product, Transaction } from '../../types';

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const [product, setProduct] = useState<Product | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Modals
  const [showStockModal, setShowStockModal] = useState<'IN' | 'OUT' | null>(null);
  const [stockQty, setStockQty] = useState('');
  const [stockUnit, setStockUnit] = useState('');
  const [stockPrice, setStockPrice] = useState('');
  const [stockNotes, setStockNotes] = useState('');

  const [showEditPrice, setShowEditPrice] = useState(false);
  const [editSellingPrice, setEditSellingPrice] = useState('');
  const [editPurchasePrice, setEditPurchasePrice] = useState('');
  const [editMinStock, setEditMinStock] = useState('');

  useEffect(() => {
    if (id) {
      loadProductData(id);
    }
  }, [id]);

  const loadProductData = async (productId: string) => {
    setLoading(true);
    setError('');
    try {
      const [prodRes, txRes] = await Promise.all([
        productsService.getById(productId),
        transactionsService.getAll({ product_id: productId, per_page: 5 }),
      ]);

      if (prodRes.success && prodRes.data) {
        const p = prodRes.data as Product;
        setProduct(p);
        setEditSellingPrice(String(p.selling_price || ''));
        setEditPurchasePrice(String(p.purchase_price || ''));
        setEditMinStock(String(p.minimum_stock || ''));
        setStockUnit(p.base_unit || 'kg');
      }

      if (txRes.success && txRes.data) {
        const txList = (txRes.data as { items: Transaction[] }).items || (txRes.data as Transaction[]) || [];
        setTransactions(txList);
      }
    } catch {
      setError('Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const handleStockAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product || !stockQty || Number(stockQty) <= 0) return;

    setActionLoading(true);
    setError('');
    try {
      const payload = {
        product_id: product.id,
        quantity: Number(stockQty),
        unit: stockUnit || product.base_unit,
        price: stockPrice ? Number(stockPrice) : undefined,
        notes: stockNotes || (showStockModal === 'IN' ? 'Manual Quick Stock In' : 'Manual Quick Stock Out'),
      };

      if (showStockModal === 'IN') {
        await inventoryService.stockIn(payload);
        setSuccessMsg(`Successfully added ${stockQty} ${stockUnit} to inventory!`);
      } else {
        await inventoryService.stockOut(payload);
        setSuccessMsg(`Successfully deducted ${stockQty} ${stockUnit} from inventory!`);
      }

      setShowStockModal(null);
      setStockQty('');
      setStockNotes('');
      await loadProductData(product.id);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Stock update failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdatePricing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product) return;

    setActionLoading(true);
    setError('');
    try {
      await productsService.update(product.id, {
        selling_price: Number(editSellingPrice) || product.selling_price,
        purchase_price: Number(editPurchasePrice) || product.purchase_price,
        minimum_stock: Number(editMinStock) || product.minimum_stock,
      });

      setSuccessMsg('Product pricing updated successfully!');
      setShowEditPrice(false);
      await loadProductData(product.id);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Pricing update failed');
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (amt: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 1,
    }).format(amt);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 animate-spin text-primary-600 mb-3" />
        <p className="text-surface-500 font-medium">{t('loading')}</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="page-container py-12 text-center">
        <Package className="w-12 h-12 text-surface-300 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-surface-900">Product not found</h3>
        <button
          onClick={() => navigate('/products')}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium"
        >
          Back to Products
        </button>
      </div>
    );
  }

  // Stock calculations
  const currentStock = product.current_stock ?? 0;
  const isLowStock = currentStock <= product.minimum_stock;
  const conversionFactor = product.conversion_factor || 1;
  const purchaseUnitsAvailable = conversionFactor > 1 ? (currentStock / conversionFactor).toFixed(1) : null;
  const costPerBaseUnit = conversionFactor > 0 ? product.purchase_price / conversionFactor : product.purchase_price;
  const profitPerUnit = (product.selling_price || 0) - costPerBaseUnit;
  const marginPct = product.selling_price > 0 ? Math.round((profitPerUnit / product.selling_price) * 100) : 0;
  const totalStockValue = currentStock * costPerBaseUnit;

  return (
    <div className="page-container py-6 space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/products')}
            className="p-2 rounded-xl bg-white border border-surface-200 hover:bg-surface-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-surface-900">{product.name}</h1>
              {product.local_name && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary-100 text-primary-800">
                  {product.local_name}
                </span>
              )}
            </div>
            <p className="text-xs text-surface-500 mt-0.5">
              {product.category || 'General'} • {product.base_unit}
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowEditPrice(true)}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-surface-200 text-surface-700 text-xs font-semibold hover:bg-surface-50 shadow-sm"
        >
          <Edit2 className="w-3.5 h-3.5" />
          <span>Edit Details</span>
        </button>
      </div>

      {/* Notifications / Alerts */}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium flex items-center gap-2 animate-slide-down">
          <Check className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm font-medium flex items-center gap-2 animate-slide-down">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Stock Card */}
      <div className="card bg-gradient-to-br from-white to-surface-50 border border-surface-200 p-6 rounded-2xl shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-100 pb-5">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-surface-400">
              {t('currentStock')}
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-4xl font-extrabold text-surface-900">{currentStock}</span>
              <span className="text-lg font-bold text-surface-500">{product.base_unit}</span>
              {purchaseUnitsAvailable && (
                <span className="text-sm font-medium text-surface-500 ml-2">
                  (≈ {purchaseUnitsAvailable} {product.purchase_unit}s)
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 mt-2">
              {isLowStock ? (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Low Stock (Min: {product.minimum_stock} {product.base_unit})
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                  <Check className="w-3.5 h-3.5" />
                  Stock Healthy (Min: {product.minimum_stock} {product.base_unit})
                </span>
              )}
              <span className="text-xs text-surface-400">• Total Value: {formatCurrency(totalStockValue)}</span>
            </div>
          </div>

          {/* Quick Stock In / Out Buttons */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => {
                setShowStockModal('IN');
                setStockQty('');
                setStockPrice(String(product.purchase_price || ''));
                setStockUnit(product.purchase_unit || product.base_unit);
              }}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 active:scale-95 transition-all shadow-sm"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t('stockIn')}</span>
            </button>

            <button
              onClick={() => {
                setShowStockModal('OUT');
                setStockQty('');
                setStockPrice(String(product.selling_price || ''));
                setStockUnit(product.selling_unit || product.base_unit);
              }}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-600 text-white text-sm font-semibold hover:bg-amber-700 active:scale-95 transition-all shadow-sm"
            >
              <MinusCircle className="w-4 h-4" />
              <span>{t('stockOut')}</span>
            </button>
          </div>
        </div>

        {/* Unit Conversion & Packaging Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          <div className="p-4 rounded-xl bg-white border border-surface-200">
            <div className="flex items-center gap-2 text-surface-500 mb-1">
              <Scale className="w-4 h-4 text-primary-600" />
              <span className="text-xs font-semibold uppercase">{t('unitConversion')}</span>
            </div>
            <p className="text-base font-bold text-surface-900">
              1 {product.purchase_unit} = {product.conversion_factor} {product.base_unit}
            </p>
            <p className="text-xs text-surface-400 mt-1">
              Sold per {product.selling_unit}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-surface-200">
            <div className="flex items-center gap-2 text-surface-500 mb-1">
              <Layers className="w-4 h-4 text-accent-600" />
              <span className="text-xs font-semibold uppercase">Pricing & Cost</span>
            </div>
            <p className="text-base font-bold text-surface-900">
              {formatCurrency(product.selling_price)} / {product.selling_unit}
            </p>
            <p className="text-xs text-surface-400 mt-1">
              Cost: {formatCurrency(costPerBaseUnit)} / {product.base_unit} ({formatCurrency(product.purchase_price)}/{product.purchase_unit})
            </p>
          </div>

          <div className="p-4 rounded-xl bg-white border border-surface-200">
            <div className="flex items-center gap-2 text-surface-500 mb-1">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-semibold uppercase">Margin & Profit</span>
            </div>
            <p className="text-base font-bold text-emerald-600">
              +{formatCurrency(profitPerUnit)} ({marginPct}%)
            </p>
            <p className="text-xs text-surface-400 mt-1">
              Profit per {product.selling_unit} sold
            </p>
          </div>
        </div>
      </div>

      {/* Recent Ledger Transactions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-surface-900">{t('recentTransactions')}</h2>
          <button
            onClick={() => navigate('/transactions')}
            className="text-xs font-semibold text-primary-600 hover:text-primary-700"
          >
            View all
          </button>
        </div>

        {transactions.length === 0 ? (
          <div className="p-6 text-center rounded-xl bg-white border border-surface-200 text-surface-400 text-sm">
            No stock transactions recorded yet for this product.
          </div>
        ) : (
          <div className="space-y-2">
            {transactions.map((tx) => (
              <div
                key={tx.id}
                className="flex items-center justify-between p-3.5 rounded-xl bg-white border border-surface-100 hover:border-surface-200 transition-all text-sm"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs ${
                      tx.transaction_type === 'STOCK_IN'
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {tx.transaction_type === 'STOCK_IN' ? '+IN' : '-OUT'}
                  </div>
                  <div>
                    <p className="font-semibold text-surface-900">
                      {tx.quantity} {tx.unit}
                    </p>
                    <p className="text-xs text-surface-400">
                      {tx.notes || tx.transaction_type}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="font-bold text-surface-900">
                    {tx.total_amount ? formatCurrency(tx.total_amount) : '—'}
                  </p>
                  <p className="text-[10px] text-surface-400 flex items-center justify-end gap-1">
                    <Calendar className="w-3 h-3" />
                    {tx.created_at ? new Date(tx.created_at).toLocaleDateString() : 'Today'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stock Adjustment Modal (IN / OUT) */}
      {showStockModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-slide-up">
            <div className="flex items-center justify-between border-b border-surface-100 pb-3">
              <h3 className="text-lg font-bold text-surface-900 flex items-center gap-2">
                {showStockModal === 'IN' ? (
                  <>
                    <PlusCircle className="w-5 h-5 text-emerald-600" />
                    <span>Quick Stock In (+ కొనుగోలు)</span>
                  </>
                ) : (
                  <>
                    <MinusCircle className="w-5 h-5 text-amber-600" />
                    <span>Quick Stock Out (- అమ్మకం)</span>
                  </>
                )}
              </h3>
              <button
                onClick={() => setShowStockModal(null)}
                className="p-1 rounded-lg hover:bg-surface-100 text-surface-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleStockAction} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  Product
                </label>
                <input
                  type="text"
                  readOnly
                  value={`${product.name} ${product.local_name ? `(${product.local_name})` : ''}`}
                  className="input-field bg-surface-50 text-surface-700 cursor-not-allowed text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">
                    Quantity *
                  </label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={stockQty}
                    onChange={(e) => setStockQty(e.target.value)}
                    placeholder="e.g. 5"
                    className="input-field text-base font-bold text-surface-900"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">
                    Unit
                  </label>
                  <select
                    value={stockUnit}
                    onChange={(e) => setStockUnit(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value={product.base_unit}>{product.base_unit} (Base)</option>
                    {product.purchase_unit !== product.base_unit && (
                      <option value={product.purchase_unit}>{product.purchase_unit} ({product.conversion_factor} {product.base_unit})</option>
                    )}
                    {product.selling_unit !== product.base_unit && product.selling_unit !== product.purchase_unit && (
                      <option value={product.selling_unit}>{product.selling_unit}</option>
                    )}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  {showStockModal === 'IN' ? 'Purchase Price (per unit)' : 'Selling Price (per unit)'} (₹)
                </label>
                <input
                  type="number"
                  step="any"
                  value={stockPrice}
                  onChange={(e) => setStockPrice(e.target.value)}
                  placeholder="Optional price"
                  className="input-field text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  Notes / Reason
                </label>
                <input
                  type="text"
                  value={stockNotes}
                  onChange={(e) => setStockNotes(e.target.value)}
                  placeholder="e.g. Received from wholesaler"
                  className="input-field text-sm"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowStockModal(null)}
                  className="px-4 py-2 rounded-xl text-surface-600 font-medium text-sm hover:bg-surface-100"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className={`px-5 py-2.5 rounded-xl text-white font-semibold text-sm shadow-md transition-all ${
                    showStockModal === 'IN'
                      ? 'bg-emerald-600 hover:bg-emerald-700'
                      : 'bg-amber-600 hover:bg-amber-700'
                  }`}
                >
                  {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : t('confirm')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Pricing & Threshold Modal */}
      {showEditPrice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-slide-up">
            <div className="flex items-center justify-between border-b border-surface-100 pb-3">
              <h3 className="text-lg font-bold text-surface-900 flex items-center gap-2">
                <Edit2 className="w-5 h-5 text-primary-600" />
                <span>Edit Product Pricing</span>
              </h3>
              <button
                onClick={() => setShowEditPrice(false)}
                className="p-1 rounded-lg hover:bg-surface-100 text-surface-400"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdatePricing} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  Selling Price per {product.selling_unit} (₹)
                </label>
                <input
                  type="number"
                  step="any"
                  required
                  value={editSellingPrice}
                  onChange={(e) => setEditSellingPrice(e.target.value)}
                  className="input-field text-base font-bold text-surface-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  Purchase Price per {product.purchase_unit} (₹)
                </label>
                <input
                  type="number"
                  step="any"
                  required
                  value={editPurchasePrice}
                  onChange={(e) => setEditPurchasePrice(e.target.value)}
                  className="input-field text-base font-bold text-surface-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">
                  Minimum Stock Alert Threshold ({product.base_unit})
                </label>
                <input
                  type="number"
                  step="any"
                  required
                  value={editMinStock}
                  onChange={(e) => setEditMinStock(e.target.value)}
                  className="input-field text-sm"
                />
                <p className="text-[11px] text-surface-400 mt-1">
                  DukaanSetu alerts you when stock dips below this limit.
                </p>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEditPrice(false)}
                  className="px-4 py-2 rounded-xl text-surface-600 font-medium text-sm hover:bg-surface-100"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-5 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-semibold text-sm shadow-md"
                >
                  {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : t('save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
