from subprocess import getoutput, run, CalledProcessError
from os import environ
import re
from justniffer.logging import logger

compatible_justniffer_version = '0.6.6'
compatible_python_version = '3.10'


def justniffer_cmd() -> str:
    return 'justniffer'


def get_justniffer_version() -> str:
    res = getoutput(f'{justniffer_cmd()} --version')
    return res


def _extract_versions(text: str) -> tuple[str, str]:
    python_version = re.search(r'Python (\d+\.\d+)', text)
    justniffer_version = re.search(r'justniffer (\d+\.\d+\.\d+)', text)
    if justniffer_version is None or python_version is None:
        raise Exception('Failed to parse justniffer version')
    return justniffer_version.group(1), python_version.group(1)


def check_justniffer_version() -> None:
    version = get_justniffer_version()
    justniffer_version, python_version = _extract_versions(version)
    logger.debug(f'justniffer version: {justniffer_version}')
    logger.debug(f'python version: {python_version}')
    if justniffer_version < compatible_justniffer_version:
        raise Exception(f'Incompatible justniffer version: {justniffer_version}, expected: {compatible_justniffer_version}')
    if python_version < compatible_python_version:
        raise Exception(f'Incompatible python version: {python_version}, expected: {compatible_python_version}')


def exec_justniffer_cmd(*,interface: str | None, filecap: str | None) -> None:
    args = []
    if interface is not None:
        args.append(f'-i {interface}')
    if filecap is not None:
        args.append(f'-f {filecap}')
    args_str = ' '.join(args)
    cmd = f'sudo -E {justniffer_cmd()} {args_str} -l "%python(justniffer.handlers)"'
    logger.debug(cmd)
    check_justniffer_version()
    try:
        run(cmd, shell=True, check=True)
    except CalledProcessError as e:
        if e.returncode != 139:
            raise
