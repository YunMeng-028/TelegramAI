# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Python Development
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run backend server
poetry run python backend/main.py

# Run tests
poetry run pytest
poetry run pytest --cov=telegram_ai  # with coverage
poetry run pytest tests/test_claude_code_integration.py -v  # specific test

# Code quality
poetry run black backend/
poetry run ruff check backend/
poetry run mypy backend/
poetry run bandit -r backend/
```

### Frontend Development
```bash
# Install dependencies
npm install

# Run development server
npm run electron:dev

# Run tests
npm run test
npm run test:ui  # UI mode
npm run test:coverage

# Code quality
npm run lint
npm run format
npm run type-check

# Build for production
npm run dist:win  # Windows
npm run dist:mac  # macOS
npm run dist:linux  # Linux
```

### Git Workflow
```bash
# Use commitizen for standardized commits
npm run commit
```

## High-Level Architecture

### System Overview
TelegramAI is an Electron + Vue desktop application with a Python backend that provides AI-powered Telegram automation. The architecture uses:
- **Electron + Vue 3** for the desktop UI
- **Python FastAPI** backend for core logic
- **ZeroMQ** for IPC between frontend and backend
- **SQLite with WAL mode** for local data storage
- **Claude Code SDK** integration for enhanced AI capabilities

### Core Architecture Components

#### Frontend Architecture
- **Electron Main Process** (`frontend/electron/main.js`): Manages application lifecycle and IPC
- **Vue 3 Application** (`frontend/src/`): Reactive UI with Pinia state management
- **IPC Bridge** (`frontend/src/services/ipc/`): Handles communication with Python backend
- **Claude Code Integration** (`frontend/src/services/claude-code/`): TypeScript SDK wrapper

#### Backend Architecture
- **Core Service** (`backend/telegram_ai/`): Python service managing Telegram accounts
- **AI Generator** (`backend/telegram_ai/ai/generator.py`): Enhanced with Claude Code for intelligent responses
- **Telethon Integration**: MTProto client for Telegram API
- **Permission System** (`backend/telegram_ai/ai/claude_code/permissions.py`): Fine-grained tool access control

#### Key Design Patterns
1. **Service Layer Pattern**: All business logic encapsulated in service classes
2. **Repository Pattern**: Data access abstracted through repository interfaces
3. **Observer Pattern**: Event-driven communication between components
4. **Strategy Pattern**: Different AI generation strategies based on context

### Claude Code Integration

The project deeply integrates Claude Code for enhanced AI capabilities:

1. **SDK Wrappers**: Both TypeScript and Python implementations
2. **Tool Permission Management**: Granular control over available Claude tools
3. **Performance Monitoring**: Tracks Claude API usage and response times
4. **Error Recovery**: Automatic retry and fallback mechanisms

Key integration points:
- `backend/telegram_ai/ai/generator.py`: AI response generation
- `frontend/src/services/claude-code/`: Frontend SDK and IPC
- `backend/telegram_ai/ai/claude_code/`: Backend implementation

### Data Flow
1. User interacts with Vue UI
2. Vue components dispatch actions to Pinia stores
3. Stores communicate with backend via IPC bridge
4. Python backend processes requests, potentially using Claude Code
5. Responses flow back through the same path

### Security Considerations
- API keys stored in encrypted local storage
- Tool permissions use whitelist approach
- Dangerous operations (Bash, Write, Edit) disabled by default
- All Telegram sessions encrypted with AES-256

### Performance Optimizations
- SQLite WAL mode for concurrent operations
- Message queue system for rate limiting
- Intelligent caching for AI responses
- Lazy loading and code splitting in frontend

## Critical Files to Understand

When making changes, these files form the core of the system:
- `backend/telegram_ai/ai/generator.py`: AI generation logic
- `frontend/src/services/claude-code/index.ts`: Claude Code service
- `backend/telegram_ai/ai/claude_code/sdk.py`: Python Claude SDK
- `frontend/electron/claude-ipc-handler.js`: IPC handler for Claude
- `backend/telegram_ai/ai/claude_code/permissions.py`: Permission system

## Environment Setup

Required environment variables in `.env`:
```
OPENAI_API_KEY=your_key
CLAUDE_CODE_API_KEY=your_key
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
DATABASE_PATH=data/telegram_ai.db
IPC_PORT=5555
LOG_LEVEL=INFO
```

## Testing Strategy

The project uses comprehensive testing:
- Unit tests for individual components
- Integration tests for Claude Code features (`tests/test_claude_code_integration.py`)
- E2E tests for critical user flows
- Performance benchmarks for AI operations

Run specific test categories:
```bash
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest tests/test_claude_code_integration.py
```