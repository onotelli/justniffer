from subprocess import PIPE, getstatusoutput, run, CalledProcessError
import re
from os import getuid, environ
from pathlib import PosixPath
import sys

from justniffer.logging import logger
from justniffer.config import load_config
from justniffer.settings import settings

compatible_justniffer_version = '0.6.7'
compatible_python_version = '3.10'
VIRTUAL_ENV_VAR = 'VIRTUAL_ENV'


def justniffer_cmd() -> str:
    return 'justniffer'


class VersionException(Exception):
    pass

class NotFoundJustniffer(VersionException):
    pass


def get_justniffer_version() -> str:
    status, res = getstatusoutput(f'{justniffer_cmd()} --version')
    if status == 127:
        raise NotFoundJustniffer( f'{justniffer_cmd()} not found')
    elif status != 0:        
        raise VersionException('Failed to get justniffer version')        
    return res


def _extract_versions(text: str) -> tuple[str, str]:
    python_version = re.search(r'Python (\d+\.\d+)', text)
    justniffer_version = re.search(r'justniffer (.+)', text)
    if justniffer_version is None or python_version is None:
        raise VersionException('Failed to parse justniffer version')
    return justniffer_version.group(1), python_version.group(1)


def check_justniffer_version() -> None:
    version = get_justniffer_version()
    justniffer_version, python_version = _extract_versions(version)
    logger.debug(f'justniffer version: {justniffer_version}')
    logger.debug(f'python version: {python_version}')
    if justniffer_version < compatible_justniffer_version:
        raise VersionException(f'Incompatible justniffer version: {justniffer_version}, expected: {compatible_justniffer_version}')
    if python_version < compatible_python_version:
        raise VersionException(f'Incompatible python version: {python_version}, expected: {compatible_python_version}')


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
                        packet_filter: str | None,
                        capture_in_the_middle: bool,
                        config_filepath: str | None,
                        formatter: str | None) -> None:

    args = []
    if interface is not None:
        args.append(f'-i {interface}')
    if filecap is not None:
        args.append(f'-f {filecap}')
    if packet_filter is not None:
        args.append(f'-p {packet_filter}')
    if capture_in_the_middle:
        args.append('-m')

    args_str = ' '.join(args)
    if filecap is None:
        sudoer_prefix = _get_sudoer_prefix()
    else:
        sudoer_prefix = ''
    env = _fix_virtualenv()
    cmd = f'{sudoer_prefix}{justniffer_cmd()} {args_str} -l "%python(justniffer.handlers)"'
    logger.debug(cmd)
    try:
        check_justniffer_version()
    except VersionException as e:
        logger.error(e)
        return
    if config_filepath is not None:
        env[settings.envvar_prefix_for_dynaconf + '_CONFIG_FILE'] = config_filepath
    if formatter is not None:
        env[settings.envvar_prefix_for_dynaconf + '_FORMATTER'] = formatter
    try:
        run(cmd, shell=True, check=True, env=env)
    except CalledProcessError as e:
        pass


def _fix_virtualenv() -> dict[str, str]:
    env: dict[str, str] = environ.copy()
    if VIRTUAL_ENV_VAR not in environ:
        p = PosixPath(sys.executable)
        virtual_env = p.parent.parent
        env[VIRTUAL_ENV_VAR] = str(virtual_env)
    return env
