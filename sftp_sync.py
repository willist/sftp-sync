import stat
from pathlib import Path

import pysftp


class SftpSync:
    def __init__(self, host, username, password, known_hosts='./known_hosts'):
        self.host = host
        self.username = username
        self.password = password
        self.known_hosts = known_hosts
        self._failures = []

    def __enter__(self):
        cnopts = pysftp.CnOpts(knownhosts=self.known_hosts)
        self._sftp = pysftp.Connection(self.host, username=self.username, password=self.password, cnopts=cnopts)
        return self

    def __exit__(self, type, value, tb):
        self._sftp.close()

    def sync(self, remote, local):
        print()
        remote_path = Path(remote)
        local_path = Path(local)

        parents = len(local_path.parents) - 1
        prefix = ('  ' * parents + '\u231E') if parents else ''
        print(f'{prefix} {local_path.name}', end="")

        self._sftp.cwd(str(remote_path))
        local_path.mkdir(exist_ok=True)

        for f in self._sftp.listdir_attr():
            remote_file = remote_path.joinpath(f.filename)
            local_file = local_path.joinpath(f.filename)

            if stat.S_ISDIR(f.st_mode):
                self.sync(remote_file, local_file)
                continue

            try:
                assert local_file.exists(), "Not Found"
                assert f.st_mtime < local_file.stat().st_mtime, "Outdated"
                print(".", end="")
                continue
            except AssertionError as e:
                print("D", end="")

            try:
                self._sftp.get(f.filename, str(local_file))
            except Exception as e:
                print("E", end="")
                self._failures.append({'file': local_file, 'error': e})
