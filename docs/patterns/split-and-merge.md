# Split-and-Merge Pattern

**Agents work in isolated parallel environments (e.g., git worktrees), then results are merged at completion.**

Like multiple developers each working on a separate feature branch from the same base commit. They work in complete isolation -- no shared state, no race conditions. When everyone is done, a merge step combines the changes. Conflicts are resolved at merge time.

## When to Use

- Multiple agents need to modify the same codebase simultaneously without conflicts
- Each agent's work is scoped to different files or modules
- You want true isolation -- no agent can see or interfere with another's work
- The merge step is well-defined (git merge, file concatenation, structured merge)
- Large refactoring tasks that can be decomposed by module or file

## When NOT to Use

- Agents need to see each other's changes in real time -- use Group Chat
- Changes are tightly coupled and conflict-heavy (merge will fail repeatedly)
- The task is small enough for a single agent (overhead of worktrees is not justified)
- You do not have a reliable merge strategy for the output format
- Sequential ordering matters -- use Sequential pipeline

## Architecture Diagram

```
                    ┌─────────────────┐
                    │   Coordinator    │
                    │  (Split Phase)   │
                    └────────┬────────┘
                             │ Decompose task into
                             │ isolated work units
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
    ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
    │  Worktree 1     │ │ Worktree 2   │ │  Worktree 3     │
    │  ┌────────────┐ │ │ ┌──────────┐ │ │  ┌────────────┐ │
    │  │  Agent A    │ │ │ │ Agent B  │ │ │  │  Agent C    │ │
    │  │  Frontend   │ │ │ │ Backend  │ │ │  │  Tests      │ │
    │  └────────────┘ │ │ └──────────┘ │ │  └────────────┘ │
    │  files: src/ui/ │ │ files: src/  │ │  files: tests/  │
    │                 │ │   api/       │ │                  │
    └────────┬───────┘ └──────┬───────┘ └────────┬────────┘
             │                │                   │
             └────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   Merge Phase    │
                    │  (Git merge /    │
                    │   conflict res.) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Validation     │
                    │  (Tests pass?)   │
                    └─────────────────┘
```

## How It Works

1. **Task Decomposition** -- A coordinator agent (or static config) breaks the task into independent work units, each scoped to specific files or modules.
2. **Worktree Creation** -- For each work unit, an isolated environment is created (e.g., `git worktree add` creates a separate checkout of the repo).
3. **Parallel Execution** -- Each agent works in its own worktree, making changes freely without affecting others.
4. **Completion Collection** -- The coordinator waits for all agents to finish (with optional timeout).
5. **Merge** -- Changes from all worktrees are merged back into the main branch:
   - Automatic merge for non-conflicting changes
   - Conflict resolution agent for overlapping changes
   - Validation step to ensure the merged result is consistent
6. **Cleanup** -- Worktrees are removed after successful merge.

## Configuration Example

```yaml
pattern: split-and-merge
name: multi-module-refactor

coordinator:
  agent: code/code-reviewer
  model: claude-sonnet-4-6
  description: Decompose refactoring task and assign file scopes

work_units:
  - name: frontend
    agent: code/refactorer
    model: claude-sonnet-4-6
    scope:
      include: ["src/ui/**", "src/components/**"]
      exclude: ["**/*.test.*"]
    worktree_branch: refactor/frontend

  - name: backend
    agent: code/refactorer
    model: claude-sonnet-4-6
    scope:
      include: ["src/api/**", "src/models/**"]
      exclude: ["**/*.test.*"]
    worktree_branch: refactor/backend

  - name: tests
    agent: code/test-writer
    model: claude-sonnet-4-6
    scope:
      include: ["tests/**", "**/*.test.*"]
    worktree_branch: refactor/tests

merge:
  strategy: git             # git, file-concat, or agent
  conflict_resolution: agent
  conflict_agent: code/code-reviewer
  conflict_model: claude-sonnet-4-6
  target_branch: refactor/combined

validation:
  run_tests: true
  test_command: "pytest tests/ -x"
  lint_command: "ruff check src/"
```

