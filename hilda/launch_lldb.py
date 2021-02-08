from pathlib import Path
import time
import os

import click


def tunnel_local_port(port):
    os.system(f'nohup iproxy {port} {port} >/dev/null 2>&1 &')


@click.command()
@click.argument('process')
@click.argument('ssh_port', type=click.INT)
@click.option('--debug-port', type=click.INT, default=1234)
def main(process, ssh_port, debug_port):
    # startup debugserver at remote
    tunnel_local_port(debug_port)
    assert not os.system(f'ssh -p {ssh_port} root@localhost "debugserver localhost:{debug_port} --attach={process} &"&')

    # wait for it to load
    time.sleep(1)

    # connect local LLDB client
    commands = [f'process connect connect://localhost:{debug_port}',
                f'command script import {os.path.join(Path(__file__).resolve().parent, "lldb_entrypoint.py")}']
    commands = '\n'.join(commands)
    os.system(f'lldb --one-line "{commands}"')


if __name__ == '__main__':
    main()
