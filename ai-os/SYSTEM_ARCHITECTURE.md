# AI OS System Architecture

Version: 1.0  
Date: 2026-05-06

## 1. Purpose

This document defines a production-grade architecture for an AI operating system that can:

- orchestrate multi-agent work across research, planning, coding, analysis, and review
- manage durable memory across sessions, projects, and domains
- route work to the right model, toolchain, and execution policy
- enforce security, governance, and evaluation before outputs are promoted
- support both human-in-the-loop operation and high-autonomy execution

The design assumes the existing AI OS repository structure remains the operator surface, while services behind it evolve into a more explicit platform.

## 2. Design Goals

### Primary goals

- Unified operating model for knowledge work, software work, and experimentation
- Explicit separation between planning, execution, memory, and governance
- Reliable multi-agent coordination without hidden state
- Full auditability of prompts, tools, decisions, outputs, and approvals
- Graceful degradation when a model, tool, or subsystem is unavailable

### Non-goals

- Fully autonomous unsupervised operation across privileged systems
- Replacing source control, ticketing, BI, or notebooks as systems of record
- Single-model dependency

## 3. Architectural Principles

- Control plane and execution plane must be separated.
- Every agent action must be traceable to a task, context bundle, and policy envelope.
- Long-term memory is curated, versioned, and retrievable; it is not just chat history.
- High-cost reasoning and low-cost execution should be routed differently.
- Unsafe autonomy must fail closed.
- Evaluation is part of the runtime, not a post-hoc report.

## 4. System Context

The AI OS sits between humans, enterprise systems, model providers, and project artifacts.

```text
Operators / Teams
    |
    v
Workspace UX (CLI, docs, templates, vault, dashboards)
    |
    v
AI OS Control Plane
    |
    +--> Policy / Identity / Approval
    +--> Planning / Routing / Scheduling
    +--> Context Assembly / Memory Retrieval
    +--> Evaluation / Promotion / Audit
    |
    v
AI OS Execution Plane
    |
    +--> Specialized agents
    +--> Tool adapters
    +--> Sandboxed runtimes
    +--> Async workers
    |
    v
Data + Knowledge + External Systems
```

## 5. Top-Level Architecture

The platform is organized into seven planes.

### 5.1 Experience Plane

Human-facing entry points:

- terminal and coding-agent interfaces
- project templates and operating documents
- dashboards for queue status, cost, incidents, and evals
- meeting notes, reports, decision packs, and review outputs

### 5.2 Control Plane

The control plane owns coordination and governance:

- task intake and normalization
- task decomposition and dependency graph generation
- model and agent routing
- policy checks and approval gates
- workflow state machine
- SLA, retries, escalation, and circuit breakers

### 5.3 Execution Plane

The execution plane runs bounded work:

- planner agents
- implementation agents
- reviewer agents
- research agents
- analysis agents
- tool runners and adapter wrappers

Execution must be stateless at the worker boundary. Durable state belongs to platform services.

### 5.4 Memory Plane

Memory is split into four layers:

- session memory: current task thread, ephemeral notes, temporary scratchpads
- project memory: project docs, design specs, task history, decisions
- institutional memory: frameworks, playbooks, standards, failure patterns
- retrieval memory: vector and lexical indexes over curated knowledge assets

### 5.5 Knowledge Plane

The knowledge plane handles ingestion, curation, versioning, and retrieval:

- raw capture from notes, web clips, docs, code, and reports
- transformation into structured knowledge objects
- metadata tagging, chunking, embeddings, and indexing
- confidence tracking and freshness policies
- promotion from raw -> reviewed -> canonical

### 5.6 Governance Plane

The governance plane enforces:

- identity and role-based permissions
- data classification and masking
- policy-aware context assembly
- approval workflows for risky actions
- retention, provenance, and audit logs

### 5.7 Observability Plane

Every task and agent emits:

- traces
- structured logs
- cost metrics
- latency metrics
- quality and evaluation metrics
- security signals

## 6. Core Services

### 6.1 Task Gateway

Responsibilities:

- receive user requests, scheduled jobs, or system events
- normalize into a canonical task envelope
- attach tenant, project, priority, and sensitivity metadata

Canonical task envelope:

