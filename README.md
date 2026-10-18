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
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.cursor/skills/` | [Cursor skills](https://cursor.com/docs/context/skills) |
| Devin | `.agents/skills/` committed in the repository | — | [Devin skills](https://docs.devin.ai/product-guides/skills) |

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
| Standalone renderer, Debian Bookworm, CPU | not verified yet | — |
| Skills CLI project/global installs | not verified yet | — |
| Manual skill copy and installed renderer | not verified yet | — |
| Claude Code end-to-end run | not verified yet | — |
| Codex end-to-end run | not verified yet | — |
| Cursor end-to-end run | not verified yet | — |
| Devin end-to-end run | not verified yet | — |
| macOS | not verified yet | — |
| Windows | not verified yet | — |
| GPU rendering | not verified yet | — |
| Claude.ai `.skill` upload and execution | not verified yet | — |

## Credits and licence

MIT License. The renderer uses [ManimGX](https://github.com/academa-labs/manimgx), developed by Academa and released under the MIT License.
