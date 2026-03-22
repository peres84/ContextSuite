# ContextSuite MVP Plan

This document is the execution checklist for building the hackathon MVP.

The MVP goal is simple:

- user sends a prompt to the Context Agent
- Context Agent retrieves relevant context and reviews the task
- approved work is sent over A2A to the ContextSuite Local Agent Client
- the Local Agent Client executes Codex, Claude Code, or Cursor CLI
- result and important memory are stored for future runs

## MVP Success Criteria

- [ ] A user can submit a prompt through a simple UI or CLI
- [ ] The Context Agent can create or review a task plan before execution
- [ ] The Context Agent can send an approved task to the Local Agent Client over A2A
- [ ] The Local Agent Client can run at least one coding assistant end to end
- [ ] The system stores run history, approvals, and issue-related memory
- [ ] The demo can show why ContextSuite is safer than direct-to-agent prompting

## Phase 0: Scope Lock

- [ ] Freeze the MVP story in one sentence
- [ ] Confirm the primary demo path: `User -> Context Agent -> A2A -> Local Agent Client -> Coding Assistant CLI`
- [ ] Confirm the supported coding assistants for MVP: Codex, Claude Code, Cursor
- [ ] Confirm the cloud stack: Supabase, Qdrant Cloud, Neo4j Aura
- [ ] Confirm the retrieval model: Gemini Embedding 2 multimodal
- [ ] Write down what is explicitly out of scope for the MVP

Exit criteria:

- [ ] The team agrees on one demo flow and one core problem to solve
- [ ] No major architecture decisions remain open

## Phase 1: Repository And Developer Setup

- [x] Create the initial app structure for backend, local client, and shared contracts
- [x] Add environment variable templates for Supabase, Qdrant Cloud, Neo4j Aura, Gemini, and A2A config
- [x] Add a basic `.env.example`
- [x] Add package management and task runner commands
- [x] Add linting and formatting
- [x] Add a simple local start command for each service
- [x] Add README sections for local setup and project structure

Exit criteria:

- [x] A new contributor can clone the repo, install dependencies, and boot the project locally

## Phase 2: Shared Contracts And A2A Design

- [x] Define the Agent Card for the Context Agent
- [x] Define the Agent Card for the Local Agent Client
- [x] Define the A2A task payload schema
- [x] Define the A2A status update schema
- [x] Define the result payload schema
- [x] Define the error payload schema
- [x] Define how approvals and risk level are represented in the contract
- [x] Define trace IDs and run IDs for observability

Exit criteria:

- [x] The Context Agent and Local Agent Client can exchange a well-defined task contract
- [x] Contracts are documented and versioned in the repo

## Phase 3: Cloud Infrastructure Bootstrap

