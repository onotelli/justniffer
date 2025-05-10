from typer import Typer, Option, Exit, echo
from justniffer.logging import logger

app = Typer()


def version_callback(value: bool):
    if value:
        import importlib.metadata
        __version__ = importlib.metadata.version('justniffer')
        from justniffer import commands
        echo(f'Justniffer CLI Version: {__version__}')
        echo(commands.get_justniffer_version())
        raise Exit()


@app.command()
def run(interface: str | None = None, filecap: str | None = None) -> None:
    from justniffer import commands
    commands.exec_justniffer_cmd(interface=interface, filecap=filecap)


@app.callback()
def common(
    version: bool = Option(None, '--version', callback=version_callback)
):
    pass


def main():
    app()
