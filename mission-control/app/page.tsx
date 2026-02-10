'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { 
  Activity, Calendar, Search, LayoutDashboard, 
  FileText, Terminal, Globe, MessageSquare, CheckCircle, XCircle, Clock 
} from 'lucide-react';
import { format } from 'date-fns';

interface ActivityItem {
  id: string;
  type: 'file' | 'command' | 'api' | 'message' | 'task';
  description: string;
  timestamp: number;
  status: 'success' | 'error' | 'pending';
  session_id: string;
}

interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  next_run: number;
  enabled: boolean;
  color: string;
}

interface SearchResult {
  id: string;
  content: string;
  source: string;
  title: string;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'activity' | 'calendar' | 'search'>('activity');
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  // Load activities
  useEffect(() => {
    if (activeTab === 'activity') {
      loadActivities();
    }
  }, [activeTab]);

  // Load tasks
  useEffect(() => {
    if (activeTab === 'calendar') {
      loadTasks();
    }
  }, [activeTab]);

  async function loadActivities() {
    setLoading(true);
    const { data, error } = await supabase
      .from('activities')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(50);
    
    if (!error && data) {
      setActivities(data);
    }
    setLoading(false);
  }

  async function loadTasks() {
    setLoading(true);
    const { data, error } = await supabase
      .from('scheduled_tasks')
      .select('*')
      .order('next_run', { ascending: true });
    
    if (!error && data) {
      setTasks(data);
    }
    setLoading(false);
  }

  async function performSearch(query: string) {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    
    setLoading(true);
    const { data, error } = await supabase
      .from('search_index')
      .select('*')
      .textSearch('content', query)
      .limit(20);
    
    if (!error && data) {
      setSearchResults(data);
    }
    setLoading(false);
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'file': return <FileText className="w-4 h-4" />;
      case 'command': return <Terminal className="w-4 h-4" />;
      case 'api': return <Globe className="w-4 h-4" />;
      case 'message': return <MessageSquare className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <LayoutDashboard className="w-8 h-8 text-primary" />
          Mission Control
        </h1>
        <p className="text-muted-foreground mt-1">
          Monitor and manage your OpenClaw agent activities
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('activity')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'activity' 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-secondary hover:bg-secondary/80'
          }`}
        >
          <Activity className="w-4 h-4" />
          Activity Feed
        </button>
        <button
          onClick={() => setActiveTab('calendar')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'calendar' 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-secondary hover:bg-secondary/80'
          }`}
        >
          <Calendar className="w-4 h-4" />
          Calendar
        </button>
        <button
          onClick={() => setActiveTab('search')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'search' 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-secondary hover:bg-secondary/80'
          }`}
        >
          <Search className="w-4 h-4" />
          Global Search
        </button>
      </div>

      {/* Content */}
      <div className="bg-card rounded-xl border border-border p-6">
        {loading && (
          <div className="text-center py-8 text-muted-foreground">
            Loading...
          </div>
        )}

        {/* Activity Feed */}
        {activeTab === 'activity' && !loading && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Recent Activities</h2>
            {activities.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No activities recorded yet.</p>
                <p className="text-sm mt-2">Activities will appear here when you start using OpenClaw.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activities.map((activity) => (
                  <div 
                    key={activity.id}
                    className="flex items-start gap-4 p-4 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors"
                  >
                    <div className="mt-1">{getIcon(activity.type)}</div>
                    <div className="flex-1">
                      <p className="font-medium">{activity.description}</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        {format(activity.timestamp, 'MMM d, yyyy HH:mm')} • {activity.session_id}
                      </p>
                    </div>
                    <div>{getStatusIcon(activity.status)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Calendar */}
        {activeTab === 'calendar' && !loading && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Scheduled Tasks</h2>
            {tasks.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No scheduled tasks yet.</p>
                <p className="text-sm mt-2">Tasks will appear here when you schedule them.</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {tasks.map((task) => (
                  <div 
                    key={task.id}
                    className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                    style={{ borderLeftColor: task.color, borderLeftWidth: '4px' }}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">{task.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                        <p className="text-sm mt-2">
                          Next run: {format(task.next_run, 'MMM d, yyyy HH:mm')}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        task.enabled 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {task.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Search */}
        {activeTab === 'search' && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Global Search</h2>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Search memories, documents, conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && performSearch(searchQuery)}
                className="flex-1 px-4 py-2 rounded-lg bg-secondary border border-border focus:border-primary focus:outline-none"
              />
              <button
                onClick={() => performSearch(searchQuery)}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                Search
              </button>
            </div>
            
            {!loading && searchResults.length > 0 && (
              <div className="space-y-3 mt-6">
                {searchResults.map((result) => (
                  <div 
                    key={result.id}
                    className="p-4 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs px-2 py-1 rounded bg-primary/20 text-primary">
                        {result.source}
                      </span>
                      {result.title && (
                        <span className="font-medium">{result.title}</span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {result.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
            
            {!loading && searchQuery && searchResults.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No results found.</p>
                <p className="text-sm mt-2">Try a different search term.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
