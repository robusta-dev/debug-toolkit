#!/usr/local/bin/python3
import os
import re
import secrets
import subprocess
import tempfile
import textwrap
import time
import pkgutil
from pathlib import Path
from typing import List, Optional
from enum import Enum

import psutil
import typer
from pydantic import BaseModel

app = typer.Typer()


class Process(BaseModel):
    pid: int
    exe: str
    cmdline: List[str]


class ProcessList(BaseModel):
    processes: List[Process]


def is_process_in_pod(pid: int, pod_id: str, container_ids: List[str]) -> bool:
    # see https://man7.org/linux/man-pages/man7/cgroups.7.html
    # and https://github.com/elastic/apm-agent-python/blob/main/elasticapm/utils/cgroup.py
    all_ids = [pod_id.lower(), *container_ids]
    all_ids = [id.lower() for id in all_ids]

    try:
        path = f"/proc/{pid}/cgroup"
        with open(path, "r") as f:
            content = f.read().lower()
            if any(id in content for id in all_ids):
                return True
    except Exception as e:
        print("exception:", e)
    return False


def get_pod_processes(pod_id: str, container_ids: Optional[List[str]]) -> ProcessList:
    processes = []
    if container_ids is None:
        container_ids = []

    for pid in psutil.pids():
        if is_process_in_pod(pid, pod_id, container_ids):
            proc = psutil.Process(pid)
            processes.append(Process(pid=pid, exe=proc.exe(), cmdline=proc.cmdline()))
    return ProcessList(processes=processes)


@app.command()
def pod_ps(pod_id: str, container_ids: Optional[List[str]] = typer.Argument(None)):
    typer.echo(get_pod_processes(pod_id, container_ids).json())


@app.command()
def find_pid(pod_id: str, cmdline: str, exe: str, container_ids: Optional[List[str]] = typer.Argument(None)):
    for proc in get_pod_processes(pod_id, container_ids).processes:
        if cmdline in " ".join(proc.cmdline) and exe in proc.exe:
            typer.echo(proc.pid)


def do_injection(pid, python_code, verbose):
    python_code = (
        python_code.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    )

    batch_file = tempfile.NamedTemporaryFile(delete=False)
    # see https://github.com/microsoft/debugpy/blob/1de552631756b2d32010595c2e605aa491532250/src/debugpy/_vendored/pydevd/pydevd_attach_to_process/add_code_to_python_process.py#L307
    batch_file.write(
        textwrap.dedent(
            f"""\
            set trace-commands on
            set logging on
            set scheduler-locking off
            call ((int (*)())PyGILState_Ensure)()
            call ((int (*)(const char *))PyRun_SimpleString)("{python_code}")
            call ((void (*) (int) )PyGILState_Release)($1)
            """
        ).encode()
    )
    batch_file.flush()
    batch_file.close()

    cmd = f"gdb -p {pid} --batch --command={batch_file.name}"
    if verbose:
        typer.echo(f"running gdb with cmd {cmd}")

    # we don't properly catch errors like trying to debug a non existent process
    # we just wait for them later... fix this by both creating a _start file and by checking stderr / error code
    output = subprocess.check_output(
        cmd, shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    
    if verbose:
        typer.echo(output.decode())


def do_trampoline_injection(pid, payload, verbose, timeout=120):
    output_filename = f"{secrets.token_hex(16)}_output.txt"
    done_filename = f"{secrets.token_hex(16)}_done.txt"
    abs_done_path = f"/proc/{pid}/cwd/{done_filename}"
    abs_output_path = f"/proc/{pid}/cwd/{output_filename}"

    trampoline = pkgutil.get_data(__package__, "trampolines/simple.py").decode()
    trampoline = trampoline.replace("OUTPUT_PATH_PLACEHOLDER", f"./{output_filename}")
    trampoline = trampoline.replace("DONE_PATH_PLACEHOLDER", f"./{done_filename}")
    payload = f"{payload}\n\n{trampoline}"

    if verbose:
        typer.echo("Code to inject is:")
        typer.secho(payload, fg="blue")

    do_injection(pid, payload, verbose)
    if verbose:
        typer.secho("Done injecting", fg="green")

    for i in range(timeout):
        if os.path.exists(abs_done_path):
            break
        if verbose:
            typer.echo(f"waiting for {abs_done_path} to exist")
        time.sleep(1)

    if not os.path.exists(abs_done_path):
        typer.secho(f"ERROR! Timed out after {timeout} seconds", fg="red")

    with open(abs_done_path, "r") as f:
        status = f.read().strip()
        if status != "SUCCESS" or verbose:
            typer.secho(f"done status is {status}")

    if os.path.exists(abs_output_path):
        with open(abs_output_path, "rb") as f:
            result = f.read()
        typer.echo(result.decode())
    else:
        result = None

    if os.path.exists(abs_output_path):
        os.remove(abs_output_path)
    if os.path.exists(abs_done_path):
        os.remove(abs_done_path)
    return result


@app.command()
def inject_string(
    pid: int,
    payload: str,
    trampoline: bool = False,
    trampoline_timeout: int = 120,
    verbose: bool = False,
):
    if not trampoline:
        return do_injection(pid, payload, verbose)
    else:
        return do_trampoline_injection(pid, payload, verbose, trampoline_timeout)


@app.command()
def inject_file(
    pid: int,
    payload_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    trampoline: bool = False,
    trampoline_timeout: int = 120,
    verbose: bool = False,
):
    with open(payload_path) as f:
        return inject_string(pid, f.read(), trampoline, trampoline_timeout, verbose)


@app.command()
def memory(pid: int, seconds: int = 60, verbose: bool = False):
    payload = pkgutil.get_data(__package__, "payloads/memory.py").decode()
    payload = payload.replace("SECONDS_PLACEHOLDER", str(seconds))
    timeout_seconds = int(seconds * 1.1 + 10)
    inject_string(pid, payload, trampoline=True, trampoline_timeout=timeout_seconds, verbose=verbose)


@app.command()
def stack_trace(pid: int, all_threads: bool = True, verbose: bool = False):
    payload = pkgutil.get_data(__package__, "payloads/stack_trace.py").decode()
    payload = payload.replace("ALL_THREADS_PLACEHOLDER", str(all_threads))
    inject_string(pid, payload, trampoline=True, trampoline_timeout=10, verbose=verbose)


@app.command()
def debugger(pid: int, port: int = 5678, verbose: bool = False):
    payload = pkgutil.get_data(__package__, "payloads/debugger.py").decode()
    payload = payload.replace("LISTENING_PORT_PLACEHOLDER", str(port))
    timeout_seconds = 120  # might take time for payload to install debugpy
    inject_string(pid, payload, trampoline=True, trampoline_timeout=timeout_seconds, verbose=verbose)


class LoggingLevel (Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@app.command()
def set_logging_level(pid: int, level: LoggingLevel, verbose: bool = False):
    payload = pkgutil.get_data(__package__, "payloads/set_logging_level.py").decode()
    payload = payload.replace("LOGGING_LEVEL_PLACEHOLDER", level.value)
    inject_string(pid, payload, trampoline=True, trampoline_timeout=10, verbose=verbose)


if __name__ == "__main__":
    app()
