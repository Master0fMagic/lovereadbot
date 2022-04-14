#write parsed data to file

from abc import ABC


class BookWriter(ABC):
    def write_to_file(data: str):
        pass
    

class PdfBookWriter(BookWriter):
    pass


class EpubBookWriter(BookWriter):
    pass


class TxtBookWriter(BookWriter):
    pass


class Fb2BookWriter(BookWriter):
    pass