#!/bin/bash
# LangSmith Setup Script

echo "═══════════════════════════════════════════════════════════"
echo "    🦜 LangSmith Integration Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if already configured
if [ -f ".env.langsmith" ]; then
    echo "✅ LangSmith config already exists"
    source .env.langsmith
    echo "   Endpoint: $LANGCHAIN_ENDPOINT"
    echo "   Project: $LANGCHAIN_PROJECT"
    echo ""
    echo "To reconfigure, delete .env.langsmith and run again"
    exit 0
fi

echo "📝 LangSmith Configuration"
echo "───────────────────────────────────────────────────────────"
echo ""
echo "1. Go to: https://smith.langchain.com"
echo "2. Sign up / Log in"
echo "3. Create API Key from Settings"
echo "4. Copy the API key and paste below"
echo ""

read -sp "🔑 Enter your LangSmith API Key: " API_KEY
echo ""

read -p "📁 Project name [default: default]: " PROJECT
PROJECT=${PROJECT:-default}

echo ""
echo "⚙️  Setting up configuration..."

# Create environment file
cat > .env.langsmith << EOF
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=$API_KEY
LANGCHAIN_PROJECT=$PROJECT
EOF

echo "✅ Configuration saved to .env.langsmith"
echo ""

# Add to shell profile if not exists
SHELL_RC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if ! grep -q "LANGSMITH" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# LangSmith Configuration" >> "$SHELL_RC"
    echo 'export $(grep -v "^#" ~/.openclaw/workspace/.env.langsmith | xargs)' >> "$SHELL_RC"
    echo "✅ Added to $SHELL_RC"
fi

echo ""
echo "🚀 Setup Complete!"
echo "───────────────────────────────────────────────────────────"
echo ""
echo "Next steps:"
echo "1. Source the config: source .env.langsmith"
echo "2. Test with: python3 -c \"import langsmith; print('OK')\""
echo "3. Add tracing to your code (see examples below)"
echo ""
echo "📚 Quick Start Examples:"
echo ""
echo "Python:"
echo "  import os"
echo "  os.environ['LANGCHAIN_TRACING_V2'] = 'true'"
echo "  # Your LLM calls will now be traced automatically"
echo ""
echo "Dashboard: https://smith.langchain.com"
echo ""
