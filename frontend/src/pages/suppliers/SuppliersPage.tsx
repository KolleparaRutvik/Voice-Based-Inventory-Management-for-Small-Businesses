import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building2, Plus, ArrowLeft, Search, Phone, Mail, 
  MapPin, MessageSquare, Loader2 
} from 'lucide-react';
import { suppliersService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { getStorePersona } from '../../utils/storePersonalization';
import type { Supplier } from '../../types';

export default function SuppliersPage() {
  const navigate = useNavigate();
  const { user, shop } = useAuth();
  const storePersona = getStorePersona(shop?.type || (user as any)?.shop_type || localStorage.getItem('dukaansetu_store_type'));
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [address, setAddress] = useState('');
  const [gst, setGst] = useState('');

  const loadSuppliers = async () => {
    setLoading(true);
    try {
      const res = await suppliersService.getAll();
      const sItems = (res.data as any)?.items;
      if (res.success && sItems) {
        setSuppliers(sItems);
      }
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSuppliers();
  }, []);

  const handleCreateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await suppliersService.create({
        name,
        phone,
        email,
        address,
        gst_number: gst,
      });
      setShowAddModal(false);
      setName('');
      setPhone('');
      setEmail('');
      setAddress('');
      setGst('');
      await loadSuppliers();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add supplier');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredSuppliers = suppliers.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    (s.phone && s.phone.includes(search)) ||
    (s.city && s.city.toLowerCase().includes(search.toLowerCase()))
  );

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
              <Building2 className="w-6 h-6 text-primary-600" />
              Supplier Directory
            </h2>
            <p className="text-sm text-surface-500">Manage distributors, wholesalers & reorder contacts</p>
          </div>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="touch-btn gradient-primary text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow-sm gap-2"
        >
          <Plus className="w-4 h-4" /> Add Supplier
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="w-4 h-4 text-surface-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search suppliers by name, phone or city..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
        />
      </div>

      {/* Suppliers Grid */}
      {loading ? (
        <div className="card py-16 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm text-surface-500 font-medium">Loading suppliers...</p>
        </div>
      ) : filteredSuppliers.length === 0 ? (
        <div className="card py-12 text-center">
          <Building2 className="w-12 h-12 text-surface-300 mx-auto mb-3" />
          <p className="text-base font-semibold text-surface-700">No suppliers found</p>
          <p className="text-sm text-surface-400 mt-1">Tap "Add Supplier" to register a wholesaler.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSuppliers.map((supplier) => (
            <div key={supplier.id} className="card p-5 space-y-4 hover:border-primary-300 transition-all flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-base text-surface-900">{supplier.name}</h3>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                    Active
                  </span>
                </div>

                {supplier.address && (
                  <p className="text-xs text-surface-500 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-surface-400 flex-shrink-0" />
                    <span>{supplier.address}</span>
                  </p>
                )}

                {supplier.phone && (
                  <p className="text-xs text-surface-600 flex items-center gap-1.5 font-medium">
                    <Phone className="w-3.5 h-3.5 text-surface-400 flex-shrink-0" />
                    <span>{supplier.phone}</span>
                  </p>
                )}

                {supplier.email && (
                  <p className="text-xs text-surface-500 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-surface-400 flex-shrink-0" />
                    <span className="truncate">{supplier.email}</span>
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-3 border-t border-surface-100">
                {supplier.phone && (
                  <>
                    <a
                      href={`tel:${supplier.phone}`}
                      className="flex-1 touch-btn bg-surface-100 hover:bg-surface-200 text-surface-700 text-xs font-semibold py-2 rounded-xl gap-1.5"
                    >
                      <Phone className="w-3.5 h-3.5" /> Call
                    </a>
                    <a
                      href={`https://wa.me/${supplier.phone.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(
                        `Namaste ${supplier.name}, sending order enquiry from ${shop?.name || storePersona.defaultShopName}.`
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 touch-btn bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold py-2 rounded-xl gap-1.5 shadow-sm shadow-emerald-600/20"
                    >
                      <MessageSquare className="w-3.5 h-3.5" /> WhatsApp
                    </a>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Supplier Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-scale-up">
            <h3 className="text-lg font-bold text-surface-900">Add New Supplier / Distributor</h3>
            <form onSubmit={handleCreateSupplier} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Company / Supplier Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Balaji Trading Co."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Phone Number</label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 00000"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Email (Optional)</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="orders@balaji.com"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">Address / Market Location</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Shop #12, Grain Market, Warangal"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-surface-600 mb-1">GST Number (Optional)</label>
                <input
                  type="text"
                  value={gst}
                  onChange={(e) => setGst(e.target.value)}
                  placeholder="36AAAAA0000A1Z5"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-surface-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="flex gap-2 pt-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl gradient-primary text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Supplier'}
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
    </div>
  );
}
