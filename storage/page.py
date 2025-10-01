import struct
from Typing import List, Tuple

PAGE_SIZE = 4096  # 4KB page size
PAGE_HEADER_FMT = '<IHH'  # page_id (4 bytes), slot_count (2 bytes), data_end_offset (2 bytes)
PAGE_HEADER_SIZE = struct.calcsize(PAGE_HEADER_FMT)
SLOT_ENTRY_FMT = '<HH'  # offset (2 bytes), length (2 bytes)
SLOT_ENTRY_SIZE = struct.calcsize(SLOT_ENTRY_FMT)

class Page:
    """
    Simple page:
    - Header at start (page_id, slot_counts, data_end_offset) (4+2+2 = 8 byte)
    - Record data grows from HEADER end (PAGE_HEADER_SIZE) upwards
    - Slot directory grows from PAGE_SIZE downwards ; each slot entry is 4 bytes (2 for offset, 2 for length) 
    - Free space is between record data and slot directory
    """

    def __init__(self, page_id:int):
        self.page_id = page_id
        self.slots: List[Tuple[int, int]] = []
        self.data_bytes = bytearray() # data_bytes stores concatenated record payloads in insertion order
        self.data_end_offset = PAGE_HEADER_SIZE # Points to the end of data_bytes in the page
