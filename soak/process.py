"""Bounded subprocess adapter; output is never retained beyond the byte limit."""
import os
import signal
import subprocess
import threading
import time


class OutputLimitError(ValueError):
    pass


def terminate(process):
    if os.name == "nt":
        if process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=5)


def invoke(command, payload, timeout, limit=65536):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=os.name != "nt")
    exceeded = threading.Event()
    buffers = [bytearray(), bytearray()]

    def read(stream, target):
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                if len(target) + len(chunk) > limit:
                    exceeded.set()
                    break
                target.extend(chunk)
        finally:
            stream.close()

    def write():
        try:
            process.stdin.write(payload.encode("utf-8"))
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    readers = [threading.Thread(target=read, args=(stream, target), daemon=True)
               for stream, target in zip((process.stdout, process.stderr), buffers)]
    writer = threading.Thread(target=write, daemon=True)
    for thread in readers + [writer]:
        thread.start()
    deadline = time.monotonic() + timeout
    try:
        while process.poll() is None or any(t.is_alive() for t in readers):
            if exceeded.is_set():
                raise OutputLimitError("adapter output limit exceeded")
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(command, timeout)
            time.sleep(0.005)
        if exceeded.is_set():
            raise OutputLimitError("adapter output limit exceeded")
        return subprocess.CompletedProcess(command, process.returncode, buffers[0].decode("utf-8"), "")
    finally:
        terminate(process)
        for thread in readers + [writer]:
            thread.join(timeout=1)