- [x] Create the Supabase project
- [x] Create the Qdrant Cloud cluster
- [x] Create the Neo4j Aura instance
- [x] Store connection details and secrets securely
- [x] Create development and demo environments
- [x] Validate network connectivity from the app to all managed services
- [x] Resolve Neo4j Aura connectivity (fixed: use neo4j+s:// with explicit database name)

Exit criteria:

- [x] All managed services are reachable from the running app (Neo4j pending resume)
- [x] Base credentials and environment configuration are stable

## Phase 4: Data Model And Persistence

- [x] Design the Supabase schema for users, repositories, runs, approvals, prompts, plans, and outcomes
- [x] Design the Qdrant collections for semantic retrieval
- [x] Design the Neo4j graph model for issues, files, entities, tasks, and relationships
- [x] Decide which data is authoritative in Supabase versus derived in Qdrant and Neo4j
- [x] Add migrations for the Supabase schema
- [x] Add repository-layer code for all core reads and writes
- [x] Add seed data for demo development

Exit criteria:

- [x] A full run can be persisted end to end
- [x] The project has clear ownership rules for each data store

## Phase 5: Context Ingestion And Retrieval

- [x] Define the input sources for MVP context ingestion
- [x] Start with a simple ingestion set: issues, docs, ADRs, and selected code summaries
- [x] Implement document chunking for text and multimodal-compatible content metadata
- [x] Generate embeddings with Gemini Embedding 2 multimodal
- [x] Store semantic vectors in Qdrant Cloud
- [x] Store structural relationships in Neo4j Aura
- [x] Store ingestion metadata and source tracking in Supabase
- [x] Add retrieval logic for similar incidents, constraints, and related artifacts
- [x] Add a simple ranking strategy across vector and graph results

Exit criteria:

- [x] The Context Agent can retrieve useful context for a prompt
- [x] Retrieval results can be shown clearly in the demo

## Phase 6: Context Agent Core Workflow

- [x] Implement prompt intake
- [x] Implement context retrieval before planning
- [x] Implement a task normalization step
- [x] Implement plan generation or plan review
- [x] Implement risk classification for low, medium, and high risk
- [x] Implement a policy check step
- [x] Implement approval routing logic
- [x] Implement final packaging of the approved task for A2A delivery
- [x] Add structured logs for each workflow step

Exit criteria:

- [x] A prompt can move from intake to reviewed, approved task creation
- [x] Every step is visible in logs or a debug view

## Phase 7: Local Agent Client

- [x] Create the installable ContextSuite Local Agent Client
- [x] Implement local configuration for assistant selection
- [x] Implement workspace selection and repository targeting
- [x] Implement A2A task receipt
- [x] Implement task execution lifecycle states
- [ ] Implement output streaming back to the Context Agent (deferred — sync for MVP)
- [x] Implement artifact capture for logs, plan, summary, and patch references
- [x] Add timeout, cancellation, and retry behavior

Exit criteria:

- [x] The Local Agent Client can receive an A2A task and return structured progress updates

## Phase 8: Coding Assistant Adapters

- [x] Implement the Codex CLI adapter
- [x] Implement the Claude Code CLI adapter
- [x] Implement the Cursor CLI adapter
- [x] Normalize prompts before passing them to each adapter
- [x] Normalize results into one common output contract
- [x] Capture failures and stderr safely
- [x] Mark unsupported capabilities explicitly instead of hiding them

Exit criteria:

- [x] At least one adapter works end to end
- [x] The other adapters have a clear integration path, even if partial

## Phase 9: Approval And Safety Layer

- [x] Define low-risk tasks eligible for auto-approval
- [x] Define medium-risk and high-risk triggers
- [ ] Add a human approval checkpoint for risky actions (deferred — MVP uses auto-approval)
- [x] Add policy rules for forbidden or sensitive actions
- [x] Add audit logging for approval decisions
- [x] Add reason codes for blocked tasks

Exit criteria:

- [x] The demo can show both an approved flow and a blocked or escalated flow

## Phase 10: API, UI, Or Demo Surface

- [x] Decide the main MVP entry point: minimal web UI or CLI → CLI chosen
- [x] Build a prompt submission screen or command
- [x] Show retrieved context summary
- [x] Show generated or reviewed plan
- [x] Show approval status
- [x] Show which coding assistant was selected
- [x] Show execution progress and final result
- [ ] Show memory saved after completion (deferred — memory persistence not yet wired)
- [x] Interactive terminal chat with prompt history
- [x] File references via `@file.py` tags
- [x] Image attachments via `#image:path.png` or `/image path.png`
- [x] Assistant selection via `/assistant codex|claude|cursor`
- [x] Project initialization via `contextsuite init`

Exit criteria:

- [x] A judge or user can understand the value of the product without reading internal docs

## Phase 11: Demo Data And Storytelling

- [ ] Prepare one sample repository or controlled project target
- [ ] Prepare a realistic incident history for retrieval
- [ ] Prepare one prompt that should be approved
- [ ] Prepare one prompt that should be blocked or escalated
- [ ] Prepare a short script for the live demo
- [ ] Prepare fallback screenshots or recordings in case of live failure

Exit criteria:

- [ ] The demo tells a clear before-and-after story
- [ ] The team can present the system in under three minutes

## Phase 12: Testing And Reliability

- [ ] Add unit tests for contract validation
- [ ] Add unit tests for risk classification
- [ ] Add unit tests for retrieval ranking logic
- [ ] Add integration tests for Supabase, Qdrant Cloud, and Neo4j Aura access
- [ ] Add an end-to-end happy-path test
- [ ] Add an end-to-end escalation-path test
- [ ] Add logging and failure inspection for local debugging

Exit criteria:

- [ ] The MVP survives a full demo run without manual patching
- [ ] The team can quickly diagnose failures during the hackathon

## Phase 13: Final Polish

- [ ] Clean up copy and labels in the UI or CLI
- [ ] Improve the README with setup and demo instructions
- [ ] Add architecture diagrams and final screenshots
- [ ] Verify environment setup from scratch on a second machine if possible
- [ ] Reduce unnecessary steps in the demo flow
- [ ] Time the demo and trim anything confusing

Exit criteria:

- [ ] The project is understandable, reproducible, and demo-ready

## Recommended Build Order

- [ ] Start with one end-to-end vertical slice using only one coding assistant adapter
- [ ] Keep retrieval simple before making it smart
- [ ] Keep approvals simple before making them configurable
- [ ] Keep the UI thin and focus on the core agent interaction
- [ ] Add second and third coding assistant adapters only after the first flow works

## Suggested Vertical Slice

- [ ] Prompt intake
- [ ] Basic retrieval from seeded project memory
- [ ] Plan generation or review
- [ ] Auto-approval for a low-risk task
- [ ] A2A dispatch to the Local Agent Client
- [ ] Codex CLI execution
- [ ] Persist run results to Supabase
- [ ] Store embeddings in Qdrant Cloud
- [ ] Store relationships in Neo4j Aura
- [ ] Display the final result in a minimal demo surface

## Out Of Scope For The MVP

- [ ] Multi-tenant enterprise administration
- [ ] Deep IDE plugins
- [ ] Native A2A servers from third-party coding assistants
- [ ] Complex policy authoring UI
- [ ] Large-scale ingestion pipelines
- [ ] Production-grade billing and account management

## Definition Of Done

- [ ] One prompt can move through the full system from intake to stored result
- [ ] One coding assistant works reliably through the Local Agent Client
- [ ] A2A messaging is real, not mocked in the final demo
- [ ] Retrieval contributes visible value to the result
- [ ] Approval logic is demonstrated clearly
- [ ] The README and demo script match what the product actually does
