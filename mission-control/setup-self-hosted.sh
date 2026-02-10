#!/bin/bash
# Self-Hosted Supabase Setup Script

set -e

echo "🚀 Setting up Self-Hosted Supabase"
echo "=================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in, then re-run this script."
    exit 0
fi

echo "✅ Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker Compose is installed"

# Create directory
SETUP_DIR="/home/faisal/.openclaw/workspace/supabase-local"
mkdir -p $SETUP_DIR
cd $SETUP_DIR

# Clone Supabase if not exists
if [ ! -d "supabase" ]; then
    echo "📥 Cloning Supabase..."
    git clone --depth 1 https://github.com/supabase/supabase.git
fi

cd supabase/docker

echo "⚙️ Configuring environment..."

# Generate passwords if not exists
if [ ! -f "../../.env.passwords" ]; then
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" > ../../.env.passwords
    echo "JWT_SECRET=$JWT_SECRET" >> ../../.env.passwords
    
    # Create .env file
    cp .env.example .env
    
    # Update .env with generated passwords
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
    
    echo "✅ Passwords generated and saved"
else
    echo "✅ Using existing passwords"
    source ../../.env.passwords
fi

echo "🐳 Starting Supabase containers..."
docker compose pull
docker compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

echo ""
echo "✅ Supabase is starting up!"
echo ""
echo "📊 Access your Supabase:"
echo "  Studio (Dashboard): http://localhost:3000"
echo "  API: http://localhost:8000"
echo "  Database: localhost:5432"
echo ""
echo "📁 Passwords saved to: $SETUP_DIR/.env.passwords"
echo ""
echo "📋 Next Steps:"
echo "1. Wait 1-2 minutes for all services to fully start"
echo "2. Open http://localhost:3000"
echo "3. Go to SQL Editor"
echo "4. Run the migration from:"
echo "   /home/faisal/.openclaw/workspace/mission-control/supabase/migrations/001_initial_schema.sql"
echo ""
echo "🔧 Useful commands:"
echo "  cd $SETUP_DIR/supabase/docker"
echo "  docker compose logs -f    # View logs"
echo "  docker compose down       # Stop Supabase"
echo "  docker compose up -d      # Start Supabase"
echo ""
echo "📖 Full guide: /home/faisal/.openclaw/workspace/mission-control/SELF_HOSTED_SETUP.md"
