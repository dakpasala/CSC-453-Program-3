#!/usr/bin/env python3

from math import inf
from collections import deque
import sys

# used for every algorithm
page_table = []
tlb = None
physical_memory = []
frame_to_page = []
free_frames = []

fifo_queue = deque() # only for FIFO
last_used = {} # only for LRU
future_values = [] # only for OPT
time_counter = 0 # tracking the time

total_addresses = page_faults = tlb_hits = tlb_misses = 0

frames = 256 # this was the default value that was mentioned on the spec
pra = "FIFO" # this was the default algo that was mentioned on the spec
backing_store = None


# ------------ TLB CRAP ------------
def tlb_lookup(page):
    global tlb
    for tlb_page, tlb_frame in tlb:
        if tlb_page == page:
            return tlb_frame
    
    return None

def tlb_insert(page, frame):
    global tlb
    tlb.append((page, frame))

def remove_from_tlb(page):
    global tlb
    tlb = deque([(p, f) for (p, f) in tlb if p != page], maxlen=16)

def translate_address(logical_address):
    global fifo_queue, page_table, physical_memory, frame_to_page, tlb, free_frames
    global page_faults, tlb_hits, tlb_misses
    global time_counter
    
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
            
            if free_frames: 
                frame = free_frames.pop(0)
                fifo_queue.append(frame)
            else:
                # this will be FIFO, OPT we gotta implement later on unfort
                if pra == "FIFO":
                    # if there are no frames, we then look at queue and pop
                    victim_frame = fifo_queue.popleft()
                    victim_page = frame_to_page[victim_frame]

                    # remove from tlb because now page doesn't map to frame anymore it can be on a diff frame 
                    remove_from_tlb(victim_page)

                    # page isn't being used anymore
                    page_table[victim_page]["present"] = False
                    frame = victim_frame

                    # append to existing queue
                    fifo_queue.append(frame)
                elif pra == "LRU":

                    # this thing tripped my ahh up but since we had the diagram from before i followed it better
                    victim_page = 0
                    min_time = inf

                    # track what's the minimum time and the index associated with it u know

                    for last_page, last_time in last_used.items():
                        if last_time < min_time:
                            min_time = last_time
                            victim_page = last_page
                    
                    last_used.pop(victim_page)
                    remove_from_tlb(victim_page)

                    frame = page_table[victim_page]["frame"]
                    page_table[victim_page]["present"] = False
                elif pra == "OPT":
                    # got to look at the future for all values

                    victim_page = 0
                    victim_addr = 0
                    max_distance = 0

                    # iterate thru current page table
                    for page, entry in enumerate(page_table):
                        # check if present else it's not there
                        if entry["present"]:

                            # this in case its the longest u know
                            # this is arguably the dirtiest code i've ever written this is my LC brain taking over
                            exists_in_future = False
                            for i in range(time_counter + 1, len(future_values)):
                                future_page, _ = get_page_offset(future_values[i])
                                if page == future_page:
                                    exists_in_future = True
                                    if i - time_counter > max_distance:
                                        max_distance = i - time_counter
                                        victim_page = page
                                        victim_addr = future_values[i]
                            
                            if not exists_in_future:
                                if len(future_values) - time_counter > max_distance:
                                    max_distance = len(future_values) - time_counter
                                    victim_page = page
                    
                    remove_from_tlb(victim_page)

                    print(f"victim page being removed: {victim_page}. this was addr: {victim_addr}")

                    frame = page_table[victim_page]["frame"]
                    page_table[victim_page]["present"] = False

            # this part i had to ask gpt, i was confused on what to store but i dont think it matters 
            backing_store.seek(page * 256)
            data = backing_store.read(256)

            physical_memory[frame] = bytearray(data)

            page_table[page]["frame"] = frame
            page_table[page]["present"] = True
            frame_to_page[frame] = page
        
        tlb_insert(page, frame)
    
    last_used[page] = time_counter
    
    physical_address = frame * 256 + offset
    value = physical_memory[frame][offset]

    time_counter += 1

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
    global total_addresses, page_faults, tlb_hits, tlb_misses

    print("program started")

    reference_file = sys.argv[1]
    n = len(sys.argv)
    
    if n >= 3: frames = int(sys.argv[2])
    print(frames)
    if n >= 4: pra = sys.argv[3]
    print(pra)

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
                total_addresses += 1
                logical_address = int(line)
                if pra != "OPT":
                    frame, physical_address, value = translate_address(logical_address)
                    frame_bytes = physical_memory[frame]
                    frame_hex = ''.join(f"{byte:02X}" for byte in frame_bytes)

                    print(f"{logical_address}, {value}, {frame}, {frame_hex}")
                else:
                    future_values.append(logical_address)
    
    # okay this is p simple implementation in main just check if it's OPT and then append to future_values and now we 
    # can iterate through it sick
    if pra == "OPT":
        for logical_address in future_values:
            frame, physical_address, value = translate_address(logical_address)
            frame_bytes = physical_memory[frame]
            frame_hex = ''.join(f"{byte:02X}" for byte in frame_bytes)

            print(f"{logical_address}, {value}, {frame}, {frame_hex}")   
    
    print(f"Number of Translated Addresses = {total_addresses}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {page_faults / total_addresses:.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {tlb_hits / total_addresses:.3f}")


if __name__ == "__main__":
    main()