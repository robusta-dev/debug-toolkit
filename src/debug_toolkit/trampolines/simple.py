import threading

output_path = "OUTPUT_PATH_PLACEHOLDER"
done_path = "DONE_PATH_PLACEHOLDER"


def wrapper():
    try:
        entrypoint(output_path)
        exc = None
    except Exception as e:
        exc = e

    with open(done_path, "w") as done_file:
        if exc is None:
            done_file.write("SUCCESS")
        else:
            done_file.write(f"ERROR: {exc}")


thread = threading.Thread(target=wrapper, daemon=True)
thread.start()
