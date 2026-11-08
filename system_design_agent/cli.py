"""
Command-Line Interface for System Design Agent.
Built with Python's standard library for universal zero-dependency compatibility.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import textwrap

from system_design_agent.config import AgentConfig
from system_design_agent.llm import get_llm_client
from system_design_agent.pipeline.orchestrator import PipelineOrchestrator
from system_design_agent.pipeline.state import PipelineStage
from system_design_agent.storage.db import SpecRepository


# ANSI styling
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner() -> None:
    banner = f"""
{CYAN}{BOLD}========================================================================{RESET}
{CYAN}{BOLD}   AUTONOMOUS SYSTEM DESIGN AGENT PIPELINE{RESET}
{DIM}   Principal Systems Architect & Engineering Lead Generator{RESET}
{CYAN}{BOLD}========================================================================{RESET}
"""
    print(banner)


def handle_generate(args: argparse.Namespace) -> None:
    print_banner()

    config = AgentConfig()
    if args.provider:
        config.provider = args.provider
    if args.model:
        if config.resolve_provider() == "gemini":
            config.gemini_model = args.model
        elif config.resolve_provider() == "openai":
            config.openai_model = args.model
        elif config.resolve_provider() == "ollama":
            config.ollama_model = args.model

    resolved_provider = config.resolve_provider()
    print(f"{BOLD}Target Scale:{RESET} ~{args.dau:,} DAU")
    print(f"{BOLD}Active LLM Provider:{RESET} {GREEN}{resolved_provider}{RESET}")
    print(f"{BOLD}Project Pitch:{RESET}\n{DIM}{textwrap.fill(args.pitch, width=78)}{RESET}\n")

    client = get_llm_client(config)
    orchestrator = PipelineOrchestrator(config=config, client=client)

    stage_emojis = {
        PipelineStage.REQUIREMENTS: "📋",
        PipelineStage.HLD: "🏗️ ",
        PipelineStage.LLD: "💾",
        PipelineStage.RESILIENCE: "🛡️ ",
        PipelineStage.SCAFFOLDING: "🚀",
        PipelineStage.VALIDATING: "🔍",
        PipelineStage.COMPLETED: "✅",
        PipelineStage.FAILED: "❌",
    }

    def on_stage(stage: PipelineStage, message: str) -> None:
        emoji = stage_emojis.get(stage, "⚡")
        if stage == PipelineStage.COMPLETED:
            print(f"\n{GREEN}{BOLD}{emoji} {message}{RESET}")
        elif stage == PipelineStage.FAILED:
            print(f"\n{RED}{BOLD}{emoji} {message}{RESET}")
        else:
            print(f"  {CYAN}{emoji} [{stage.value}]{RESET} {message}")

    output_path = Path(args.output) if args.output else None
    spec = orchestrator.run(
        pitch=args.pitch,
        title=args.title,
        target_dau=args.dau,
        output_file=output_path,
        on_stage_update=on_stage,
    )

    print("\n" + "=" * 72)
    print(f"{BOLD}Specification Title:{RESET} {spec.title}")
    print(f"{BOLD}Total Duration:{RESET} {spec.duration_seconds}s | {BOLD}Tokens Used:{RESET} {spec.tokens_used:,}")
    
    report = spec.validation_report
    if report.is_valid and not report.issues:
        print(f"{GREEN}{BOLD}Validation Report:{RESET} PASSED (All 5 sections & schemas structurally compliant)")
    else:
        status_color = GREEN if report.is_valid else RED
        status_text = "PASSED WITH WARNINGS" if report.is_valid else "FAILED"
        print(f"{status_color}{BOLD}Validation Status: {status_text}{RESET}")
        for issue in report.issues:
            c = RED if issue.severity == "ERROR" else YELLOW
            print(f"  {c}[{issue.severity}] {issue.stage}:{RESET} {issue.message}")

    target_md = output_path or (config.output_dir / f"{spec.generate_slug()}.md")
    print(f"{BOLD}Saved Artifact:{RESET} file://{target_md.resolve()}")
    print("=" * 72 + "\n")


def handle_interactive(args: argparse.Namespace) -> None:
    print_banner()
    print(f"{BOLD}Interactive System Pitching Mode{RESET}\n")

    print(f"Enter the raw, ambiguous, or early-stage software project idea.")
    print(f"(Press Ctrl+D or EOF on an empty line when finished):\n")

    try:
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        pitch = "\n".join(lines).strip()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)

    if not pitch:
        print(f"{RED}No pitch provided. Exiting.{RESET}")
        sys.exit(1)

    custom_title = input(f"\nOptional Specification Title (Leave blank to auto-infer): ").strip()
    dau_str = input(f"Target DAU baseline [Default 50,000]: ").strip()
    dau = int(dau_str.replace(",", "")) if dau_str.isdigit() else 50_000

    args.pitch = pitch
    args.title = custom_title or None
    args.dau = dau
    args.output = None
    args.provider = None
    args.model = None

    handle_generate(args)


def handle_list(args: argparse.Namespace) -> None:
    print_banner()
    repo = SpecRepository(Path("specs.db"))
    specs = repo.list_specs(limit=args.limit)

    if not specs:
        print(f"{YELLOW}No specifications generated yet.{RESET}")
        print("Run: python3 -m system_design_agent generate \"Your idea here...\"")
        return

    print(f"{BOLD}{'DATE':<20} {'ID':<10} {'SLUG':<30} {'DAU':<10} {'STATUS':<8}{RESET}")
    print("-" * 80)
    for s in specs:
        date_str = s['created_at'][:19].replace("T", " ")
        status = f"{GREEN}VALID{RESET}" if s['is_valid'] else f"{RED}WARN{RESET}"
        print(f"{date_str:<20} {s['id'][:8]:<10} {s['slug'][:28]:<30} {s['target_dau']:<10} {status}")
    print("-" * 80)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="system_design_agent",
        description="Autonomous System Design Agent Pipeline for generating production-ready technical specs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate a technical specification from a pitch")
    gen_parser.add_argument("pitch", type=str, help="Raw project idea or user pitch")
    gen_parser.add_argument("--title", type=str, default=None, help="Explicit title for the specification")
    gen_parser.add_argument("--dau", type=int, default=50_000, help="Target Daily Active Users scale baseline (default: 50,000)")
    gen_parser.add_argument("--output", "-o", type=str, default=None, help="Output markdown file path")
    gen_parser.add_argument("--provider", "-p", type=str, choices=["gemini", "openai", "ollama", "mock"], default=None, help="LLM Provider override")
    gen_parser.add_argument("--model", "-m", type=str, default=None, help="Model name override")

    # Command: interactive
    subparsers.add_parser("interactive", help="Start interactive CLI pitch wizard")

    # Command: mock (shortcut for dry run)
    mock_parser = subparsers.add_parser("mock", help="Execute a mock dry run pipeline (no external API calls)")
    mock_parser.add_argument("pitch", type=str, nargs="?", default="A high-throughput URL shortener with real-time click analytics and custom vanity domains.", help="Project pitch")
    mock_parser.add_argument("--dau", type=int, default=50_000, help="Target DAU baseline")
    mock_parser.add_argument("--output", "-o", type=str, default=None, help="Output markdown path")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List previously generated specifications")
    list_parser.add_argument("--limit", type=int, default=15, help="Number of items to show")

    return parser


def main() -> None:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "generate":
        handle_generate(args)
    elif args.command == "interactive":
        handle_interactive(args)
    elif args.command == "mock":
        args.provider = "mock"
        args.model = "mock-architect-v1"
        args.title = None
        handle_generate(args)
    elif args.command == "list":
        handle_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