## Code Example

```python
from multiagent import Catalog, patterns

catalog = Catalog()

# Define the split-and-merge workflow
workflow = patterns.split_and_merge(
    coordinator=catalog.load("code/code-reviewer"),
    work_units=[
        {
            "name": "frontend",
            "agent": catalog.load("code/refactorer"),
            "scope": {"include": ["src/ui/**", "src/components/**"]},
            "branch": "refactor/frontend",
        },
        {
            "name": "backend",
            "agent": catalog.load("code/refactorer"),
            "scope": {"include": ["src/api/**", "src/models/**"]},
            "branch": "refactor/backend",
        },
        {
            "name": "tests",
            "agent": catalog.load("code/test-writer"),
            "scope": {"include": ["tests/**"]},
            "branch": "refactor/tests",
        },
    ],
    merge_strategy="git",
    conflict_agent=catalog.load("code/code-reviewer"),
    model="claude-sonnet-4-6",
    repo_path="/path/to/repo",
)

# Run
result = workflow.run(
    "Rename the User model to Account across the entire codebase",
    context={
        "old_name": "User",
        "new_name": "Account",
        "preserve_backwards_compat": True,
    },
)

# Inspect results
for unit in result.work_units:
    print(f"{unit.name}: {unit.files_changed} files, {unit.lines_changed} lines")

print(f"Merge conflicts: {result.merge_conflicts}")
print(f"Conflicts resolved: {result.conflicts_resolved}")
print(f"Tests passed: {result.validation.tests_passed}")
print(f"Total cost: ${result.total_cost:.4f}")
print(f"Wall time: {result.wall_time:.1f}s")
```

## Real-World Examples

- **Multi-File Refactoring** -- Rename a class across the entire codebase. Frontend agent handles UI files, backend agent handles API files, test agent updates all test files. Git merge combines the results.
- **Large Codebase Migration** -- Migrate from one ORM to another. Each agent handles a different module (users, payments, inventory) in its own worktree. Merge combines all migrations.
- **Parallel Feature Development** -- Three agents each build a different component of a feature (API endpoint, UI component, database migration) in isolated worktrees.
- **Documentation Overhaul** -- Separate agents rewrite API docs, tutorial guides, and reference documentation simultaneously. File scopes ensure no overlap.
- **Dependency Upgrade** -- One agent upgrades the dependency, another updates all call sites, a third updates tests. Each works in isolation and changes are merged.

## Pros and Cons

| Pros | Cons |
|------|------|
| True isolation prevents interference | Merge conflicts require resolution (extra cost/logic) |
| Maximum parallelism for large changes | Worktree setup/teardown adds overhead |
| Each agent has a clean working environment | Agents cannot share discoveries in real time |
| Git-native -- uses standard branching and merging | Tightly coupled changes across modules are hard to split |
| Auditable -- each worktree's changes are a separate diff | Requires careful scope definition to minimize conflicts |
| Scales to many agents without coordination overhead | Validation must run on the merged result, not individual units |

## Cost Implications

- **Agent costs are parallel**: Like the Parallel pattern, all agents run simultaneously, so total agent cost is N times a single agent. But wall time is the slowest agent.
- **Merge cost is usually small**: Git merge is free (automated). A conflict-resolution agent adds one LLM call per conflict, typically $0.01-0.05.
- **Coordinator overhead**: The initial decomposition step costs one LLM call. Use a cheaper model if scopes are predefined in config.
- **Validation costs**: Running tests and linters after merge adds compute cost (not LLM cost). Budget for CI time.
- **Scope precision reduces conflicts**: Well-defined, non-overlapping scopes mean fewer merge conflicts and lower conflict-resolution cost.
- **Amortized for large changes**: The overhead of worktree setup (seconds) is negligible for tasks that take minutes per agent. Not worth it for small changes.
- **Typical cost range**: $0.05-0.30 per run (3 agents with Sonnet + merge), plus CI validation time.
