import dataclasses
from pathlib import Path
from typing import List

import typer as typer
from rich.panel import Panel
from rich.table import Table

from gdatalog import utils
from gdatalog.program import Program, Repeat
from gdatalog.utils import console


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
        number_of_models: int = typer.Option(0, help="Maximum number of stable models to compute (0 for unbounded)"),
        debug: bool = typer.Option(False, "--debug", help="Don't minimize browser"),
):
    """
    Esse3 command line utility, to save my future time!
    """
    global app_options

    utils.validate('number_of_models', number_of_models, min_value=0)
    for filename in filenames:
        utils.validate('filenames', filename.exists() and filename.is_file(), equals=True,
                       help_msg=f"File {filename} does not exists")

    lines = []
    for filename in filenames:
        with open(filename) as f:
            lines += f.readlines()
    program = Program('\n'.join(lines))

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

    console.print(Panel('\n'.join(str(term) for term in res.delta_terms), title="Delta Terms", title_align="left"))
    if res.state.satisfiable:
        for index, model in enumerate(res.models, start=1):
            console.print(Panel('\n'.join(str(atom) for atom in model), title=f"Model {index} of {len(res.models)}",
                                title_align="left"))
    else:
        console.print('NO STABLE MODELS')


@app.command(name="repeat")
def command_repeat(
        number_of_times: int = typer.Option(100, "--number-of-times", "-n", help="Number of runs"),
) -> None:
    """
    Run the program multiple times and print stats (frequency analysis).
    """
    utils.validate('number_of_times', number_of_times, min_value=1)
    with console.status(f'Repeating {number_of_times} times...'):
        res = Repeat.on(app_options.program, number_of_times)

    freq = res.sets_of_stable_models_frequency()

    table = Table(title=f"Stats on {number_of_times} runs")
    table.add_column("Probability", justify="right")
    table.add_column("Model #", justify="center")
    table.add_column("Model")
    for (probability, models) in sorted(freq.values(), key=lambda x: x[0], reverse=True):
        if len(models) == 0:
            table.add_row(f"{probability}", "0")
            table.add_row()
            continue
        for model_index, model in enumerate(models, start=1):
            for atom_index, atom in enumerate(sorted(model, key=lambda m: str(m)), start=1):
                table.add_row(
                    f"{probability}" if model_index == atom_index == 1 else "",
                    f"{model_index}/{len(models)}" if atom_index == 1 else "",
                    f"{atom}",
                )
            table.add_row()
    console.print(table)
