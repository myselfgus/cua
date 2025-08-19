## Project Engineering Playbook & Onboarding Checklist

This file drives automation and assistant actions. Keep it current. Remove explanatory comments once the stack is chosen and scaffolded.

---
### 0. Core Metadata (Fill Before Scaffolding)
- [ ] Chosen stack (ONE): `node-express-ts` | `react-vite` | `python-fastapi` | `.net-webapi`
- [ ] Project name:
- [ ] Business/domain goal (1 sentence):
- [ ] Primary deliverable (artifact / API / UI):
- [ ] Deployment target(s): (e.g. Azure App Service, Vercel, GCP Cloud Run, Docker Swarm)
- [ ] Runtime constraints (memory, latency, throughput):
- [ ] Security/compliance notes (PII? GDPR? SOC2?):

---
### 1. Delivery Phases & Gates
| Phase | Gate Criteria (tick all) | Status |
|-------|--------------------------|--------|
| 1. Stack Selection | Chosen stack recorded; README updated | [ ] |
| 2. Scaffold | Folder created; hello world runs locally | [ ] |
| 3. Tooling | Lint, format, test baseline added | [ ] |
| 4. Quality Gates | Build + Lint + Tests pass in one command | [ ] |
| 5. DX Enhancements | VS Code tasks + launch + devcontainer | [ ] |
| 6. Containerization | Dockerfile builds & runs locally | [ ] |
| 7. CI Bootstrap | Workflow runs build+lint+tests | [ ] |
| 8. Docs Finalization | README + this file cleaned | [ ] |

---
### 2. Stack Options (DO NOT scaffold all)
| Id | Stack | Dir | Baseline Runtime | Core Deps | Prod Start Command |
|----|-------|-----|------------------|-----------|--------------------|
| 1 | Node + TS Express API | `api/` | Node 20 LTS | express, zod, ts-node-dev (dev), typescript | node dist/index.js |
| 2 | React + Vite | `web/` | Node 20 LTS | react, react-dom, vite, typescript | vite preview |
| 3 | Python FastAPI | `python-api/` | Python 3.11 | fastapi, uvicorn[standard], pydantic | uvicorn app.main:app --host 0.0.0.0 --port 8000 |
| 4 | .NET 8 Web API | `dotnet-api/` | .NET SDK 8 | (template) | dotnet run --no-build |

Decision notes: (why this stack?)

---
### 3. Environment & Conventions
- Version control: Git (main + feature branches)
- Branch naming: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`, `docs/<scope>`
- Commit style: Conventional Commits (e.g. `feat(api): add health endpoint`)
- Code style:
  - Node/React: ESLint + Prettier
  - Python: Ruff + Black
  - .NET: dotnet format
- Testing frameworks (after choice):
  - Node: Vitest / Jest
  - React: Vitest + Testing Library
  - Python: pytest
  - .NET: xUnit
- Env vars naming: `APP_` prefix for app-level, `SECRET_` for sensitive values (not committed)

---
### 4. Actionable Checklist
#### A. Stack Selection
- [ ] Confirm stack (update Section 0 + README)
- [ ] Remove unused stack rows (optional)

#### B. Scaffolding (Assistant will run commands)
- [ ] Initialize project skeleton
- [ ] Add minimal hello world endpoint / page
- [ ] Generate lock file (npm/pnpm/yarn / pip / dotnet)
- [ ] Verify run command succeeds (PowerShell)

#### C. Tooling Layer
- [ ] Add linter & formatter config
- [ ] Add test framework + sample test
- [ ] Add `lint`, `format`, `test`, `build` scripts (or equivalents)
- [ ] Configure `.editorconfig`

#### D. Quality Gates
- [ ] Single command (e.g. `npm run ci` / `make ci`) runs build+lint+tests
- [ ] Pre-commit hook optional (Husky / pre-commit)

#### E. Developer Experience
- [ ] VS Code `tasks.json` (dev, test, format)
- [ ] VS Code `launch.json` (debug) (skip if trivial until needed)
- [ ] Dev Container (optional until remote/devcloud workflow)

#### F. Containerization
- [ ] Dockerfile created for chosen stack only
- [ ] `.dockerignore` tuned
- [ ] Local image builds & starts

#### G. CI (Optional until requested)
- [ ] Workflow: install deps, build, lint, test
- [ ] Cache strategy defined

#### H. Documentation Finalization
- [ ] Remove unused sections here
- [ ] Update README with full usage
- [ ] Add Architecture Overview (link or section)

---
### 5. Dev Container (Multi-Stack Base - Optional Pre-Selection)
If enabled before choosing stack, image contains broad toolset (heavier). Optimize later.

Featured tools: Node 20, Python 3.11, .NET 8 SDK, Git, Powershell.

Post-selection slimming tasks:
- Remove unused language toolchains
- Prune Docker image layers

---
### 6. Security & Secrets Handling (Initial Policy)
- No secrets committed.
- Use local `.env` (ignored) or VS Code secret storage.
- Rotate any demo API tokens every 30 days.

---
### 7. Observability (Future Placeholder)
- Logging baseline: console (structured JSON recommended) → later centralize.
- Metrics: add after production readiness decision.

---
### 8. Assistant Operating Notes
- Do NOT scaffold until stack chosen.
- Always run validation (build/lint/test) after edits that affect code.
- Keep diffs minimal; avoid unrelated reformatting.
- Use PowerShell-friendly scripts in docs.

---
### 9. Architectural Placeholders (Fill Once Known)
- High-level data flow:
- External integrations:
- Persistence:
- Caching strategy:
- Authentication model:

---
### 10. Cleanup Steps (Finalization)
- [ ] Remove all placeholder comments
- [ ] Collapse unused sections
- [ ] Tag initial stable release (v0.1.0)

---
### 11. Change Log (inline until RELEASES.md created)
- (pending)

---
### 12. Appendix: Quick Command Templates (Do NOT run until stack chosen)
Node Express (scaffold): `npm init -y; npm pkg set type="module"` then install deps.
React Vite: `npm create vite@latest web -- --template react-ts`
FastAPI: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install fastapi uvicorn`
.NET Web API: `dotnet new webapi -o dotnet-api`

---
End of operational document.
