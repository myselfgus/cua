# **Project CUA Playbook**

Este documento serve como guia único para o desenvolvimento do projeto, cobrindo desde a setup inicial até as convenções de codificação para o assistente de IA. Mantenha-o conciso e atualizado.

## 🎯 **Core Metadata**
- **Project name:** Project CUA (Computer User Assistance)
- **Business goal:** Construir um sistema de agente com interface conversacional rica e capacidade de execução (CUA) via E2B.
- **Primary deliverable:** Interface baseada no LobeChat modificado com abas para artefatos (terminal, editor, mídia, sandbox) e backend FastAgent para orquestração.
- **Deployment target:** GCP (Frontend/API) + ISADP (MCPs com GPU) via Cloudflare Tunnel.
- **Runtime constraints:** Latência baixa (<200ms para UI), suporte a streaming WebRTC.
- **Security notes:** Dados de sessão em Redis, segredos via GCP Secret Manager, sem PII crítico.

## 🔧 **Stack Selecionada**
- **Frontend:** LobeChat modificado (React/Next.js) com hooks customizados.
- **Backend:** FastAgent (Python/FastAPI) para orquestração.
- **Protocolo:** MCP para ferramentas (GitHub, Playwright, E2B).
- **Cache:** Redis via API (não MCP) para sessões e artefatos.
- **IA:** Cloudflare AI Gateway + OpenAI (STT/TTS).
- **Ferramentas:** Docker MCP Gateway para gerenciar servidores MCP.

**Decision notes:** Escolhido por suporte nativo a MCP, performance comprovada com E2B, e flexibilidade para client rico com visualização de artefatos.

## 📋 **Delivery Phases & Gates**
| Phase | Gate Criteria | Status |
|-------|---------------|--------|
| 1. Stack Selection | Stack confirmada e documentada | [x] |
| 2. Scaffold | Hello world rodando localmente | [ ] |
| 3. Tooling | Lint, format, test configurados | [ ] |
| 4. Quality Gates | Build + Lint + Tests passam em um comando | [ ] |
| 5. DX Enhancements | VS Code tasks e devcontainer opcional | [ ] |
| 6. Containerization | Dockerfile para backend e frontend | [ ] |
| 7. CI Bootstrap | GitHub Actions para build e test | [ ] |
| 8. Docs Finalization | Este documento e README atualizados | [ ] |

## 🛠️ **Environment & Conventions**
- **Version control:** Git com branches `feat/`, `fix/`, `chore/`, `docs/`.
- **Commit style:** Conventional Commits (ex: `feat(api): add health endpoint`).
- **Code style:**
  - Frontend: ESLint + Prettier
  - Backend: Ruff + Black
- **Testing:**
  - Frontend: Vitest + Testing Library
  - Backend: pytest
- **Env vars:** Use `APP_` para app-level e `SECRET_` para sensíveis (via `.env` ou GCP Secret Manager).

### 🔐 Variáveis de Ambiente (Definir antes do scaffold real)
Obrigatórias (frontend/backend):
- `APP_API_URL` (endpoint FastAgent)
- `APP_AI_GATEWAY_URL`
- `APP_MCP_GATEWAY_URL`
- `APP_QDRANT_URL`
- `APP_NEO4J_URL`
- `APP_REDIS_URL`
- `APP_E2B_ENDPOINT`
- `SECRET_OPENAI_API_KEY`
- `SECRET_CF_AI_TOKEN` (se aplicável)

Boas práticas:
- Nunca hardcode URLs; sempre via env.
- Use arquivos `.env.local` ignorados pelo git.

## 🚨 **Coding Guidelines for AI (Regras Estritas)**
- **Nenhum localhost/mock:** Todos os endpoints usam variáveis de ambiente (ex: `process.env.API_URL` ou `os.getenv('API_URL')`).
- **Frontend (LobeChat):** Sempre use hooks customizados do projeto (`useArtifacts()`, `useCUA()`) em vez de implementar lógica nova diretamente.
- **Backend (FastAgent):**
  - Todas as chamadas a ferramentas passam pelo `ToolExecutor`.
  - Todo acesso a dados usa `CacheManager` (padrão cache-aside com Redis).
