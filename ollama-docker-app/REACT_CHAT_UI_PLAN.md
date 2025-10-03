# React Vite Chat UI Plan

## Goals & Scope
- Deliver a modern, responsive chat experience styled after ChatGPT / OpenWebUI.
- Integrate with the existing Ollama backend (default host `http://localhost:11434`).
- Support streaming assistant responses, conversation history, and lightweight settings management.
- Provide a maintainable codebase with testing, linting, and deployment guidance.

## Backend Context Snapshot
- `docker-compose.yml` launches the official `ollama/ollama` image, exposing port `11434`.
- `main.py` demonstrates Python-side streaming via `/api/chat` and fallback `/api/generate` calls.
- `quick-start.sh` ensures model `granite4:micro-h` is available and highlights expected environment variables (`OLLAMA_URL`, `OLLAMA_MODEL`).
- No HTTP proxy or REST facade currently exists; the UI will hit Ollama directly or through a thin proxy to address CORS and secrets.

## High-Level Architecture
| Layer | Tech | Key Responsibilities |
| --- | --- | --- |
| Frontend | Vite + React 18 + TypeScript | SPA shell, routing (if needed), component rendering, optimistic UX. |
| State | Zustand (for UI/session state) + React Query (API/cache) | Conversation list, active thread, settings, async mutations. |
| Styling | Tailwind CSS + CSS variables | Theme system (light/dark), responsive layout, utility-first styling. |
| Messaging | Fetch streaming via `ReadableStream` or Server-Sent Events | Live token streaming, incremental rendering, abort support. |
| Markdown | `react-markdown` + `rehype-highlight` | Rich message formatting, code blocks. |
| Persistence | LocalStorage (conversations, settings) | Offline-first caching, quick reloads. |
| Optional Proxy | Express or Vite dev proxy | Solve CORS, sanitize requests, centralize headers/tokens. |

## Phased Roadmap
1. **Project Bootstrap**
   - Scaffold with `npm create vite@latest my-chat --template react-ts`.
   - Add Tailwind, ESLint/Prettier, Husky (pre-commit), React Query, Zustand, and testing libs (Vitest, Testing Library).
   - Configure Vite proxy (`/ollama` → `http://localhost:11434`).
2. **Core Chat Flow**
   - Build layout (sidebar + chat panel) with responsive breakpoints.
   - Implement message composer with multi-line input, send button, keyboard shortcuts.
   - Integrate streaming fetch; render incremental assistant bubbles with typing indicator.
   - Persist conversation turns in Zustand + localStorage.
3. **Conversation Management**
   - Sidebar list with conversation titles, creation timestamps, delete/archive.
   - Allow renaming and duplication (like ChatGPT).
   - Implement "New chat" flow resetting composer + history.
4. **Advanced Controls**
   - Settings modal for model selection, temperature, system prompt, max tokens.
   - Display token counts, latency, backend health badge.
   - Add `/help`, `/reset`, `/model` command shortcuts mirroring CLI.
5. **Polish & QA**
   - Markdown rendering, code block copy, syntax highlighting.
  - Accessibility passes (focus traps, ARIA, color contrast).
   - Unit/integration tests, visual regression snapshots.
   - Dockerfile/compose adjustments to serve static build behind existing stack.

## Detailed Feature Breakdown
### Layout & Navigation
- Split view: collapsible conversation sidebar + main chat area.
- Header with app name, model selector, settings trigger, backend status indicator.
- Mobile-first design with sidebar drawer and persistent bottom composer.

### Chat Thread
- Message bubble component with roles: user, assistant, system, error.
- Streaming bubble uses incremental append with smooth scrolling.
- Action menu: copy text, regenerate (resend last user message), share/download.
- Markdown support, code fences with language auto-detect, callouts for `<thinking>` tags from Ollama.

### Composer & Controls
- Textarea with auto-resize, Shift+Enter newline, Enter to send.
- Attachments placeholder (future file uploads).
- Temperature / top-p quick sliders (optional advanced section).
- Token usage preview calculated from last prompt + system message.

### Conversation Sidebar
- List with truncated titles (first user prompt or custom name).
- Hover actions: rename, delete, favorite.
- Search/filter field for long histories.
- "Clear all chats" confirmation dialogue.

