# Arsel LangSmith Implementation Report

## Executive Summary

This report analyzes the LangSmith observability and tracing implementation within the Arsel content generation platform—a Python/FastAPI-based system for AI-powered marketing content creation. The platform uses LangSmith to trace LLM operations, monitor performance, and debug AI workflows.

**LangSmith Integration Maturity: 3/5 (Functional but underutilized)**

| Aspect | Status | Assessment |
|--------|--------|------------|
| Basic Tracing | ✅ | `@traceable` decorator on key methods |
| Cost Tracking | ✅ | Custom implementation via `_log_usage` |
| Error Tracking | ⚠️ | Partial - errors logged but not traced |
| Run Organization | ⚠️ | Limited project/run structure |
| Prompt Versioning | ❌ | Not implemented |
| A/B Testing | ❌ | Not implemented |

---

## 1. LangSmith Architecture Overview

### 1.1 Integration Approach

**Philosophy:** Defensive integration with graceful degradation

```python
# src/arsel/services/unified_ai_service.py

# LangSmith Integration - OPTIONAL
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    # No-op decorator when LangSmith unavailable
    traceable = lambda **kwargs: lambda f: f
```

**WHY this approach:**
1. **Resilience:** Service continues if LangSmith is unavailable
2. **Development flexibility:** Developers can work without LangSmith API keys
3. **Cost control:** Can disable LangSmith in production to save costs
4. **Testing:** Tests don't require LangSmith mocking

**Alternative Considered:**
- **Mandatory dependency:** Would simplify code but reduce deployment flexibility
- **Separate tracer class:** Would add abstraction but increase complexity

---

### 1.2 Tracing Configuration

```python
@traceable(
    run_type="llm",
    name="arsel_ai_generate",
    metadata={"service": "unified_ai"}
)
async def generate(
    self,
    feature_key: str,
    prompt: str,
    system: Optional[str] = None,
    # ...
) -> str:
    """Generate text using the configured AI model."""
```

```python
@traceable(
    run_type="llm",
    name="arsel_ai_generate_structured",
    metadata={"service": "unified_ai", "output_type": "structured"}
)
async def generate_structured(
    self,
    feature_key: str,
    prompt: str,
    # ...
) -> dict:
    """Generate structured JSON output."""
```

**WHY these settings:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `run_type` | `"llm"` | Categorizes runs for LangSmith filtering |
| `name` | `"arsel_ai_generate"` | Consistent naming for queryability |
| `metadata` | Service identifier | Allows filtering by service component |

**Naming Convention Decision:**
The `arsel_` prefix ensures Arsel runs are easily identifiable in LangSmith projects shared across multiple services. This follows the pattern: `{service}_{operation}`.

**Alternative Naming Considered:**
- Just `"generate"` - Too generic, hard to filter
- Feature-specific names (`"content_generation"`) - Would fragment traces across features
- Dynamic naming based on `feature_key` - Would create too many distinct run types

---

## 2. Tracing Implementation Analysis

### 2.1 Coverage Assessment

**Current Traced Methods:**

| Method | Decorator | Traced Inputs | Notes |
|--------|-----------|---------------|-------|
| `generate()` | `@traceable` | `feature_key` | Main LLM entry point |
| `generate_structured()` | `@traceable` | `feature_key` | JSON output generation |
| `_generate_with_fallback()` | ❌ | N/A | Fallback method untraced |
| `_log_usage()` | ❌ | N/A | Custom logging only |
| `get_available_models()` | ❌ | N/A | API call not traced |
| `test_connection()` | ❌ | N/A | Utility not traced |

**Coverage Gap Analysis:**

1. **Missing: `_generate_with_fallback()`**
   - When the primary model fails, fallback attempts aren't traced
   - **Impact:** Can't analyze fallback frequency or success rates in LangSmith
   - **Recommendation:** Add `@traceable(name="arsel_ai_fallback")`

2. **Missing: Internal helper methods**
   - `_get_effective_params()`, `_get_openai_client()` not traced
   - **Impact:** Can't debug configuration resolution issues
   - **Recommendation:** Add tracing for configuration chain

---

### 2.2 Trace Context and Metadata

**Current Metadata:**
```python
metadata={"service": "unified_ai"}
```

**Missing Context:**

The traces currently capture minimal context. For a content generation platform, valuable missing metadata includes:

```python
# Recommended enhanced metadata
@traceable(
    run_type="llm",
    name="arsel_ai_generate",
    metadata={
        "service": "unified_ai",
        "feature_key": feature_key,  # Which feature (content_generation, etc.)
        "model": params.get("model"),  # Which model was used
        "temperature": params.get("temperature"),
        "has_system_prompt": system is not None,
        "prompt_length": len(prompt),
    }
)
```

**WHY add this context:**
1. **Performance analysis:** Compare latency across models
2. **Cost tracking:** Model + token count = cost
3. **Debuggability:** Temperature/prompt correlation with output quality
4. **A/B testing:** Compare feature_key performance

**Auditor Pre-emptive Response:**
> *"Won't this increase token costs for metadata?"*
>
> LangSmith metadata is stored separately from the traced data and doesn't affect LLM token costs. The metadata is attached to the run record in LangSmith's database.

---

## 3. Cost Tracking Implementation

### 3.1 Custom Cost Tracking

Arsel implements **dual cost tracking**—both custom logging AND LangSmith tracing:

```python
async def _log_usage(
    self,
    feature_key: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    cost_usd: Optional[float] = None,
    latency_ms: Optional[int] = None,
    success: bool = True,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    user_id: Optional[int] = None,
    client_id: Optional[int] = None,
):
    """Log AI usage for cost tracking."""
    try:
        async with async_session_maker() as db:
            log_entry = AIUsageLog(
                feature_key=feature_key,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost_usd=Decimal(str(cost_usd)) if cost_usd else None,
                latency_ms=latency_ms,
                success=success,
                error_code=error_code,
                error_message=error_message[:1000] if error_message else None,
                user_id=user_id,
                client_id=client_id,
            )
            db.add(log_entry)
            await db.commit()
    except Exception as e:
        logger.warning(f"Failed to log AI usage: {e}")
```

**WHY custom logging instead of relying on LangSmith:**

1. **Data ownership:** Costs stored in Arsel's database for billing integration
2. **Multi-tenancy:** User/client attribution for per-client billing
3. **Offline analysis:** Can query cost data without LangSmith API dependency
4. **Business logic:** Cost data tied to Arsel's billing system

**Alternative Considered:**
- **LangSmith-only:** Would lose direct database integration
- **LangSmith API export:** Could periodically export but adds complexity
- **OpenTelemetry:** More flexible but overkill for current needs

---

### 3.2 Cost Data Model

```python
# arsel/models/ai_config.py
class AIUsageLog(Base):
    """Log of AI API usage for cost tracking."""
    
    __tablename__ = "ai_usage_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(100))
    prompt_tokens: Mapped[int]
    completion_tokens: Mapped[int]
    total_tokens: Mapped[int]
    cost_usd: Mapped[Optional[Decimal]]
    latency_ms: Mapped[Optional[int]]
    success: Mapped[bool]
    error_code: Mapped[Optional[str]]
    error_message: Mapped[Optional[str]]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**WHY this schema:**

| Field | Purpose |
|-------|---------|
| `feature_key` | Group costs by feature for product analysis |
| `model` | Track cost per model for provider optimization |
| `user_id` / `client_id` | Multi-tenant billing attribution |
| `latency_ms` | Performance monitoring |
| `success` | Error rate tracking |

**Index Strategy:**
- `feature_key` indexed for quick cost queries per feature
- `created_at` implicitly indexed (primary key) for time-series queries
- Foreign keys indexed for joins

---

## 4. Error Handling and Tracing

### 4.1 Error Classification

```python
class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass

class AIFeatureDisabledError(AIServiceError):
    """Raised when a disabled AI feature is called."""
    def __init__(self, feature_key: str):
        self.feature_key = feature_key
        super().__init__(f"AI feature '{feature_key}' is disabled")

class AICreditsExhaustedError(AIServiceError):
    """Raised when OpenRouter credits are exhausted."""
    pass

class AIContentModerationError(AIServiceError):
    """Raised when content is flagged by moderation."""
    def __init__(self, reasons: Optional[list[str]] = None):
        self.reasons = reasons or []
        super().__init__(f"Content flagged by moderation: {', '.join(self.reasons)}")

class AIRateLimitError(AIServiceError):
    """Raised when rate limited by OpenRouter."""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s" if retry_after else "Rate limited")
