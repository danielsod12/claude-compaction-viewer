"""CLI (non-TUI) modes: --scan and --summary."""

from pathlib import Path

from .parser import CLAUDE_DIR, parse_jsonl, humanize_project_name
from .fmt import format_tokens, format_timestamp_full, format_duration


def cli_scan():
    """Scan all projects and print a summary table of conversations with compactions."""
    if not CLAUDE_DIR.exists():
        print(f"No Claude Code projects found at {CLAUDE_DIR}")
        return

    print(
        f"\n\033[1m{'Project':<40} {'Session':<10} {'Lines':>6} "
        f"{'Compactions':>11} {'Tokens In':>10} {'Tokens Out':>10} {'Duration':>10}\033[0m"
    )
    print("\u2500" * 105)

    total_compactions = 0
    for project_dir in sorted(CLAUDE_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        display_name = humanize_project_name(project_dir.name)
        if len(display_name) > 38:
            display_name = "\u2026" + display_name[-37:]

        for jf in sorted(project_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
            _, compactions, stats = parse_jsonl(str(jf))
            duration = format_duration(stats.first_timestamp, stats.last_timestamp)

            comp_str = str(stats.compactions)
            if stats.compactions > 0:
                comp_str = f"\033[33;1m{stats.compactions}\033[0m"
                total_compactions += stats.compactions

            print(
                f"{display_name:<40} {jf.stem[:8]+'\u2026':<10} "
                f"{stats.total_messages:>6} {comp_str:>20} "
                f"{format_tokens(stats.total_input_tokens):>10} "
                f"{format_tokens(stats.total_output_tokens):>10} "
                f"{duration:>10}"
            )

    print("\u2500" * 105)
    print(f"\033[1mTotal compaction events: {total_compactions}\033[0m\n")


def cli_summary(filepath: str):
    """Print compaction summaries from a specific JSONL file."""
    _, compactions, stats = parse_jsonl(filepath)

    fname = Path(filepath).name
    print(f"\n\033[1m{fname}\033[0m")
    print(f"  Messages: {stats.total_messages} | User: {stats.user_messages} | Assistant: {stats.assistant_messages}")
    print(f"  Tool calls: {stats.tool_calls} | Models: {', '.join(stats.models_used) or 'N/A'}")
    print(f"  Tokens in: {format_tokens(stats.total_input_tokens)} | out: {format_tokens(stats.total_output_tokens)}")
    print(f"  Cache read: {format_tokens(stats.total_cache_read)} | Cache create: {format_tokens(stats.total_cache_create)}")
    print(f"  CWD: {stats.cwd} | Branch: {stats.git_branch}")

    if not compactions:
        print("\n  \033[90mNo compaction events found.\033[0m\n")
        return

    print(f"\n  \033[33;1m{len(compactions)} compaction(s) found:\033[0m\n")

    for ci, ce in enumerate(compactions):
        pre_pct = ""
        if stats.total_messages > 0:
            pre_pct = f" ({ce.line_idx * 100 // stats.total_messages}% through conversation)"
        print(f"  \033[33m{'\u2501' * 70}\033[0m")
        print(f"  \033[1;33m\u26a1 Compaction {ci+1}\033[0m{pre_pct}")
        print(f"  \033[90mLine: {ce.line_idx} \u2192 {ce.summary_line_idx} | Trigger: {ce.trigger} | Pre-tokens: {format_tokens(ce.pre_tokens)}\033[0m")
        print(f"  \033[90mTimestamp: {format_timestamp_full(ce.timestamp)} | Summary: {format_tokens(ce.summary_length)} chars\033[0m")
        print()
        for line in ce.summary_text.split("\n"):
            print(f"    {line}")
        print()
