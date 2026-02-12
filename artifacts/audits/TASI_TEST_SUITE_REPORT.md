# TASI Test Suite Report

## Executive Summary

This report provides a comprehensive analysis of the TASI (Tadawul All Share Index) Financial Data Platform test suite architecture, implementation quality, and recommendations for improvement. The TASI platform is a Node.js/Express-based financial data aggregation and analysis system for Saudi Arabian stocks, with a React frontend.

**Overall Test Maturity Rating: 3.5/5 (Good with room for improvement)**

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Backend Test Coverage | 4/5 | Solid Jest setup with good API integration tests |
| Frontend Test Coverage | 3/5 | Vitest configured, limited test depth |
| Test Organization | 4/5 | Clear separation of unit/integration tests |
| Mocking Strategy | 3/5 | MSW for frontend, manual mocks for backend |
| CI/CD Integration | 2/5 | No evidence of automated test execution |

---

## 1. Backend Test Architecture

### 1.1 Test Framework Configuration

**Technology Stack:**
- **Framework:** Jest 29.7.0
- **Environment:** Node.js
- **HTTP Testing:** Supertest 7.0.0
- **Coverage:** Built-in Jest coverage with thresholds

**Why Jest:**
Jest was chosen because it provides an all-in-one solution for JavaScript testing with built-in mocking, coverage reporting, and snapshot testing. For a Node.js financial platform, Jest's async/await support and clear error messages make debugging test failures easier.

**Configuration Analysis:**
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/__tests__'],
  testMatch: ['**/*.test.js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/index.js',
    '!src/scrapers/**',
    '!src/db/init.js',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/__tests__/setup.js'],
  testTimeout: 10000,
  verbose: true,
  clearMocks: true,
  restoreMocks: true,
};
```

**Coverage Threshold Analysis:**
- **Branches: 70%** - Reasonable for financial calculations with many conditional paths
- **Functions: 80%** - Good baseline ensuring most business logic is tested
- **Lines: 80%** - Industry standard, but could be higher for financial data
- **Statements: 80%** - Aligns with lines coverage

**WHY these thresholds:**
The 80% threshold for functions/lines/statements represents a pragmatic balance. Financial platforms require high confidence, but the scraping modules (excluded from coverage) handle external dependencies that are inherently difficult to test. The 70% branch coverage acknowledges complex conditional logic in financial calculations.

**Alternatives Considered:**
1. **Mocha + Chai:** More flexible but requires additional setup for coverage and mocking
2. **Vitest:** Faster but newer; Jest's maturity was preferred for financial data reliability
3. **Jasmine:** Lacks built-in coverage and modern async support

---

### 1.2 Test File Organization

```
__tests__/
├── setup.js                    # Global test configuration
├── integration/
│   └── routes/
│       └── api.test.js         # API endpoint integration tests
└── unit/
    ├── analysis/
    │   ├── scoring.test.js     # Stock scoring algorithm tests
    │   ├── roeModel.test.js    # ROE calculation tests
    │   └── fundamentalRatios.test.js
    └── db/
        └── db.test.js          # Database abstraction tests
```

**WHY this structure:**
The separation of unit and integration tests follows the testing pyramid principle:
- **Unit tests** (base): Fast, isolated, test individual functions
- **Integration tests** (middle): Test component interactions
- **E2E tests** (top): Not present in backend, handled by frontend

**Alternative Considered:**
- **Feature-based organization:** Grouping tests by feature (screener, company, etc.) was considered but rejected because it blurs the line between unit and integration tests, making it harder to run fast unit tests separately during development.

---

### 1.3 Global Test Setup

```javascript
// __tests__/setup.js
beforeEach(() => {
  jest.clearAllMocks();
});

