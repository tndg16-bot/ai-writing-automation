# Testing Guide

Complete guide for testing the AI Writing Automation system.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [WebSocket Testing](#websocket-testing)
- [E2E Testing](#e2e-testing)
- [Running All Tests](#running-all-tests)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Overview

The AI Writing Automation project has a comprehensive testing suite covering:

1. **Backend (FastAPI)** - Unit tests for API endpoints, business logic, database operations
2. **Frontend (Next.js)** - Component tests using React Testing Library
3. **WebSocket** - Real-time communication tests
4. **E2E (Playwright)** - End-to-end user flow tests

### Test Statistics

| Category | Test Files | Test Cases |
|----------|-----------|-----------|
| Backend | 19 | 85+ |
| Frontend | 3 | 30+ |
| WebSocket | 1 | 15+ |
| E2E | 1 | 20+ |
| **Total** | **24** | **150+** |

---

## Prerequisites

### Python (Backend)

```bash
cd api
pip install -e ".[dev]"
```

Required packages:
- pytest >= 7.0
- pytest-asyncio >= 0.21
- pytest-cov >= 4.0
- httpx >= 0.24
- moto >= 4.0

### Node.js (Frontend & E2E)

```bash
cd frontend
npm install --save-dev \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jest \
  jest-environment-jsdom \
  @types/jest
```

For E2E tests:
```bash
npm install --save-dev @playwright/test
npx playwright install
```

---

## Backend Testing

### Running Backend Tests

```bash
# Run all backend tests
cd api
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run with verbose output
pytest tests/ -vv

# Run only fast tests
pytest tests/ -m "not slow"
```

### Backend Test Structure

```
api/tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_api.py              # API endpoint tests
├── test_database.py         # Database operation tests
├── test_pipeline.py          # Pipeline execution tests
├── test_websocket.py        # WebSocket connection tests
└── test_integration.py      # Integration tests
```

### Common Backend Fixtures

```python
# conftest.py provides these fixtures:

@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses"""

@pytest.fixture
async def client():
    """Test HTTP client for FastAPI"""

@pytest.fixture
async def test_db():
    """In-memory test database"""
```

### Example Backend Test

```python
import pytest
from httpx import AsyncClient

async def test_create_generation(client: AsyncClient, mock_openai):
    response = await client.post(
        "/api/generate",
        json={"keyword": "AI副業", "content_type": "blog"}
    )
    assert response.status_code == 202
    assert "task_id" in response.json()
```

### Running Specific Backend Test Categories

```bash
# Only API tests
pytest tests/test_api.py -v

# Only WebSocket tests
pytest tests/test_websocket.py -v

# Only database tests
pytest tests/test_database.py -v

# Run tests matching pattern
pytest tests/ -k "generation" -v
```

---

## Frontend Testing

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test page.test.tsx
```

### Frontend Test Structure

```
frontend/__tests__/
├── page.test.tsx            # Home page tests
├── generate-page.test.tsx   # Generation form tests
└── progress-page.test.tsx    # Progress page tests
```

### Frontend Test Configuration

```typescript
// jest.config.ts
export default {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
};
```

### Example Frontend Test

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import HomePage from '../app/page';

describe('HomePage', () => {
  it('renders dashboard title', () => {
    render(<HomePage />);
    expect(screen.getByText('AI Writing Dashboard')).toBeInTheDocument();
  });

  it('refreshes data on button click', async () => {
    render(<HomePage />);
    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);
    // Verify refresh behavior
  });
});
```

### Frontend Testing Best Practices

1. **Test user behavior, not implementation**
   ```tsx
   // ✅ Good - tests what user sees
   expect(screen.getByText('Submit')).toBeVisible();

   // ❌ Bad - tests implementation details
   expect(component.state().isSubmitting).toBe(true);
   ```

2. **Use semantic queries**
   ```tsx
   // ✅ Good
   screen.getByRole('button', { name: 'Submit' })

   // ⚠️ Acceptable
   screen.getByText('Submit')

   // ❌ Avoid
   screen.getByClassName('submit-btn')
   ```

3. **Mock external dependencies**
   ```tsx
   jest.mock('@/lib/api', () => ({
     getStats: jest.fn().mockResolvedValue({ total: 10 }),
   }));
   ```

---

## WebSocket Testing

### WebSocket Test Categories

1. **Connection Tests**
   - Valid task ID connection
   - Invalid task ID rejection
   - Connection timeout handling

2. **Message Tests**
   - Progress message format
   - Result message format
   - Error message format

3. **Behavior Tests**
   - Real-time updates
   - Disconnect handling
   - Multiple concurrent connections

### Running WebSocket Tests

```bash
cd api
pytest tests/test_websocket.py -v
```

### WebSocket Test Example

```python
async def test_websocket_receives_progress(client, mock_openai):
    # Start generation
    response = await client.post(
        "/api/generate",
        json={"keyword": "test", "content_type": "blog"}
    )
    task_id = response.json()["task_id"]

    # Connect WebSocket
    with client.websocket_connect(f"/api/generate/ws/{task_id}") as websocket:
        # Receive progress
        data = websocket.receive_json(timeout=5)
        assert data["type"] == "progress"
        assert "stage" in data
```

### WebSocket Message Formats

**Progress Message:**
```json
{
  "type": "progress",
  "task_id": "uuid",
  "stage": "Generating content",
  "stage_index": 2,
  "total_stages": 6,
  "status": "running",
  "message": "Processing..."
}
```

**Result Message:**
```json
{
  "type": "result",
  "task_id": "uuid",
  "status": "completed",
  "generation_id": 123,
  "markdown": "# Generated Content..."
}
```

**Error Message:**
```json
{
  "type": "progress",
  "status": "failed",
  "error": "API rate limit exceeded"
}
```

---

## E2E Testing

### Running E2E Tests

```bash
# Install Playwright browsers
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test complete-flow.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run with UI mode
npx playwright test --ui

# Run specific browsers
npx playwright test --project=chromium
npx playwright test --project=firefox
```

### E2E Test Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'cd frontend && npm run dev',
    port: 3000,
  },
});
```

### Example E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('complete generation flow', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('/');

  // Start generation
  await page.click('text=New Generation');
  await page.fill('input#keyword', 'AI副業');
  await page.selectOption('select#content-type', 'blog');
  await page.click('button:has-text("Generate Content")');

  // Verify progress page
  await page.waitForURL(/\/progress/);
  await expect(page.getByText('Generation Progress')).toBeVisible();

  // Wait for completion
  await expect(page.getByText('Result')).toBeVisible({ timeout: 60000 });
});
```

