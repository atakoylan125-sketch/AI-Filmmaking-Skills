# Top-down staging

Top-down staging is an agent-agnostic [Agent Skill](https://agentskills.io/specification) and an independent Python renderer CLI. The skill guides an agent from a scene brief to a spatial previsualization plan; the renderer consumes the shared JSON scene spec and can be used without an agent.

![Finished park-bench staging map](docs/media/poster.png)

![Park-bench staging animation](docs/media/demo.gif)

## Architecture

```text
SKILL.md (Agent Skills format; any compatible agent)
    → scene.json (references/scene.schema.json)
    → scripts/staging_render.py (standalone ManimGX CLI)
    → preview PNG, rendered MP4, finished-map PNG, JSON report
```

The skill describes intake, layout and approval. The JSON format is shared between agents and the CLI. `--check`, `--preview` and full rendering are renderer operations and do not call an LLM.

## Requirements

Install [uv](https://docs.astral.sh/uv/). Network access is required on first run so `uv` can obtain Python 3.13 or newer, ManimGX, and the bundled ffmpeg from `imageio-ffmpeg`. Rendering runs on the CPU; a GPU is not required.

On one x86_64 machine, a fresh `debian:bookworm-slim` container with an empty uv cache selected CPython 3.15.0 and ManimGX 0.1.1. Measured with `date +%s.%N` around `uv run ... --check`, the cold first run took 2.311 s wall time (including downloads); the warm second run took 0.207 s. The renderer's own `elapsed_seconds` was 0.0 s for both checks. After the warm run, `du -sh ~/.cache/uv ~/.local/share/uv` reported 365M and 116M, respectively. Timings and cache sizes depend on network and machine.

## Use the renderer without an agent

From the repository root, validate a spec without launching ManimGX:

```bash
uv run skills/top-down-staging/scripts/staging_render.py \
  examples/park-bench.json --check
```

Render a quick map preview and report:

```bash
uv run skills/top-down-staging/scripts/staging_render.py \
  examples/blocking-demo.json -o blocking-demo.mp4 --preview
```

Render the complete animation:

```bash
uv run skills/top-down-staging/scripts/staging_render.py \
  examples/park-bench.json -o park-bench.mp4 --quality h
```

The CLI writes a report and finished-map PNG beside the output. Preview mode writes `<stem>.preview.png`; a full render writes `<stem>.last.png` and an MP4. `--check` prints the resolved report and does not render; when `-o` is supplied it also writes `<stem>.report.json`. Without `-o`, rendered output defaults to `staging.mp4` in the current directory. `--version` prints the renderer and ManimGX versions. The JSON schema and field reference are in [SKILL.md](skills/top-down-staging/SKILL.md) and [scene.schema.json](skills/top-down-staging/references/scene.schema.json).

## Install the skill

### Skills CLI

Install into a supported agent's project environment with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add atakoylan125-sketch/top-down-staging -a claude-code
npx skills add atakoylan125-sketch/top-down-staging -a codex
npx skills add atakoylan125-sketch/top-down-staging -a cursor
npx skills add atakoylan125-sketch/top-down-staging -a devin
```

Add `-g` for a global installation.

### Manual copy

Copy the `skills/top-down-staging/` directory into the appropriate skill folder:

| Agent | Project scope | User scope | Documentation |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` | [Codex skills](https://developers.openai.com/codex/skills) |
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.agents/skills/` or `~/.cursor/skills/` | [Cursor skills](https://cursor.com/docs/context/skills) |
| Devin | `.agents/skills/` or `.devin/skills/` | `~/.agents/skills/` or `~/.config/devin/skills/` | [Devin Cloud skills](https://docs.devin.ai/product-guides/skills); [Devin CLI skills](https://docs.devin.ai/cli/extensibility/skills/overview) |

### Optional Claude distributions

The Claude Code plugin marketplace is an optional installer:

```text
/plugin marketplace add atakoylan125-sketch/top-down-staging
/plugin install top-down-staging@top-down-staging
```

The release also includes `top-down-staging.skill` for upload in Claude.ai under **Settings → Capabilities → Skills**. Both are distribution formats for the same skill; neither is required to use the renderer or the generic `.zip` archive.

## Workflow

Intake questions → plan + preview approval → render.

The files in `examples/` are format demos, not templates.

## Platform status

Agent end-to-end rows refer to tests where an agent receives a brief and runs the skill, not merely installs the files. Status is limited to the free checks documented here; no paid LLM tests are used.

| Surface | Status | Evidence |
| --- | --- | --- |
| Standalone renderer, Debian Bookworm, CPU | verified | Clean `debian:bookworm-slim` on x86_64; only curl and ca-certificates were explicitly installed via apt, plus uv 0.13.1. uv selected CPython 3.15.0 with ManimGX 0.1.1; all three examples pass `--check` and render at `l`, 30 fps. Cold/warm `--check`: 2.311/0.207 s wall time. |
| Skills CLI project/global installs | verified (files copied; no agent run) | `npx skills add` installed files for claude-code, codex, cursor, and devin at project and global scope. The installed Codex copy ran `--check` and `--preview`. |
| Manual skill copy and installed renderer | verified (`--check` and `--preview`) | A manual `.agents/skills/` copy passed `--check`; the installed Codex copy passed `--check` and `--preview`. |
| Claude Code end-to-end run | not verified yet | No agent runtime or LLM test run |
| Codex end-to-end run | not verified yet | No agent runtime or LLM test run |
| Cursor end-to-end run | not verified yet | No agent runtime or LLM test run |
| Devin end-to-end run | not verified yet | No agent runtime or LLM test run |
| macOS | not verified yet | Not tested |
| Windows | not verified yet | Not tested |
| GPU rendering | not verified yet | Container verification used CPU only; GPU not tested |
| Claude.ai `.skill` upload and execution | not verified yet | Not tested |

## Credits and licence

MIT License. The renderer uses [ManimGX](https://github.com/academa-labs/manimgx), developed by Academa and released under the MIT License.
