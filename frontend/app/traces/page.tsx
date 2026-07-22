"use client";

import { Suspense, useEffect, useState, useCallback } from "react";
import { GitPullRequest, Search, Clock, Server, AlertCircle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { fetchApi } from "@/lib/api";

function TreeNode({ node, maxDuration }: { node: any; maxDuration: number }) {
  const durationPercentage = maxDuration > 0 ? (node.duration_ms / maxDuration) * 100 : 100;
  const isSlow = node.duration_ms > 200;
  const displayService = node.service_name === "unknown_service:server" ? "microservice" : node.service_name;

  return (
    <div className="ml-4 border-l border-slate-700/60 pl-4 my-3 space-y-2">
      <div className="border border-slate-800 bg-slate-800/40 p-4 rounded-lg hover:border-slate-700 transition-colors">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Server className="h-4 w-4 text-indigo-400" />
            <span className="font-semibold text-white text-sm">{displayService}</span>
            <span className="text-slate-500 text-xs font-mono">{node.operation_name}</span>
          </div>
          <div className={`flex items-center gap-1 text-xs font-mono ${isSlow ? "text-rose-400 font-bold" : "text-amber-400"}`}>
            <Clock className="h-3.5 w-3.5" />
            <span>{node.duration_ms.toFixed(1)} ms</span>
          </div>
        </div>

        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${isSlow ? "bg-rose-500" : "bg-indigo-500"}`}
            style={{ width: `${Math.max(durationPercentage, 2)}%` }}
          />
        </div>
      </div>

      {node.children && node.children.length > 0 && (
        <div className="space-y-2">
          {node.children.map((child: any) => (
            <TreeNode key={child.span_id} node={child} maxDuration={maxDuration} />
          ))}
        </div>
      )}
    </div>
  );
}

function TraceContent() {
  const searchParams = useSearchParams();
  const urlTraceId = searchParams.get("id");

  const [recentTraces, setRecentTraces] = useState<string[]>([]);
  const [searchTraceId, setSearchTraceId] = useState("");
  const [traceTree, setTraceTree] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchTraceById = useCallback(async (id: string) => {
    const targetId = id.trim();
    if (!targetId) return;

    setLoading(true);
    setError("");
    setTraceTree(null);

    try {
      const data = await fetchApi<any>(`/traces/${targetId}`);
      if (!data) {
        setError("No trace found with the given Trace ID.");
      } else {
        setTraceTree(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch trace details.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    async function initPage() {
      try {
        const data = await fetchApi<string[]>("/traces");
        setRecentTraces(data || []);

        if (urlTraceId) {
          setSearchTraceId(urlTraceId);
          fetchTraceById(urlTraceId);
        } else if (data && data.length > 0) {
          const latestId = data[data.length - 1];
          setSearchTraceId(latestId);
          fetchTraceById(latestId);
        }
      } catch (err) {
        console.error("Failed to load recent traces:", err);
      }
    }
    initPage();
  }, [urlTraceId, fetchTraceById]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <h1 className="text-2xl font-bold text-white">Trace Explorer</h1>
          <p className="text-slate-400 text-sm mt-1">Visualize distributed gRPC call trees & latency bottlenecks</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900 border border-slate-800 p-4 rounded-xl">
        <div className="md:col-span-1">
          <select
            value={searchTraceId}
            onChange={(e) => {
              const selected = e.target.value;
              setSearchTraceId(selected);
              if (selected) fetchTraceById(selected);
            }}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="">-- Select Recent Trace ID --</option>
            {recentTraces.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchTraceById(searchTraceId);
          }}
          className="md:col-span-2 flex gap-2"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={searchTraceId}
              onChange={(e) => setSearchTraceId(e.target.value)}
              placeholder="Or enter custom Trace ID..."
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !searchTraceId.trim()}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? "Searching..." : "Inspect"}
          </button>
        </form>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm rounded-xl">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 min-h-[300px]">
        {!traceTree && !loading && !error && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-500">
            <GitPullRequest className="h-10 w-10 mb-2 opacity-50" />
            <p className="text-sm font-medium">Select or enter a Trace ID above to visualize its call hierarchy.</p>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
            Loading trace tree...
          </div>
        )}

        {traceTree && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-semibold uppercase text-slate-400">Call Hierarchy</span>
              <span className="text-xs text-slate-400 font-mono">
                Total Root Latency: <strong className="text-amber-400">{traceTree.duration_ms.toFixed(1)} ms</strong>
              </span>
            </div>

            <div className="-ml-4">
              <TreeNode node={traceTree} maxDuration={traceTree.duration_ms} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function TracesPage() {
  return (
    <Suspense fallback={<div className="p-8 text-slate-400 text-sm">Loading Trace Explorer...</div>}>
      <TraceContent />
    </Suspense>
  );
}
