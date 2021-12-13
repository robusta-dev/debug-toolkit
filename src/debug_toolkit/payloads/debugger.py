def entrypoint(output_path: str):
    import subprocess

    LISTENING_PORT = int(LISTENING_PORT_PLACEHOLDER)

    def install(package):
        subprocess.check_output(f"pip install {package}", shell=True)

    install("debugpy")
    import debugpy
    debugpy.listen(("0.0.0.0", LISTENING_PORT))

    with open(output_path, "w") as output_file:
        output_file.write(f"now listening for connections on port {LISTENING_PORT}")
