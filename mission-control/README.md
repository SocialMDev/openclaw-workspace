# Mission Control Dashboard (Supabase Edition)

A comprehensive dashboard to monitor and manage your OpenClaw agent activities, built with **Supabase** (PostgreSQL + Real-time).

## Why Supabase Instead of Convex?

| Feature | Supabase | Convex |
|---------|----------|--------|
| **Database** | PostgreSQL (industry standard) | Proprietary |
| **Self-hosted** | ✅ Yes | ❌ No |
| **SQL Support** | ✅ Full SQL | ❌ Limited |
| **Community** | 🔥 Massive | Smaller |
| **Vendor Lock-in** | ❌ None | ⚠️ Risk |
| **Free Tier** | ✅ Generous | ✅ Generous |

## Features

### 📊 Activity Feed
- Real-time logging of all OpenClaw actions
- Filter by action type (file, command, API, message, task)
- Status tracking (success, error, pending)
- Timestamps and session tracking

### 📅 Calendar View
- View scheduled cron jobs and proactive tasks
- Color-coded by task type
- Enable/disable tasks
- Next run scheduling

### 🔍 Global Search
- Full-text search across all indexed content
- Filter by source (memory, document, conversation, activity)
- PostgreSQL full-text search with relevance ranking

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Database**: Supabase (PostgreSQL)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Icons**: Lucide React

## Setup Instructions

### 1. Create Supabase Account

1. Go to https://supabase.com
2. Sign up (GitHub or email)
3. Create a new project
4. Wait for database to be provisioned (2-3 minutes)

### 2. Get Your Credentials

In your Supabase project dashboard:
1. Go to **Settings** → **API**
2. Copy `Project URL` and `anon public` key
3. You'll need these for the environment variables

### 3. Set Up Database Schema

In the Supabase dashboard:
1. Go to **SQL Editor**
2. Click **New query**
3. Copy and paste the contents of `supabase/migrations/001_initial_schema.sql`
4. Click **Run**

This creates:
- `activities` table
- `scheduled_tasks` table  
- `search_index` table
- Indexes and full-text search

### 4. Configure Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

Replace with your actual values from step 2.

### 5. Install Dependencies

```bash
cd /home/faisal/.openclaw/workspace/mission-control-supabase
npm install
```

### 6. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

## Database Schema

### activities
```sql
- id: UUID (primary key)
- type: enum ('file', 'command', 'api', 'message', 'task')
- description: text
- metadata: JSONB
- timestamp: bigint
- session_id: text
- status: enum ('success', 'error', 'pending')
```

### scheduled_tasks
```sql
- id: UUID (primary key)
- name: text
- description: text
- cron_expression: text
- next_run: bigint
- enabled: boolean
- color: text
- last_run: bigint
- run_count: integer
```

### search_index
```sql
- id: UUID (primary key)
- content: text (full-text searchable)
- source: enum ('memory', 'document', 'conversation', 'activity')
- source_id: text
- title: text
- timestamp: bigint
```

## Integration with OpenClaw

### Log an Activity

```typescript
import { supabase } from '@/lib/supabase';

await supabase.from('activities').insert({
  type: 'file',
  description: 'Created file: example.txt',
  session_id: 'session-123',
  status: 'success',
  metadata: { filePath: '/path/to/file' }
});
```

### Add a Scheduled Task

```typescript
await supabase.from('scheduled_tasks').insert({
  name: 'Daily heartbeat check',
  description: 'Check emails and calendar',
  cron_expression: '0 */6 * * *',
  next_run: Date.now() + 6 * 60 * 60 * 1000,
  enabled: true,
  color: '#3b82f6'
});
```

### Index Content for Search

```typescript
await supabase.from('search_index').insert({
  content: 'Text to be searchable',
  source: 'memory',
  source_id: 'memory-file-id',
  title: 'Optional title'
});
```

## Real-time Subscriptions (Optional)

To get real-time updates:

```typescript
// Subscribe to new activities
const subscription = supabase
  .channel('activities')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'activities' },
    (payload) => {
      console.log('New activity:', payload.new);
    }
  )
  .subscribe();
```

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

Add environment variables in Vercel dashboard.

### Self-hosted

```bash
npm run build
npm start
```

## Troubleshooting

### "Failed to fetch" error
- Check that `NEXT_PUBLIC_SUPABASE_URL` is correct
- Ensure your Supabase project is active

### "Invalid API key" error
- Verify `NEXT_PUBLIC_SUPABASE_ANON_KEY` is correct
- Check that you're using the `anon public` key, not the service role key

### Search not working
- Make sure you ran the SQL migration
- Check that the full-text search index was created

### Tables not found
- Run the SQL migration in Supabase SQL Editor
- Check that tables were created in Table Editor

## Migration from Convex

If you're switching from Convex:

1. Export your Convex data
2. Import into Supabase using SQL or CSV
3. Update your application code to use Supabase client
4. Deploy with new environment variables

## Advantages Over Convex

1. **PostgreSQL**: Industry standard, not proprietary
2. **SQL**: Full SQL power for complex queries
3. **Self-hostable**: You can host your own Supabase instance
4. **No vendor lock-in**: Standard PostgreSQL, easy to migrate
5. **Auth included**: Built-in authentication if you need it later
6. **Storage included**: File uploads if needed
7. **Bigger community**: More resources and support

## License

MIT

## Credits

Built for OpenClaw users. Originally inspired by Alex Finn's tweet.
Rewritten for Supabase for better long-term viability.
