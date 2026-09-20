import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, ArrowLeft, AlertTriangle, Sparkles, Check, 
  Package, Clock, Loader2, Calendar, ShoppingCart, 
  CheckCircle2, Flame, AlertCircle, RefreshCw
} from 'lucide-react';
import { notificationsService, festivalService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { getStorePersona } from '../../utils/storePersonalization';

interface NotificationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  data?: Record<string, any>;
}

interface FestivalRecommendation {
  item_name: string;
  product_id?: string;
  product_name?: string;
  current_stock: number;
  base_unit: string;
  multiplier: number;
  surge_target: number;
  deficit: number;
  reorder_needed: boolean;
  supplier_lead_time_days: number;
  is_lead_time_critical: boolean;
  unit_price: number;
  estimated_reorder_cost: number;
  supplier_id?: string;
}

interface SeasonalItem {
  item_name: string;
  category: string;
  multiplier: number;
  supplier_lead_time_days: number;
  note: string;
}

interface FestivalAnalysis {
  festival: {
    event: string;
    date: string;
    days_until: number;
    is_prior_window: boolean;
    description: string;
    telugu_name?: string;
    hindi_name?: string;
  } | null;
  recommendations: FestivalRecommendation[];
  deficit_items_count: number;
  seasonal_new_items: SeasonalItem[];
  total_estimated_reorder_cost: number;
}

