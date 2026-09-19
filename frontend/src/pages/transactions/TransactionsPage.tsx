import { useState, useEffect } from 'react';
import { ArrowLeftRight, ArrowUpRight, ArrowDownRight, Search, Loader2 } from 'lucide-react';
import { transactionsService } from '../../services/api';
import type { Transaction } from '../../types';
import { TRANSACTION_TYPES } from '../../types';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  useEffect(() => { loadTransactions(); }, []);

  const loadTransactions = async () => {
    try {
      const result = await transactionsService.getAll();
      if (result.success && result.data) {
        setTransactions((result.data as { items: Transaction[] }).items || result.data as Transaction[]);
      }
    } catch {
      // Demo data
      const now = new Date();
      const demoTx: Transaction[] = [
        { id: '1', shop_id: '', product_id: '1', transaction_type: 'STOCK_IN', quantity: 10, unit: 'bag', price: 1450, total_amount: 14500, source: 'manual', created_at: new Date(now.getTime() - 3600000).toISOString(), product_name: 'Rice (Biyyam)' },
        { id: '2', shop_id: '', product_id: '2', transaction_type: 'SALE', quantity: 5, unit: 'kg', price: 48, total_amount: 240, source: 'manual', created_at: new Date(now.getTime() - 7200000).toISOString(), product_name: 'Sugar (Chakkera)' },
        { id: '3', shop_id: '', product_id: '3', transaction_type: 'SALE', quantity: 2, unit: 'litre', price: 165, total_amount: 330, source: 'voice', created_at: new Date(now.getTime() - 10800000).toISOString(), product_name: 'Sunflower Oil' },
        { id: '4', shop_id: '', product_id: '5', transaction_type: 'STOCK_IN', quantity: 2, unit: 'carton', price: 240, total_amount: 480, source: 'manual', created_at: new Date(now.getTime() - 14400000).toISOString(), product_name: 'Parle-G Biscuits' },
        { id: '5', shop_id: '', product_id: '1', transaction_type: 'BORROW_OUT', quantity: 2, unit: 'bag', price: 0, total_amount: 0, source: 'voice', created_at: new Date(now.getTime() - 18000000).toISOString(), product_name: 'Rice (Biyyam)', customer_name: 'Ramesh' },
        { id: '6', shop_id: '', product_id: '4', transaction_type: 'STOCK_OUT', quantity: 1, unit: 'kg', price: 0, total_amount: 0, source: 'manual', created_at: new Date(now.getTime() - 86400000).toISOString(), product_name: 'Toor Dal', notes: 'Damage' },
      ];
      setTransactions(demoTx);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    if (!amount) return '';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  };

  const isPositive = (type: string) => ['STOCK_IN', 'PURCHASE', 'BORROW_RETURN', 'RETURN'].includes(type);

  const filtered = transactions.filter(tx => {
    const matchesSearch = !search || (tx.product_name || '').toLowerCase().includes(search.toLowerCase());
    const matchesType = !typeFilter || tx.transaction_type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in">
      <div>
        <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
          <ArrowLeftRight className="w-5 h-5 text-primary-500" /> Transactions
        </h2>
        <p className="text-sm text-surface-500">{filtered.length} records</p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search..." className="input-field pl-10" />
        </div>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} className="input-field w-auto min-w-[100px]">
          <option value="">All Types</option>
          {Object.entries(TRANSACTION_TYPES).map(([key, val]) => (
            <option key={key} value={key}>{val.label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary-500" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 rounded-2xl bg-white border border-surface-100">
          <ArrowLeftRight className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-surface-600 font-medium">No transactions found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((tx) => {
            const typeInfo = TRANSACTION_TYPES[tx.transaction_type] || { label: tx.transaction_type, color: 'surface' };
            const positive = isPositive(tx.transaction_type);
            return (
              <div key={tx.id} className="flex items-center gap-3 p-4 rounded-2xl bg-white border border-surface-100">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  positive ? 'bg-emerald-50' : 'bg-rose-50'
                }`}>
                  {positive ? (
                    <ArrowDownRight className="w-5 h-5 text-emerald-600" />
                  ) : (
                    <ArrowUpRight className="w-5 h-5 text-rose-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-surface-900 truncate">{tx.product_name || 'Product'}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={`status-badge ${
                      positive ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                    }`}>
                      {typeInfo.label}
                    </span>
                    {tx.source === 'voice' && (
                      <span className="status-badge bg-purple-50 text-purple-700">🎙 Voice</span>
                    )}
                    <span className="text-[10px] text-surface-400">{formatTime(tx.created_at)}</span>
                  </div>
                  {tx.customer_name && (
                    <p className="text-xs text-surface-500 mt-0.5">Customer: {tx.customer_name}</p>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <p className={`text-sm font-bold ${positive ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {positive ? '+' : '-'}{tx.quantity} {tx.unit}
                  </p>
                  {tx.total_amount > 0 && (
                    <p className="text-xs text-surface-500 mt-0.5">{formatCurrency(tx.total_amount)}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
