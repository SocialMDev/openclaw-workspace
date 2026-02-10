"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Calendar,
  Search,
  LayoutDashboard,
  Settings,
  Terminal,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Activity Feed",
    href: "/activity",
    icon: Activity,
  },
  {
    name: "Calendar",
    href: "/calendar",
    icon: Calendar,
  },
  {
    name: "Search",
    href: "/search",
    icon: Search,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col h-full w-64 bg-slate-900 border-r border-slate-800">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Terminal className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Mission Control</h1>
            <p className="text-xs text-slate-400">OpenClaw Dashboard</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-blue-600/10 text-blue-400 border border-blue-600/20"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-800/50">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-slate-300">System Online</span>
        </div>
      </div>
    </div>
  );
}
