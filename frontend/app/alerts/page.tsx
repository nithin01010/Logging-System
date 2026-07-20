"use client";

import { useEffect, useState } from "react";
import { Bell, Plus, Trash2, ShieldAlert, CheckCircle2, AlertTriangle } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function AlertsPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [triggers, setTriggers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Form state
  const [name, setName] = useState("");
  const [service, setService] = useState("checkoutservice");
  const [metric, setMetric] = useState("error_rate");
  const [threshold, setThreshold] = useState("5.0");
  const [windowMinutes, setWindowMinutes] = useState("5");
  const [formLoading, setFormLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rulesData, triggersData] = await Promise.all([
        fetchApi<any[]>("/alerts/rules").catch(() => []),
        fetchApi<any[]>("/alerts/triggers").catch(() => []),
      ]);
      setRules(rulesData);
      setTriggers(triggersData);
    } catch (err) {
      console.error("Failed to load alerts data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setFormLoading(true);

    try {
      await fetchApi("/alerts/rules", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          service,
          metric,
          threshold: parseFloat(threshold),
          window_minutes: parseInt(windowMinutes, 10),
          is_active: true,
        }),
      });

      setName("");
      setThreshold("5.0");
      setWindowMinutes("5");
      await loadData();
    } catch (err) {
      console.error("Failed to create rule:", err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await fetchApi(`/alerts/rules/${ruleId}`, { method: "DELETE" });
      await loadData();
    } catch (err) {
      console.error("Failed to delete rule:", err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <h1 className="text-2xl font-bold text-white">Alerts Manager</h1>
          <p className="text-slate-400 text-sm mt-1">Configure threshold rules and view incident history</p>
        </div>
      </div>

      {/* Create Rule Form Card */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Plus className="h-5 w-5 text-indigo-400" /> Create New Alert Rule
        </h2>

        <form onSubmit={handleCreateRule} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Rule Name (e.g. High Error Rate)"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />

          <select
            value={service}
            onChange={(e) => setService(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          >
            <option value="checkoutservice">checkoutservice</option>
            <option value="paymentservice">paymentservice</option>
            <option value="frontend">frontend</option>
            <option value="emailservice">emailservice</option>
            <option value="shippingservice">shippingservice</option>
            <option value="cartservice">cartservice</option>
            <option value="productcatalogservice">productcatalogservice</option>
          </select>

          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          >
            <option value="error_rate">error_rate (%)</option>
            <option value="latency">latency (ms)</option>
          </select>

          <input
            type="number"
            step="0.1"
            required
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            placeholder="Threshold (e.g. 5.0)"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />

          <input
            type="number"
            required
            value={windowMinutes}
            onChange={(e) => setWindowMinutes(e.target.value)}
            placeholder="Window (minutes)"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />

          <button
            type="submit"
            disabled={formLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {formLoading ? "Saving..." : "Save Rule"}
          </button>
        </form>
      </div>

      {/* Rules Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 font-semibold text-white text-sm">
          Active Alert Rules ({rules.length})
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="py-3 px-4">Name</th>
                <th className="py-3 px-4">Service</th>
                <th className="py-3 px-4">Metric</th>
                <th className="py-3 px-4">Threshold</th>
                <th className="py-3 px-4">Window</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {rules.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-sans">
                    No active rules found.
                  </td>
                </tr>
              ) : (
                rules.map((r) => (
                  <tr key={r._id || r.id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-medium text-white font-sans">{r.name}</td>
                    <td className="py-3 px-4 text-indigo-300 font-sans">{r.service}</td>
                    <td className="py-3 px-4 text-slate-300">{r.metric}</td>
                    <td className="py-3 px-4 text-slate-300">
                      {r.threshold} {r.metric === "error_rate" ? "%" : "ms"}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-sans">{r.window_minutes} mins</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => handleDeleteRule(r._id || r.id)}
                        className="text-rose-400 hover:text-rose-300 transition-colors p-1"
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

      {/* Triggers Incident History Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 font-semibold text-white text-sm flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-rose-400" /> Recent Incident Triggers ({triggers.length})
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase">
              <tr>
                <th className="py-3 px-4">Triggered At</th>
                <th className="py-3 px-4">Rule</th>
                <th className="py-3 px-4">Actual Value</th>
                <th className="py-3 px-4">Message</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {triggers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-500 font-sans">
                    No incident triggers recorded yet.
                  </td>
                </tr>
              ) : (
                triggers.map((t, idx) => (
                  <tr key={t._id || idx} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {t.triggered_at ? new Date(t.triggered_at).toLocaleString() : "N/A"}
                    </td>
                    <td className="py-3 px-4 text-rose-300 font-sans font-medium">{t.rule_name}</td>
                    <td className="py-3 px-4 text-amber-400">{t.actual_value?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-slate-200 font-sans">{t.message}</td>
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
