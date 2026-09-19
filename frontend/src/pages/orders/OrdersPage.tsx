import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShoppingBag, Plus, ArrowLeft, Building2, 
  MessageSquare, Loader2 
} from 'lucide-react';
import { purchaseOrdersService, suppliersService, productsService } from '../../services/api';
import type { Supplier, Product } from '../../types';

interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier_id: string;
  supplier_name?: string;
  status: 'DRAFT' | 'SENT' | 'CONFIRMED' | 'RECEIVED' | 'CANCELLED';
  total_amount: number;
  created_at: string;
}

export default function OrdersPage() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [selectedSupplierId, setSelectedSupplierId] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unitPrice, setUnitPrice] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [oRes, sRes, pRes] = await Promise.all([
        purchaseOrdersService.getAll(),
        suppliersService.getAll(),
        productsService.getAll(),
      ]);
      const oItems = (oRes.data as any)?.items;
      if (oRes.success && oItems) setOrders(oItems);
      const sItems = (sRes.data as any)?.items;
      if (sRes.success && sItems) {
        setSuppliers(sItems);
        if (sItems.length > 0) setSelectedSupplierId(sItems[0].id);
      }
      const pItems = (pRes.data as any)?.items;
      if (pRes.success && pItems) {
        setProducts(pItems);
        if (pItems.length > 0) {
          setSelectedProductId(pItems[0].id);
          setUnitPrice(String(pItems[0].purchase_price || 1000));
        }
      }
    } catch {
      // Fallback sample orders for demo
      setOrders([
        {
          id: 'po-1',
          order_number: 'PO-2026-001',
          supplier_id: 's1',
          supplier_name: 'ABC Traders',
          status: 'SENT',
          total_amount: 14500,
          created_at: new Date().toISOString(),
        },
        {
          id: 'po-2',
          order_number: 'PO-2026-002',
          supplier_id: 's2',
          supplier_name: 'Srinivas Wholesale',
          status: 'CONFIRMED',
          total_amount: 4200,
          created_at: new Date(Date.now() - 86400000).toISOString(),
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplierId || !selectedProductId || !quantity) return;
    setSubmitting(true);
    try {
      const prod = products.find(p => p.id === selectedProductId);
      const supp = suppliers.find(s => s.id === selectedSupplierId);
      const q = parseFloat(quantity);
      const pr = parseFloat(unitPrice) || (prod?.purchase_price || 1000);
      
      const newOrder: PurchaseOrder = {
        id: `po-${Date.now()}`,
        order_number: `PO-2026-${String(orders.length + 1).padStart(3, '0')}`,
        supplier_id: selectedSupplierId,
        supplier_name: supp?.name || 'Wholesale Supplier',
        status: 'SENT',
        total_amount: q * pr,
        created_at: new Date().toISOString(),
      };

      setOrders(prev => [newOrder, ...prev]);
      setShowCreateModal(false);
      setQuantity('');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create order');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in pb-12">
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
            <p className="text-sm text-surface-500">Create reorder slips & send directly to suppliers via WhatsApp</p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="touch-btn gradient-primary text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow-sm gap-2"
        >
          <Plus className="w-4 h-4" /> Create Purchase Order
        </button>
      </div>

      {/* Orders List */}
      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Loading orders...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="card py-12 text-center">
          <ShoppingBag className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-surface-700">No purchase orders created</p>
          <p className="text-sm text-surface-400 mt-1">Tap "Create Purchase Order" to generate a restock request.</p>
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
                  <span>• {new Date(po.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span>
                </p>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-surface-100">
                <div className="text-left sm:text-right">
                  <p className="text-xs text-surface-400">Order Value</p>
                  <p className="text-xl font-black text-surface-900">
                    ₹{po.total_amount.toLocaleString('en-IN')}
                  </p>
                </div>

                <a
                  href={`https://wa.me/?text=${encodeURIComponent(
                    `Namaste! Purchase Order ${po.order_number} from Sri Lakshmi Kirana Store.\nTotal Amount: Rs. ${po.total_amount}\nPlease confirm dispatch.`
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="touch-btn bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold px-3 py-2 rounded-xl gap-1.5 shadow-sm"
                >
                  <MessageSquare className="w-4 h-4" /> Share on WhatsApp
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
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
                    <option key={s.id} value={s.id}>{s.name} ({s.phone})</option>
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
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate PO'}
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
