import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart3, ArrowLeft, TrendingUp, TrendingDown, 
  IndianRupee, Package, AlertTriangle, Sparkles, Loader2 
} from 'lucide-react';
import { analyticsService, productsService } from '../../services/api';
import type { DashboardData, Product } from '../../types';

export default function AnalyticsPage() {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<DashboardData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsService.getDashboard(),
      productsService.getAll(),
    ]).then(([aRes, pRes]) => {
      if (aRes.success && aRes.data) setAnalytics(aRes.data as any);
      if (pRes.success && (pRes.data as any)?.items) setProducts((pRes.data as any).items);
    }).finally(() => setLoading(false));
  }, []);

  const totalCatalogValue = products.reduce((sum, p) => sum + (p.stock_value || 0), 0);

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
          <ArrowLeft className="w-5 h-5 text-surface-600" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-primary-600" />
            Business Intelligence & Analytics
          </h2>
          <p className="text-sm text-surface-500">Sales velocity, stock health, and profit margins</p>
        </div>
      </div>

      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Computing analytics...</p>
        </div>
      ) : (
        <>
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
            <div className="card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-surface-400">Total Stock Value</span>
                <Package className="w-4 h-4 text-primary-500" />
              </div>
              <p className="text-2xl font-black text-surface-900">
                ₹{(analytics?.inventory_value || totalCatalogValue).toLocaleString('en-IN')}
              </p>
              <p className="text-xs text-emerald-600 font-medium flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> Across {products.length} products
              </p>
            </div>

            <div className="card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-surface-400">Estimated Margin</span>
                <IndianRupee className="w-4 h-4 text-emerald-500" />
              </div>
              <p className="text-2xl font-black text-emerald-600">
                ₹{(analytics?.estimated_margin || 0).toLocaleString('en-IN')}
              </p>
              <p className="text-xs text-surface-500">Sell value − purchase cost of inventory</p>
            </div>

            <div className="card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-surface-400">Low Stock Risk</span>
                <AlertTriangle className="w-4 h-4 text-amber-500" />
              </div>
              <p className="text-2xl font-black text-amber-600">
                {analytics?.low_stock_count || 0} Item{(analytics?.low_stock_count || 0) !== 1 ? 's' : ''}
              </p>
              <p className="text-xs text-amber-700">Needs immediate reorder</p>
            </div>

            <div className="card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-surface-400">Customer Udhar</span>
                <TrendingDown className="w-4 h-4 text-blue-500" />
              </div>
              <p className="text-2xl font-black text-surface-900">
                ₹{(analytics?.borrowed_value || 0).toLocaleString('en-IN')}
              </p>
              <p className="text-xs text-surface-500">{analytics?.active_borrowings || 0} pending credit</p>
            </div>
          </div>

          {/* Product Stock Breakdown */}
          <div className="card p-5 space-y-4">
            <h3 className="text-base font-bold text-surface-900 flex items-center justify-between">
              <span>Catalog Stock Breakdown & Margins</span>
              <span className="text-xs font-normal text-surface-500">Sorted by stock quantity</span>
            </h3>

            <div className="space-y-3">
              {products.map((prod) => {
                const margin = prod.selling_price > 0 && prod.purchase_price > 0
                  ? ((prod.selling_price - (prod.purchase_price / (prod.conversion_factor || 1))) / prod.selling_price * 100).toFixed(1)
                  : '0';

                return (
                  <div key={prod.id} className="space-y-1.5 border-b border-surface-100 pb-3 last:border-0 last:pb-0">
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="font-bold text-surface-900">{prod.name}</span>
                        <span className="text-xs text-surface-400 ml-2">({prod.category})</span>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-surface-900">{prod.current_stock || 0} {prod.base_unit}</span>
                        <span className="text-xs text-emerald-600 font-semibold ml-2">+{margin}% margin</span>
                      </div>
                    </div>

                    {/* Visual Progress Bar */}
                    <div className="w-full bg-surface-100 rounded-full h-2 overflow-hidden">
                      <div 
                        className={`h-2 rounded-full ${
                          (prod.current_stock || 0) <= (prod.minimum_stock || 10) 
                            ? 'bg-amber-500' 
                            : 'bg-primary-600'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(8, ((prod.current_stock || 0) / (prod.recommended_stock || 200)) * 100))}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Reorder Insights */}
          <div className="card p-5 bg-gradient-to-r from-purple-500/10 via-purple-500/5 to-transparent border-l-4 border-l-purple-500 space-y-3">
            <div className="flex items-center gap-2 text-purple-900">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-sm">Vyapari Voice Smart Reorder Suggestions</h3>
            </div>
            <div className="space-y-2 text-xs text-purple-950">
              {(analytics?.low_stock_products || []).length > 0 ? (
                (analytics?.low_stock_products || []).slice(0, 3).map((item: any, idx: number) => (
                  <p key={idx}>• <strong>{item.product_name}</strong> is at {item.current_stock} {item.stock_unit} (minimum: {item.minimum_stock} {item.stock_unit}). Consider ordering more soon.</p>
                ))
              ) : (
                <p>All products are above minimum stock levels. No urgent reorders needed.</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