```json
{
  "task_id": "tsk_20260506_001",
  "intent": "design_system_architecture",
  "domain": "agentic_workflow",
  "priority": "high",
  "risk_tier": "medium",
  "project": "ai-os",
  "inputs": [],
  "constraints": [],
  "requested_outputs": ["architecture_doc"]
}
```

### 6.2 Planner

The planner converts a task into an executable work graph:

- objective tree
- subtask graph with dependencies
- acceptance criteria
- required tools and memory sources
- approval checkpoints

Output artifact:

- `ExecutionPlan`
- `ContextRequirements`
- `EvalPlan`

### 6.3 Context Compiler

The context compiler assembles the minimum viable context for a subtask:

- repository artifacts
- knowledge documents
- memory objects
- prior decisions
- security filters
- token budget

This service is critical. It prevents both hallucination from missing context and waste from dumping entire corpora into prompts.

### 6.4 Model Router

The model router selects:

- model family
- reasoning tier
- tool-enabled or plain model mode
- sync vs async execution
- fallback chain

Routing dimensions:

- task type
- task difficulty
- latency budget
- cost budget
- confidentiality class
- required tool reliability

### 6.5 Agent Runtime Manager

The runtime manager handles:

- agent lifecycle
- leases and heartbeats
- state checkpoints
- retry policy
- deadlock detection
- cancellation and escalation

Recommended topology:

- central orchestrator for task lifecycle
- scoped sub-orchestrators for complex workflows
- isolated workers for execution

### 6.6 Tool and Adapter Fabric

Adapters provide a stable boundary to:

- coding tools
- shell
- browsers and search
- notebooks
- ticketing systems
- storage systems
- communication tools
- internal APIs

Each adapter must declare:

- capabilities
- auth scope
- side-effect class
- retry semantics
- observability hooks

### 6.7 Memory Services

Core services:

- session store
- document store
- vector index
- lexical index
- knowledge graph
- artifact registry

Recommended storage split:

- relational DB for workflows, tasks, approvals, metadata
- object store for large artifacts
- vector DB for semantic retrieval
- graph or symbol index for dependency-aware code reasoning

### 6.8 Evaluation Service

The evaluation service runs:

- output schema validation
- regression checks
- policy validation
- quality scoring
- retrieval quality checks
- cost and latency checks
- human review queues where required

Nothing reaches promoted state without passing the eval plan for its risk tier.

## 7. Data Architecture

### 7.1 Canonical object types

- `Task`
- `Plan`
- `AgentRun`
- `ContextBundle`
- `KnowledgeAsset`
- `DecisionRecord`
- `EvalResult`
- `Approval`
- `Artifact`
- `Incident`

### 7.2 Knowledge asset lifecycle

```text
Capture -> Normalize -> Classify -> Chunk -> Embed -> Index -> Review -> Promote
```

States:

- `raw`
- `processed`
- `reviewed`
- `canonical`
- `deprecated`

### 7.3 Memory segmentation

To avoid cross-contamination, memory boundaries must exist by:

- tenant
- project
- confidentiality level
- modality
- time horizon

## 8. Control Flows

### 8.1 Standard interactive task

```text
User Request
-> Task Gateway
-> Planner
-> Context Compiler
-> Model Router
-> Agent Runtime
-> Tool Execution / Reasoning
-> Evaluation
-> Approval Gate if needed
-> Artifact Promotion
-> Audit Log
-> User Response
```

### 8.2 Multi-agent design workflow

```text
Primary task
-> Planner creates decomposition
-> Orchestrator assigns planner / researcher / implementer / reviewer roles
-> Shared context bundle with role-specific slices
-> Workers emit structured outputs
-> Aggregator reconciles conflicts
-> Evaluation validates output package
-> Human approval for promotion
```

### 8.3 Knowledge ingestion workflow

```text
Raw source capture
-> parser and metadata extraction
-> chunking and embedding
-> retrieval tests
-> optional editorial review
-> promotion to canonical knowledge
-> availability to context compiler
```

## 9. Security Architecture

### 9.1 Trust boundaries

- human operator boundary
- control plane boundary
- execution sandbox boundary
- data service boundary
- external integration boundary

### 9.2 Security controls

- least-privilege tokens per adapter
- prompt-injection filtering at ingress and retrieval time
- secret masking before prompt assembly
- scoped filesystem and API access per task class
- output filtering for leakage, unsafe actions, and policy violations
- append-only audit trails for high-risk runs

