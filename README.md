# Introduction
This repo contains source code for the docker container that powers the following Robusta features:

1. List processes in a pod
2. Profile cpu and memory usage of Python apps
3. Inject code into Python apps

Essentially, it is just a small docker container that Robusta runs on the same node as the pod you want to debug.

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