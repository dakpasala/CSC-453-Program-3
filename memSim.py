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

def get_page_offset(logical_address):
    page = (logical_address >> 8) & 0xFF
    offset = logical_address & 0xFF
    return page, offset

def main():
    global page_table, tlb, physical_memory
    global frame_to_page, free_frames
    global frames, pra, backing_store


    reference_file = sys.argv[1]
    frames = int(sys.argv[2])
    pra = sys.argv[3]

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
            line = line.strip()
            if line:
                logical_address = int(line)
                page, offset = get_page_offset(logical_address)

                print(f"logical address: {logical_address} maps to page: {page} and offset: {offset}")