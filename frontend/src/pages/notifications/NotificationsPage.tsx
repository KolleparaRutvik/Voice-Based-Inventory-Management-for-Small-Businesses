import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, ArrowLeft, AlertTriangle, Sparkles, Check, 
  Package, Clock, Loader2 
} from 'lucide-react';
import { notificationsService } from '../../services/api';

interface NotificationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  data?: Record<string, any>;
}

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const res = await notificationsService.getAll();
      const nItems = (res.data as any)?.items;
      if (res.success && nItems) {
        setNotifications(nItems);
      }
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await notificationsService.markRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch {
      // Handled
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
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
            <p className="text-sm text-surface-500">Low stock warnings, reorder suggestions & reminders</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Checking alerts...</p>
        </div>
      ) : notifications.length === 0 ? (
        <div className="card py-16 text-center space-y-2">
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
                item.type === 'LOW_STOCK' ? 'bg-amber-100 text-amber-600' :
                item.type === 'SMART_REORDER' ? 'bg-purple-100 text-purple-600' :
                'bg-blue-100 text-blue-600'
              }`}>
                {item.type === 'LOW_STOCK' ? <AlertTriangle className="w-5 h-5" /> :
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
                <p className="text-xs text-surface-600 leading-relaxed">{item.message}</p>

                <div className="flex items-center gap-3 pt-2">
                  {item.type === 'LOW_STOCK' && (
                    <button
                      onClick={() => navigate('/stock/in')}
                      className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1"
                    >
                      Reorder Now →
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
  );
}
