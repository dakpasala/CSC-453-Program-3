#!/usr/bin/env python3

from collections import deque
import sys

def main():

    if len(sys.argv) < 2:
        print("usage: ./memSim <referenceFile.txt> [frames] [pra]")
        sys.exit(1)

    reference_file = sys.argv[1]

    frames = 256
    pra = "FIFO"

    if len(sys.argv) >= 3:
        frames = int(sys.argv[2])

    if len(sys.argv) >= 4:
        pra = sys.argv[3]

    if frames <= 0 or frames > 256:
        print("frames must be between 1 and 256")
        sys.exit(1)

    if pra not in ["FIFO", "LRU", "OPT"]:
        print("pra must be FIFO, LRU, or OPT")
        sys.exit(1)

    page_table_size = 28
    page_table = [
        {"frame": None, "present": False}
        for _ in range(page_table_size)
    ]

    tlb_size = 16
    tlb = deque(maxlen=tlb_size)

    physical_memory = [
        bytearray(256)
        for _ in range(frames)
    ]

    frame_to_page = [None] * frames
    free_frames = list(range(frames))

    last_used = {}
    time_counter = 0

    reference_list = []

    total_addresses = 0
    page_faults = 0
    tlb_hits = 0
    tlb_misses = 0

    with open(reference_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                reference_list.append(int(line))

    backing_store = open("BACKING_STORE.bin", "rb")

    print("Initialization complete.")
    print(f"Frames: {frames}")
    print(f"PRA: {pra}")
    print(f"Loaded {len(reference_list)} addresses")


if __name__ == "__main__":
    main()
