from subprocess import PIPE, getoutput, run, CalledProcessError
import re
from os import getuid, environ
from justniffer.logging import logger
from pathlib import PosixPath
import sys

compatible_justniffer_version = '0.6.7'
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


def _get_sudoer_prefix() -> str:
    return ''
    if getuid() == 0:
        return ''
    else:
        # TODO: check if
        # 1. sudo is installed
        # 2. user is in sudoers
        # 3. if password is required 
        return 'sudo -E '


def exec_justniffer_cmd(*, interface: str | None,
                        filecap: str | None,
                        capture_filter: str | None,
                        capture_in_the_middle: bool) -> None:
    args = []
    if interface is not None:
        args.append(f'-i {interface}')
    if filecap is not None:
        args.append(f'-f {filecap}')
    if capture_filter is not None:
        args.append(f'-p {capture_filter}')
    if capture_in_the_middle:
        args.append('-m')

    args_str = ' '.join(args)
    if filecap is None:
        sudoer_prefix = _get_sudoer_prefix()
    else:
        sudoer_prefix = ''
    env = _find_virtualenv()
    cmd = f'{sudoer_prefix}{justniffer_cmd()} {args_str} -l "%python(justniffer.handlers)"'
    logger.debug(cmd)
    check_justniffer_version()
    try:
        run(cmd, shell=True, check=True, stderr=PIPE, env=env)
    except CalledProcessError as e:
        if e.returncode != 139:
            logger.error(e.stderr.decode('utf-8'))


VIRTUAL_ENV_VAR = 'VIRTUAL_ENV'


def _find_virtualenv() -> dict[str, str] | None:
    env: dict[str, str] | None = None
    if VIRTUAL_ENV_VAR not in environ:
        p = PosixPath(sys.executable)
        virtual_env = p.parent.parent
        env = {}
        env[VIRTUAL_ENV_VAR] = str(virtual_env)
    return env
