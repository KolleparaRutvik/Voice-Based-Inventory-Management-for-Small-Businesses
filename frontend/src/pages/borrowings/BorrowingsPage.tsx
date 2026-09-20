import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, Plus, ArrowLeft, Search, MessageSquare, 
  IndianRupee, Clock, CheckCircle2, AlertCircle, Loader2 
} from 'lucide-react';
import { borrowingsService, productsService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { getStorePersona } from '../../utils/storePersonalization';
import type { Product } from '../../types';

interface BorrowingItem {
  id: string;
  customer_id: string;
  customer_name: string;
  status: 'ACTIVE' | 'PARTIALLY_RETURNED' | 'RETURNED' | 'OVERDUE';
  total_value: number;
  paid_amount: number;
  remaining_balance: number;
  notes?: string;
  created_at: string;
  items?: Array<{
    product_name?: string;
    quantity: number;
    unit: string;
    price: number;
  }>;
}

export default function BorrowingsPage() {
  const navigate = useNavigate();
  const { user, shop } = useAuth();
  const storePersona = getStorePersona(shop?.type || (user as any)?.shop_type || localStorage.getItem('dukaansetu_store_type'));
  const [borrowings, setBorrowings] = useState<BorrowingItem[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'RETURNED'>('ACTIVE');
  
  // Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [showReturnModal, setShowReturnModal] = useState<BorrowingItem | null>(null);
  const [returnAmount, setReturnAmount] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // New borrowing form state
  const [newCustomerName, setNewCustomerName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [borrowNotes, setBorrowNotes] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [bRes, pRes] = await Promise.all([
        borrowingsService.getAll(),
        productsService.getAll(),
      ]);
      const bItems = (bRes.data as any)?.items;
      if (bRes.success && bItems) {
        setBorrowings(bItems);
      }
      const pItems = (pRes.data as any)?.items;
      if (pRes.success && pItems) {
        setProducts(pItems);
        if (pItems.length > 0) {
          setSelectedProductId(pItems[0].id);
        }
      }
    } catch {
      // Handled gracefully
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateBorrowing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCustomerName || !selectedProductId || !quantity) return;
    setSubmitting(true);
    try {
      const prod = products.find(p => p.id === selectedProductId);
      await borrowingsService.create({
        customer_name: newCustomerName,
        customer_phone: newCustomerPhone,
        notes: borrowNotes,
        items: [{
          product_id: selectedProductId,
          quantity: parseFloat(quantity),
          unit: prod?.base_unit || 'kg',
          price: prod?.selling_price || 50,
        }],
      });
      setShowAddModal(false);
      setNewCustomerName('');
      setNewCustomerPhone('');
      setQuantity('');
      setBorrowNotes('');
      await loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to record credit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRecordReturn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showReturnModal || !returnAmount) return;
    setSubmitting(true);
    try {
      await borrowingsService.returnItems(showReturnModal.id, {
        amount_paid: parseFloat(returnAmount),
      });
      setShowReturnModal(null);
      setReturnAmount('');
      await loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  const totalOutstanding = borrowings
    .filter(b => b.status === 'ACTIVE' || b.status === 'PARTIALLY_RETURNED')
    .reduce((sum, b) => sum + (b.remaining_balance || b.total_value || 0), 0);

  const filteredBorrowings = borrowings.filter(b => {
    const matchesSearch = b.customer_name.toLowerCase().includes(search.toLowerCase());
    if (filter === 'ALL') return matchesSearch;
    if (filter === 'ACTIVE') return matchesSearch && (b.status === 'ACTIVE' || b.status === 'PARTIALLY_RETURNED');
    if (filter === 'RETURNED') return matchesSearch && b.status === 'RETURNED';
    return matchesSearch;
  });

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
              <Users className="w-6 h-6 text-primary-600" />
              Customer Credit / Udhar Ledger
            </h2>
            <p className="text-sm text-surface-500">Track items given on borrow and payment status</p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="touch-btn gradient-primary text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow-sm gap-2"
        >
          <Plus className="w-4 h-4" /> Give Credit (Udhar)
        </button>
      </div>

      {/* Outstanding Balance Banner */}
      <div className="card p-5 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-l-amber-500 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold text-amber-800 uppercase tracking-wider">Total Udhar / Outstanding Balance</p>
          <p className="text-3xl font-black text-amber-950 mt-1 flex items-center">
            <IndianRupee className="w-7 h-7" />
            {totalOutstanding.toLocaleString('en-IN')}
          </p>
          <p className="text-xs text-amber-700 mt-1">Across active customer accounts</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium text-amber-900 bg-amber-100/80 px-3 py-2 rounded-xl border border-amber-200/60 self-start sm:self-auto">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>Timely reminders increase repayment speed by 40%</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-surface-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search customer name..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
          />
        </div>
        <div className="flex gap-1.5 p-1 rounded-xl bg-surface-100 self-start">
          {(['ACTIVE', 'ALL', 'RETURNED'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filter === f ? 'bg-white text-surface-900 shadow-sm' : 'text-surface-500 hover:text-surface-700'
              }`}
            >
              {f === 'ACTIVE' ? 'Active Udhar' : f === 'ALL' ? 'All Records' : 'Settled'}
            </button>
          ))}
        </div>
      </div>

      {/* Ledger Table / Cards */}
      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Loading credit ledger...</p>
        </div>
      ) : filteredBorrowings.length === 0 ? (
        <div className="card py-12 text-center">
          <Users className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-surface-700">No credit records found</p>
          <p className="text-sm text-surface-400 mt-1">Tap "Give Credit" to record a customer borrow.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredBorrowings.map((item) => (
            <div key={item.id} className="card p-4 hover:border-primary-200 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <p className="text-base font-bold text-surface-900">{item.customer_name}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                    item.status === 'ACTIVE' ? 'bg-amber-100 text-amber-800' :
                    item.status === 'PARTIALLY_RETURNED' ? 'bg-blue-100 text-blue-800' :
                    'bg-emerald-100 text-emerald-800'
                  }`}>
                    {item.status.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs text-surface-500 flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5" />
                  Given on {new Date(item.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  {item.notes && <span>• {item.notes}</span>}
                </p>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-surface-100">
                <div className="text-left sm:text-right">
                  <p className="text-xs text-surface-400">Balance Due</p>
                  <p className="text-xl font-black text-amber-700">
                    ₹{(item.remaining_balance || item.total_value || 0).toLocaleString('en-IN')}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {/* WhatsApp Reminder Button */}
                  <a
                    href={`https://wa.me/?text=${encodeURIComponent(
                      `Namaste ${item.customer_name}, this is a gentle reminder from ${shop?.name || storePersona.defaultShopName} regarding your pending bill of Rs. ${item.remaining_balance || item.total_value}. Thank you!`
                    )}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="touch-btn border border-emerald-300 bg-emerald-50 text-emerald-700 w-9 h-9 hover:bg-emerald-100"
                    title="Send WhatsApp Reminder"
                  >
                    <MessageSquare className="w-4 h-4" />
                  </a>

                  {item.status !== 'RETURNED' && (
                    <button
                      onClick={() => setShowReturnModal(item)}
                      className="touch-btn bg-surface-900 hover:bg-black text-white text-xs font-semibold px-3 py-2 rounded-xl gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" /> Settle / Pay
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Give Credit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-scale-up">
            <h3 className="text-lg font-bold text-surface-900">Record Customer Credit (Udhar)</h3>
            <form onSubmit={handleCreateBorrowing} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Customer Name</label>
                <input
                  type="text"
                  required
                  value={newCustomerName}
                  onChange={(e) => setNewCustomerName(e.target.value)}
                  placeholder="e.g. Ramesh (Kirana Regular)"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Phone Number (Optional)</label>
                <input
                  type="tel"
                  value={newCustomerPhone}
                  onChange={(e) => setNewCustomerPhone(e.target.value)}
                  placeholder="+91 98480 00000"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">Product</label>
                  <select
                    value={selectedProductId}
                    onChange={(e) => setSelectedProductId(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                  >
                    {products.map(p => (
                      <option key={p.id} value={p.id}>{p.name} (₹{p.selling_price})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">Quantity</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="e.g. 2"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Notes</label>
                <input
                  type="text"
                  value={borrowNotes}
                  onChange={(e) => setBorrowNotes(e.target.value)}
                  placeholder="e.g. Promoted to pay on Monday"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl gradient-primary text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Record Credit'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2.5 rounded-xl border border-surface-200 text-surface-600 font-semibold text-sm hover:bg-surface-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Settle Return Modal */}
      {showReturnModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-scale-up">
            <h3 className="text-lg font-bold text-surface-900">Record Payment from {showReturnModal.customer_name}</h3>
            <p className="text-sm text-surface-500">
              Outstanding Due: <span className="font-bold text-amber-700">₹{(showReturnModal.remaining_balance || showReturnModal.total_value).toLocaleString('en-IN')}</span>
            </p>
            <form onSubmit={handleRecordReturn} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Amount Paid (₹)</label>
                <input
                  type="number"
                  step="any"
                  required
                  autoFocus
                  value={returnAmount}
                  onChange={(e) => setReturnAmount(e.target.value)}
                  placeholder={`e.g. ${showReturnModal.remaining_balance || showReturnModal.total_value}`}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-lg font-bold"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm Payment'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowReturnModal(null)}
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
