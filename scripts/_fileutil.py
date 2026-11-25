"""Shared helpers: an exclusive file lock and atomic writes. Standard library only, Python 3.8+."""
import os
import sys
import tempfile
from pathlib import Path


class Lock(object):
    """Exclusive lock via fcntl; without fcntl (Windows) it runs without a lock and warns."""

    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(str(self.path), "a+")
        try:
            import fcntl
            fcntl.flock(self.f, fcntl.LOCK_EX)
            self.fcntl = fcntl
        except ImportError:
            self.fcntl = None
            print("(warning: fcntl is missing, concurrent windows are not guarded)", file=sys.stderr)
        return self

    def __exit__(self, *a):
        if self.fcntl:
            self.fcntl.flock(self.f, self.fcntl.LOCK_UN)
        self.f.close()


def atomic_write(path, text):
    """Write a temp file in the same directory, then os.replace it over the target."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        if path.exists():
            os.chmod(tmp, path.stat().st_mode & 0o7777)
        else:
            um = os.umask(0)
            os.umask(um)
            os.chmod(tmp, 0o666 & ~um)  # mkstemp creates 0600; keep normal file permissions
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
