# storage/heap_file.py
import os
import struct
from storage.page import Page, PAGE_SIZE

FILE_HEADER_SIZE = 4096
FILE_HEADER_FMT = "<I"   # next_page_id uint32 (at offset 0)

class HeapFile:
    """
    Very small heap file manager.
    File layout:
      - first FILE_HEADER_SIZE bytes: file header (stores next_page_id)
      - then pages laid out sequentially: page 0 at offset FILE_HEADER_SIZE + 0*PAGE_SIZE
    """
    def __init__(self, path: str):
        self.path = path
        self._f = None
        self.next_page_id = 0

    def create(self):
        # create a new file and write empty header
        with open(self.path, "wb") as f:
            hdr = struct.pack(FILE_HEADER_FMT, 0)
            f.write(hdr)
            # pad header to FILE_HEADER_SIZE
            f.write(b"\x00" * (FILE_HEADER_SIZE - len(hdr)))
        self._open_file()
        self.next_page_id = 0

    def open(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(self.path)
        self._open_file()
        # read header
        self._f.seek(0)
        data = self._f.read(struct.calcsize(FILE_HEADER_FMT))
        self.next_page_id = struct.unpack(FILE_HEADER_FMT, data)[0]

    def _open_file(self):
        self._f = open(self.path, "r+b")  # read/write binary

    def close(self):
        if self._f:
            self._f.flush()
            os.fsync(self._f.fileno())
            self._f.close()
            self._f = None

    def _write_header(self):
        self._f.seek(0)
        self._f.write(struct.pack(FILE_HEADER_FMT, self.next_page_id))
        # keep rest of header intact (we assume was zeroed)
        self._f.flush()
        os.fsync(self._f.fileno())

    def allocate_page(self) -> int:
        """Allocate a fresh empty page and return its page_id."""
        pid = self.next_page_id
        p = Page(pid)
        self.write_page(p)
        self.next_page_id += 1
        # persist header
        self._write_header()
        return pid

    def _page_offset(self, page_id: int) -> int:
        return FILE_HEADER_SIZE + page_id * PAGE_SIZE

    def write_page(self, page: Page) -> None:
        """Write full page bytes to its spot on disk."""
        if self._f is None:
            raise RuntimeError("file not open")
        b = page.to_bytes()
        off = self._page_offset(page.page_id)
        self._f.seek(off)
        self._f.write(b)
        self._f.flush()
        os.fsync(self._f.fileno())

    def read_page(self, page_id: int) -> Page:
        if self._f is None:
            raise RuntimeError("file not open")
        off = self._page_offset(page_id)
        self._f.seek(off)
        b = self._f.read(PAGE_SIZE)
        if len(b) != PAGE_SIZE:
            raise ValueError("page does not exist or partial read")
        return Page.from_bytes(b)

    def page_count(self) -> int:
        return self.next_page_id