"use client";

import { useState, useEffect } from "react";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  FileText,
  MessageSquare,
  Activity,
  Brain,
  Clock,
  X,
} from "lucide-react";
import { cn, formatTimestamp, getRelativeTime } from "@/lib/utils";

const sourceIcons = {
  memory: Brain,
  document: FileText,
  conversation: MessageSquare,
  activity: Activity,
};

const sourceColors = {
  memory: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  document: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  conversation: "bg-green-500/10 text-green-500 border-green-500/20",
  activity: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
};

export function GlobalSearch() {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const searchResults = useQuery(
    api.search.search,
    debouncedQuery.length >= 2
      ? {
          query: debouncedQuery,
          source: activeTab !== "all" ? (activeTab as any) : undefined,
          limit: 20,
        }
      : "skip"
  );

  const stats = useQuery(api.search.getStats);

  const allResults = searchResults ?? [];
  
  const filteredResults =
    activeTab === "all"
      ? allResults
      : allResults.filter((r) => r.source === activeTab);

  const groupedResults = filteredResults.reduce((acc, result) => {
    if (!acc[result.source]) acc[result.source] = [];
    acc[result.source].push(result);
    return acc;
  }, {} as Record<string, typeof filteredResults>);

  const handleClear = () => {
    setQuery("");
    setDebouncedQuery("");
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(stats?.bySource ?? {}).map(([source, count]) => {
          const Icon = sourceIcons[source as keyof typeof sourceIcons];
          return (
            <Card key={source} className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className={cn("p-2 rounded-lg", sourceColors[source as keyof typeof sourceColors])}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-white">{count}</div>
                    <div className="text-xs text-slate-400 capitalize">{source}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Search Input */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <Input
              placeholder="Search across memories, documents, conversations, and activities..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-12 pr-12 h-14 text-lg bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
            />
            {query && (
              <button
                onClick={handleClear}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-slate-700 text-slate-400"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-2">
            {debouncedQuery.length < 2
              ? "Type at least 2 characters to search"
              : `Found ${allResults.length} results`}
          </p>
        </CardContent>
      </Card>

      {/* Results */}
      {debouncedQuery.length >= 2 && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Search Results</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="bg-slate-800/50 border border-slate-700 mb-6">
                <TabsTrigger value="all" className="data-[state=active]:bg-slate-700">
                  All ({allResults.length})
                </TabsTrigger>
                <TabsTrigger value="memory" className="data-[state=active]:bg-slate-700">
                  Memories ({groupedResults.memory?.length ?? 0})
                </TabsTrigger>
                <TabsTrigger value="document" className="data-[state=active]:bg-slate-700">
                  Documents ({groupedResults.document?.length ?? 0})
                </TabsTrigger>
                <TabsTrigger value="conversation" className="data-[state=active]:bg-slate-700">
                  Conversations ({groupedResults.conversation?.length ?? 0})
                </TabsTrigger>
                <TabsTrigger value="activity" className="data-[state=active]:bg-slate-700">
                  Activities ({groupedResults.activity?.length ?? 0})
                </TabsTrigger>
              </TabsList>

              <TabsContent value={activeTab} className="mt-0">
                {filteredResults.length === 0 ? (
                  <div className="text-center py-12 text-slate-400">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No results found</p>
                    <p className="text-sm mt-1">Try adjusting your search terms</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredResults.map((result) => {
                      const Icon = sourceIcons[result.source];
                      return (
                        <div
                          key={result._id}
                          className="group p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 hover:bg-slate-800/50 hover:border-slate-600 transition-all cursor-pointer"
                        >
                          <div className="flex items-start gap-4">
                            <div
                              className={cn(
                                "p-2 rounded-lg shrink-0",
                                sourceColors[result.source]
                              )}
                            >
                              <Icon className="h-5 w-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge
                                  variant="outline"
                                  className={cn(
                                    "text-xs capitalize",
                                    sourceColors[result.source]
                                  )}
                                >
                                  {result.source}
                                </Badge>
                                {result.title && (
                                  <span className="text-sm font-medium text-white">
                                    {result.title}
                                  </span>
                                )}
                                <span className="text-xs text-slate-500 flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {getRelativeTime(result.timestamp)}
                                </span>
                              </div>
                              <p className="text-sm text-slate-300 line-clamp-3">
                                {highlightQuery(result.content, debouncedQuery)}
                              </p>
                              <p className="text-xs text-slate-500 mt-2 font-mono">
                                ID: {result.sourceId}
                              </p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Quick Tips */}
      {debouncedQuery.length < 2 && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white text-lg">Search Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50">
                <h4 className="font-medium text-white mb-2">Search Sources</h4>
                <ul className="text-sm text-slate-400 space-y-1">
                  <li className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-purple-500" />
                    Memories - Long-term curated memories
                  </li>
                  <li className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-blue-500" />
                    Documents - Files and workspace documents
                  </li>
                  <li className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-green-500" />
                    Conversations - Chat history
                  </li>
                  <li className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-yellow-500" />
                    Activities - Action logs and events
                  </li>
                </ul>
              </div>
              <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50">
                <h4 className="font-medium text-white mb-2">Search Features</h4>
                <ul className="text-sm text-slate-400 space-y-1">
                  <li>• Full-text search across all content</li>
                  <li>• Filter by source type using tabs</li>
                  <li>• Results ranked by relevance</li>
                  <li>• Real-time updates as you type</li>
                  <li>• Timestamp and source information</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function highlightQuery(content: string, query: string) {
  if (!query) return content;
  
  const parts = content.split(new RegExp(`(${query})`, "gi"));
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase() ? (
      <mark key={i} className="bg-yellow-500/30 text-yellow-200 rounded px-0.5">
        {part}
      </mark>
    ) : (
      part
    )
  );
}