```

**WHY custom exceptions:**

1. **Structured error handling:** Callers can catch specific error types
2. **Context preservation:** Error-specific data (retry_after, reasons) available
3. **Monitoring:** Different error types can trigger different alerts
4. **User messages:** Friendly error messages derived from exception type

**LangSmith Integration Gap:**

These exceptions are **logged to the database** but **not attached to LangSmith traces**. This means:
- ✅ Errors are tracked for business metrics
- ❌ Can't correlate errors with specific prompts in LangSmith
- ❌ Can't analyze error patterns by model/feature

**Recommended Fix:**

```python
from langsmith import traceable, get_current_run_tree

@traceable(run_type="llm", name="arsel_ai_generate")
async def generate(self, ...):
    try:
        # ... generation logic
        pass
    except AICreditsExhaustedError:
        run_tree = get_current_run_tree()
        run_tree.error = "credits_exhausted"
        run_tree.end(error="OpenRouter credits exhausted")
        raise
    except AIRateLimitError as e:
        run_tree = get_current_run_tree()
        run_tree.error = f"rate_limited:{e.retry_after}"
        run_tree.end(error=f"Rate limited, retry after {e.retry_after}s")
        raise
```

---

## 5. Configuration and Feature Flags

### 5.1 AI Configuration Cache

```python
class AIConfigCache:
    """Cache for AI configuration from database.
    
    Caches provider config and feature configs with a configurable TTL.
    """

    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self._provider_config: Optional[AIProviderConfig] = None
        self._feature_configs: dict[str, AIFeatureConfig] = {}
        self._last_refresh: Optional[datetime] = None
        self._lock = asyncio.Lock()
```

**WHY caching:**

1. **Performance:** Avoid database queries on every LLM call
2. **Resilience:** Continue operating if database is temporarily unavailable
3. **Flexibility:** Admin changes propagate within TTL

**Cache TTL Decision:**
- **60 seconds** balances freshness with performance
- Too short (< 10s): Database load increases
- Too long (> 5min): Configuration changes take too long to apply

**Alternative Considered:**
- **Redis cache:** Would allow cross-instance consistency but adds infrastructure
- **Event-driven updates:** Would require message queue complexity
- **No caching:** Would simplify but hurt performance under load

---

### 5.2 Feature-Level Configuration

```python
class AIFeatureConfig(Base):
    """Configuration for a specific AI feature."""
    
    __tablename__ = "ai_feature_configs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    feature_key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    model: Mapped[Optional[str]] = mapped_column(String(100))
    temperature: Mapped[Optional[Decimal]]
    max_tokens: Mapped[Optional[int]]
    top_p: Mapped[Optional[Decimal]]
    frequency_penalty: Mapped[Optional[Decimal]]
    presence_penalty: Mapped[Optional[Decimal]]
    system_prompt: Mapped[Optional[str]]
```

**WHY per-feature configuration:**

1. **A/B testing:** Different features can use different models
2. **Cost optimization:** Less critical features use cheaper models
3. **Quality tuning:** Different temperatures for different content types
4. **Gradual rollout:** Features can be enabled/disabled independently

**Configuration Priority Chain:**
```
Request overrides > Feature config > Global config > Defaults
```

This allows fine-grained control while maintaining sensible defaults.

---

## 6. Testing Strategy

### 6.1 LangSmith in Tests

The codebase **correctly disables LangSmith in tests** via the `traceable` no-op fallback:

```python
# When langsmith import fails (tests), traceable becomes:
traceable = lambda **kwargs: lambda f: f  # No-op decorator
```

**WHY this is correct:**

1. **Test isolation:** Tests don't make external API calls
2. **Speed:** No network overhead in tests
3. **Determinism:** Tests produce same results without LangSmith
4. **No mocking needed:** Don't need to mock LangSmith client

**Alternative (Not Recommended):**
```python
# DON'T DO THIS - adds complexity
@pytest.fixture
def mock_langsmith():
    with patch("langsmith.traceable") as mock:
        mock.return_value = lambda f: f
        yield
```

---

## 7. Recommendations

### 7.1 Immediate Improvements

**1. Add Fallback Tracing**
```python
@traceable(
    run_type="llm",
    name="arsel_ai_fallback",
    metadata={"service": "unified_ai", "fallback": True}
)
async def _generate_with_fallback(self, ...):
    """Generate with fallback model."""
