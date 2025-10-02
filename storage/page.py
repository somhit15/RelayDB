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

    ## we need to calculate the free space and return
    ## -> page_size = 4096 and the slot_dir starts from end and captures 4bytes each, so 1 slot = 4 byte
    ## now , slot_dir_start = page_size - len(self.slots)*slot_entry_size ==> 4096 - 0*4 = 4096 (initially)
    # suppose, slot used = 2, so far, -> slot_dir_start = 4096 - 2*4 = 4088 (2 slots consumes , -> slot index 0 and 1)
    #  now, next_slot_dir_start = page_size - (len(self.slots)+1)*slot_entry_size ==> 4096 - (2+1)*4 = 4084
    # we are adding +1 because , while inserting data/record, we are intersing the slots entry as well, so the +1 is for reserving the next slot size (4byte)

    def free_space(self) -> int:
        slot_dir_start = PAGE_SIZE - len(self.slots)*SLOT_ENTRY_SIZE
        next_slot_dir_start = PAGE_SIZE - (len(self.slots)+1)*SLOT_ENTRY_SIZE
        free_space = next_slot_dir_start - self.data_end_offset
        return free_space

    
    def has_space_for(self, record_len : int) -> bool:
        required_space = record_len + SLOT_ENTRY_SIZE
        return self.free_space() >= required_space
        #eg.4096>10
    
    
    def insert(self, record_bytes : bytes) -> int:
        rlen = len(record_bytes)

        if not self.has_space_for(rlen):
            raise ValueError("Not enough space in the page to insert the record.")
        
        # Insert the record data
        current_offset_in_page = self.data_end_offset

        self.data_bytes.extend(record_bytes)

        self.data_end_offset += rlen

        self.slots.append((current_offset_in_page, rlen))

        slot_number = len(self.slots)-1
        return slot_number


    
    def read(self, slot_no: int) -> bytes:
        if slot_no < 0 or slot_no >= len(self.slots):
            raise IndexError("Invalid slot number.")
        
        offset, length = self.slots[slot_no]

        if length == 0:
            raise ValueError("Record has been deleted.")

        #b = self.data_bytes[offset - PAGE_HEADER_SIZE : offset - PAGE_HEADER_SIZE + length]

        b = self.to_bytes()
        return b[offset:offset+length]

    
    def to_bytes(self) ->  bytes:
        """ Serialize the entire page into bytes """

        ## Serializing the data content
        page = bytearray(PAGE_SIZE)
        page[PAGE_HEADER_SIZE:PAGE_HEADER_SIZE+len(self.data_bytes)] = self.data_bytes

        ## Serializing the slot
        slot_dir_start = PAGE_SIZE - len(self.slots)*SLOT_ENTRY_SIZE

        for i, (offset, length) in enumerate(self.slots):
            entry_offset = slot_dir_start + i * SLOT_ENTRY_SIZE
            page[entry_offset:entry_offset+SLOT_ENTRY_SIZE] = struct.pack(SLOT_ENTRY_FMT, offset, length)


        ## Serializing the header
        struct.pack_into(PAGE_HEADER_FMT, page, 0, self.page_id, len(self.slots), self.data_end_offset)

        return bytes(page)

    def delete(self, slot_no: int):
        if slot_no<0 or slot_no >= len(self.slots):
            raise IndexError("Invalid slot number.")
        
        offset, length = self.slots[slot_no]

        if length == 0:
            return

        self.slot[slot_no] = (offset,0)

    def from_byte(cls, b: bytes) -> 'Page':
        page_id, slot_count, data_end_offset = struct.unpack_from(PAGE_HEADER_FMT, b, 0)
        p = cls(page_id)
        p.data_end_offset = data_end_offset
        data_len = data_end_offset - PAGE_HEADER_SIZE
        p.data_bytes = bytearray(b[PAGE_HEADER_SIZE:PAGE_HEADER_SIZE+data_len])
        p.slots = []
        slot_dir_start = PAGE_SIZE - slot_count * SLOT_ENTRY_SIZE

        for i in range(slot_count):
            entry_offset = slot_dir_start + i * SLOT_ENTRY_SIZE
            offset, length = struct.unpack_from(SLOT_ENTRY_FMT, b, entry_offset)
            p.slots.append((offset, length))
        return p

    
    def __repr__(self):
        return f"<Page id={self.page_id} slots={len(self.slots)} data_end={self.data_end_offset}>"

    




    

    


