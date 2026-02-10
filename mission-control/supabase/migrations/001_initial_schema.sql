-- Create activities table
CREATE TABLE IF NOT EXISTS activities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('file', 'command', 'api', 'message', 'task')),
  description TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  timestamp BIGINT NOT NULL DEFAULT extract(epoch from now()) * 1000,
  session_id TEXT NOT NULL,
  status TEXT CHECK (status IN ('success', 'error', 'pending')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes
CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);
CREATE INDEX idx_activities_type ON activities(type);
CREATE INDEX idx_activities_session ON activities(session_id);

-- Enable Row Level Security
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for demo purposes)
CREATE POLICY "Allow all" ON activities FOR ALL USING (true) WITH CHECK (true);

-- Create scheduled_tasks table
CREATE TABLE IF NOT EXISTS scheduled_tasks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  cron_expression TEXT NOT NULL,
  next_run BIGINT NOT NULL,
  enabled BOOLEAN DEFAULT true,
  color TEXT DEFAULT '#3b82f6',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  last_run BIGINT,
  run_count INTEGER DEFAULT 0
);

CREATE INDEX idx_scheduled_tasks_next_run ON scheduled_tasks(next_run);
CREATE INDEX idx_scheduled_tasks_enabled ON scheduled_tasks(enabled);

ALTER TABLE scheduled_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON scheduled_tasks FOR ALL USING (true) WITH CHECK (true);

-- Create search_index table
CREATE TABLE IF NOT EXISTS search_index (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('memory', 'document', 'conversation', 'activity')),
  source_id TEXT NOT NULL,
  title TEXT,
  timestamp BIGINT NOT NULL DEFAULT extract(epoch from now()) * 1000,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX idx_search_index_source ON search_index(source);
CREATE INDEX idx_search_index_timestamp ON search_index(timestamp DESC);

-- Create full-text search index
CREATE INDEX idx_search_index_content ON search_index USING gin(to_tsvector('english', content));

ALTER TABLE search_index ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all" ON search_index FOR ALL USING (true) WITH CHECK (true);
