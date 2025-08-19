# Project CUA (Computer User Assistance)

Rich conversational + execution agent platform: modified LobeChat frontend (React/Next.js) + FastAgent backend (FastAPI) + MCP Gateway + E2B sandbox integration.

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Frontend | LobeChat (React/Next.js) | Custom hooks: artifacts, CUA, STT/TTS |
| Backend | FastAgent (FastAPI) | Orquestração + tool routing |
| Tools | MCP Servers (GitHub, Playwright, SSH, Qdrant, Neo4j, E2B) | Via MCP Gateway |
| AI | Cloudflare AI Gateway + OpenAI | Routing, caching, STT/TTS |
| Cache | Redis | Sessões + artefatos |
| Data | Qdrant (vetores), Neo4j (grafo) | Context injection |

## Repository Layout (planned)

```text
frontend/
backend/
infra/
	docker-mcp-gateway/
	cloudflare-tunnel/
docs/
```

## Environment Variables (core)

```dotenv
APP_API_URL=...
APP_AI_GATEWAY_URL=...
APP_MCP_GATEWAY_URL=...
APP_QDRANT_URL=...
APP_NEO4J_URL=...
APP_REDIS_URL=...
APP_E2B_ENDPOINT=...
SECRET_OPENAI_API_KEY=...
SECRET_CF_AI_TOKEN=...
```

## Planned Commands

Will be added after scaffold:

- Frontend dev: `npm run dev` (frontend)
- Backend dev: `uvicorn app.main:app --reload`
- Unified CI: `pwsh ./scripts/ci.ps1`

## Roadmap (Initial)

1. Scaffold frontend + backend minimal hello world
2. Add artifact viewer skeleton (Monaco + XTerm + media panel)
3. Implement FastAgent intent endpoint + tool executor abstraction
4. Integrate Redis cache manager
5. Add Qdrant + Neo4j client wrappers
6. Add MCP gateway config + connection negotiator
7. Add CI & coverage gates
8. Architecture doc finalize

## Contributing

Follow Conventional Commits. Small focused PRs.

## License

TBD

See `.github/copilot-instructions.md` for detailed playbook.
