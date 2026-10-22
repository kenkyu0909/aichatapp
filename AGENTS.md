# AGENTS.md — Codex continuous development handoff

This file is specific to the Codex working branch of kenkyu0909/aichatapp.

## Source of truth for active tasks

Before starting work, after each completed repair/test cycle, and at least every 15–20 minutes while the session is running, fetch and read the latest instructions from the separate **control branch**. This avoids hourly Git conflicts with the development branch.

```bat
git fetch origin refs/heads/codex/directive-control:refs/remotes/origin/codex/directive-control
git show origin/codex/directive-control:docs/verification/CODEX_CONTINUOUS_DIRECTIVE.md
```

The control branch is read-only for Codex. Do not merge or cherry-pick it into this branch. The instruction file is maintained by ChatGPT's hourly GitHub review and contains current priorities, acceptance tests, constraints and the continuing-work policy.

## Continuous autonomous work

Keep improving and testing while the environment remains active. If a test FAILs, record it, diagnose, fix and retest; **do not stop solely because quality is not yet passing**. If a task passes, proceed to the next unfulfilled quality goal without waiting for an hourly instruction update. Preserve an explicit next task and checkpoint in docs/verification/PROGRESS.md. A session/tool shutdown cannot be bypassed; save progress before termination.

Protect the existing Draft PR #4 and work exclusively on `codex/full-system-verification`. Never merge PRs, use production/private data, expose credentials, exceed authorized API budgets, or change paid settings without user approval. Use Firefox rather than Chrome.

Conversation simulation `conversation_004` and new conversation HTML are not authorized merely because the quality gate passes; wait for the user's separate explicit instruction.

The current source of truth is the dynamically updated control file, not an old one-off task or time-of-day cutoff.
