"use client";

import { useEffect, useState } from "react";
import { API_ENDPOINTS } from "@/lib/constants";

export default function PropertiesManager() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<any>({ name: "", city: "", price: 0, description: "", images: "", slots: 50, status: "draft", publish: false });
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : undefined;

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_ENDPOINTS.ADMIN}/properties`, { headers: { Authorization: `Bearer ${token}` } });
      const j = await res.json();
      if (j.success) setItems(j.properties || []);
    } catch (e) {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const upsert = async () => {
    setSaving(true);
    try {
      const method = form.id ? 'PUT' : 'POST';
      const url = form.id ? `${API_ENDPOINTS.ADMIN}/properties/${form.id}` : `${API_ENDPOINTS.ADMIN}/properties`;
      const payload = {
        ...form,
        images: typeof form.images === 'string' ? form.images.split(',').map((s: string) => s.trim()).filter(Boolean) : Array.isArray(form.images) ? form.images : [],
        slots: Number(form.slots) || 50,
        price: Number(form.price) || 0,
        publish: !!form.publish,
      };
      const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify({ data: payload }) });
      const j = await res.json();
      if (j.success) {
        setForm({ name: "", city: "", price: 0, description: "", images: "", slots: 50, status: "draft", publish: false });
        await load();
      }
    } catch (e) {}
    setSaving(false);
  };

  const remove = async (id: string) => {
    if (!confirm('Delete property?')) return;
    try {
      await fetch(`${API_ENDPOINTS.ADMIN}/properties/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
      await load();
    } catch (e) {}
  };

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Properties</h3>
      <div className="grid gap-3 sm:grid-cols-3">
        <label className="flex flex-col text-sm text-gray-300">
          <span className="mb-1">Name</span>
          <input value={form.name || ""} onChange={(e) => setForm({ ...form, name: e.target.value })} className="bg-gray-800 border border-gray-700 rounded px-3 py-2" />
        </label>
        <label className="flex flex-col text-sm text-gray-300">
          <span className="mb-1">City</span>
          <input value={form.city || ""} onChange={(e) => setForm({ ...form, city: e.target.value })} className="bg-gray-800 border border-gray-700 rounded px-3 py-2" />
        </label>
        <label className="flex flex-col text-sm text-gray-300">
          <span className="mb-1">Price (USD)</span>
          <input value={form.price ?? 0} onChange={(e) => setForm({ ...form, price: Number(e.target.value) || 0 })} inputMode="decimal" className="bg-gray-800 border border-gray-700 rounded px-3 py-2" />
        </label>
        <label className="flex flex-col text-sm text-gray-300 sm:col-span-3">
          <span className="mb-1">Description</span>
          <textarea value={form.description || ""} onChange={(e) => setForm({ ...form, description: e.target.value })} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 min-h-[80px]" />
        </label>
        <label className="flex flex-col text-sm text-gray-300 sm:col-span-2">
          <span className="mb-1">Images (comma-separated URLs)</span>
          <input value={typeof form.images === 'string' ? form.images : (Array.isArray(form.images) ? form.images.join(', ') : '')} onChange={(e) => setForm({ ...form, images: e.target.value })} className="bg-gray-800 border border-gray-700 rounded px-3 py-2" />
        </label>
        <label className="flex flex-col text-sm text-gray-300">
          <span className="mb-1">Slots</span>
          <input value={form.slots ?? 50} onChange={(e) => setForm({ ...form, slots: Number(e.target.value) || 50 })} inputMode="numeric" className="bg-gray-800 border border-gray-700 rounded px-3 py-2" />
        </label>
        <label className="flex flex-col text-sm text-gray-300">
          <span className="mb-1">Status</span>
          <select value={form.status || 'draft'} onChange={(e) => setForm({ ...form, status: e.target.value })} className="bg-gray-800 border border-gray-700 rounded px-3 py-2">
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-300">
          <input type="checkbox" checked={!!form.publish} onChange={(e) => setForm({ ...form, publish: e.target.checked })} className="h-4 w-4" />
          <span>Publish</span>
        </label>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={upsert} disabled={saving} className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-black font-semibold rounded-lg">{saving ? 'Saving...' : (form.id ? 'Update' : 'Create')}</button>
        {form.id && <button onClick={() => setForm({ name: "", city: "", price: 0 })} className="px-4 py-2 bg-gray-800 text-gray-200 rounded-lg">Reset</button>}
      </div>

      <div className="mt-6">
        {loading ? (
          <div className="text-gray-400">Loading...</div>
        ) : items.length === 0 ? (
          <div className="text-gray-400 text-sm">No properties yet.</div>
        ) : (
          <div className="grid gap-2">
            {items.map((p) => (
              <div key={p.id} className="flex items-center justify-between bg-gray-800/50 border border-gray-700 rounded-lg p-3">
                <div>
                  <div className="text-white font-medium">{p.name}</div>
                  <div className="text-xs text-gray-400">{p.city || '—'} • ${Number(p.price || 0).toLocaleString()}</div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => setForm(p)} className="px-3 py-1 text-xs bg-blue-600/20 border border-blue-500/30 rounded text-blue-300">Edit</button>
                  <button onClick={() => remove(p.id)} className="px-3 py-1 text-xs bg-red-600/20 border border-red-500/30 rounded text-red-300">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
