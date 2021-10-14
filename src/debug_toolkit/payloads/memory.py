def entrypoint(output_path: str):
    import time
    import json
    import tracemalloc

    SECONDS = int(SECONDS_PLACEHOLDER)

    limit = 10
    tracemalloc.start(15)
    base_snapshot = tracemalloc.take_snapshot()
    time.sleep(SECONDS)
    snapshot = tracemalloc.take_snapshot()
    overhead = tracemalloc.get_tracemalloc_memory()
    tracemalloc.stop()

    #snapshot = snapshot.filter_traces(
    #    (
    #        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
    #        #tracemalloc.Filter(False, "<unknown>"),
    #    )
    #)
    stats = snapshot.compare_to(base_snapshot, "traceback")
    top_stats = stats[:limit]
    other_stats = stats[limit:]

    data = [{"size": s.size, "count": s.size, "traceback": s.traceback.format()} for s in top_stats]
    other_data = {"size": sum(s.size for s in other_stats), "count": sum(s.size for s in other_stats)}
    total = sum(s.size for s in top_stats)

    with open(output_path, "w") as output_file:
        output_file.write(json.dumps({"data": data, "other_data" : other_data, "total": total, "overhead": overhead}))
