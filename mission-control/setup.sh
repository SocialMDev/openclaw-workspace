# Quick Setup Script for Supabase

echo "🚀 Mission Control Dashboard - Supabase Setup"
echo "=============================================="
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local template..."
    cat > .env.local << EOF
# Get these from your Supabase dashboard
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
EOF
    echo "⚠️  Please update .env.local with your Supabase credentials"
    echo ""
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create Supabase account at https://supabase.com"
echo "2. Create a new project"
echo "3. Get your Project URL and Anon Key from Settings → API"
echo "4. Update .env.local with your credentials"
echo "5. Run SQL migration in Supabase SQL Editor:"
echo "   - Open supabase/migrations/001_initial_schema.sql"
echo "   - Copy contents and run in Supabase SQL Editor"
echo "6. Run: npm run dev"
echo ""
echo "📖 See README.md for full documentation"