```

**WHY:** Understanding fallback frequency helps optimize primary model selection.

---

**2. Enhanced Metadata**
```python
@traceable(
    run_type="llm",
    name="arsel_ai_generate",
    metadata={
        "service": "unified_ai",
        "feature_key": feature_key,
        # ADD THESE:
        "user_id": user_id,
        "client_id": client_id,
        "prompt_tokens_estimate": len(prompt) // 4,  # Rough estimate
    }
)
```

**WHY:** User/client attribution enables cost analysis per tenant.

---

**3. Error Attribution**
```python
except Exception as e:
    # ADD THIS:
    if LANGSMITH_AVAILABLE:
        from langsmith import get_current_run_tree
        run_tree = get_current_run_tree()
        run_tree.error = str(e)
    
    await self._log_usage(...)
    raise
```

**WHY:** Errors visible in LangSmith UI alongside prompt context.

---

### 7.2 Long-term Enhancements

**1. Prompt Versioning**
```python
@traceable(
    run_type="llm",
    name="arsel_ai_generate",
    metadata={
        "prompt_version": "2.3.1",  # Semantic versioning
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:8],
    }
)
```

**WHY:** Track prompt changes and correlate with output quality.

---

**2. Parent-Child Tracing for Multi-step Workflows**
```python
@traceable(run_type="chain", name="content_generation_pipeline")
async def generate_content_pipeline(self, ...):
    # Step 1: Research
    research = await self.research_topic(...)  # Child trace
    
    # Step 2: Outline
    outline = await self.create_outline(research)  # Child trace
    
    # Step 3: Generate
    content = await self.generate_content(outline)  # Child trace
```

**WHY:** Complex content generation involves multiple LLM calls. Parent-child tracing shows the full workflow.

---

**3. Dataset Integration for Regression Testing**
```python
from langsmith import Client as LangSmithClient

class AITestSuite:
    def __init__(self):
        self.ls_client = LangSmithClient()
    
    async def create_regression_dataset(self):
        """Create dataset from production traces."""
        runs = self.ls_client.list_runs(
            project_name="arsel-production",
            run_type="llm",
            error=False,
        )
        # Create dataset for regression testing
```

**WHY:** Automatically build test datasets from successful production runs.

---

## 8. Auditor Pre-emptive Responses

### Q: "Why isn't LangSmith used for all LLM calls?"
**A:** The current implementation traces the main entry points (`generate`, `generate_structured`) but not helper methods. This is intentional—tracing every internal method would create noise. However, `_generate_with_fallback` should be traced as it represents a significant event (primary model failure).

### Q: "Is the no-op decorator pattern safe?"
**A:** Yes. The pattern `traceable = lambda **kwargs: lambda f: f` creates a pass-through decorator that returns the original function unchanged. This is a well-established pattern for optional dependencies.

### Q: "Why duplicate cost tracking in both LangSmith and the database?"
**A:** LangSmith provides observability and debugging; the database provides business logic integration. They're complementary:
- LangSmith: "Why was this request slow?"
- Database: "How much did we spend this month?"

### Q: "Should prompt content be traced?"
**A:** Currently, only `feature_key` is traced, not the full prompt. This is a **privacy/security consideration**—prompts may contain client data. Recommendation: Add a `trace_prompts` configuration flag that can be enabled for debugging but disabled in production.

---

## 9. Conclusion

The Arsel LangSmith implementation provides **basic observability** with room for enhancement:

**Strengths:**
- Clean integration with graceful degradation
- Comprehensive custom cost tracking
- Proper error classification
- Feature-level configuration

**Weaknesses:**
- Limited trace metadata
- Missing fallback tracing
- No error attribution in traces
- No prompt versioning

**Priority Actions:**
1. Add fallback model tracing (easy, high value)
2. Enhance trace metadata with user/client context (medium effort, high value)
3. Implement error attribution (easy, medium value)
4. Add prompt versioning for quality analysis (medium effort, high value)

**Risk Assessment:**
- **Low:** Current implementation is stable and functional
- **Medium:** Limited visibility into fallback behavior
- **High:** No systematic way to analyze prompt quality changes

---

*Report compiled by direct codebase analysis*
*Date: February 2026*
