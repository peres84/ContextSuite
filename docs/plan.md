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

- [ ] Create the initial app structure for backend, local client, and shared contracts
- [ ] Add environment variable templates for Supabase, Qdrant Cloud, Neo4j Aura, Gemini, and A2A config
- [ ] Add a basic `.env.example`
- [ ] Add package management and task runner commands
- [ ] Add linting and formatting
- [ ] Add a simple local start command for each service
- [ ] Add README sections for local setup and project structure

Exit criteria:

- [ ] A new contributor can clone the repo, install dependencies, and boot the project locally

## Phase 2: Shared Contracts And A2A Design

- [ ] Define the Agent Card for the Context Agent
- [ ] Define the Agent Card for the Local Agent Client
- [ ] Define the A2A task payload schema
- [ ] Define the A2A status update schema
- [ ] Define the result payload schema
- [ ] Define the error payload schema
- [ ] Define how approvals and risk level are represented in the contract
- [ ] Define trace IDs and run IDs for observability

Exit criteria:

- [ ] The Context Agent and Local Agent Client can exchange a well-defined task contract
- [ ] Contracts are documented and versioned in the repo

## Phase 3: Cloud Infrastructure Bootstrap

- [ ] Create the Supabase project
- [ ] Create the Qdrant Cloud cluster
- [ ] Create the Neo4j Aura instance
- [ ] Store connection details and secrets securely
- [ ] Create development and demo environments
- [ ] Validate network connectivity from the app to all managed services

Exit criteria:

- [ ] All managed services are reachable from the running app
- [ ] Base credentials and environment configuration are stable

## Phase 4: Data Model And Persistence

- [ ] Design the Supabase schema for users, repositories, runs, approvals, prompts, plans, and outcomes
- [ ] Design the Qdrant collections for semantic retrieval
- [ ] Design the Neo4j graph model for issues, files, entities, tasks, and relationships
- [ ] Decide which data is authoritative in Supabase versus derived in Qdrant and Neo4j
- [ ] Add migrations for the Supabase schema
- [ ] Add repository-layer code for all core reads and writes
- [ ] Add seed data for demo development

Exit criteria:

- [ ] A full run can be persisted end to end
- [ ] The project has clear ownership rules for each data store

## Phase 5: Context Ingestion And Retrieval

- [ ] Define the input sources for MVP context ingestion
- [ ] Start with a simple ingestion set: issues, docs, ADRs, and selected code summaries
- [ ] Implement document chunking for text and multimodal-compatible content metadata
- [ ] Generate embeddings with Gemini Embedding 2 multimodal
- [ ] Store semantic vectors in Qdrant Cloud
- [ ] Store structural relationships in Neo4j Aura
- [ ] Store ingestion metadata and source tracking in Supabase
- [ ] Add retrieval logic for similar incidents, constraints, and related artifacts
- [ ] Add a simple ranking strategy across vector and graph results

Exit criteria:

- [ ] The Context Agent can retrieve useful context for a prompt
- [ ] Retrieval results can be shown clearly in the demo

## Phase 6: Context Agent Core Workflow

- [ ] Implement prompt intake
- [ ] Implement context retrieval before planning
- [ ] Implement a task normalization step
- [ ] Implement plan generation or plan review
- [ ] Implement risk classification for low, medium, and high risk
- [ ] Implement a policy check step
- [ ] Implement approval routing logic
- [ ] Implement final packaging of the approved task for A2A delivery
- [ ] Add structured logs for each workflow step

Exit criteria:

- [ ] A prompt can move from intake to reviewed, approved task creation
- [ ] Every step is visible in logs or a debug view

## Phase 7: Local Agent Client

- [ ] Create the installable ContextSuite Local Agent Client
- [ ] Implement local configuration for assistant selection
- [ ] Implement workspace selection and repository targeting
- [ ] Implement A2A task receipt
- [ ] Implement task execution lifecycle states
- [ ] Implement output streaming back to the Context Agent
- [ ] Implement artifact capture for logs, plan, summary, and patch references
- [ ] Add timeout, cancellation, and retry behavior

Exit criteria:

- [ ] The Local Agent Client can receive an A2A task and return structured progress updates

## Phase 8: Coding Assistant Adapters

- [ ] Implement the Codex CLI adapter
- [ ] Implement the Claude Code CLI adapter
- [ ] Implement the Cursor CLI adapter
- [ ] Normalize prompts before passing them to each adapter
- [ ] Normalize results into one common output contract
- [ ] Capture failures and stderr safely
- [ ] Mark unsupported capabilities explicitly instead of hiding them

Exit criteria:

- [ ] At least one adapter works end to end
- [ ] The other adapters have a clear integration path, even if partial

## Phase 9: Approval And Safety Layer

- [ ] Define low-risk tasks eligible for auto-approval
- [ ] Define medium-risk and high-risk triggers
- [ ] Add a human approval checkpoint for risky actions
- [ ] Add policy rules for forbidden or sensitive actions
- [ ] Add audit logging for approval decisions
- [ ] Add reason codes for blocked tasks

Exit criteria:

- [ ] The demo can show both an approved flow and a blocked or escalated flow

## Phase 10: API, UI, Or Demo Surface

- [ ] Decide the main MVP entry point: minimal web UI or CLI
- [ ] Build a prompt submission screen or command
- [ ] Show retrieved context summary
- [ ] Show generated or reviewed plan
- [ ] Show approval status
- [ ] Show which coding assistant was selected
- [ ] Show execution progress and final result
- [ ] Show memory saved after completion

Exit criteria:

- [ ] A judge or user can understand the value of the product without reading internal docs

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
