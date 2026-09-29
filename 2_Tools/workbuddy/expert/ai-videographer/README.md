# AI Videographer expert for WorkBuddy

A single-agent WorkBuddy expert that runs the AI Videographer harness in this workspace. Its prompt
(`agents/ai-videographer.md`) is a short playbook built around `vg next`, so a fast, cheap model
(GLM-5.3-Flash or MiniMax-M3.1-Flash-Preview) can drive the pipeline one step at a time. The skills,
rules and tool stay in the workspace: WorkBuddy reads `AGENTS.md` and `.codebuddy/skills/`.

Install with `bash 2_Tools/workbuddy/install_workbuddy.sh` from the workspace root. The installer
copies this folder into `~/.workbuddy-ai/plugins/marketplaces/my-experts/plugins/` and registers it
with WorkBuddy's own `register_expert.py`.

Change the expert here, never in the copy, and raise `version` in `.codebuddy-plugin/plugin.json`:
WorkBuddy caches experts by version, so an edit under the same version is not picked up.