### E2E Test Scenarios

1. **Happy Path Tests**
   - Complete generation flow
   - Multiple content types
   - Progress tracking

2. **Validation Tests**
   - Empty keyword validation
   - Invalid content types
   - Required field checks

3. **Error Handling Tests**
   - API error handling
   - WebSocket connection errors
   - Network timeout handling

4. **UI/UX Tests**
   - Responsive design
   - Accessibility
   - Performance

---

## Running All Tests

### Full Test Suite

```bash
# Run all tests (requires all services)
./scripts/run-all-tests.sh
```

### Manual Full Test Run

```bash
# 1. Backend tests
cd api
pytest tests/ --cov=. --cov-report=html

# 2. Frontend tests
cd ../frontend
npm test -- --coverage

# 3. E2E tests (requires running services)
npm run test:e2e
```

### Test Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Backend API | 80%+ | ✓ |
| Database | 70%+ | ✓ |
| Frontend Components | 80%+ | ✓ |
| Pipelines | 75%+ | ✓ |
| **Overall** | **75%+** | **✓** |

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd api
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd api
          pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

  e2e:
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Troubleshooting

### Backend Test Issues

**Issue: Tests fail with database errors**
```bash
# Solution: Use test database fixtures
pytest tests/ -v --override-ini="test_db=memory"
```

**Issue: OpenAI API calls not mocked**
```bash
# Solution: Ensure mock_openai fixture is used
pytest tests/test_pipeline.py -v -k "mock_openai"
```

**Issue: Async tests hang**
```bash
# Solution: Ensure pytest-asyncio is installed and configured
pip install pytest-asyncio
pytest tests/ -v --asyncio-mode=auto
```

### Frontend Test Issues

**Issue: Jest cannot find modules**
```bash
# Solution: Check jest.config.ts moduleNameMapper
npm test -- --no-cache
```

**Issue: Tests fail with "act is not defined"**
```bash
# Solution: Import from @testing-library/react
npm install --save-dev @testing-library/react
```

**Issue: Test timeouts**
```bash
# Solution: Increase timeout in test
await waitFor(() => {
  expect(element).toBeVisible();
}, { timeout: 5000 });
```

### E2E Test Issues

**Issue: Browser not found**
```bash
# Solution: Install Playwright browsers
npx playwright install
```

**Issue: Connection refused**
```bash
# Solution: Ensure services are running
npm run dev  # Frontend
python api/main.py  # Backend
```

**Issue: Tests flaky/timing issues**
```bash
# Solution: Add explicit waits
await page.waitForSelector('selector', { timeout: 5000 });
```

---

## Test Writing Guidelines

### Backend Test Guidelines

1. **Use descriptive test names**
   ```python
   # ✅ Good
   async def test_create_generation_returns_task_id(client, mock_openai):
       pass

   # ❌ Bad
   async def test_1(client):
       pass
   ```

2. **Arrange-Act-Assert pattern**
   ```python
   async def test_update_generation(client):
       # Arrange
       gen_id = await create_test_generation(client)
       update_data = {"keyword": "updated"}

       # Act
       response = await client.put(f"/api/generation/{gen_id}", json=update_data)

       # Assert
       assert response.status_code == 200
   ```

3. **Isolate tests**
   ```python
   # Use fixtures for isolated test data
   @pytest.fixture
   async def test_generation(client):
       # Create isolated test data
       ...
   ```

### Frontend Test Guidelines

1. **Test user interactions**
   ```typescript
   // ✅ Good
   fireEvent.click(screen.getByText('Submit'))

   // ❌ Bad
   component.props.onSubmit()
   ```

2. **Wait for async operations**
   ```typescript
   // ✅ Good
   await waitFor(() => {
     expect(screen.getByText('Success')).toBeVisible();
   });

   // ❌ Bad
   expect(screen.getByText('Success')).toBeVisible();
   ```

3. **Clean up after tests**
   ```typescript
   afterEach(() => {
     cleanup();
   });
   ```

### E2E Test Guidelines

1. **Use page objects pattern**
   ```typescript
   class DashboardPage {
     constructor(private page: Page) {}

     async navigateToGenerate() {
       await this.page.click('text=New Generation');
     }
   }
   ```

2. **Add retries for flaky tests**
   ```typescript
   test.configure({
     retries: process.env.CI ? 2 : 0,
   });
   ```

3. **Take screenshots on failure**
   ```typescript
   test.afterEach(async ({ page }, testInfo) => {
     if (testInfo.status === 'failed') {
       await page.screenshot({ path: `failure-${testInfo.title}.png` });
     }
   });
   ```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Maintain coverage** > 75%
3. **Test edge cases** and error conditions
4. **Document complex scenarios** with comments
5. **Update this guide** with new test patterns

---

**Happy Testing! 🧪**
