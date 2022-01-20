def entrypoint(output_path: str):
    import faulthandler

    ALL_THREADS = bool(ALL_THREADS_PLACEHOLDER)
    with open(output_path, "w+") as output_file:
        faulthandler.dump_traceback(file=output_file, all_threads=ALL_THREADS)


