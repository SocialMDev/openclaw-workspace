#!/bin/bash
# Convex Setup Script for Mission Control
# Run this interactively in your terminal

echo "🚀 Convex Setup for Mission Control Dashboard"
echo "=============================================="
echo ""

# Check if already logged in
if npx convex whoami &> /dev/null; then
    echo "✅ Already logged into Convex"
else
    echo "🔑 Please login to Convex first:"
    echo "   Run: npx convex login"
    echo ""
    echo "This will open a browser for authentication."
    echo "After logging in, run this script again."
    exit 1
fi

# Initialize Convex project
echo "📦 Initializing Convex project..."
npx convex dev --once

# Check if initialization succeeded
if [ ! -d "convex/_generated" ]; then
    echo "❌ Convex initialization failed"
    echo "Please run: npx convex dev manually"
    exit 1
fi

echo ""
echo "✅ Convex project initialized!"
echo ""

# Get the Convex URL
CONVEX_URL=$(grep -o 'NEXT_PUBLIC_CONVEX_URL=.*' .env.local 2>/dev/null || echo "")

if [ -z "$CONVEX_URL" ]; then
    echo "📝 Please create .env.local file with your Convex URL:"
    echo ""
    echo "   NEXT_PUBLIC_CONVEX_URL=your_convex_url_here"
    echo ""
    echo "Get your URL from the Convex dashboard: https://dashboard.convex.dev"
else
    echo "✅ Found Convex URL in .env.local"
fi

echo ""
echo "📊 Next steps:"
echo "1. Ensure .env.local has your Convex URL"
echo "2. Run: npm run dev"
echo "3. Open: http://localhost:3000"
echo ""
echo "🎉 Your Mission Control dashboard will be ready!"
