"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, FileText, GitPullRequest, Bell, Key, LayoutDashboard } from "lucide-react";

const navItems = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Logs Explorer", href: "/logs", icon: FileText },
  { name: "Traces", href: "/traces", icon: GitPullRequest },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "API Keys", href: "/keys", icon: Key },
];

export default function Navbar() {
  const pathname = usePathname();

  if (pathname === "/login") return null;

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 min-h-screen p-4 border-r border-slate-800 shrink-0">
      <div className="flex items-center gap-2 mb-8 px-2">
        <Activity className="h-6 w-6 text-indigo-400" />
        <span className="font-bold text-lg text-white">Observability</span>
      </div>
      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
