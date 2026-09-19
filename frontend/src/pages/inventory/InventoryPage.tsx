import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Package, AlertTriangle, Loader2, PackagePlus, PackageMinus } from 'lucide-react';
import { inventoryService } from '../../services/api';
import type { InventoryItem } from '../../types';

export default function InventoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showLowOnly, setShowLowOnly] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('filter') === 'low_stock') setShowLowOnly(true);
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      const result = await inventoryService.getAll();
      if (result.success && result.data) {
        setItems((result.data as { items: InventoryItem[] }).items || result.data as InventoryItem[]);
      }
    } catch {
      setItems([
        { id: '1', shop_id: '', product_id: '1', current_stock: 450, stock_unit: 'kg', product_name: 'Rice (Biyyam)', product_category: 'Grains & Rice', purchase_price: 58, selling_price: 65, minimum_stock: 125, stock_value: 26100, is_low_stock: false },
        { id: '2', shop_id: '', product_id: '2', current_stock: 8, stock_unit: 'kg', product_name: 'Sugar (Chakkera)', product_category: 'Sugar & Jaggery', purchase_price: 42, selling_price: 48, minimum_stock: 10, stock_value: 336, is_low_stock: true },
        { id: '3', shop_id: '', product_id: '3', current_stock: 22, stock_unit: 'litre', product_name: 'Sunflower Oil', product_category: 'Oils & Ghee', purchase_price: 150, selling_price: 165, minimum_stock: 5, stock_value: 3300, is_low_stock: false },
        { id: '4', shop_id: '', product_id: '4', current_stock: 3, stock_unit: 'kg', product_name: 'Toor Dal', product_category: 'Pulses & Dal', purchase_price: 110, selling_price: 125, minimum_stock: 5, stock_value: 330, is_low_stock: true },
        { id: '5', shop_id: '', product_id: '5', current_stock: 45, stock_unit: 'packet', product_name: 'Parle-G Biscuits', product_category: 'Snacks & Biscuits', purchase_price: 10, selling_price: 10, minimum_stock: 20, stock_value: 450, is_low_stock: false },
        { id: '6', shop_id: '', product_id: '6', current_stock: 28, stock_unit: 'packet', product_name: 'Red Label Tea', product_category: 'Beverages', purchase_price: 100, selling_price: 110, minimum_stock: 10, stock_value: 2800, is_low_stock: false },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
  };

  const filtered = items.filter(item => {
    const matchesSearch = !search || item.product_name.toLowerCase().includes(search.toLowerCase());
    const matchesLow = !showLowOnly || item.is_low_stock;
    return matchesSearch && matchesLow;
  });

  const totalValue = items.reduce((sum, i) => sum + (i.stock_value || 0), 0);
  const lowStockCount = items.filter(i => i.is_low_stock).length;

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-surface-900">Inventory</h2>
          <p className="text-sm text-surface-500">Total value: {formatCurrency(totalValue)}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate('/stock/in')} className="touch-btn bg-emerald-500 text-white px-3 text-sm gap-1">
            <PackagePlus className="w-4 h-4" /> In
          </button>
          <button onClick={() => navigate('/stock/out')} className="touch-btn bg-rose-500 text-white px-3 text-sm gap-1">
            <PackageMinus className="w-4 h-4" /> Out
          </button>
        </div>
      </div>

      {/* Search + Filter */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search inventory..." className="input-field pl-10" />
        </div>
        <button
          onClick={() => setShowLowOnly(!showLowOnly)}
          className={`touch-btn border px-3 gap-1 text-xs font-medium ${
            showLowOnly ? 'border-red-300 bg-red-50 text-red-700' : 'border-surface-200 text-surface-600'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          Low ({lowStockCount})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary-500" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 rounded-2xl bg-white border border-surface-100">
          <Package className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-surface-600 font-medium">No items found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((item) => (
            <div
              key={item.id}
              className={`flex items-center gap-3 p-4 rounded-2xl bg-white border transition-all ${
                item.is_low_stock ? 'border-red-200 bg-red-50/50' : 'border-surface-100'
              }`}
            >
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${
                item.is_low_stock ? 'bg-red-100' : 'bg-primary-50'
              }`}>
                {item.is_low_stock ? (
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                ) : (
                  <Package className="w-5 h-5 text-primary-600" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-surface-900 truncate">{item.product_name}</p>
                <p className="text-xs text-surface-500">{item.product_category}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className={`text-lg font-bold ${item.is_low_stock ? 'text-red-600' : 'text-surface-900'}`}>
                  {item.current_stock}
                </p>
                <p className="text-[10px] text-surface-400">{item.stock_unit}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
