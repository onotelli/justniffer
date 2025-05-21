from typer import Typer, Option, Exit, echo
from typing import Iterable, cast

app = Typer()


def version_callback(value: bool):
    if value:
        import importlib.metadata
        __version__ = importlib.metadata.version('justniffer-cli')
        from justniffer import commands
        from justniffer.logging import logger

        echo(f'Justniffer CLI Version: {__version__}')
        try:
            echo(commands.get_justniffer_version())
        except commands.VersionException as e:
            logger.error(f'{e}')
            pass
        raise Exit()


def _interfaces(incomplete: str) -> Iterable[str]:
    import psutil
    interfaces = list(psutil.net_if_addrs().keys()) + ['any']
    return [iface for iface in interfaces if iface.startswith(incomplete)]


@app.command()
def run(interface: str | None = Option(None, autocompletion=_interfaces),
        filecap: str | None = None,
        packet_filter: str | None = None,
        capture_in_the_middle: bool = False,
        config_filepath: str | None = None,
        formatter: str | None = Option(None, autocompletion=lambda: ('str', 'json'))) -> None:
    from justniffer import commands
    commands.exec_justniffer_cmd(interface=interface,
                                 filecap=filecap,
                                 packet_filter=packet_filter,
                                 capture_in_the_middle=capture_in_the_middle,
                                 config_filepath=config_filepath,
                                 formatter=formatter)


@app.callback()
def common(
    version: bool = Option(None, '--version', callback=version_callback)
):
    pass


def main():
    app()
