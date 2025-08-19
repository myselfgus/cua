# Referenced Repositories & Integration Examples

This document provides detailed information about the key repositories and technologies that Project CUA integrates with, along with practical examples and integration patterns.

## 🏗️ Core Platform Components

### 🤖 LobeChat - Modern AI Chat Interface

**Repository:** [lobehub/lobe-chat](https://github.com/lobehub/lobe-chat)

**What it provides:**
- Modern React-based chat interface
- Plugin architecture for extensibility
- Multi-model AI provider support
- Rich message formatting
- File upload and media handling

**Our Integration:**
```typescript
// Extended LobeChat with artifact capabilities
import { LobeChat } from '@lobehub/ui';
import { ArtifactViewer } from '@/components/ArtifactViewer';

export const CUAChat = () => {
  const { messages, sendMessage } = useLobeChat();
  const { artifacts, addArtifact } = useArtifacts();

  const handleMessage = async (content: string) => {
    const response = await sendMessage(content);
    
    // Extract artifacts from response
    if (response.artifacts) {
      response.artifacts.forEach(addArtifact);
    }
  };

  return (
    <div className="flex h-full">
      <LobeChat 
        messages={messages}
        onSendMessage={handleMessage}
        plugins={[
          ArtifactPlugin,
          TerminalPlugin,
          CodeEditorPlugin
        ]}
      />
      <ArtifactViewer artifacts={artifacts} />
    </div>
  );
};
```

**Key Features We Extend:**
- Custom artifact rendering
- Integration with MCP tools
- Real-time collaboration
- Voice input/output
- Multi-tab artifact management

---

### ⚡ FastAgent - High-Performance Agent Framework

**Repository:** [agentic-ai/fast-agent](https://github.com/agentic-ai/fast-agent)

**What it provides:**
- High-performance agent orchestration
- Tool execution framework
- Async processing pipeline
- Multi-model coordination

**Our Integration:**
```python
# FastAgent integration for CUA
from fast_agent import Agent, Tool, Pipeline
from app.core.tool_executor import CUAToolExecutor
from app.core.intent_router import IntentRouter

class CUAAgent(Agent):
    def __init__(self):
        super().__init__()
        self.tool_executor = CUAToolExecutor()
        self.intent_router = IntentRouter()
        
        # Register MCP tools
        self.register_tools([
            GitHubTool(),
            PlaywrightTool(),
            E2BSandboxTool(),
            QdrantTool(),
            Neo4jTool()
        ])
    
    async def process_intent(self, intent: UserIntent) -> AgentResponse:
        # Route intent to appropriate handler
        handler = await self.intent_router.route(intent)
        
        # Execute with tool coordination
        result = await handler.execute(
            tools=self.tools,
            context=intent.context
        )
        
        return self.format_response(result)

# Pipeline configuration
pipeline = Pipeline([
    ContextEnrichmentStage(),
    IntentClassificationStage(),
    ToolSelectionStage(),
    ExecutionStage(),
    ArtifactGenerationStage(),
    ResponseFormattingStage()
])
```

**Key Features We Leverage:**
- Multi-step planning
- Tool coordination
- Error handling and retries
- Performance monitoring
- Streaming responses

---

## 🔌 MCP (Model Context Protocol) Ecosystem

### 📝 GitHub MCP Server

**Repository:** [github/github-mcp-server](https://github.com/github/github-mcp-server)

**Integration Example:**
```python
# GitHub MCP integration
from mcp_sdk import MCPClient

class GitHubMCPTool:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
    
    async def search_repositories(self, query: str, language: str = None) -> List[Repository]:
        """Search GitHub repositories"""
        params = {"query": query}
        if language:
            params["language"] = language
            
        result = await self.client.call_tool(
            "github.search_repositories",
            params
        )
        
        return [Repository.from_dict(repo) for repo in result.data]
    
    async def create_issue(self, repo: str, title: str, body: str) -> Issue:
        """Create a new GitHub issue"""
        result = await self.client.call_tool(
            "github.create_issue",
            {
                "repository": repo,
                "title": title,
                "body": body
            }
        )
        
        return Issue.from_dict(result.data)
```

**Available Capabilities:**
- Repository search and analysis
- Issue management
- Pull request operations
- Code review automation
- Release management

### 🌐 Playwright MCP Server

**Repository:** [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)

**Integration Example:**
```python
# Playwright MCP integration
class PlaywrightMCPTool:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
    
    async def navigate_and_screenshot(self, url: str) -> Artifact:
        """Navigate to URL and take screenshot"""
        # Navigate
        await self.client.call_tool("playwright.navigate", {"url": url})
        
        # Take screenshot
        result = await self.client.call_tool(
            "playwright.screenshot",
            {"full_page": True}
        )
        
        return ImageArtifact(
            content=result.data["image"],
            metadata={
                "url": url,
                "timestamp": datetime.utcnow(),
                "dimensions": result.data["dimensions"]
            }
        )
    
    async def extract_content(self, selector: str) -> str:
        """Extract text content from page"""
        result = await self.client.call_tool(
            "playwright.extract_text",
            {"selector": selector}
        )
        
        return result.data["text"]
```

**Available Capabilities:**
- Web navigation and interaction
- Form filling and submission
- Content extraction
- Screenshot generation
- Performance monitoring

### 🕸️ Neo4j MCP Server

**Repository:** [neo4j-labs/mcp-server-neo4j](https://github.com/neo4j-labs/mcp-server-neo4j)

**Integration Example:**
```python
# Neo4j MCP integration
class Neo4jMCPTool:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
    
    async def find_related_concepts(self, concept: str, depth: int = 2) -> List[dict]:
        """Find concepts related to the given concept"""
        cypher_query = """
        MATCH (c:Concept {name: $concept})-[r*1..""" + str(depth) + """]->(related:Concept)
        RETURN related.name as name, type(r) as relationship, length(r) as distance
        ORDER BY distance, related.name
        LIMIT 20
        """
        
        result = await self.client.call_tool(
            "neo4j.cypher_query",
            {
                "query": cypher_query,
                "parameters": {"concept": concept}
            }
        )
        
        return result.data["results"]
    
    async def create_knowledge_path(self, start: str, end: str) -> List[dict]:
        """Find shortest knowledge path between concepts"""
        cypher_query = """
        MATCH path = shortestPath((a:Concept {name: $start})-[*]->(b:Concept {name: $end}))
        RETURN [n in nodes(path) | n.name] as path,
               [r in relationships(path) | type(r)] as relationships
        """
        
        result = await self.client.call_tool(
            "neo4j.cypher_query",
            {
                "query": cypher_query,
                "parameters": {"start": start, "end": end}
            }
        )
        
        return result.data["results"]
```

### 🔍 Qdrant MCP Server

**Repository:** [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant)

**Integration Example:**
```python
# Qdrant MCP integration
class QdrantMCPTool:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
    
    async def semantic_search(self, query: str, collection: str = "text_embeddings") -> List[dict]:
        """Perform semantic search using vector similarity"""
        # Generate embedding for query
        embedding = await self.generate_embedding(query)
        
        result = await self.client.call_tool(
            "qdrant.search",
            {
                "collection_name": collection,
                "query_vector": embedding,
                "limit": 10,
                "with_payload": True
            }
        )
        
        return result.data["results"]
    
    async def store_document(self, content: str, metadata: dict) -> str:
        """Store document with vector embedding"""
        embedding = await self.generate_embedding(content)
        
        result = await self.client.call_tool(
            "qdrant.upsert",
            {
                "collection_name": "text_embeddings",
                "points": [{
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {
                        "content": content,
                        **metadata
                    }
                }]
            }
        )
        
        return result.data["operation_id"]
```

---

## 📦 E2B - Secure Code Execution

**Repository:** [e2b-dev/e2b](https://github.com/e2b-dev/e2b)

**What it provides:**
- Secure sandboxed environments
- Code execution isolation
- GPU access for AI workloads
- File system virtualization

**Our Integration:**
```python
# E2B integration for CUA
from e2b import Sandbox

class E2BSandboxTool:
    def __init__(self):
        self.active_sandboxes = {}
    
    async def create_sandbox(self, user_id: str, template: str = "base") -> str:
        """Create a new sandbox environment"""
        sandbox = Sandbox(template=template)
        await sandbox.start()
        
        sandbox_id = str(uuid.uuid4())
        self.active_sandboxes[sandbox_id] = {
            "sandbox": sandbox,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        
        return sandbox_id
    
    async def execute_code(self, sandbox_id: str, code: str, language: str = "python") -> CodeExecutionResult:
        """Execute code in sandbox environment"""
        if sandbox_id not in self.active_sandboxes:
            raise ValueError("Sandbox not found")
        
        sandbox = self.active_sandboxes[sandbox_id]["sandbox"]
        
        try:
            if language == "python":
                result = await sandbox.run_python(code)
            elif language == "bash":
                result = await sandbox.run_bash(code)
            else:
                raise ValueError(f"Unsupported language: {language}")
            
            return CodeExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.exit_code,
                execution_time=result.execution_time
            )
            
        except Exception as e:
            return CodeExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=1,
                execution_time=0
            )
    
    async def install_package(self, sandbox_id: str, package: str, manager: str = "pip") -> bool:
        """Install package in sandbox"""
        sandbox = self.active_sandboxes[sandbox_id]["sandbox"]
        
        if manager == "pip":
            result = await sandbox.run_bash(f"pip install {package}")
        elif manager == "npm":
            result = await sandbox.run_bash(f"npm install {package}")
        else:
            raise ValueError(f"Unsupported package manager: {manager}")
        
        return result.exit_code == 0
```

**Key Features:**
- Multiple language support
- Package installation
- File system access
- Network isolation
- Resource limits

---

## 🔧 MCP Gateway (Docker)

**Repository:** [docker/mcp-gateway](https://github.com/docker/mcp-gateway)

**Configuration Example:**
```yaml
# MCP Gateway configuration
version: "1.0"
gateway:
  port: 8080
  health_check_interval: 30s
  
servers:
  github:
    image: "ghcr.io/github/github-mcp-server:latest"
    replicas: 3
    environment:
      GITHUB_TOKEN: "${SECRET_GITHUB_TOKEN}"
    resources:
      cpu: "500m"
      memory: "512Mi"
    
  playwright:
    image: "mcr.microsoft.com/playwright-mcp:latest"
    replicas: 2
    environment:
      BROWSER_HEADLESS: "true"
    resources:
      cpu: "1000m"
      memory: "2Gi"
  
  qdrant:
    image: "qdrant/mcp-server:latest"
    replicas: 2
    environment:
      QDRANT_URL: "${APP_QDRANT_URL}"
    resources:
      cpu: "500m"
      memory: "1Gi"

routing:
  load_balancer: "round_robin"
  health_checks: true
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 30s

monitoring:
  metrics_enabled: true
  prometheus_endpoint: "/metrics"
  tracing_enabled: true
```

---

## 📊 Integration Patterns

### 1. Tool Orchestration Pattern

```python
class ToolOrchestrator:
    """Coordinates multiple tools for complex tasks"""
    
    async def create_project_dashboard(self, repo_url: str) -> DashboardArtifact:
        """Create a comprehensive project dashboard"""
        
        # 1. Analyze repository
        repo_info = await self.github_tool.analyze_repository(repo_url)
        
        # 2. Generate code in sandbox
        dashboard_code = await self.e2b_tool.generate_dashboard_code(repo_info)
        
        # 3. Take screenshot of result
        screenshot = await self.playwright_tool.screenshot_dashboard(dashboard_code.url)
        
        # 4. Store in knowledge graph
        await self.neo4j_tool.create_project_nodes(repo_info)
        
        # 5. Create vector embeddings
        await self.qdrant_tool.store_embeddings(repo_info.description)
        
        return DashboardArtifact(
            code=dashboard_code,
            screenshot=screenshot,
            metadata=repo_info
        )
```

### 2. Context Enhancement Pattern

```python
class ContextEnhancer:
    """Enhances user queries with relevant context"""
    
    async def enhance_query(self, query: str, user_id: str) -> EnhancedQuery:
        """Add context from multiple sources"""
        
        # Vector similarity search
        similar_docs = await self.qdrant_tool.semantic_search(query)
        
        # Knowledge graph traversal
        related_concepts = await self.neo4j_tool.find_related_concepts(query)
        
        # User history
        user_context = await self.get_user_context(user_id)
        
        return EnhancedQuery(
            original=query,
            similar_documents=similar_docs,
            related_concepts=related_concepts,
            user_context=user_context
        )
```

---

## 🚀 Getting Started

### 1. Clone Referenced Repositories

```bash
# Create a workspace for referenced repos
mkdir -p workspace/references
cd workspace/references

# Clone key repositories
git clone https://github.com/lobehub/lobe-chat.git
git clone https://github.com/agentic-ai/fast-agent.git
git clone https://github.com/github/github-mcp-server.git
git clone https://github.com/microsoft/playwright-mcp.git
git clone https://github.com/neo4j-labs/mcp-server-neo4j.git
git clone https://github.com/qdrant/mcp-server-qdrant.git
git clone https://github.com/e2b-dev/e2b.git
```

### 2. Study Integration Patterns

Each referenced repository provides examples and documentation for integration. Focus on:

- **LobeChat**: Plugin architecture and UI components
- **FastAgent**: Agent orchestration and tool coordination
- **MCP Servers**: Tool implementation patterns
- **E2B**: Sandbox security and execution models

### 3. Build on Existing Work

Rather than reinventing, we extend and integrate:

```typescript
// Example: Extending LobeChat's plugin system
import { createPlugin } from '@lobehub/ui';

export const CUAArtifactPlugin = createPlugin({
  name: 'cua-artifacts',
  component: ArtifactViewer,
  hooks: {
    onMessage: handleArtifactGeneration,
    onToolResult: processToolArtifacts
  }
});
```

This approach ensures we leverage the best practices and proven patterns from the ecosystem while building our unique value proposition.