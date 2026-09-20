import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShoppingBag, Plus, ArrowLeft, Building2, 
  MessageSquare, Loader2, Download, Sparkles, RefreshCw
} from 'lucide-react';
import { purchaseOrdersService, suppliersService, productsService, reorderService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { getStorePersona } from '../../utils/storePersonalization';
import type { Supplier, Product } from '../../types';

interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier_id: string;
  supplier_name?: string;
  supplier_phone?: string;
  status: 'DRAFT' | 'SENT' | 'CONFIRMED' | 'RECEIVED' | 'CANCELLED';
  total_amount: number;
  created_at: string;
}

interface ReorderRecommendation {
  product_id: string;
  product_name: string;
  local_name?: string;
  category?: string;
  current_stock: number;
  base_unit: string;
  purchase_unit: string;
  minimum_stock: number;
  recommended_quantity: number;
  estimated_cost: number;
  urgency: 'HIGH' | 'MEDIUM' | 'NORMAL';
  reason: string;
  supplier_id?: string;
  supplier_name: string;
  avg_daily_sales: number;
}

export default function OrdersPage() {
  const navigate = useNavigate();
  const { user, shop } = useAuth();
  const storePersona = getStorePersona(shop?.type || (user as any)?.shop_type || localStorage.getItem('dukaansetu_store_type'));
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [recommendations, setRecommendations] = useState<ReorderRecommendation[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [selectedSupplierId, setSelectedSupplierId] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unitPrice, setUnitPrice] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [oRes, sRes, pRes] = await Promise.all([
        purchaseOrdersService.getAll(),
        suppliersService.getAll(),
        productsService.getAll(),
      ]);

      if (oRes.success && (oRes.data as any)?.items) {
        setOrders((oRes.data as any).items);
      } else {
        setOrders([]);
      }

      if (sRes.success && (sRes.data as any)?.items) {
        const sItems = (sRes.data as any).items;
        setSuppliers(sItems);
        if (sItems.length > 0 && !selectedSupplierId) setSelectedSupplierId(sItems[0].id);
      }

      if (pRes.success && (pRes.data as any)?.items) {
        const pItems = (pRes.data as any).items;
        setProducts(pItems);
        if (pItems.length > 0 && !selectedProductId) {
          setSelectedProductId(pItems[0].id);
          setUnitPrice(String(pItems[0].purchase_price || 1000));
        }
      }

      // Load AI reorder recommendations
      loadReorderRecommendations();

    } catch (err: any) {
      setError(err?.message || 'Failed to load purchase orders from database');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const loadReorderRecommendations = async () => {
    try {
      const recRes = await reorderService.getRecommendations();
      if (recRes.success && (recRes.data as any)?.items) {
        setRecommendations((recRes.data as any).items);
      }
    } catch {
      setRecommendations([]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleQuickReorder = (rec: ReorderRecommendation) => {
    setSelectedProductId(rec.product_id);
    if (rec.supplier_id) setSelectedSupplierId(rec.supplier_id);
    setQuantity(String(rec.recommended_quantity));
    const prod = products.find(p => p.id === rec.product_id);
    if (prod) setUnitPrice(String(prod.purchase_price || 1000));
    setShowCreateModal(true);
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId || !selectedProductId || !quantity) return;
    setSubmitting(true);
    try {
      const prod = products.find(p => p.id === selectedProductId);
      const q = parseFloat(quantity);
      const pr = parseFloat(unitPrice) || (prod?.purchase_price || 1000);

      const res = await purchaseOrdersService.create({
        supplier_id: selectedSupplierId,
        product_id: selectedProductId,
        quantity: q,
        unit: prod?.base_unit || 'unit',
        unit_price: pr,
        notes: `Reorder for ${prod?.name || 'product'}`
      });

      if (res.success && res.data) {
        setShowCreateModal(false);
        setQuantity('');
        await loadData();
      } else {
        throw new Error('Failed to create purchase order');
      }
    } catch (err: any) {
      alert(err instanceof Error ? err.message : 'Failed to create order');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDownloadPdf = async (orderId: string, orderNum: string) => {
    setDownloadingId(orderId);
    try {
      const blob = await purchaseOrdersService.getPdf(orderId);
      const url = window.URL.createObjectURL(new Blob([blob as any], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Purchase_Order_${orderNum}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      alert('Failed to download PDF invoice: ' + (err?.message || 'Server error'));
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
              <ShoppingBag className="w-6 h-6 text-primary-600" />
              Purchase Orders & Reorders
            </h2>
            <p className="text-sm text-surface-500">Automated Kirana restock planner with live Supabase synchronization</p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="touch-btn gradient-primary text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow-sm gap-2"
        >
          <Plus className="w-4 h-4" /> Create Purchase Order
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          <span>{error}</span>
          <button onClick={loadData} className="flex items-center gap-1 font-semibold underline">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      )}

      {/* Smart Reorder Recommendations Banner */}
      {recommendations.length > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-600" />
              <h3 className="font-bold text-amber-900 text-base">Smart Reorder Recommendations</h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-200 text-amber-900">
                {recommendations.length} items need restock
              </span>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {recommendations.map((rec) => (
              <div key={rec.product_id} className="bg-white/90 backdrop-blur-sm p-3.5 rounded-xl border border-amber-200 flex items-center justify-between gap-3 shadow-xs">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-bold text-sm text-surface-900 truncate">{rec.product_name}</p>
                    <span className="px-1.5 py-0.2 text-[10px] font-bold rounded bg-red-100 text-red-800">
                      {rec.urgency}
                    </span>
                  </div>
                  <p className="text-xs text-surface-500 mt-0.5">
                    Stock: <b className="text-red-600">{rec.current_stock} {rec.base_unit}</b> (Min: {rec.minimum_stock})
                  </p>
                  <p className="text-[11px] text-surface-400 truncate mt-0.5">{rec.reason}</p>
                </div>
                <button
                  onClick={() => handleQuickReorder(rec)}
                  className="flex-shrink-0 px-3 py-1.5 rounded-lg gradient-primary text-white text-xs font-semibold shadow-xs hover:opacity-95"
                >
                  Order {rec.recommended_quantity} {rec.purchase_unit}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Orders List */}
      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Loading orders from database...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="card py-12 text-center">
          <ShoppingBag className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-surface-700">No purchase orders created</p>
          <p className="text-sm text-surface-400 mt-1">Tap "Create Purchase Order" or order from the recommendations above.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((po) => (
            <div key={po.id} className="card p-4 hover:border-primary-200 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <p className="text-base font-bold text-surface-900">{po.order_number}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                    po.status === 'RECEIVED' ? 'bg-emerald-100 text-emerald-800' :
                    po.status === 'SENT' ? 'bg-blue-100 text-blue-800' :
                    'bg-amber-100 text-amber-800'
                  }`}>
                    {po.status}
                  </span>
                </div>
                <p className="text-xs text-surface-500 flex items-center gap-2">
                  <Building2 className="w-3.5 h-3.5 text-surface-400" />
                  Supplier: <span className="font-semibold text-surface-700">{po.supplier_name || 'Wholesale Supplier'}</span>
                  <span>• {new Date(po.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                </p>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-3 sm:pt-0 border-surface-100">
                <div className="text-left sm:text-right mr-2">
                  <p className="text-xs text-surface-400">Order Total</p>
                  <p className="text-lg font-black text-surface-900">
                    ₹{po.total_amount.toLocaleString('en-IN')}
                  </p>
                </div>

                {/* PDF Download Button */}
                <button
                  onClick={() => handleDownloadPdf(po.id, po.order_number)}
                  disabled={downloadingId === po.id}
                  className="touch-btn border border-surface-200 hover:bg-surface-50 text-surface-700 text-xs font-semibold px-3 py-2 rounded-xl gap-1.5 shadow-2xs"
                  title="Download PDF Invoice"
                >
                  {downloadingId === po.id ? (
                    <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                  ) : (
                    <Download className="w-4 h-4 text-primary-600" />
                  )}
                  <span>PDF</span>
                </button>

                {/* WhatsApp Share Button */}
                <a
                  href={`https://wa.me/${po.supplier_phone || ''}?text=${encodeURIComponent(
                    `Namaste! Purchase Order ${po.order_number} from ${shop?.name || storePersona.defaultShopName}.\nTotal Amount: Rs. ${po.total_amount}\nPlease confirm dispatch.`
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="touch-btn bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold px-3 py-2 rounded-xl gap-1.5 shadow-sm"
                >
                  <MessageSquare className="w-4 h-4" /> WhatsApp
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create PO Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-scale-up">
            <h3 className="text-lg font-bold text-surface-900">Create Purchase Order (PO)</h3>
            <form onSubmit={handleCreateOrder} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Select Supplier</label>
                <select
                  value={selectedSupplierId}
                  onChange={(e) => setSelectedSupplierId(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                >
                  {suppliers.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.phone || 'No phone'})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Item to Reorder</label>
                <select
                  value={selectedProductId}
                  onChange={(e) => {
                    setSelectedProductId(e.target.value);
                    const found = products.find(p => p.id === e.target.value);
                    if (found) setUnitPrice(String(found.purchase_price));
                  }}
                  className="w-full px-3 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                >
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.name} (Stock: {p.current_stock} {p.base_unit})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">Quantity</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="e.g. 10"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">Est. Unit Price (₹)</label>
                  <input
                    type="number"
                    step="any"
                    value={unitPrice}
                    onChange={(e) => setUnitPrice(e.target.value)}
                    placeholder="e.g. 1450"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl gradient-primary text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate & Save PO'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2.5 rounded-xl border border-surface-200 text-surface-600 font-semibold text-sm hover:bg-surface-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