export default function NotificationsPage() {
  const navigate = useNavigate();
  const { user, shop } = useAuth();
  const storePersona = getStorePersona(shop?.type || (user as any)?.shop_type || localStorage.getItem('dukaansetu_store_type'));
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [festivalData, setFestivalData] = useState<FestivalAnalysis | null>(null);
  const [selectedFestival, setSelectedFestival] = useState<string>('');
  const [availableFestivals, setAvailableFestivals] = useState<Array<{ event: string; days_until: number; is_prior_window: boolean }>>([]);
  const [creatingPo, setCreatingPo] = useState(false);
  const [poSuccessMessage, setPoSuccessMessage] = useState('');

  const loadData = async (festivalName?: string) => {
    setLoading(true);
    try {
      // 1. Fetch notifications
      const notifRes = await notificationsService.getAll();
      const nItems = (notifRes.data as any)?.items;
      if (notifRes.success && nItems) {
        setNotifications(nItems);
      }

      // 2. Fetch upcoming festival list for selector
      const upRes = await festivalService.getUpcoming();
      if (upRes.success && upRes.data) {
        const list = (upRes.data as any)?.items || [];
        setAvailableFestivals(list);
      }

      // 3. Fetch festival recommendations (active 15-day window or selected festival)
      const festRes = await festivalService.getRecommendations(festivalName ? { festival: festivalName } : undefined);
      if (festRes.success && festRes.data) {
        const fData = festRes.data as FestivalAnalysis;
        setFestivalData(fData);
        if (fData.festival && !selectedFestival) {
          setSelectedFestival(fData.festival.event);
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

  const handleFestivalChange = (event: string) => {
    setSelectedFestival(event);
    loadData(event);
  };

  const handleMarkRead = async (id: string) => {
    try {
      await notificationsService.markRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch {
      // Handled
    }
  };

  const handleCreateFestivalPO = async () => {
    if (!festivalData || !festivalData.festival) return;
    const deficitItems = festivalData.recommendations.filter(r => r.reorder_needed && r.product_id);
    if (deficitItems.length === 0) return;

    setCreatingPo(true);
    setPoSuccessMessage('');

    try {
      const itemsPayload = deficitItems.map(d => ({
        product_id: d.product_id!,
        quantity: d.deficit,
        unit_price: d.unit_price
      }));

      const res = await festivalService.createFestivalPo({
        festival_name: festivalData.festival.event,
        items: itemsPayload,
        supplier_id: deficitItems[0]?.supplier_id
      });

      if (res.success && res.data) {
        const msg = (res.data as any).message || 'Purchase order created successfully!';
        setPoSuccessMessage(msg);
        // Refresh notifications
        const updatedNotifs = await notificationsService.getAll();
        if (updatedNotifs.success && (updatedNotifs.data as any)?.items) {
          setNotifications((updatedNotifs.data as any).items);
        }
      }
    } catch (err: any) {
      alert(err?.message || 'Failed to create purchase order');
    } finally {
      setCreatingPo(false);
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const currentFest = festivalData?.festival;
  const deficitRecs = festivalData?.recommendations.filter(r => r.reorder_needed) || [];

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
              <Bell className="w-6 h-6 text-primary-600" />
              Notifications & Smart Alerts
              {unreadCount > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-red-500 text-white font-bold">
                  {unreadCount} new
                </span>
              )}
            </h2>
            <p className="text-sm text-surface-500">15-day festival demand alerts, low stock warnings & procurement</p>
          </div>
        </div>

        <button 
          onClick={() => loadData(selectedFestival)} 
          disabled={loading}
          className="px-3 py-1.5 rounded-xl border border-surface-200 bg-white text-xs font-semibold text-surface-700 hover:bg-surface-50 flex items-center gap-1.5 shadow-2xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* SUCCESS BANNER FOR FESTIVAL PO */}
      {poSuccessMessage && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center justify-between gap-3 animate-fade-in shadow-xs">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="text-sm font-bold">{poSuccessMessage}</span>
          </div>
          <button
            onClick={() => navigate('/orders')}
            className="text-xs font-bold text-emerald-700 underline hover:text-emerald-900"
          >
            View in Orders →
          </button>
        </div>
      )}

      {/* PROACTIVE 15-DAY PRIOR FESTIVAL DEMAND CARD */}
      {currentFest && (
        <div className={`rounded-2xl border-2 p-5 space-y-4 shadow-sm transition-all ${
          currentFest.is_prior_window
            ? 'bg-gradient-to-br from-amber-50 via-orange-50/40 to-red-50/30 border-amber-300'
            : 'bg-white border-surface-200'
        }`}>
          {/* Card Top Banner */}
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="p-2 rounded-xl bg-amber-500 text-white shadow-xs">
                  <Flame className="w-5 h-5 animate-pulse" />
                </span>
                <h3 className="text-lg font-black text-surface-900 tracking-tight">
                  {currentFest.event} {currentFest.telugu_name ? `(${currentFest.telugu_name})` : ''}
                </h3>
                {currentFest.is_prior_window ? (
                  <span className="px-2.5 py-0.5 rounded-full bg-red-500 text-white text-xs font-bold flex items-center gap-1 animate-pulse shadow-xs">
                    <Clock className="w-3.5 h-3.5" />
                    <span>In {currentFest.days_until} Days • 15-Day Prior Alert Active</span>
                  </span>
                ) : (
                  <span className="px-2.5 py-0.5 rounded-full bg-surface-100 text-surface-700 text-xs font-semibold">
                    In {currentFest.days_until} Days
                  </span>
                )}
              </div>
              <p className="text-xs text-surface-600 max-w-2xl leading-relaxed">
                {currentFest.description} (Analyzed from {storePersona.name} Seasonal Demand Dataset).
              </p>
            </div>

            {/* Festival Selector Dropdown */}
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-surface-500 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-primary-600" />
                <span>Festival:</span>
              </label>
              <select
                value={selectedFestival}
                onChange={(e) => handleFestivalChange(e.target.value)}
                className="px-2.5 py-1.5 rounded-xl border border-surface-300 text-xs font-semibold bg-white text-surface-800 shadow-2xs focus:ring-2 focus:ring-primary-400 outline-none"
              >
                {availableFestivals.map((f, idx) => (
                  <option key={idx} value={f.event}>
                    {f.event} ({f.days_until}d {f.is_prior_window ? '★ 15-Day Alert' : ''})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Demand Surge Summary & Action Header */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1 text-xs">
            <div className="p-3 rounded-xl bg-white/90 border border-amber-200/80 shadow-2xs">
              <span className="text-[10px] text-surface-500 font-bold uppercase">Anticipated Surge</span>
              <p className="text-base font-black text-amber-700 mt-0.5">1.3x – 2.0x Multiplier</p>
              <p className="text-[11px] text-surface-500">Based on regional holiday demand</p>
            </div>

            <div className="p-3 rounded-xl bg-white/90 border border-amber-200/80 shadow-2xs">
              <span className="text-[10px] text-surface-500 font-bold uppercase">Stock Deficits Detected</span>
              <p className="text-base font-black text-red-600 mt-0.5">
                {deficitRecs.length} item{deficitRecs.length === 1 ? '' : 's'} short
              </p>
              <p className="text-[11px] text-surface-500">
                Est. Reorder: ₹{festivalData?.total_estimated_reorder_cost?.toLocaleString() || 0}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-white/90 border border-amber-200/80 shadow-2xs">
              <span className="text-[10px] text-surface-500 font-bold uppercase">Supplier Lead Time Notice</span>
              <p className="text-base font-black text-surface-900 mt-0.5">7 – 14 Days Lead</p>
              <p className="text-[11px] text-amber-700 font-semibold">
                {currentFest.days_until <= 14 ? '⚠️ Order now before delivery cut-off' : 'Planning in advance'}
              </p>
            </div>
          </div>

          {/* Deficit Items Table / List */}
          {deficitRecs.length > 0 ? (
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-surface-700 flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                  Recommended Reorder Quantities (Shop Inventory vs Festival Surge):
                </span>
                <span className="text-[11px] font-semibold text-surface-500">
                  Target = Base Demand × Multiplier
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-amber-200 bg-white shadow-2xs">
                <table className="w-full text-left text-xs">
                  <thead className="bg-amber-50/80 text-amber-900 font-bold border-b border-amber-200">
                    <tr>
                      <th className="py-2.5 px-3">Item / Product</th>
                      <th className="py-2.5 px-3">Current Stock</th>
                      <th className="py-2.5 px-3">Festival Target</th>
                      <th className="py-2.5 px-3">Deficit (To Order)</th>
                      <th className="py-2.5 px-3">Lead Time</th>
                      <th className="py-2.5 px-3 text-right">Est. Cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-100">
                    {deficitRecs.map((r, i) => (
                      <tr key={i} className="hover:bg-amber-50/30">
                        <td className="py-2 px-3 font-bold text-surface-900">
                          {r.product_name || r.item_name}
                        </td>
                        <td className="py-2 px-3 text-surface-600 font-medium">
                          {r.current_stock} {r.base_unit}
                        </td>
                        <td className="py-2 px-3 text-surface-900 font-bold">
                          {r.surge_target} {r.base_unit} <span className="text-[10px] text-amber-600 font-normal">({r.multiplier}x)</span>
                        </td>
                        <td className="py-2 px-3">
                          <span className="font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded-md border border-red-200">
                            +{r.deficit} {r.base_unit}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-surface-600">
                          {r.supplier_lead_time_days} days
                          {r.is_lead_time_critical && (
                            <span className="ml-1 text-[10px] text-red-600 font-bold">URGENT</span>
                          )}
                        </td>
                        <td className="py-2 px-3 text-right font-bold text-surface-900">
                          ₹{r.estimated_reorder_cost?.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 1-Click Purchase Order Button */}
              <div className="pt-2 flex justify-end gap-2">
                <button
                  onClick={handleCreateFestivalPO}
                  disabled={creatingPo}
                  className="px-4 py-2.5 rounded-xl gradient-primary text-white text-xs font-bold shadow-md flex items-center gap-2 hover:opacity-95 disabled:opacity-50 active:scale-95 transition-all"
                >
                  {creatingPo ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <ShoppingCart className="w-4 h-4" />
                      <span>⚡ Auto-Generate Festival Purchase Order (₹{festivalData?.total_estimated_reorder_cost?.toLocaleString()})</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 font-medium">
              <Check className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>Current inventory for core {storePersona.name} items meets or exceeds {currentFest.event} surge targets!</span>
            </div>
          )}

          {/* Seasonal Items Not Yet Stocked */}
          {festivalData?.seasonal_new_items && festivalData.seasonal_new_items.length > 0 && (
            <div className="pt-2 space-y-1.5 border-t border-amber-200/60">
              <p className="text-[11px] font-bold uppercase tracking-wider text-surface-500 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-primary-600" />
                High-Demand Seasonal Items to Consider Stocking:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {festivalData.seasonal_new_items.slice(0, 8).map((s, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-white border border-surface-200 text-xs font-semibold text-surface-700 flex items-center gap-1 shadow-2xs"
                  >
                    <span>{s.item_name}</span>
                    <span className="text-[10px] text-amber-700 font-bold">({s.multiplier}x)</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ALL NOTIFICATIONS LIST */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-surface-700 uppercase tracking-wider flex items-center gap-2">
          <span>General Activity & Alert History</span>
          <span className="text-xs font-semibold text-surface-400">({notifications.length})</span>
        </h3>

        {loading ? (
          <div className="card py-16 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
            <p className="text-sm text-surface-500 font-medium">Checking live notifications & festival sync...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="card py-12 text-center space-y-2">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-3">
              <Check className="w-6 h-6" />
            </div>
            <p className="text-base font-bold text-surface-900">All Clear!</p>
            <p className="text-sm text-surface-500">No active stock alerts or pending notifications right now.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((item) => (
              <div
                key={item.id}
                className={`card p-4 transition-all flex items-start gap-4 ${
                  !item.is_read ? 'border-primary-300 bg-primary-50/20 shadow-sm' : 'border-surface-100 opacity-80'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  item.type === 'FESTIVAL_DEMAND' || item.type === 'FESTIVAL_SPIKE' ? 'bg-amber-100 text-amber-700' :
                  item.type === 'FAST_MOVING' ? 'bg-orange-100 text-orange-700' :
                  item.type === 'LOW_STOCK' || item.type === 'STOCK_WARNING' ? 'bg-red-100 text-red-600' :
                  item.type === 'ORDER_CREATED' ? 'bg-emerald-100 text-emerald-600' :
                  item.type === 'SMART_REORDER' ? 'bg-purple-100 text-purple-600' :
                  'bg-blue-100 text-blue-600'
                }`}>
                  {item.type === 'FESTIVAL_DEMAND' || item.type === 'FESTIVAL_SPIKE' ? <Flame className="w-5 h-5 text-amber-600" /> :
                   item.type === 'FAST_MOVING' ? <Flame className="w-5 h-5 text-orange-600" /> :
                   item.type === 'LOW_STOCK' || item.type === 'STOCK_WARNING' ? <AlertTriangle className="w-5 h-5" /> :
                   item.type === 'ORDER_CREATED' ? <ShoppingCart className="w-5 h-5" /> :
                   item.type === 'SMART_REORDER' ? <Sparkles className="w-5 h-5" /> :
                   <Package className="w-5 h-5" />}
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-bold text-sm text-surface-900">{item.title}</h4>
                    <span className="text-xs text-surface-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-xs text-surface-600 leading-relaxed whitespace-pre-line">{item.message}</p>

                  <div className="flex items-center gap-3 pt-2">
                    {(item.type === 'LOW_STOCK' || item.type === 'FAST_MOVING' || item.type === 'STOCK_WARNING') && (
                      <button
                        onClick={() => navigate('/stock/in')}
                        className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1"
                      >
                        Reorder / Stock In →
                      </button>
                    )}
                    {item.type === 'ORDER_CREATED' && (
                      <button
                        onClick={() => navigate('/orders')}
                        className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
                      >
                        View Purchase Orders →
                      </button>
                    )}
                    {!item.is_read && (
                      <button
                        onClick={() => handleMarkRead(item.id)}
                        className="text-xs font-medium text-surface-400 hover:text-surface-600"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
