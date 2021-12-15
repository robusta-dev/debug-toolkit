def entrypoint(output_path: str):
    import subprocess
    import json
    import sys
    import inspect

    LISTENING_PORT = int(LISTENING_PORT_PLACEHOLDER)
    EXISTING_LISTENING_PORT = "__DEBUG_TOOLS_LISTENING_PORT"

    def install(package):
        subprocess.check_output(f"pip install {package}", shell=True)

    def debug():
        install("debugpy")
        import debugpy

        if hasattr(debugpy, EXISTING_LISTENING_PORT):
            return f"Debugger already running on port {getattr(debugpy, EXISTING_LISTENING_PORT)}"

        try:
            debugpy.listen(("0.0.0.0", LISTENING_PORT))
            setattr(debugpy, EXISTING_LISTENING_PORT, LISTENING_PORT)
            return f"success"
        except Exception as e:
            return f"Error attaching a debugger. Did you already attach a debugger? If so, ignore this message. Error={e.args[0]}"

    def get_module_paths():
        return {name: inspect.getabsfile(module) for (name, module) in sys.modules.items()
                if getattr(module, "__file__", None)}

    message = debug()

    with open(output_path, "w") as output_file:
        output_file.write(json.dumps({
            "loaded_modules": get_module_paths(),
            "message": message,
        }))
