# Setup Guide for Testing

Complete setup instructions for running tests in the AI Writing Automation project.

## Table of Contents

- [Quick Start](#quick-start)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [E2E Testing Setup](#e2e-testing-setup)
- [Environment Configuration](#environment-configuration)
- [IDE Configuration](#ide-configuration)
- [Verification](#verification)

---

## Quick Start

Get everything running in 5 minutes:

```bash
# 1. Clone and navigate
git clone https://github.com/tndg16-bot/ai-writing-automation.git
cd ai-writing-automation

# 2. Backend setup
cd api
pip install -e ".[dev]"

# 3. Frontend setup
cd ../frontend
npm install

# 4. Run tests
cd ../api && pytest tests/ -v
cd ../frontend && npm test
```

---

## Backend Setup

### 1. Python Environment

```bash
# Check Python version (requires 3.11+)
python --version

# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
cd api

# Install with dev dependencies
pip install -e ".[dev]"

# Or manually install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx moto
```

### 3. Environment Variables

```bash
# Copy example .env file
cd ..
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required variables:
```bash
# OpenAI API (required for some tests)
OPENAI_API_KEY=sk-your-key-here

# Database (use test database for testing)
DATABASE_URL=sqlite:///./test.db
```

### 4. Verify Backend Setup

```bash
cd api

# Run pytest to verify
pytest tests/ --collect-only

# Run a quick smoke test
pytest tests/test_api.py::test_health_check -v
```

---

## Frontend Setup

### 1. Node.js Environment

```bash
# Check Node.js version (requires 18+)
node --version
npm --version

# If not installed, download from https://nodejs.org/
```

### 2. Install Dependencies

```bash
cd frontend

# Install all dependencies
npm install

# Install testing dependencies
npm install --save-dev \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jest \
  jest-environment-jsdom \
  @types/jest
```

### 3. Configure Jest

The following files should exist:

```
frontend/
├── jest.config.ts          # Jest configuration
├── jest.setup.js          # Test setup file
├── __tests__/             # Test files
│   ├── page.test.tsx
│   ├── generate-page.test.tsx
│   └── progress-page.test.tsx
└── package.json           # Updated with test scripts
```

### 4. Update package.json

Ensure these scripts are in `frontend/package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "@testing-library/react": "^14",
    "@testing-library/jest-dom": "^6",
    "@testing-library/user-event": "^14",
    "jest": "^29",
    "jest-environment-jsdom": "^29",
    "@types/jest": "^29"
  }
}
```

### 5. Verify Frontend Setup

```bash
cd frontend

# Run Jest to verify
npm test -- --passWithNoTests

# Run tests
npm test
```

---

## E2E Testing Setup

### 1. Install Playwright

```bash
cd frontend

# Install Playwright
npm install --save-dev @playwright/test

# Install browser binaries
npx playwright install

# Install browser binaries for CI (optional)
npx playwright install --with-deps chromium firefox webkit
```

### 2. Configure Playwright

Create `playwright.config.ts` in project root:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'cd frontend && npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

### 3. Create E2E Test Directory

```bash
# Create e2e directory
mkdir -p e2e

# Create test file
touch e2e/complete-flow.spec.ts
```

### 4. Verify E2E Setup

```bash
# Run Playwright tests (will fail if no API running)
npx playwright test

# Run in UI mode (recommended for development)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed
```

---

## Environment Configuration

### Development Environment

Create `.env.development`:

```bash
# API
OPENAI_API_KEY=sk-dev-key
DATABASE_URL=sqlite:///./dev.db

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Debug
DEBUG=true
LOG_LEVEL=debug
```

### Test Environment

Create `.env.test`:

```bash
# API
OPENAI_API_KEY=sk-test-key
DATABASE_URL=sqlite:///./test.db

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Test settings
MOCK_OPENAI=true
TEST_TIMEOUT=30000
```

### CI Environment

Configure in GitHub Actions (`.github/workflows/tests.yml`):

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  DATABASE_URL: sqlite:///./ci.db
  NEXT_PUBLIC_API_URL: http://localhost:8000
```

---

## IDE Configuration

### VS Code

Install these extensions:

1. **Python**
   - Python (Microsoft)
   - Python Test Explorer (LittleFoxTeam)

2. **JavaScript/TypeScript**
   - ESLint
   - Prettier
   - Jest Runner (Firsttris)

3. **Testing**
   - Playwright Test for VSCode

Configure `.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "jest.autoRun": "watch",
  "jest.pathToJest": "node_modules/.bin/jest",
  "playwright.reuseBrowser": true
}
```

### PyCharm

Configure pytest:

1. Open Settings → Tools → Python Integrated Tools
2. Set Default test runner to **pytest**
3. Click **Apply**

Configure Jest:

1. Open Settings → Languages & Frameworks → JavaScript → Libraries
2. Add Jest detection
3. Set Jest package directory to `frontend/node_modules/jest`

### VS Code Code Lenses

Enable for pytest:

```json
{
  "python.testing.pytestArgs": [
    "--markers",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')"
  ],
  "python.testing.codeLensEnabled": true
}
```

---

## Verification

### Backend Verification

```bash
cd api

# Run all backend tests
pytest tests/ -v --tb=short

# Expected output:
# tests/test_api.py::test_health_check PASSED
# tests/test_api.py::test_create_generation PASSED
# ...
# ================== 85 passed in 10.23s ==================

# Check coverage
pytest tests/ --cov=. --cov-report=term-missing

# Expected: > 75% coverage
```

### Frontend Verification

```bash
cd frontend

# Run all frontend tests
npm test -- --watchAll=false

# Expected output:
# PASS  __tests__/page.test.tsx
# PASS  __tests__/generate-page.test.tsx
# PASS  __tests__/progress-page.test.tsx
# Test Suites: 3 passed, 3 total
# Tests:       30 passed, 30 total

# Check coverage
npm test -- --coverage

# Expected: > 75% coverage
```

### E2E Verification

```bash
# Start services in separate terminals
# Terminal 1:
cd api && python main.py

# Terminal 2:
cd frontend && npm run dev

# Terminal 3:
npx playwright test

# Expected output:
# Running 20 tests using 1 worker
# ✓  complete-flow.spec.ts:5:3 › complete-generation-flow (12s)
# ...
# 20 passed (2m)
```

### Full Verification Script

Create `scripts/verify-setup.sh`:

```bash
#!/bin/bash

echo "🔍 Verifying backend setup..."
cd api && pytest tests/ --collect-only -q
if [ $? -eq 0 ]; then
    echo "✅ Backend setup verified"
else
    echo "❌ Backend setup failed"
    exit 1
fi

echo "🔍 Verifying frontend setup..."
cd ../frontend && npm test -- --passWithNoTests
if [ $? -eq 0 ]; then
    echo "✅ Frontend setup verified"
else
    echo "❌ Frontend setup failed"
    exit 1
fi

echo "🔍 Verifying Playwright setup..."
npx playwright --version
if [ $? -eq 0 ]; then
    echo "✅ Playwright setup verified"
else
    echo "❌ Playwright setup failed"
    exit 1
fi

echo ""
echo "🎉 All setups verified successfully!"
```

Run verification:

```bash
chmod +x scripts/verify-setup.sh
./scripts/verify-setup.sh
```

---

## Common Setup Issues

### Issue: Python version too old

```bash
# Solution: Use pyenv or conda
pyenv install 3.11.7
pyenv local 3.11.7
```

### Issue: Node.js not found

```bash
# Solution: Use nvm
nvm install 18
nvm use 18
```

### Issue: Playwright browsers missing

```bash
# Solution: Reinstall browsers
npx playwright install --force
```

### Issue: Jest can't find modules

```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Pytest can't find tests

```bash
# Solution: Check pytest.ini or pyproject.toml
# Ensure tests directory is in configuration
```

---

## Next Steps

After setup is complete:

1. **Read the Testing Guide**: [TESTING.md](TESTING.md)
2. **Run smoke tests**: Verify basic functionality
3. **Write your first test**: Follow examples in test files
4. **Set up CI/CD**: Configure automated testing
5. **Contribute tests**: Add tests for new features

---

## Support

If you encounter setup issues:

1. Check the [Troubleshooting](TESTING.md#troubleshooting) section
2. Review existing test files for examples
3. Open an issue on GitHub with setup details

---

**Happy Testing! 🚀**