- **MCP:** Priorize usar servidores MCP existentes (Docker Toolkit) em vez de criar novos.
- **Arquitetura:** Client Rico. Frontend comunica-se DIRETAMENTE com serviços especializados (Qdrant, Neo4j, AI Gateway) para baixa latência.
- **Artefatos:** A interface deve ter aba unificada para código (Monaco), terminal (XTerm), mídia (imagem/vídeo) e sandbox (iframe/E2B).
- **Estado:** Gerencie estado de artefatos/aba ativa via Zustand (frontend) e Redis (backend).

## 📁 **Estrutura de Pastas**
```
/project-cua
├── frontend/                 # LobeChat modificado
│   ├── src/hooks/           # useArtifacts, useCUA, useSTT
│   ├── src/components/ArtifactViewer/ # Componente unificado
│   └── src/utils/cache/     # Cliente Redis para frontend
├── backend/                 # FastAgent
│   ├── app/core/tool_executor.py
│   ├── app/core/cache_manager.py
│   └── app/models/artifacts.py
├── infra/
│   ├── docker-mcp-gateway/  # Configuração do MCP Gateway
│   └── cloudflare-tunnel/   # Config do túnel
└── docs/
    ├── README.md
    └── ARCHITECTURE.md      # Visão técnica detalhada
```

## ✅ **Actionable Checklist**
### A. Stack Selection
- [ ] Confirmar stack (atualizar esta seção e README)
- [ ] Remover opções não utilizadas

### B. Scaffolding
- [ ] Inicializar frontend e backend
- [ ] Adicionar endpoint hello world em cada
- [ ] Gerar lock files (npm/pip)
- [ ] Verificar se comandos de run funcionam

### C. Tooling Layer
- [ ] Adicionar linter e formatter para frontend e backend
- [ ] Adicionar testes de exemplo
- [ ] Adicionar scripts `lint`, `format`, `test`, `build`
- [ ] Configurar `.editorconfig`

### D. Quality Gates
- [ ] Script unificado (`pwsh ./scripts/ci.ps1`) executa build+lint+tests
- [ ] Cobertura mínima backend 70% (pytest) / frontend smoke + key components
- [ ] Configurar pre-commit hooks (opcional)

### E. Developer Experience
- [ ] Adicionar VS Code `tasks.json` para dev e test
- [ ] Adicionar VS Code `launch.json` para debug
- [ ] Configurar devcontainer (opcional)

### F. Containerization
- [ ] Criar Dockerfile para frontend e backend
- [ ] Ajustar `.dockerignore`
- [ ] Testar build e run local das imagens

### G. CI (GitHub Actions)
- [ ] Workflow para instalar deps, build, lint, test
- [ ] Cache: node (actions/setup-node com cache=pnpm|npm), pip wheels, pytest cache

### H. Documentation
- [ ] Atualizar README com instruções completas
- [ ] Adicionar ARCHITECTURE.md com diagramas
- [ ] Remover seções não usadas deste documento

## 🔒 **Security & Secrets Handling**
- **Nunca comitar segredos:** Use GCP Secret Manager ou `.env` (no `.gitignore`).
- **Redis:** Configurar autenticação e TLS para conexões.

## 📊 **Observability (Future Placeholder)**
- Logging: Estruturado em JSON para facilidade de parsing.
- Metrics: Adicionar Prometheus/Grafana após deploy inicial.

## 💡 **Assistant Operating Notes**
- **Sempre pergunte** se deve estender um hook existente ou criar novo.
- **Verifique** se já existe um servidor MCP antes de criar um.
- **Prefira** funções pequenas e testáveis em vez de monólitos.
- **Use** PowerShell-friendly scripts na documentação.

## 🧹 **Cleanup Steps**
- [ ] Remover comentários placeholder deste documento
- [ ] Colapsar seções não usadas
- [ ] Tag inicial v0.1.0

---
### 📌 Versioning Policy
- SemVer: `MAJOR.MINOR.PATCH`
- Primeira tag: `v0.1.0` após completar Fases 1–4.
- Patch: correções sem quebrar API
- Minor: novas features backward compatible
- Major: breaking changes documentados

**Change Log:**
- (2025-08-19) Documento criado com base na fusão do Playbook e Instructions.

---

Este documento é vivo. Atualize-o conforme as decisões evoluírem. Para detalhes técnicos profundos, consulte `ARCHITECTURE.md`.