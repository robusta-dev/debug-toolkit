# TL;DR
A modern code-injection framework for Python + useful utilities.

This is like [Pyrasite](https://github.com/lmacken/pyrasite) but without the bugs and Kubernetes-aware.

This powers many [Robusta](http://robusta.dev/) features. You should probably use Robusta instead of using this directly.

# Overview
This repo contains source code for the docker container that powers the following [Robusta](http://robusta.dev/) features:

1. Inject code into Python apps
2. [Attach a VSCode debugger to any Python application running on Kubernetes](https://docs.robusta.dev/master/catalog/actions/python-troubleshooting.html#python-debugger)
3. [Profile cpu and memory usage of Python apps](https://docs.robusta.dev/master/catalog/actions/python-troubleshooting.html#python-profiler)
4. List processes in any pod (not just Python)
 
Essentially, it is two things:
1. A [Pyrasite](https://github.com/lmacken/pyrasite) replacement that fixes deadlocks and other issues.
2. A Docker container containing that Pyrasite replacement, which is used by Robusta to troubleshoot and debug containers

# Adding new python injection payloads
1. Add a new payload in src/debug_toolkit/payloads
   1. Make sure ALL of your code is inside the `entrypoint` function, even imports. Errors are not handled or reported for code outside of the entrypoint.
2. Add a wrapper command in src/debug_toolkit/main.py

# Releasing a new version

1. Bump the version in pyproject.toml 
2. Run the following, replacing "v4" with the tag of the new release.

```
skaffold build --tag v4
```

That is all. We're not pushing versions to pypi right now.
