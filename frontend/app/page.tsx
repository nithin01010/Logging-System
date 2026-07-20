"use client";

import { useEffect, useState } from "react";
import { Activity, Bell, FileText, ShieldCheck, Server } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function OverviewPage() {
  const [logCount, setLogCount] = useState<number>(0);
  const [serviceCount, setServiceCount] = useState<number>(0);
  const [triggerCount, setTriggerCount] = useState<number>(0);
  const [lastLogin, setLastLogin] = useState<string>("Not recorded");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Read last login time from localStorage
    const savedTime = localStorage.getItem("last_login_time");
    if (savedTime) setLastLogin(savedTime);

    const loadMetrics = async () => {
      try {
        const [logs, triggers] = await Promise.all([
          fetchApi<any[]>("/logs/?limit=1000").catch(() => []),
          fetchApi<any[]>("/alerts/triggers").catch(() => []),
        ]);

        setLogCount(logs.length);
        setTriggerCount(triggers.length);

        // Calculate unique services count
        const services = new Set(logs.map((l) => l.service).filter(Boolean));
        setServiceCount(services.size);
      } catch (err) {
        console.error("Failed to load overview metrics:", err);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header & Security Audit Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <h1 className="text-2xl font-bold text-white">System Overview</h1>
          <p className="text-slate-400 text-sm mt-1">Real-time health & telemetry summary</p>
        </div>

        <div className="flex items-center gap-2 px-3 py-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-lg text-sm">
          <ShieldCheck className="h-4 w-4 text-indigo-400" />
          <span>Last Login: <strong className="text-white">{lastLogin}</strong></span>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-400 text-sm font-medium">Total Ingested Logs</span>
            <FileText className="h-5 w-5 text-indigo-400" />
          </div>
          <p className="text-3xl font-bold text-white">{loading ? "..." : logCount}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-400 text-sm font-medium">Monitored Microservices</span>
            <Server className="h-5 w-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-bold text-white">{loading ? "..." : serviceCount}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-400 text-sm font-medium">Alert Triggers</span>
            <Bell className="h-5 w-5 text-rose-400" />
          </div>
          <p className="text-3xl font-bold text-white">{loading ? "..." : triggerCount}</p>
        </div>
      </div>
    </div>
  );
}
