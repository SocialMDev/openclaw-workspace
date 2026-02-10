#!/bin/bash
# Setup script for Mission Control Dashboard

echo "🚀 Setting up Mission Control Dashboard for OpenClaw..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the mission-control directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if Convex is initialized
if [ ! -d "convex/_generated" ]; then
    echo ""
    echo "🔧 Initializing Convex..."
    echo "You'll need to:"
    echo "1. Create a Convex account at https://convex.dev"
    echo "2. Run: npx convex dev"
    echo "3. Copy the deployment URL to .env.local"
    echo ""
fi

# Create .env.local template
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local template..."
    cat > .env.local << EOF
# Get this from your Convex dashboard
NEXT_PUBLIC_CONVEX_URL=your_convex_deployment_url_here
EOF
    echo "⚠️  Please update .env.local with your Convex URL"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.local with your Convex URL"
echo "2. Run: npx convex dev (to start Convex dev server)"
echo "3. Run: npm run dev (to start Next.js)"
echo "4. Open http://localhost:3000"
echo ""
echo "📖 See README.md for full documentation"
