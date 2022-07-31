def entrypoint(output_path: str):
    import time
    import json

    ALL_THREADS = bool(ALL_THREADS_PLACEHOLDER)
    AMOUNT = int(AMOUNT_PLACEHOLDER)
    SLEEP_DURATION_S = int(SLEEP_DURATION_S_PLACEHOLDER)

    thread_stack_dumps=[]
    for _ in range(AMOUNT):
        stack_trace = get_traceback(ALL_THREADS)
        formated_trace = format_stack_trace(stack_trace)
        thread_stack_dumps.append({"time": time.time(), "trace": formated_trace})
        time.sleep(SLEEP_DURATION_S)
    with open(output_path, "w+") as output_file:
        json_formatted_str = json.dumps(thread_stack_dumps, indent=4)
        output_file.write(json_formatted_str)


def format_stack_trace(stack_trace: str):

        import sys
        import threading
        try:
            for thr in threading.enumerate():
                thread_identity = thr._ident
                if not thread_identity:
                    continue
                if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
                    #  _native_id is only from python3.8+
                    replacement_str = f"{thr.getName()} tid:{thr._native_id}"
                else:
                    replacement_str = f"{thr.getName()} thread identity:{thread_identity}"

                thread_id_str = '0x{:016x}'.format(thread_identity)
                stack_trace = stack_trace.replace(thread_id_str, replacement_str)
        except Exception:
            # formatting sometimes can fail based on python version
            pass
        finally:
            return stack_trace



def get_traceback(all_threads: bool):
    import tempfile
    import faulthandler
    with tempfile.TemporaryFile() as tmp:
        faulthandler.dump_traceback(file=tmp, all_threads=all_threads)
        tmp.seek(0)
        return tmp.read().decode("utf-8")

