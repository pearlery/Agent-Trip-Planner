import sys
import io
import datetime
from rich.console import Console
from rich.panel import Panel

# Force UTF-8 on Windows so Thai characters render correctly
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console()


def _ts():
    return datetime.datetime.now().strftime("%H:%M:%S")


def log_step(step_type: str, content: str, color: str = "cyan"):
    console.print(f"[dim]{_ts()}[/dim] [{color}][{step_type}][/{color}] {content}")


def log_thought(thought: str):
    console.print(Panel(thought.strip(), title="[yellow]Thought[/yellow]", border_style="yellow"))


def log_action(action: str, action_input: dict):
    body = f"Tool: [bold cyan]{action}[/bold cyan]\nInput: {action_input}"
    console.print(Panel(body, title="[cyan]Action[/cyan]", border_style="cyan"))


def log_observation(observation: str):
    preview = observation[:800] + "..." if len(observation) > 800 else observation
    console.print(Panel(preview, title="[green]Observation[/green]", border_style="green"))


def log_final_answer(answer: str):
    console.print(Panel(answer, title="[bold magenta]Final Answer[/bold magenta]", border_style="magenta"))


def log_retrieved_docs(docs: list, scores: list, metadatas: list = None):
    console.print("\n[bold blue]--- Retrieved Documents ---[/bold blue]")
    for i, (doc, score) in enumerate(zip(docs, scores), 1):
        meta = metadatas[i - 1] if metadatas else {}
        if meta.get("program_tour"):
            meta_line = (
                f"[magenta]{meta.get('program_tour', '')}[/magenta]  "
                f"ราคา:[yellow]{meta.get('price', '-')}[/yellow]  "
                f"region:[cyan]{meta.get('region', '-')}[/cyan]"
            )
        else:
            meta_line = f"source:[blue]{meta.get('source', 'unknown')}[/blue]"
        console.print(f"  [dim][{i}][/dim] Score: [green]{score:.4f}[/green]  {meta_line}")
        console.print(f"      {doc[:200].strip()}...")
    console.print()
