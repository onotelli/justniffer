from typer import Typer
from justniffer.logging import logger

app = Typer()

@app.command()
def decrypt_tls(encrypted_file: str, key_file: str):
    from justniffer import dec
    logger.info(f'Decrypting {encrypted_file=} with {key_file=}')
    res = dec.read_private_key( key_file)
    dec.decript_data_file(encrypted_file, res)
    
    breakpoint()
    logger.info(f'res = {res=}')
    

def main():
    app()       

