#!/usr/bin/env python3

from collections import deque
import sys

page_table = []
tlb = None
physical_memory = []
frame_to_page = []
free_frames = []
last_used = {}
time_counter = 0

total_addresses = page_faults = tlb_hits = tlb_misses= 0

frames = 256
pra = ""
backing_store = None


# ------------ TLB CRAP ------------
def tlb_lookup(page):
    for tlb_page, tlb_frame in tlb:
        if tlb_page == page:
            return tlb_frame
    
    return None

def tlb_insert(page, frame):
    tlb.append((page, frame))

def translate_address(logical_address):
    global page_faults, tlb_hits, tlb_misses
    
    # get the page and offset idk if we need offset
    page, offset = get_page_offset(logical_address)
    
    # check if it's in the TLB
    frame = tlb_lookup(page)

    if frame is not None: tlb_hits += 1
    else:
        tlb_misses += 1

        # check if page table is present or not, im not sure if this is correct or not, we can fix tho
        if page_table[page]["present"]:
            frame = page_table[page]["frame"]
        else:
            page_faults += 1
            
            if free_frames: frame = free_frames.pop(0)
            #else:
                # this will be FIFO, OPT we gotta implement later on unfort

                



            backing_store.seek(page * 256)
            data = backing_store.read(256)

            physical_memory[frame] = bytearray(data)

            page_table[page]["frame"] = frame
            page_table[page]["present"] = True
            frame_to_page[frame] = page
        
        tlb_insert(page, frame)
    
    physical_address = frame * 256 + offset
    value = physical_memory[frame][offset]

    return frame, physical_address, value

# ------------------------------------

def get_page_offset(logical_address):
    page = (logical_address >> 8) & 0xFF
    offset = logical_address & 0xFF
    return page, offset

def main():
    global page_table, tlb, physical_memory
    global frame_to_page, free_frames
    global frames, pra, backing_store

    print("program started")

    reference_file = sys.argv[1]
    if reference_file: print("good file")
    frames = int(sys.argv[2])
    pra = sys.argv[3]
    if len(pra) > 0: print("pra good")

    if frames <= 0 or frames > 256:
        print("frames are wrong try again")
        sys.exit(1)
    
    if pra not in ["FIFO", "LRU", "OPT"]:
        print("wrong algorithm cuh")
        sys.exit(1)
    
    # okay page_table
    page_table = [
        {"frame": None, "present": False}
        for _ in range(256)
    ]

    tlb = deque(maxlen=16)

    physical_memory = [
        bytearray(256)
        for _ in range(frames)
    ]

    frame_to_page = [None] * frames
    free_frames = list(range(frames))

    backing_store = open("BACKING_STORE.bin", "rb")

    with open(reference_file, "r") as f:
        for line in f:
            print(line)
            line = line.strip()
            if line:
                logical_address = int(line)
                frame, physical_address, value = translate_address(logical_address)

                print(f"logical address: {logical_address} maps to frame {frame}, value: {value}, and physical_address: {physical_address}")

if __name__ == "__main__":
    main()