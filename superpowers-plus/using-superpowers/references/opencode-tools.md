# OpenCode / OhMyOpenCode / OMO Tool Mapping

Skills speak in actions such as "invoke a skill", "dispatch a subagent", "create a todo", and "read a file". Resolve those actions through the current OpenCode/OMO host schema; prefer the live tool contract over stale runtime-specific names. OMO releases and harnesses can expose different delegation surfaces, so never call a tool or pass a parameter that is absent from the active schema.

## Instruction Hierarchy

Follow active system, developer, user, project, permission, and tool-contract instructions before skill guidance. Treat `AGENTS.md`, configured instruction files, and OMO rule injections as project/user instructions under the host hierarchy. `CLAUDE.md` may be loaded for compatibility when configured, but it is not the only possible instruction source.

Skills guide workflow and tool selection. They do not override permissions, safety rules, sandbox limits, or the user's explicit scope.

## Main-Orchestrator Bootstrap

The main/orchestrating agent evaluates skill relevance and invokes relevant skills with `skill(name="<skill-name>")` before answering, clarifying, exploring, planning, editing, reviewing, or delegating.

A subagent dispatched for a specific task should receive task-relevant skills through the host's supported injection mechanism. Use `load_skills` when the active delegation tool exposes it; otherwise include the relevant skill requirements in the delegated prompt or use the host's documented equivalent. The subagent should not independently bootstrap the full skill system unless explicitly asked. This applies to OhMyOpenCode/OMO orchestration; older configurations may use the related OhMyOpenAgent name.

## Tool Mapping

| Skill action | OpenCode / OMO equivalent |
| --- | --- |
| Invoke a skill | `skill(name="<skill-name>")` |
| Dispatch category-routed work | When exposed: `task(category="...", load_skills=[...], run_in_background=..., prompt="...")` |
| Dispatch a named specialist | When `task` is exposed: `task(subagent_type="...", load_skills=[...], run_in_background=..., prompt="...")`; on older/alternate OMO surfaces, use the exposed `call_omo_agent(subagent_type="...", run_in_background=..., prompt="...")` schema |
| Continue the same subagent session | Use the continuation field supported by the active tool: for example `task(task_id="ses_...", prompt="...")` or `call_omo_agent(session_id="ses_...", prompt="...")`; never pass a session ID to `background_output` |
| Track work | `todowrite` |
| Read files or directories | `read` |
| Edit files deterministically | `apply_patch` when available, otherwise the host's native editing tool |
| Search file contents | `grep` |
| Find files by name | `glob` |
| Run commands | `bash`, subject to permissions and safety constraints |
| Search or fetch documentation | Use the available host web/docs tools, including Context7 when appropriate |

## Delegation Contract

First inspect the active delegation tool's schema. Do not assume every OpenCode/OMO installation exposes `task`, `call_omo_agent`, category routing, named specialists, or skill injection in the same form.

- If `task(...)` is available, use exactly one of `category` or `subagent_type`. Use `category` for host-routed implementation/QA and `subagent_type` for a named specialist supported by that schema.
- If only `call_omo_agent(...)` is available, use its advertised `subagent_type` values and `session_id` continuation field; do not copy unsupported `task` parameters into it.
- Pass only task-relevant skills with `load_skills=[...]` when that parameter exists. Use `[]` when supported and no skill domain overlaps. If injection is unavailable, state the relevant workflow requirements in the prompt instead of inventing a parameter.
- Continue an existing subagent with the session field accepted by its delegation tool. Keep every `ses_...` session ID distinct from a background task's `bg_...` ID.

## Background Work

Use `run_in_background=true` only for independent work suitable for parallel execution. Wait for the host's completion notification before calling `background_output(task_id="bg_...")`; do not poll a running task. Use `from_end=true` when only the final result is needed and `full_session=true` only when transcript detail is necessary.

## Repository Memory Gate

Repository memory is a Superpowers/OMO workflow supplement, not an OpenCode core feature. When the repository-memory skills are installed, check `docs/superpowers/memory/` after process skills and before implementation skills.

If memory is missing or sparse for the target area, invoke `bootstrapping-repository-memory` before planning or implementation. If completed work creates durable knowledge, invoke `curating-repository-memory` after implementation and review. Do not block or invent a memory workflow when these skills are unavailable.

## Avoid Stale Claude-Only Assumptions

Older skills may mention tools such as `Skill`, `Task`, `TodoWrite`, `Read`, `Edit`, `Grep`, or `Glob`. Translate the intended action to the current OpenCode/OMO tools above instead of executing Claude-specific syntax literally.
