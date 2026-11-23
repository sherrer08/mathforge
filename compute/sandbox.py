import multiprocessing
import os
import resource

TIMEOUT_SECONDS = float(os.environ.get("COMPUTE_TIMEOUT_SECONDS", "3"))
MEMORY_LIMIT_BYTES = int(os.environ.get("COMPUTE_MEMORY_LIMIT_MB", "1024")) * 1024 * 1024

_ctx = multiprocessing.get_context("forkserver")
_ctx.set_forkserver_preload(["sympy", "safe_parser", "tasks"])

class ComputationTimeout(Exception):
    pass

class ComputationFailed(Exception):
    pass

def _child(conn, func, args):
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    try:
        conn.send(("ok", func(*args)))
    except MemoryError:
        conn.send(("error", ComputationFailed("Ran out of memory.")))
    except Exception as exc:
        conn.send(("error", exc))
    finally:
        conn.close()

def run_limited(func, *args, timeout: float | None = None):
    timeout = TIMEOUT_SECONDS if timeout is None else timeout
    parent_conn, child_conn = _ctx.Pipe(duplex=False)
    proc = _ctx.Process(target=_child, args=(child_conn, func, args), daemon=True)
    proc.start()
    child_conn.close()
    try:
        if not parent_conn.poll(timeout):
            raise ComputationTimeout()
        try:
            status, payload = parent_conn.recv()
        except EOFError:
            raise ComputationFailed("Computation crashed.")
    finally:
        if proc.is_alive():
            proc.kill()
        proc.join()
        parent_conn.close()
    if status == "error":
        raise payload
    return payload