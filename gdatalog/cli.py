import dataclasses
import typer

from functools import reduce
from pathlib import Path
from typing import List

from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from dumbo_utils.console import console
from dumbo_utils.validation import validate

from gdatalog.delta_terms import Probability
from gdatalog.program import Program, Repeat, SmallRepeat


@dataclasses.dataclass(frozen=True)
class AppOptions:
    program: Program = dataclasses.field(default=Program(""))
    debug: bool = dataclasses.field(default=False)


app_options = AppOptions()
app = typer.Typer()


def is_debug_on():
    return app_options.debug


def run_app():
    try:
        app()
    except Exception as e:
        if is_debug_on():
            raise e
        else:
            console.print(f"[red bold]Error:[/red bold] {e}")


@app.callback()
def main(
        filenames: List[Path] = typer.Option(
            ...,
            "--filename",
            "-f",
            help="One or more files to parse",
        ),
        number_of_models: int = typer.Option(
            0,
            "--number-of-models",
            "-n",
            help="Maximum number of stable models to compute (0 for unbounded)"
        ),
        debug: bool = typer.Option(False, "--debug", help="Don't minimize browser"),
):
    """
    Generative Datalog with negation under stable model semantics.
    """
    global app_options

    validate('number_of_models', number_of_models, min_value=0)
    for filename in filenames:
        validate('filenames', filename.exists() and filename.is_file(), equals=True,
                       help_msg=f"File {filename} does not exists")

    lines = []
    for filename in filenames:
        with open(filename) as f:
            lines += f.readlines()
    program = Program('\n'.join(lines), max_stable_models=number_of_models)

    app_options = AppOptions(
        program=program,
        debug=debug,
    )


@app.command(name="run")
def command_run() -> None:
    """
    Run the program once and print stable models.
    """
    with console.status("Running..."):
        res = app_options.program.sms()

    probability = reduce(lambda p, d: p * d.probability, res.delta_terms, Probability.of(1, 1))
    console.print(Panel(
        '\n'.join(str(term) for term in res.delta_terms),
        title=f"Delta Terms - probability of this outcome {probability}",
        title_align="left",
    ))
    if res.state.satisfiable:
        for index, model in enumerate(res.models, start=1):
            console.print(Panel('\n'.join(str(atom) for atom in model), title=f"Model {index} of {len(res.models)}",
                                title_align="left"))
    else:
        console.print('NO STABLE MODELS')


@app.command(name="repeat")
def command_repeat(
        number_of_times: int = typer.Option(1000, "--number-of-times", "-n", help="Number of runs"),
        update_frequency: int = typer.Option(100, "--update-frequency", "-u", help="Update table every N runs"),
        small_enumeration: bool = typer.Option(
            False, "--small-enumeration", "-s",
            help="Activate small delta enumeration (unpredictable behavior in case of non-small delta-terms)"
        )
) -> None:
    """
    Run the program multiple times and print stats (frequency analysis).
    """
    validate('number_of_times', number_of_times, min_value=1)
    validate('update_frequency', update_frequency, min_value=1)

    def stats_table(repeat_result: Repeat | SmallRepeat):
        freq = repeat_result.sets_of_stable_models_frequency()

        table = Table(title=f"Stats on {repeat_result.number_of_calls} runs")
        table.add_column("Probability", justify="right")
        table.add_column("Model #", justify="center")
        table.add_column("Model")
        for (probability, models) in sorted(freq.values(), key=lambda x: x[0], reverse=True):
            if len(models) == 0:
                table.add_row(f"{probability}", "0")
                table.add_row()
                continue
            for model_index, model in enumerate(models, start=1):
                if len(model) == 0:
                    table.add_row(
                        f"{probability}" if model_index == 1 else "",
                        f"{model_index}/{len(models)}"
                    )
                    table.add_row()
                    continue
                for atom_index, atom in enumerate(sorted(model, key=lambda m: str(m)), start=1):
                    table.add_row(
                        f"{probability}" if model_index == atom_index == 1 else "",
                        f"{model_index}/{len(models)}" if atom_index == 1 else "",
                        f"{atom}",
                    )
                table.add_row()

        progress = Progress(console=console)
        progress.add_task("Repeating...", completed=res.number_of_calls, total=number_of_times)

        grid = Table.grid()
        if res.number_of_calls < number_of_times:
            grid.add_row(progress)
        grid.add_row(table)
        return grid

    to_be_done = number_of_times
    with Live(console=console) as live:
        repeat_class = SmallRepeat if small_enumeration else Repeat
        res = repeat_class.on(app_options.program)
        live.update(stats_table(res))

        while to_be_done > 0:
            n = min(to_be_done, update_frequency)
            early_stop = res.repeat(n)
            if early_stop:
                to_be_done = 0
                number_of_times = res.number_of_calls
            else:
                to_be_done -= n
            live.update(stats_table(res))



