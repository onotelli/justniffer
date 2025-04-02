from typer import Typer
from justniffer.logging import logger

app = Typer()

@app.command()
def decrypt_tls(encrypted_file: str, key_file: str):
    from justniffer import dec
    logger.info(f'Decrypting {encrypted_file=} with {key_file=}')
    res = dec.read_private_key( key_file)
    dec.decript_data_file(encrypted_file, res) # type: ignore
    
    breakpoint()
    logger.info(f'res = {res=}')
    
@app.command()
def capture(interface: str = 'any', filter: str | None = None):
    from subprocess import run
    from shlex import split    
    filter_option = (f'-p "{filter}"') if filter is not None else ""
    from loguru import logger
    cmd = f'justniffer  -i {interface}  -l "%python(justniffer.test2:Pippo2)" {filter_option}   -m -N'
    logger.info(f'Running {cmd}')
    run(split(cmd))

def main():
    app()       

