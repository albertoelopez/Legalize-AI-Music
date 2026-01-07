"""CLI interface for the workflow."""

import click
import asyncio
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
import json
from .orchestrator import WorkflowOrchestrator


console = Console()


class CLI:
    """Command-line interface for the workflow."""

    def __init__(self):
        self.orchestrator = None
        self.state_file = Path("output/.cli_state.json")

    def _save_state(self, state: dict):
        """Save CLI state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> dict:
        """Load CLI state."""
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}


@click.group()
def cli():
    """Suno AI to MIDI FL Studio Automation CLI."""
    pass


@cli.command()
@click.option(
    "--prompt",
    "-p",
    required=True,
    help="Task prompt for the workflow"
)
@click.option(
    "--model",
    "-m",
    default="mistral",
    help="Ollama model to use (default: mistral)"
)
@click.option(
    "--ollama-url",
    default="http://localhost:11434",
    help="Ollama API URL"
)
@click.option(
    "--async-mode",
    is_flag=True,
    help="Run workflow asynchronously"
)
def start(prompt: str, model: str, ollama_url: str, async_mode: bool):
    """Start the workflow with a prompt."""
    console.print(Panel(
        f"[bold cyan]Starting Workflow[/bold cyan]\n\n"
        f"Prompt: {prompt}\n"
        f"Model: {model}\n"
        f"Ollama URL: {ollama_url}",
        title="Suno AI to MIDI Workflow"
    ))

    try:
        orchestrator = WorkflowOrchestrator(
            model_name=model,
            ollama_url=ollama_url
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing workflow...", total=None)

            if async_mode:
                result = asyncio.run(orchestrator.start_async(prompt))
            else:
                result = orchestrator.start(prompt)

            progress.update(task, completed=True)

        if result.get("success"):
            console.print("[bold green]✓ Workflow completed successfully![/bold green]")
            console.print("\n[bold]Agent Output:[/bold]")
            console.print(result.get("agent_output", {}).get("output", "No output"))
        else:
            console.print(f"[bold red]✗ Workflow failed:[/bold red] {result.get('error')}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
def stop():
    """Stop the running workflow."""
    cli_handler = CLI()
    state = cli_handler._load_state()

    if state.get("is_running"):
        console.print("[yellow]Stopping workflow...[/yellow]")
        state["is_running"] = False
        cli_handler._save_state(state)
        console.print("[bold green]✓ Workflow stopped[/bold green]")
    else:
        console.print("[yellow]No workflow is currently running[/yellow]")


@cli.command()
def status():
    """Check workflow status."""
    cli_handler = CLI()
    state = cli_handler._load_state()

    table = Table(title="Workflow Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Status", "Running" if state.get("is_running") else "Idle")
    table.add_row("Output Directory", str(Path("output").absolute()))
    table.add_row("Model", state.get("model", "Not set"))

    console.print(table)


@cli.command()
@click.argument("audio_files", nargs=-1, required=True)
@click.option(
    "--output-dir",
    "-o",
    default="output/midi",
    help="Output directory for MIDI files"
)
@click.option(
    "--add-to-fl",
    is_flag=True,
    help="Automatically add to FL Studio"
)
def convert(audio_files: tuple, output_dir: str, add_to_fl: bool):
    """Convert audio files to MIDI."""
    console.print(f"[cyan]Converting {len(audio_files)} audio file(s) to MIDI...[/cyan]")

    orchestrator = WorkflowOrchestrator()

    with Progress(console=console) as progress:
        task_id = progress.add_task("Converting...", total=len(audio_files))

        result = orchestrator.process_audio_batch(
            list(audio_files),
            add_to_fl_studio=add_to_fl
        )

        progress.update(task_id, completed=len(audio_files))

    # Display results
    table = Table(title="Conversion Results")
    table.add_column("Audio File", style="cyan")
    table.add_column("MIDI File", style="green")
    table.add_column("Status", style="yellow")

    for r in result.get("results", []):
        status = "✓" if r.get("success") else "✗"
        table.add_row(
            Path(r.get("audio_file", "")).name,
            Path(r.get("midi_file", "N/A")).name if r.get("success") else "Failed",
            status
        )

    console.print(table)


@cli.command()
@click.option(
    "--model",
    "-m",
    default="mistral",
    help="Model to test"
)
def test_ollama(model: str):
    """Test Ollama connection."""
    console.print(f"[cyan]Testing Ollama connection with model: {model}[/cyan]")

    try:
        from langchain_community.llms import Ollama

        llm = Ollama(model=model)
        response = llm.invoke("Hello, please respond with 'Connection successful!'")

        console.print("[bold green]✓ Ollama connection successful![/bold green]")
        console.print(f"Response: {response}")

    except Exception as e:
        console.print(f"[bold red]✗ Ollama connection failed:[/bold red] {str(e)}")
        console.print("\n[yellow]Make sure:[/yellow]")
        console.print("1. Ollama is installed")
        console.print(f"2. Model '{model}' is pulled: ollama pull {model}")
        console.print("3. Ollama service is running")


if __name__ == "__main__":
    cli()
