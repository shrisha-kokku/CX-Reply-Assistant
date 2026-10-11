import { useEffect, useState } from "react";
import { api } from "../api";

const CATEGORIES = ["return", "refund", "shipping", "cancellation", "other"];
const EMPTY = { category: "return", title: "", content: "" };

export default function KBManager() {
  const [brands, setBrands] = useState([]);
  const [brandId, setBrandId] = useState(null);
  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listBrands().then((list) => {
      setBrands(list);
      if (list.length) setBrandId(list[0].id);
    }).catch((e) => setError(e.message));
  }, []);

  function loadEntries() {
    if (brandId) api.listKB(brandId).then(setEntries).catch((e) => setError(e.message));
  }

  useEffect(loadEntries, [brandId]);

  async function save() {
    setError("");
    try {
      if (editingId) await api.updateKB(brandId, editingId, form);
      else await api.createKB(brandId, form);
      cancel();
      loadEntries();
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(id) {
    if (!window.confirm("Delete this entry?")) return;
    try {
      await api.deleteKB(brandId, id);
      loadEntries();
    } catch (e) {
      setError(e.message);
    }
  }

  function edit(entry) {
    setEditingId(entry.id);
    setForm({ category: entry.category, title: entry.title, content: entry.content });
  }

  function cancel() {
    setEditingId(null);
    setForm(EMPTY);
  }

  return (
    <div className="page">
      <h2>Knowledge base</h2>
      <label>
        Brand{" "}
        <select value={brandId || ""} onChange={(e) => { setBrandId(Number(e.target.value)); cancel(); }}>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>
      </label>

      {error && <p className="error">{error}</p>}

      {entries.map((e) => (
        <div key={e.id} className="kb-card">
          <strong>{e.title}</strong> <span className="badge">{e.category}</span>
          <p>{e.content}</p>
          <button onClick={() => edit(e)}>Edit</button> <button onClick={() => remove(e.id)}>Delete</button>
        </div>
      ))}

      <div className="kb-form">
        <h3>{editingId ? "Edit entry" : "Add entry"}</h3>
        <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
          {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
        </select>
        <input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <textarea placeholder="Content" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
        <div className="row">
          <button className="primary" onClick={save}>{editingId ? "Save changes" : "Add entry"}</button>
          {editingId && <button onClick={cancel}>Cancel</button>}
        </div>
      </div>
    </div>
  );
}
