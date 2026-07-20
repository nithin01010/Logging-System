"use client";

import { useEffect, useState } from "react";
import { Key, Plus, Trash2, Copy, Check, ShieldCheck, AlertOctagon } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [formLoading, setFormLoading] = useState(false);

  // Modal / Display generated raw key
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadKeys = async () => {
    setLoading(true);
    try {
      const data = await fetchApi<any[]>("/keys/");
      setKeys(data);
    } catch (err) {
      console.error("Failed to load API keys:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const handleGenerateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setFormLoading(true);

    try {
      const data = await fetchApi<any>("/keys/", {
        method: "POST",
        body: JSON.stringify({ name: name.trim() }),
      });

      setGeneratedKey(data.raw_key);
      setName("");
      await loadKeys();
    } catch (err) {
      console.error("Failed to generate key:", err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    try {
      await fetchApi(`/keys/${keyId}`, { method: "DELETE" });
      await loadKeys();
    } catch (err) {
      console.error("Failed to revoke key:", err);
    }
  };

  const copyToClipboard = () => {
    if (generatedKey) {
      navigator.clipboard.writeText(generatedKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <h1 className="text-2xl font-bold text-white">API Keys Management</h1>
          <p className="text-slate-400 text-sm mt-1">Generate machine API keys for Log Shipper & OpenTelemetry Collector</p>
        </div>
      </div>

      {/* Generated Key Modal / Callout */}
      {generatedKey && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 p-6 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
            <ShieldCheck className="h-5 w-5" /> API Key Generated Successfully!
          </div>
          <p className="text-xs text-slate-300">
            Copy this key now. For security reasons, it will <strong>never be shown again</strong>.
          </p>

          <div className="flex items-center gap-2 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-sm text-emerald-300">
            <span className="flex-1 select-all break-all">{generatedKey}</span>
            <button
              type="button"
              onClick={copyToClipboard}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-sans font-medium transition-colors shrink-0"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>

          <button
            type="button"
            onClick={() => setGeneratedKey(null)}
            className="text-xs text-slate-400 hover:text-slate-200 underline pt-1"
          >
            I have saved this key
          </button>
        </div>
      )}

      {/* Generate Key Form */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Plus className="h-5 w-5 text-indigo-400" /> Generate New API Key
        </h2>

        <form onSubmit={handleGenerateKey} className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Key Description (e.g. Production Log Shipper)"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />

          <button
            type="submit"
            disabled={formLoading || !name.trim()}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg text-sm transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {formLoading ? "Generating..." : "Generate Key"}
          </button>
        </form>
      </div>

      {/* Active API Keys Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 font-semibold text-white text-sm flex items-center gap-2">
          <Key className="h-4 w-4 text-indigo-400" /> Active API Keys ({keys.length})
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Key Hash (SHA-256)</th>
                <th className="py-3 px-4">Created At</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {keys.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 font-sans">
                    No active API keys found.
                  </td>
                </tr>
              ) : (
                keys.map((k) => (
                  <tr key={k._id || k.id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-medium text-white font-sans">{k.name}</td>
                    <td className="py-3 px-4 text-slate-400">{k.key_hash ? k.key_hash.slice(0, 16) + "..." : "-"}</td>
                    <td className="py-3 px-4 text-slate-400 font-sans">
                      {k.created_at ? new Date(k.created_at).toLocaleString() : "N/A"}
                    </td>
                    <td className="py-3 px-4 font-sans">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                        ACTIVE
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => handleRevokeKey(k._id || k.id)}
                        className="text-rose-400 hover:text-rose-300 transition-colors p-1"
                        title="Revoke Key"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