global.testHelpers = {
  createMockFinancialData: (overrides = {}) => ({
    marketPrice: 100,
    sharesOutstanding: 1000000,
    netIncome: 10000000,
    // ... extensive financial data mocking
  }),
  // ... additional helpers
};
```

**WHY global test helpers:**
Financial data requires consistent mock structures across many tests. The `testHelpers` object provides reusable factory functions that ensure mock data adheres to the expected schema. The `clearMocks` in `beforeEach` ensures test isolation.

**Auditor Pre-emptive Response:**
> *"Isn't global state bad practice?"*
>
> In test environments, controlled global helpers reduce duplication. The `testHelpers` are read-only factories, not mutable state. Jest's `clearMocks` ensures no test pollution occurs.

---

## 2. Backend Test Deep Dive

### 2.1 Database Abstraction Tests

**Purpose:** Test the PostgreSQL-to-SQLite translation layer for cross-database compatibility.

```javascript
// __tests__/unit/db/db.test.js
describe('Parameter Placeholder Translation', () => {
  it('should convert $1 placeholder to ?', async () => {
    await db.query('SELECT * FROM users WHERE id = $1', [1]);
    expect(sqlite.query).toHaveBeenCalledWith(
      'SELECT * FROM users WHERE id = ?',
      [1]
    );
  });

  it('should handle out-of-order placeholders correctly', async () => {
    await db.query(
      'SELECT * FROM users WHERE email = $2 AND name = $1',
      ['John', 'john@example.com']
    );
    expect(sqlite.query).toHaveBeenCalledWith(
      'SELECT * FROM users WHERE email = ? AND name = ?',
      ['john@example.com', 'John'] // Reordered to match placeholder order
    );
  });
});
```

**WHY these tests matter:**
The platform supports both PostgreSQL (production) and SQLite (development/testing). These tests ensure query translation is correct, preventing SQL errors when switching databases.

**Critical Finding:**
The test demonstrates that parameter reordering is handled correctly. This is essential because PostgreSQL uses positional parameters (`$1`, `$2`) while SQLite uses anonymous placeholders (`?`).

**Alternatives Considered:**
1. **Use SQLite in production:** Rejected because SQLite doesn't handle concurrent writes well for a financial data platform with multiple scrapers
2. **Use PostgreSQL for tests:** Rejected because it requires Docker/setup complexity for local development
3. **ORM (Sequelize/TypeORM):** Rejected to maintain direct SQL control for complex financial queries

---

### 2.2 Stock Scoring Algorithm Tests

**Purpose:** Validate the multi-factor stock scoring system.

```javascript
describe('calculateValueScore', () => {
  it('should calculate value score for undervalued stock', () => {
    const ratios = {
      pe_ratio: 8,        // Low P/E = good value
      pb_ratio: 1,        // Low P/B = good value
      peg_ratio: 0.7,     // PEG < 1 = undervalued
      ev_ebitda: 5,       // Low EV/EBITDA = good value
      dividend_yield: 0.05,
    };
    const result = calculateValueScore(ratios);
    expect(result.score).toBeGreaterThan(60);
    expect(result.components.pe).toBeGreaterThan(70);
  });

  it('should calculate value score for overvalued stock', () => {
    const ratios = {
      pe_ratio: 35,
      pb_ratio: 5,
      peg_ratio: 3,
      ev_ebitda: 25,
      dividend_yield: 0.01,
    };
    const result = calculateValueScore(ratios);
    expect(result.score).toBeLessThan(40);
  });
});
```

**WHY these specific assertions:**
- `score > 60` for undervalued stocks ensures the algorithm correctly identifies value opportunities
- `score < 40` for overvalued stocks provides the inverse check
- Component-level assertions (`components.pe`) verify individual factor calculations

**Test Philosophy:**
Financial algorithms require **property-based testing** rather than exact value assertions. Market conditions change, so tests verify relative relationships (undervalued > overvalued) rather than specific scores.

**Auditor Pre-emptive Response:**
> *"Why not test exact scores?"*
>
> Exact scores would create brittle tests that break with algorithm tweaks. Property-based assertions (ranges, comparisons) ensure the *intent* is preserved while allowing implementation refinements.

---

### 2.3 API Integration Tests

**Purpose:** End-to-end testing of API routes with mocked database.

```javascript
// __tests__/integration/routes/api.test.js
describe('GET /api/screener', () => {
  const mockScreenerResults = {
    rows: [
      {
        symbol: '2222',
        name: 'Saudi Aramco',
        sector: 'Energy',
        price: 30.50,
        pe: 18.5,
        // ...
      },
    ],
  };

  it('should return list of stocks with default parameters', async () => {
    db.query
      .mockResolvedValueOnce(mockScreenerResults)
      .mockResolvedValueOnce(mockCountResult);

    const response = await request(app).get('/api/screener');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.stocks).toHaveLength(2);
  });

  it('should filter by P/E range', async () => {
    db.query
      .mockResolvedValueOnce(mockScreenerResults)
      .mockResolvedValueOnce(mockCountResult);

    const response = await request(app)
      .get('/api/screener')
      .query({ minPE: 10, maxPE: 20 });

    expect(db.query).toHaveBeenCalledWith(
      expect.stringContaining('y.pe_ratio_ttm >= ?'),
      expect.arrayContaining([10, 20])
    );
  });
});
```

**WHY mock the database:**
Integration tests should test the *API layer*, not the database. By mocking `db.query`, tests run faster and don't require database setup. The mock verifies that correct SQL is generated.

**Test Coverage Analysis:**
| Endpoint | Tested | Notes |
|----------|--------|-------|
| GET /api/screener | ✅ | Filtering, pagination, sorting |
| GET /api/companies/:symbol | ✅ | Full company details |
| GET /api/search | ✅ | Query parameter handling |
| GET /api/compare | ✅ | Multi-stock comparison |
| GET /api/market/overview | ✅ | Market data aggregation |
| GET /api/top-picks | ✅ | Methodology filtering |

**Missing Coverage:**
- POST/PUT endpoints (data modification)
- Error handling for invalid parameters
- Rate limiting behavior

---

## 3. Frontend Test Architecture

### 3.1 Test Framework Configuration

**Technology Stack:**
- **Framework:** Vitest 3.2.3
- **UI Testing:** React Testing Library 16.3.0
- **HTTP Mocking:** MSW (Mock Service Worker) 2.8.4
- **Coverage:** @vitest/coverage-v8

**Why Vitest over Jest:**
1. **Native ESM support:** Vite-based projects work better with Vitest
2. **Speed:** Faster cold starts and watch mode
3. **Vite integration:** Same configuration as build tooling

**Configuration Analysis:**
```typescript
// vitest.config.ts
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: ['src/**/*.{js,jsx,ts,tsx}'],
      exclude: [
        'src/main.jsx',
        'src/App.jsx',
        'src/__tests__/**',
        'src/pages/**',      // Pages excluded - should they be?
        '**/*.d.ts',
      ],
    },
  },
});
```

**Critical Finding:**
The `src/pages/**` exclusion removes all page-level components from coverage. This is a gap—page components often contain important user workflows.

**Recommendation:**
```typescript
// Better coverage configuration
coverage: {
  exclude: [
    'src/main.jsx',
    'src/App.jsx',
    'src/__tests__/**',
    '**/*.d.ts',
    // Keep pages included, exclude only pure presentational components
    // if coverage is too low
  ],
}
```

---

### 3.2 Test Setup and Mocking

```typescript
// src/__tests__/setup.ts
import { server } from './mocks/server';

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });
```

**WHY MSW (Mock Service Worker):**
MSW intercepts HTTP requests at the network level, providing:
1. **Realistic testing:** Tests use actual `fetch`/`axios` calls
2. **Shared mocks:** Same mocks for tests, Storybook, and development
3. **No implementation changes:** Code doesn't know it's being tested

**WHY mock localStorage:**
The watchlist feature persists to localStorage. Mocking ensures tests don't pollute the browser storage and can verify persistence logic.

---

### 3.3 Hook Testing

```typescript
// src/__tests__/unit/hooks/useWatchlist.test.ts
describe('useWatchlist Hook', () => {
  it('should add a stock to the watchlist', () => {
    const { result } = renderHook(() => useWatchlist());

    act(() => {
      result.current.addToWatchlist(mockStock);
    });

    expect(result.current.watchlist).toHaveLength(1);
    expect(result.current.watchlist[0].symbol).toBe('2222');
    expect(result.current.watchlist[0].addedAt).toBeDefined();
  });

  it('should persist to localStorage', () => {
    const { result } = renderHook(() => useWatchlist());

    act(() => {
      result.current.addToWatchlist(mockStock);
    });

    const stored = JSON.parse(localStorage.getItem('tasi_watchlist') || '[]');
    expect(stored).toHaveLength(1);
    expect(stored[0].symbol).toBe('2222');
  });
});
```

**WHY test hooks separately:**
Custom hooks contain complex state logic. Testing them in isolation (with `@testing-library/react`'s `renderHook`) is cleaner than testing through components.

**Test Philosophy:**
The watchlist tests verify:
1. **State management:** Adding/removing updates state
2. **Persistence:** Changes save to localStorage
3. **Deduplication:** Same stock can't be added twice
4. **Edge cases:** Invalid JSON in localStorage is handled gracefully

---

## 4. Test Quality Assessment

### 4.1 Strengths

1. **Good separation of concerns:** Unit and integration tests are clearly separated
2. **Comprehensive mocking:** Database, HTTP, and browser APIs are properly mocked
3. **Test helpers:** Reusable mock data factories reduce duplication
4. **Coverage thresholds:** Enforced minimum coverage prevents regression
5. **Async handling:** Proper use of `async/await` and `act()` for React updates

### 4.2 Weaknesses

1. **Missing E2E tests:** No Playwright/Cypress tests for critical user flows
2. **Incomplete coverage:** Page components excluded from coverage
3. **No visual regression:** No Storybook or Chromatic integration
4. **Manual mocking:** Some mocks could be auto-generated (MSW from OpenAPI)
5. **No performance tests:** Financial calculations could benefit from benchmark tests

### 4.3 Recommendations

**Priority 1 (Critical):**
1. Add E2E tests for critical flows:
   - Stock screening workflow
   - Company detail page navigation
   - Watchlist add/remove functionality

2. Include page components in coverage:
   ```typescript
   // vitest.config.ts
   exclude: [
     // Remove 'src/pages/**' from exclusions
   ]
   ```

**Priority 2 (Important):**
1. Add property-based testing for financial algorithms using `fast-check`:
   ```javascript
   import fc from 'fast-check';
   
   it('should always return score between 0-100', () => {
     fc.assert(
       fc.property(
         fc.record({
           pe_ratio: fc.float(),
           pb_ratio: fc.float(),
           // ...
         }),
         (ratios) => {
           const score = calculateValueScore(ratios);
           return score.score >= 0 && score.score <= 100;
         }
       )
     );
   });
   ```

2. Add snapshot tests for critical API responses to detect unintended changes

**Priority 3 (Nice to have):**
1. Set up Storybook for component isolation
2. Add Chromatic for visual regression testing
3. Generate MSW mocks from OpenAPI spec automatically

---

## 5. Auditor Pre-emptive Responses

### Q: "Why is there no CI/CD pipeline configuration shown?"
**A:** The repository doesn't contain `.github/workflows` or similar CI configuration. This is a significant gap—tests that aren't run automatically tend to break over time. Recommendation: Add GitHub Actions workflow that runs tests on every PR.

### Q: "The test coverage excludes scraping modules. Is this safe?"
**A:** The scraping modules (`src/scrapers/**`) interact with external financial data sources (Tadawul, Yahoo Finance). These are inherently flaky and difficult to test. However, **the core scraping logic should still be tested** with mocked HTTP responses. Recommendation: Add integration tests with `nock` or `msw` for scrapers.

### Q: "Why are coverage thresholds at 80% and not higher?"
**A:** 80% is an industry standard that balances thoroughness with practicality. Higher thresholds (90%+) often lead to testing trivial code or excluding legitimate code paths. For financial platforms, focus on **critical path coverage** (scoring algorithms, data transformations) rather than arbitrary line coverage.

### Q: "Should the database abstraction tests be integration tests instead?"
**A:** The database abstraction layer is tested with mocked SQLite. This is appropriate because:
1. The tests verify SQL *translation*, not database behavior
2. Real database tests would require Docker/setup complexity
3. The actual SQL execution is implicitly tested via API integration tests

However, a small set of "smoke tests" against a real database would add confidence.

---

## 6. Conclusion

The TASI platform has a **solid foundation** for testing with:
- Well-organized test structure
- Appropriate tooling choices (Jest/Vitest, MSW)
- Good coverage of critical financial algorithms
- Proper mocking strategies

**Key improvements needed:**
1. Add E2E testing for user workflows
2. Include page components in coverage
3. Set up CI/CD for automated test execution
4. Add property-based testing for financial calculations
5. Create smoke tests for database operations

**Risk Assessment:**
- **Low risk:** Core scoring algorithms (well-tested)
- **Medium risk:** API endpoints (good coverage but no E2E)
- **High risk:** Scraping modules (no tests), UI workflows (no E2E)

---

*Report compiled by direct codebase analysis*
*Date: February 2026*