### Settings & Model Management
- Modal or drawer with tabs: General, Models, Advanced.
- General: theme (light/dark/system), font size, dense mode.
- Models: fetch `/api/tags` to list available models, allow selecting default.
- Advanced: system prompt editor, temperature/top-k, toggle thinking tag visibility.

### Notifications & Feedback
- Toasts for errors (network, validation) using headless library (`sonner` or `radix-toast`).
- Inline skeletons/spinners while loading conversation history.
- Connection health indicator updating based on `/api/chat` test ping.

## API Integration Strategy
- Create `src/lib/api/ollama.ts` for typed wrappers (`chat`, `generate`, `listModels`).
- Streaming implemented via `fetch('/ollama/api/chat', { body, signal })` and manual reader loop.
- Parse JSON chunks (`chunk.done`, `chunk.message.content`) similar to `main.py` to extract `<think>`/`<response>` segments.
- Handle abort via `AbortController` on cancel button in UI.
- Use React Query mutations for sends; update Zustand store on `onSuccess`.
- Retry logic for recoverable HTTP 5xx with exponential backoff (configurable).

## State & Persistence
- Zustand slices: `sessions` (list metadata), `currentSession`, `settings`, `ui` (panels, theme).
- React Query caches individual conversation fetches; fallback to localStorage rehydration on load.
- Session schema:
  ```ts
  type Message = { id: string; role: 'user' | 'assistant' | 'system' | 'error'; content: string; createdAt: number; tokens?: number; meta?: Record<string, unknown> };
  type Session = { id: string; title: string; model: string; systemPrompt?: string; messages: Message[]; createdAt: number; updatedAt: number; archived?: boolean };
  ```

## Styling & UX Guidelines
- Tailwind config with custom color palette inspired by OpenWebUI (muted dark background, accent green).
- Use CSS variables to enable theme switching.
- Apply Radix UI primitives (Dialog, Dropdown, Toggle) for accessibility.
- Support reduced-motion media query; animate streaming caret only when allowed.
- Ensure high contrast ratio (WCAG AA) and keyboard navigable controls.

## Testing & Quality Gates
- **Unit tests**: component logic (composer, message parser, store slices) via Vitest + Testing Library.
- **Integration tests**: mock streaming API with MSW to validate incremental rendering.
- **Visual regression**: optional Playwright or Storybook with Chromatic.
- **Lint/format**: ESLint (typescript-eslint, jsx-a11y), Prettier, Tailwind class sorting.
- Continuous integration workflow: pnpm install, lint, test, build.

## Deployment & Ops
- Production build served with `npm run build` → `dist/`.
- Bundle static assets via lightweight Node/Express server or Vite preview inside Docker.
- Extend `docker-compose.yml` with a `ui` service:
  ```yaml
  ui:
    build: ./ui
    ports:
      - "5173:4173" # dev vs prod port
    environment:
      - VITE_OLLAMA_URL=http://ollama:11434
    depends_on:
      - ollama
  ```
- Configure Nginx reverse proxy for TLS if exposed publicly.
- Document .env usage (`VITE_OLLAMA_URL`, `VITE_DEFAULT_MODEL`).

## Risks & Mitigations
- **CORS restrictions**: use Vite dev proxy and ship prod UI behind same origin reverse proxy.
- **Streaming parsing differences**: mirror logic from `main.py`, add robust error handling for malformed chunks.
- **Large histories**: paginate or chunk messages, lazy-load older turns.
- **Browser resource usage**: throttle rendering, virtualize long transcripts (e.g., `react-virtuoso`).
- **Model availability**: UI should surface when requested model missing and offer to pull/install (guide user).

## Nice-to-Have Enhancements
- Chat commands (`/reset`, `/model`, `/system`) recognized in composer with inline helpers.
- Prompt library drawer with reusable templates.
- Shared links exporting chat as Markdown/JSON.
- System prompt diff viewer to compare sessions.
- Multi-user support with simple auth and server-side persistence (future Node/Express service).

## Immediate Next Steps
1. Initialize Vite React-TS project under `ollama-docker-app/ui/`.
2. Add Tailwind, React Query, Zustand, and baseline layout components.
3. Implement streaming chat request + renderer using local proxy.
4. Iterate on sidebar + settings UI, wire to backend endpoints.
5. Establish CI workflow and document developer onboarding in `README.md`.
