def entrypoint(output_path: str):
    import threading
    import sys

    ALL_THREADS = bool(ALL_THREADS_PLACEHOLDER)
    stack_trace = get_traceback(ALL_THREADS)
    for thr in threading.enumerate():
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
            #  _native_id is only from python3.8+
            replacement_str = f"{thr.getName()} tid:{thr._native_id}"
        else:
            replacement_str = f"{thr.getName()} thread identity:{thr._ident}"
        thread_id_str = '0x{:016x}'.format(thr._ident)
        stack_trace = stack_trace.replace(thread_id_str, replacement_str)
    stack_trace = stack_trace.replace(thread_id_str, replacement_str)
    with open(output_path, "w+") as output_file:
        output_file.write(stack_trace)


def get_traceback(all_threads: bool):
    import tempfile
    import faulthandler
    with tempfile.TemporaryFile() as tmp:
        faulthandler.dump_traceback(file=tmp, all_threads=all_threads)
        tmp.seek(0)
        return tmp.read().decode("utf-8")

