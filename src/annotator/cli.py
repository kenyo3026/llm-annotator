import argparse
import sys
from rich.console import Console

from .main import Main
from .utils import resolve_config_path


console = Console()


def cmd_annotate(args):
    """Execute annotation command"""
    try:
        # Resolve config path
        config_path = resolve_config_path(args.config)

        # Initialize main
        main = Main(config_path=config_path)

        # Execute annotation
        response = main.annotate(
            context=args.context,
            annotator_name=args.annotator,
            model_name=args.model,
        )

        # Display results
        if response.tags:
            console.print(f"[bold green]Tags:[/bold green] {', '.join(response.tags)}")
        else:
            console.print("[yellow]No tags generated[/yellow]")

        # Display metadata if present
        if response.metadata:
            console.print(f"[dim]Metadata: {response.metadata.__dict__}[/dim]")

        return 0

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1


def cmd_list(args):
    """List available annotators and models"""
    try:
        # Resolve config path
        config_path = resolve_config_path(args.config)

        main = Main(config_path=config_path)

        # List annotators
        annotators = main.list_annotators()
        console.print("[bold cyan]Available Annotators:[/bold cyan]")
        for annotator in annotators:
            console.print(f"  - {annotator}")

        # List models
        models = main.list_models()
        console.print("\n[bold cyan]Available Models:[/bold cyan]")
        for model in models:
            console.print(f"  - {model}")

        return 0

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='LLM Tag Annotator - Multi-label text classification tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global arguments
    parser.add_argument(
        '-c', '--config',
        default='configs/config.yaml',
        help='Path to config file (default: configs/config.yaml)'
    )
    parser.add_argument(
        '-a', '--annotator',
        help='Annotator name to use (default: first annotator in config)'
    )
    parser.add_argument(
        '-m', '--model',
        help='Model name to use (default: first model in config)'
    )
    parser.add_argument(
        '--context',
        help='Text context to annotate (if not provided, will prompt interactively)'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Annotate command (explicit subcommand, for backward compatibility)
    parser_annotate = subparsers.add_parser('annotate', help='Annotate text (explicit command)')
    parser_annotate.add_argument('context', nargs='?', help='Text context to annotate')

    # List command
    subparsers.add_parser('list', help='List available annotators and models')

    # Parse arguments
    args = parser.parse_args()

    # Handle 'list' command
    if args.command == 'list':
        return cmd_list(args)

    # Handle annotate (default behavior or explicit 'annotate' command)
    # Priority: --context/global > explicit context argument > interactive input
    context = None
    # Global --context
    if getattr(args, "context", None) and args.command != "annotate":
        context = args.context
    # annotate subcommand positional context
    elif args.command == 'annotate' and getattr(args, "context", None):
        context = args.context

    # If no context provided, prompt interactively
    if not context:
        console.print("[bold cyan]Enter text context to annotate:[/bold cyan]")
        try:
            context = input().strip()
        except EOFError:
            console.print("[bold red]No input provided[/bold red]")
            return 1
        if not context:
            console.print("[bold red]No context provided[/bold red]")
            return 1

    # Execute annotation
    return cmd_annotate(type('Args', (), {
        'config': args.config,
        'context': context,
        'annotator': args.annotator,
        'model': args.model,
    })())


if __name__ == '__main__':
    sys.exit(main())
