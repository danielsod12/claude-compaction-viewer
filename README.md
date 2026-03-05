# Claude Code Compaction Viewer

A TUI and CLI tool for inspecting [Claude Code](https://docs.anthropic.com/en/docs/claude-code) conversation history and **compaction events**.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

## What is compaction?

When a Claude Code session runs long, the context window fills up. Rather than crashing or losing everything, Claude Code performs **compaction**: it inserts a boundary marker in the conversation, generates a structured summary of everything before it, and continues with the summary replacing the full history in the active context.

The full conversation is preserved on disk in JSONL files at `~/.claude/projects/`. This tool lets you see exactly what happened:

- **Where** compaction boundaries were inserted
- **What** the compressed summary contains (the "outcome" of compaction)
- **How many tokens** were in context before each compaction triggered
- **Whether** compaction was auto-triggered or manual (`/compact`)

Inspired by [Tal Raviv's article](https://www.talraviv.co/p/i-wanted-to-know-how-compaction-works) on doing "brain surgery" on Claude Code.

## Install

```bash
# With uv (recommended)
uv tool install claude-compaction-viewer

# With pip
pip install claude-compaction-viewer

# Or run directly without installing
uvx claude-compaction-viewer --scan
```

## Usage

### Scan all conversations for compactions

```bash
ccv --scan
```

Prints a table of every Claude Code conversation across all your projects, highlighting which ones have compaction events:

```
Project                                  Session     Lines Compactions  Tokens In Tokens Out   Duration
─────────────────────────────────────────────────────────────────────────────────────────────────────────
~/Work/my-project                        a272d8b9…    3086           3       1.8k     262.4k       4.1h
~/Work/other-project                     f359f046…      79           0         36       3.8k       1min
```

### View compaction summaries

```bash
ccv --summary ~/.claude/projects/<project>/<session>.jsonl
```

Prints full details for each compaction event — the trigger, token count, and the complete summary text that Claude sees after compaction.

### Interactive TUI

```bash
ccv
```

Launches a full terminal UI:

- **Left sidebar**: tree of all Claude Code projects and conversation files
- **Stats bar**: message counts, token usage, model, duration
- **Compaction bar**: highlighted summary of all compaction events
- **Message table**: scrollable list of every message (user, assistant, tool calls, system)
- **Detail panel**: full content of selected message with metadata

#### TUI Keybindings

| Key | Action |
|-----|--------|
| `c` | Jump to next compaction boundary |
| `Shift+C` | Jump to previous compaction boundary |
| `s` | Show all compaction summaries in detail panel |
| `t` | Toggle progress messages (hidden by default) |
| `j` / `k` | Scroll down / up |
| `q` | Quit |

You can also open a specific file directly:

```bash
ccv ~/.claude/projects/<project>/<session>.jsonl
```

## How Claude Code stores conversations

Claude Code saves every conversation as a JSONL file at:

```
~/.claude/projects/<project-path>/<session-uuid>.jsonl
```

Each line is a JSON object with a `type` field:

| Type | Description |
|------|-------------|
| `user` | User messages and tool results |
| `assistant` | Claude's responses, thinking, and tool calls |
| `system` | System messages including compaction boundaries (`subtype: "compact_boundary"`) |
| `progress` | Progress updates for long-running tool calls |
| `file-history-snapshot` | File state snapshots for undo |

Compaction creates two adjacent lines:

1. A `system` message with `subtype: "compact_boundary"` and `compactMetadata` (trigger type, pre-compaction token count)
2. A `user` message with `isCompactSummary: true` containing the structured summary

The conversation continues after the summary. The full history stays in the file — the summary just becomes what's loaded into the active context window going forward.

## Development

```bash
git clone https://github.com/swyxio/claude-compaction-viewer
cd claude-compaction-viewer
uv sync
uv run ccv --scan
```

## License

MIT
