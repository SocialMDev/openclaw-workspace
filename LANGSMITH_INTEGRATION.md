# 🦜 LangSmith Integration for Arsel

## Current Status
- ✅ LangSmith SDK installed
- ✅ Found AI service: `unified_ai_service.py`
- ⏳ Configuration needed

## Setup Required

### Step 1: Get API Key
```bash
# Visit https://smith.langchain.com
# Create account → Settings → API Keys → Create Key
```

### Step 2: Configure Environment
```bash
cd /home/faisal/.openclaw/workspace
./setup_langsmith.sh
```

Or manually create `.env.langsmith`:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_api_key_here
LANGCHAIN_PROJECT=arsel-production
```

### Step 3: Source Configuration
```bash
source /home/faisal/.openclaw/workspace/.env.langsmith
```

## 🔧 Integration Points Found

### 1. Unified AI Service
**File:** `src/arsel/services/unified_ai_service.py`
**Current:** Uses OpenAI client directly
**Integration:** Wrap LLM calls with LangSmith tracing

### 2. Integration Code

Add to `unified_ai_service.py`:
```python
from langsmith import traceable
from langsmith.run_trees import RunTree

# Wrap the main generate method
@traceable(run_type="llm", name="arsel_ai_generate")
async def generate_with_tracing(self, feature_key: str, messages: list, **kwargs):
    """Wrapped version with LangSmith tracing."""
    return await self._generate(feature_key, messages, **kwargs)
```

## 📊 What Will Be Traced

| Component | Traced Data |
|-----------|-------------|
| AI Requests | Prompts, model, parameters |
| AI Responses | Completion, tokens used |
| Timing | Latency per request |
| Errors | Failures and fallbacks |
| Cost | Token usage tracking |

## 🎯 Benefits for Arsel

1. **Debug Content Generation** - See exactly what prompts produce what content
2. **Cost Optimization** - Track which features use most tokens
3. **Performance Monitoring** - Identify slow AI calls
4. **Prompt Versioning** - Track prompt changes over time
5. **Team Collaboration** - Share AI traces with team

## 🚀 Next Steps

1. Run setup script: `./setup_langsmith.sh`
2. Add LangSmith decorators to AI service
3. Deploy and verify traces in dashboard
4. Set up monitoring alerts

## 📚 Resources

- Dashboard: https://smith.langchain.com
- Docs: https://docs.langchain.com/langsmith
- Pricing: Free tier available
