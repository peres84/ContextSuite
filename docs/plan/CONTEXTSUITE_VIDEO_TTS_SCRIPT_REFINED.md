# ContextSuite Video TTS Script

## Main Version (about 2 minutes)
AI coding assistants are fast, but teams still repeat old mistakes because critical context gets lost across sessions and across people.

That is the problem ContextSuite solves.

ContextSuite is an AI governance and memory layer for coding assistants. For existing projects, every prompt goes to the Context Agent first. The Context Agent classifies the task, retrieves relevant issue history, checks constraints, and prepares a context brief before coding begins.

Then the coding agent creates a structured plan and sends it back for review. ContextSuite checks risky file edits, variable and constant changes, and git diff scope against known constraints. If the plan is safe, it moves forward. If not, ContextSuite sends refinement feedback and the coding agent iterates.

For low-risk tasks, approval can be automatic under policy. For medium and high-risk tasks, approval is delegated to a human. Every decision records who approved, when, and why. After approval, ContextSuite issues an execution token, and only then execution is allowed.

After execution, ContextSuite indexes only issue-related outcomes. If there is no real issue, it does not index noise. If there is an issue, it stores rationale, commit evidence, and trust signals, so teams can avoid breaking the same logic again.

Under the hood, PostgreSQL stores approvals, audit history, preferences, and commit evidence. Qdrant powers semantic retrieval of similar issues and fixes. Neo4j models relationships like blocks, contradicts, and supersedes.

ContextSuite does not replace coding assistants. It makes them safer, more consistent, and enterprise-ready. From prompt, to plan, to approval, to execution, ContextSuite helps teams stop repeating the same failures.

## Optional Short Version (about 60 seconds)
ContextSuite is an AI governance and memory layer for coding assistants.

For existing projects, prompts go to the Context Agent first. It retrieves issue history, checks constraints, and briefs the coding agent before planning starts.

The coding agent submits a structured plan. ContextSuite reviews it, then either approves it or requests refinement. Low-risk changes can be auto-approved. Medium and high-risk changes require human approval. Execution only happens with a valid execution token.

ContextSuite indexes only issue-related outcomes, so memory stays clean and useful.

PostgreSQL stores approvals and audit history, Qdrant handles semantic recall, and Neo4j maps dependency and contradiction relationships.

ContextSuite does not replace coding assistants. It makes them safer, explainable, and ready for real team workflows.
