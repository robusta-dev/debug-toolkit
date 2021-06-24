This repo contains source code for the `docker container` that powers Robusta features like:

1. RobustaPod.get_processes()
2. The python_profiler playbook

Essentially, it is just a small docker container with a useful python script that Robusta runs on the same node as the pod you want to debug.