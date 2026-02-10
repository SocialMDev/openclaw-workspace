# Mission Control Dashboard for OpenClaw

A comprehensive dashboard to monitor and manage your OpenClaw agent activities.

## Features

### 📊 Activity Feed
- Real-time logging of all OpenClaw actions
- Filter by action type (file, command, API, message, task)
- Search through activity history
- View status (success, error, pending) for each action
- Timestamps with relative time display

### 📅 Calendar View
- Weekly calendar display
- View scheduled cron jobs and proactive tasks
- Color-coded by task type
- See when OpenClaw will work autonomously
- Add, edit, and delete scheduled tasks

### 🔍 Global Search
- Full-text search across:
  - Memory files (MEMORY.md, memory/*.md)
  - Workspace documents
  - Past conversation history
  - Activity logs
  - Tasks and commands
- Filter by source type
- Fast results with Convex search indexing

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Database**: Convex (real-time sync)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **UI Components**: Custom shadcn/ui-style components
- **Icons**: Lucide React

## Project Structure

```
mission-control/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main dashboard with tabs
│   ├── layout.tsx         # Root layout with Convex provider
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ActivityFeed.tsx   # Activity feed component
│   ├── CalendarView.tsx   # Calendar view component
│   ├── GlobalSearch.tsx   # Global search component
│   ├── Sidebar.tsx        # Navigation sidebar
│   └── ui/               # UI components (buttons, cards, etc.)
├── convex/               # Convex backend
│   ├── schema.ts         # Database schema
│   ├── activities.ts     # Activity mutations/queries
│   ├── calendar.ts       # Calendar mutations/queries
│   └── search.ts         # Search mutations/queries
├── lib/                  # Utilities
│   └── utils.ts          # Helper functions
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd /home/faisal/.openclaw/workspace/mission-control
npm install
```

### 2. Set Up Convex

```bash
# Initialize Convex (you'll need a Convex account)
npx convex dev

# Or deploy to production
npx convex deploy
```

### 3. Configure Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_CONVEX_URL=your_convex_deployment_url
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 5. Build for Production

```bash
npm run build
npm start
```

## Integration with OpenClaw

To feed real data into the dashboard:

### Activity Feed
Activities are automatically tracked when you use the Convex mutations. To log an activity from OpenClaw:

```typescript
import { api } from "@/convex/_generated/api";

// Log a file operation
await convex.mutation(api.activities.create, {
  type: "file",
  description: "Created file: example.txt",
  sessionId: "session-123",
  status: "success",
  metadata: { filePath: "/path/to/file" }
});
```

### Calendar
Add scheduled tasks via the UI or API:

```typescript
await convex.mutation(api.calendar.createTask, {
  name: "Daily heartbeat check",
  description: "Check emails and calendar",
  cronExpression: "0 */6 * * *", // Every 6 hours
  enabled: true,
});
```

### Global Search
The search index is automatically populated. To add content:

```typescript
await convex.mutation(api.search.indexContent, {
  content: "Text to be searchable",
  source: "memory",
  sourceId: "memory-file-id",
  title: "Optional title"
});
```

## Features in Detail

### Activity Feed
- **Real-time updates**: Activities appear instantly as they're logged
- **Filtering**: Filter by type (file, command, API, message, task)
- **Search**: Search through activity descriptions
- **Pagination**: Load more activities as you scroll
- **Statistics**: View activity counts by type and status

### Calendar View
- **Weekly view**: See your week at a glance
- **Task management**: Add, edit, delete scheduled tasks
- **Cron support**: Use cron expressions for complex schedules
- **Color coding**: Different colors for different task types
- **Next run**: See when each task will execute next

### Global Search
- **Full-text search**: Search through all indexed content
- **Source filtering**: Filter by memory, document, conversation, or activity
- **Relevance ranking**: Most relevant results shown first
- **Fast indexing**: Convex search index for sub-second results

## Customization

### Styling
The dashboard uses Tailwind CSS with CSS variables for theming. Edit `app/globals.css` to customize colors.

### Adding New Activity Types
1. Update the schema in `convex/schema.ts`
2. Add the icon and color in `components/ActivityFeed.tsx`
3. Update the union type in activities.ts

### Extending Search
Add new sources to the search index:
1. Update the schema in `convex/schema.ts`
2. Add indexing logic in `convex/search.ts`
3. Update the UI filter in `components/GlobalSearch.tsx`

## Deployment

### Vercel (Recommended)
```bash
npm i -g vercel
vercel
```

### Self-hosted
```bash
npm run build
# Copy .next folder to your server
```

## Troubleshooting

### Convex connection issues
- Make sure `NEXT_PUBLIC_CONVEX_URL` is set correctly
- Run `npx convex dev` to start the local dev server

### Activities not appearing
- Check browser console for errors
- Verify Convex mutations are being called
- Check network tab for failed requests

### Search not working
- Ensure content is indexed via the search mutations
- Check Convex dashboard for search index status

## License

MIT - Feel free to use and modify for your own OpenClaw setup!

## Credits

Built for OpenClaw users to better manage and monitor their AI agents.
Inspired by Alex Finn's tweet: https://x.com/alexfinn/status/2019816560190521563
