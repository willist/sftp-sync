import click

from sftp_sync import SftpSync


@click.command()
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.argument('host')
@click.argument('remote_path')
@click.argument('local_path')
def run_sync(username, password, host, remote_path, local_path):
    with SftpSync(host, username, password) as sync:
        try:
            sync.sync(remote_path, local_path)
        finally:
            for failure in sync._failures:
                print(f'Failed to download {failure.file}: {failure.error}')


if __name__ == "__main__":
    run_sync()
