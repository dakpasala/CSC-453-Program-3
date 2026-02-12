# imports, im gonna use venv but idk how python works on unix servers....
from collections import deque
import sys

# intial data structures (so much easier than C thank god)

def main():
    page_table_size = 28
    page_table = [
        {"frame": None, "present": False}
        for _ in range(page_table_size)
    ]

    tlb_size = 16
    tlb = deque(maxlen=tlb_size)

    frames = 256
    physical_memory = [
        bytearray(256)
        for _ in range(frames)
    ]

    frame_to_page = [None] * frames

    free_frames = list(range(frames))

    last_used = {}
    time_counter = 0

    victim_page = min(last_used, key=last_used.get)
    reference_list = []

    total_addresses = page_faults = tlb_hits = tlb_misses = 0


    # parsing

    if len(sys.argv) < 2:
        print("usage has to be : ./memsim <referenceFile.txt> <frames> <pra>")
        sys.exit(1)

    reference_file = sys.argv[1]

    pra = "FIFO"

    if len(sys.argv) >= 3: frames = int(sys.argv[2])
    if len(sys.argv) >= 4: pra = sys.argv[3]

    if frames <= 0 or frames > 256:
        print("frames have to be in between 1 and 256")
        sys.exit(1)

    if pra not in ["FIFO", "LRU", "OPT"]:
        print("pra has to be FIFO, LRU, or OPT")
        sys.exit(1)

if __name__ == "__main__":
    main()
