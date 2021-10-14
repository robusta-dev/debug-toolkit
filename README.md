This repo contains source code for the docker container that powers the following Robusta features:

1. List processes in a pod
2. Profile cpu and memory usage of Python apps
3. Inject code into Python apps

Essentially, it is just a small docker container that Robusta runs on the same node as the pod you want to debug.

For historical reasons, the Docker image is named python-tools and not debug-toolkit. We'll probably fix that eventually.