### 9.3 Risk tiers

- `L0`: read-only reasoning and summarization
- `L1`: low-risk artifact generation
- `L2`: code edits, config changes, structured business outputs
- `L3`: external side effects, privileged access, production actions

`L2` and `L3` require explicit eval and approval policies. `L3` should default to human confirmation.

## 10. Reliability and Failure Handling

### 10.1 Failure classes

- model unavailable
- tool timeout
- invalid context bundle
- policy denial
- deadlock between agents
- stale knowledge
- eval failure

### 10.2 Reliability patterns

- queue-backed async execution
- idempotent task replay
- checkpointed workflow state
- backoff and retry by side-effect class
- fallback model chain
- circuit breakers on unstable adapters
- degraded-mode operation with reduced capability

### 10.3 Recovery policy

- retry transient failures automatically
- escalate repeated failures to a supervisor queue
- quarantine suspect knowledge sources
- mark partial artifacts as non-promotable

## 11. Observability Model

### Required telemetry

- task latency by stage
- model spend by task and project
- retrieval hit rate and groundedness score
- approval wait time
- eval pass rate
- incident count by subsystem
- agent utilization and queue depth

### Audit trail requirements

For each promoted artifact, store:

- originating task
- planner version
- context bundle references
- models and tools used
- evaluation results
- approver identity if applicable

## 12. Deployment Topology

### 12.1 Logical topology

```text
Clients
  |
API / CLI Gateway
  |
Control Plane Services
  |------ Workflow DB
  |------ Policy Engine
  |------ Context Compiler
  |------ Router
  |
Execution Plane
  |------ Agent Workers
  |------ Tool Runtimes
  |------ Async Queues
  |
Memory + Knowledge Services
  |------ Object Store
  |------ Relational Store
  |------ Vector Store
  |------ Graph Index
  |
Observability + Security
```

### 12.2 Suggested implementation phases

Phase 1:

- filesystem-centric workspace
- single orchestrator
- local state DB
- vector retrieval
- manual approvals

Phase 2:

- task queue and worker pool
- explicit context compiler
- evaluation service
- centralized logs and cost dashboards

Phase 3:

- multi-tenant policy engine
- graph-enhanced memory and dependency reasoning
- durable approval workflows
- autonomous background jobs with bounded authority

Phase 4:

- adaptive planning
- self-healing workflow policies
- continuous knowledge freshness scoring
- cross-project learning loops with strict governance

## 13. Mapping to Current Repository

Current repository areas align to the architecture as follows:

- `ai-os/knowledge/` -> institutional memory and canonical knowledge
- `ai-os/knowledge-pipeline/` -> ingestion and retrieval layer
- `ai-os/templates/` -> experience plane and standardized outputs
- `ai-os/shared/` -> shared standards, scripts, and policy assets
- `ai-os/work/`, `ai-os/competitions/` -> project memory domains

This means the current repo can evolve without a rewrite:

- docs remain the operator-facing contract
- orchestration code hardens into platform services
- memory and eval become first-class services instead of implicit conventions

## 14. Reference Runtime Policies

### Promotion policy

- raw outputs are never canonical by default
- reviewed outputs require eval pass
- canonical outputs require either human approval or a pre-approved policy path

### Context policy

- include only relevant assets
- prefer canonical over raw knowledge
- attach provenance to every retrieved chunk
- enforce token budgets per task class

### Agent policy

- one agent, one explicit role
- structured input and output contracts
- no silent cross-agent state mutation
- every handoff must be logged

## 15. Open Decisions

- whether workflow state stays in SQLite initially or moves directly to Postgres
- whether the graph layer is GitNexus-only for code intelligence or generalized to all knowledge objects
- how much autonomy `L2` tasks should receive by default
- whether approvals are embedded in CLI/docs or exposed through a dedicated UI

## 16. Recommended Next Documents

- `ai-os/RUNTIME_CONTRACTS.md`
- `ai-os/POLICY_MODEL.md`
- `ai-os/EVENT_MODEL.md`
- `ai-os/MEMORY_MODEL.md`
- `ai-os/EVAL_ARCHITECTURE.md`
- `ai-os/DEPLOYMENT_RUNBOOK.md`
