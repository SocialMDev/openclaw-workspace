# Convex Setup Guide for Mission Control

## Quick Start

### Step 1: Login to Convex

```bash
cd /home/faisal/.openclaw/workspace/mission-control
npx convex login
```

This will open a browser to authenticate with Convex.

### Step 2: Initialize the Project

```bash
npx convex dev
```

This will:
- Create a new Convex project
- Deploy the schema (activities, calendar, search)
- Start the Convex dev server
- Generate the client code

### Step 3: Get Your Convex URL

After running `npx convex dev`, you'll see output like:

```
Convex dev server running at https://happy-fox-123.convex.cloud
```

Copy this URL.

### Step 4: Create .env.local

```bash
echo "NEXT_PUBLIC_CONVEX_URL=https://your-url.convex.cloud" > .env.local
```

Replace `https://your-url.convex.cloud` with your actual URL.

### Step 5: Start the App

```bash
npm run dev
```

Open http://localhost:3000

---

## Manual Setup (If Above Doesn't Work)

### 1. Create Convex Account

1. Go to https://convex.dev
2. Sign up (GitHub or email)
3. Create a new project

### 2. Install Convex CLI

```bash
npm install -g convex
```

### 3. Login

```bash
convex login
```

### 4. Initialize in Project

```bash
cd /home/faisal/.openclaw/workspace/mission-control
convex init
```

### 5. Deploy Schema

```bash
convex deploy
```

### 6. Get Deployment URL

Go to https://dashboard.convex.dev and copy your deployment URL.

### 7. Create Environment File

```bash
cat > .env.local << EOF
NEXT_PUBLIC_CONVEX_URL=https://your-deployment-url.convex.cloud
EOF
```

### 8. Start Development

```bash
npm run dev
```

---

## Troubleshooting

### "Cannot prompt for input in non-interactive terminals"

**Solution:** Run the login command in an interactive terminal:
```bash
npx convex login
```

### "Project not found" or "Unauthorized"

**Solution:** Make sure you're logged in:
```bash
npx convex whoami
npx convex login
```

### "Schema validation failed"

**Solution:** Check your schema.ts file for errors, then redeploy:
```bash
npx convex deploy
```

### "NEXT_PUBLIC_CONVEX_URL is not defined"

**Solution:** Create the .env.local file with your Convex URL:
```bash
echo "NEXT_PUBLIC_CONVEX_URL=https://your-url.convex.cloud" > .env.local
```

### Client not connecting

1. Check that the URL in .env.local is correct
2. Make sure `npx convex dev` is running in another terminal
3. Check browser console for errors

---

## Testing the Setup

After setup, test each feature:

### Test Activity Feed

1. Open the dashboard
2. Go to Activity tab
3. You should see an empty state (no activities yet)

### Test Calendar

1. Go to Calendar tab
2. You should see a weekly calendar view
3. Try adding a test task

### Test Search

1. Go to Search tab
2. Search box should be available
3. (Won't return results until content is indexed)

---

## Next Steps After Setup

### Populate with Sample Data

Run this to add sample activities:

```bash
npx convex run activities:create --arg '{"type": "task", "description": "Mission Control dashboard initialized", "sessionId": "setup", "status": "success"}'
```

### Deploy to Production

When ready to deploy:

```bash
# Deploy Convex backend
npx convex deploy

# Build Next.js app
npm run build

# Start production server
npm start
```

---

## Dashboard URL

Once running, access your dashboard at:

**Development:** http://localhost:3000  
**Production:** Your deployed URL

---

## Need Help?

- Convex Docs: https://docs.convex.dev
- Dashboard: https://dashboard.convex.dev
- Discord: https://discord.gg/convex
