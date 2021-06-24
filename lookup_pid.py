#!/usr/local/bin/python3
import re
import typer
import psutil
from pydantic import BaseModel
from typing import List

kube_regex = re.compile(r'\d+:.+:/kubepods/[^/]+/pod([^/]+)/([0-9a-f]{64})')
docker_regex = re.compile(r'\d+:.+:/docker/pod([^/]+)/([0-9a-f]{64})')
other_regex = re.compile(r'\d+:.+:/docker/.*/pod([^/]+)/([0-9a-f]{64})')
other_regex2 = re.compile(r'\d+:.+:/kubepods/.*/pod([^/]+)/([0-9a-f]{64})')
other_regex3 = re.compile(r'\d+:.+:/kubepods\.slice/kubepods-[^/]+\.slice/kubepods-[^/]+-pod([^/]+)\.slice/docker-([0-9a-f]{64})')

app = typer.Typer()


class Process (BaseModel):
    pid: int
    exe: str
    cmdline: List[str]

class ProcessList (BaseModel):
    processes: List[Process]


def get_process_details(pid: int):
    # see https://man7.org/linux/man-pages/man7/cgroups.7.html
    try:
        path = "/proc/%d/cgroup" % (pid,)
        with open(path, "r") as f:
            lines = f.readlines()
            for line in lines:
                match = kube_regex.match(line) or docker_regex.match(line) or other_regex.match(line) or other_regex2.match(line) or other_regex3.match(line)
                if match is not None:
                    # pod, container
                    return match.group(1).replace("_", "-"), match.group(2)
    except Exception as e:
        print("exception:", e)
    return None, None


@app.command()
def get_processes_in_pod(desired_pod_uid: str, process_name_substring: str = None):
    processes = []

    for pid in psutil.pids():
        pod_uid, container_uid = get_process_details(pid)
        if pod_uid is not None and pod_uid.lower() == desired_pod_uid.lower():
            proc = psutil.Process(pid)
            processes.append(Process(pid=pid, exe=proc.exe(), cmdline=proc.cmdline()))
            #print("container_uid is", container_uid)

    typer.echo(ProcessList(processes=processes).json())


if __name__ == "__main__":
    app()
