"use client";

import { useState } from "react";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Activity,
  FileText,
  Terminal,
  Globe,
  MessageSquare,
  CheckCircle,
  XCircle,
  Clock,
  Search,
} from "lucide-react";
import { getRelativeTime, cn } from "@/lib/utils";

const activityIcons = {
  file: FileText,
  command: Terminal,
  api: Globe,
  message: MessageSquare,
  task: Activity,
};

const activityColors = {
  file: "bg-blue-500/10 text-blue-500",
  command: "bg-purple-500/10 text-purple-500",
  api: "bg-green-500/10 text-green-500",
  message: "bg-yellow-500/10 text-yellow-500",
  task: "bg-pink-500/10 text-pink-500",
};

const statusIcons = {
  success: CheckCircle,
  error: XCircle,
  pending: Clock,
};

const statusColors = {
  success: "text-green-500",
  error: "text-red-500",
  pending: "text-yellow-500",
};

export function ActivityFeed() {
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  
  const activitiesData = useQuery(api.activities.list, {
    limit: 50,
    type: filter !== "all" ? (filter as any) : undefined,
  });

  const stats = useQuery(api.activities.getStats);

  const activities = activitiesData?.activities ?? [];
  
  const filteredActivities = activities.filter((activity) =>
    activity.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-white">{stats?.total ?? 0}</div>
            <div className="text-xs text-slate-400">Total Activities</div>
          </CardContent>
        </Card>
        {Object.entries(stats?.byType ?? {}).map(([type, count]) => {
          const Icon = activityIcons[type as keyof typeof activityIcons];
          return (
            <Card key={type} className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-slate-400" />
                  <div className="text-2xl font-bold text-white">{count}</div>
                </div>
                <div className="text-xs text-slate-400 capitalize">{type}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Filters */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search activities..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-700 text-white"
              />
            </div>
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-[180px] bg-slate-800/50 border-slate-700 text-white">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="file">File Operations</SelectItem>
                <SelectItem value="command">Commands</SelectItem>
                <SelectItem value="api">API Calls</SelectItem>
                <SelectItem value="message">Messages</SelectItem>
                <SelectItem value="task">Tasks</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Activity List */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Activity Feed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredActivities.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No activities found</p>
              </div>
            ) : (
              filteredActivities.map((activity) => {
                const Icon = activityIcons[activity.type];
                const StatusIcon = activity.status ? statusIcons[activity.status] : null;
                
                return (
                  <div
                    key={activity._id}
                    className="flex items-start gap-4 p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 hover:bg-slate-800/50 transition-colors"
                  >
                    <div className={cn("p-2 rounded-lg", activityColors[activity.type])}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-white">
                          {activity.description}
                        </p>
                        <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                          {activity.type}
                        </Badge>
                        {StatusIcon && (
                          <StatusIcon className={cn("h-4 w-4", statusColors[activity.status!])} />
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-xs text-slate-400">
                        <span>{getRelativeTime(activity.timestamp)}</span>
                        <span className="text-slate-600">•</span>
                        <span className="truncate">{activity.sessionId}</span>
                      </div>
                      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                        <div className="mt-2 text-xs text-slate-500">
                          <pre className="bg-slate-950/50 p-2 rounded overflow-x-auto">
                            {JSON.stringify(activity.metadata, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
          
          {activitiesData?.hasMore && (
            <div className="mt-6 text-center">
              <Button variant="outline" className="border-slate-700 text-slate-300">
                Load More
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
