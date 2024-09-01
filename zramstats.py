#!/usr/bin/env python3
import argparse
import json

docs = """
 orig_data_size   uncompressed size of data stored in this disk.
                  This excludes same-element-filled pages (same_pages) since
                  no memory is allocated for them.
                  Unit: bytes
 compr_data_size  compressed size of data stored in this disk
 mem_used_total   the amount of memory allocated for this disk. This
                  includes allocator fragmentation and metadata overhead,
                  allocated for this disk. So, allocator space efficiency
                  can be calculated using compr_data_size and this statistic.
                  Unit: bytes
 mem_limit        the maximum amount of memory ZRAM can use to store
                  the compressed data
 mem_used_max     the maximum amount of memory zram have consumed to
                  store the data
 same_pages       the number of same element filled pages written to this disk.
                  No memory is allocated for such pages.
 pages_compacted  the number of pages freed during compaction
 huge_pages       the number of incompressible pages
"""

suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]


def size(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return "%s %s" % (f, suffixes[i])


def main(args):
    swaps = []
    stats = {}

    with open("/sys/block/zram0/mm_stat", "r") as f:
        d = f.read().strip().split()
        stats = {
            "orig_data_size": int(d[0]),
            "compr_data_size": int(d[1]),
            "mem_used_total": int(d[2]),
            "mem_limit": int(d[3]),
            "mem_used_max": int(d[4]),
            "same_pages": int(d[5]),
            "pages_compacted": int(d[6]),
            "huge_pages": int(d[7]),
            "compression_ratio": int(d[0]) / int(d[1]),
        }

    with open("/proc/swaps", "r") as f:
        lines = f.read().strip().split("\n")[1:]
        for s in lines:
            s = s.split()
            swaps.append(
                {"name": s[0], "size": int(s[2]) * 1024, "used": int(s[3]) * 1024}
            )

    if args.json:
        print(json.dumps(stats))
        return

    for k, v in stats.items():
        if v > 10000:
            h = size(v)
        else:
            h = v
        print(f"{k:18}{h}")

    if args.verbose:
        print(docs)
    else:
        print()

    for s in swaps:
        used = size(s["used"])
        siz = size(s["size"])
        print(f"{s['name']:18}{used:8} [{siz}]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="zramstats")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    main(args)
