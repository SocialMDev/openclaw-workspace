# Self-Hosted Supabase Setup Guide

This guide will help you set up Supabase on your own server (no registration required).

## Prerequisites

- Docker installed
- Docker Compose installed
- At least 2GB RAM available
- Ports 3000, 8000, 5432 available

## Step 1: Install Docker (if not installed)

```bash
# Check if Docker is installed
docker --version

# If not installed:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

## Step 2: Clone Supabase Repository

```bash
cd /home/faisal/.openclaw/workspace
git clone --depth 1 https://github.com/supabase/supabase.git supabase-docker
cd supabase-docker/docker
```

## Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Generate secure passwords
openssl rand -base64 32 > db_password.txt
openssl rand -base64 32 > jwt_secret.txt

# Edit .env file with your settings
nano .env
```

**Required changes in .env:**
```
POSTGRES_PASSWORD=your_secure_password_from_file
JWT_SECRET=your_jwt_secret_from_file
ANON_KEY=generate_with_jwt_tool
SERVICE_ROLE_KEY=generate_with_jwt_tool
```

## Step 4: Start Supabase

```bash
# Pull and start all services
docker compose pull
docker compose up -d

# Check status
docker compose ps
```

## Step 5: Access Your Supabase

- **Studio (Dashboard):** http://localhost:3000
- **API:** http://localhost:8000
- **Database:** localhost:5432

Default credentials:
- User: supabase
- Password: (what you set in POSTGRES_PASSWORD)

## Step 6: Create Database Schema

1. Open Studio: http://localhost:3000
2. Go to SQL Editor
3. Run the migration from:
   `/home/faisal/.openclaw/workspace/mission-control/supabase/migrations/001_initial_schema.sql`

## Step 7: Configure Mission Control

Create `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## Step 8: Start Dashboard

```bash
cd /home/faisal/.openclaw/workspace/mission-control
npm install
npm run dev
```

## Maintenance Commands

```bash
# View logs
docker compose logs -f

# Stop Supabase
docker compose down

# Restart Supabase
docker compose restart

# Update Supabase
docker compose pull
docker compose up -d

# Backup database
docker exec -t supabase-db pg_dumpall -c -U supabase > backup.sql

# Restore database
cat backup.sql | docker exec -i supabase-db psql -U supabase
```

## Troubleshooting

### Port already in use
```bash
# Find what's using port 3000
sudo lsof -i :3000

# Change port in docker-compose.yml
```

### Database connection refused
```bash
# Check if database container is running
docker compose ps db

# Check logs
docker compose logs db
```

### Out of memory
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Security Notes

- Change default passwords immediately
- Use strong JWT secrets
- Set up firewall rules
- Regular backups recommended
- Don't expose ports to internet without SSL

## Migration to Cloud Later

If you want to move to Supabase Cloud later:
1. Export: `pg_dump -h localhost -U supabase postgres > backup.sql`
2. Import to cloud via Supabase Dashboard

## Resources

- Docs: https://supabase.com/docs/guides/self-hosting
- GitHub: https://github.com/supabase/supabase
- Community: https://github.com/supabase/supabase/discussions
