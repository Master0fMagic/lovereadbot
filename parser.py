import logging
import urllib.error
import urllib.request
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup


class Parser:
    def __init__(self, bot_name: str):
        self.bot_name = bot_name

    def get_book_id(self, url: str) -> str:
        params = parse_qs(urlparse(url).query)
        book_id = params['id'][0]
        return book_id

    def read_book_page(self, book_id: str, page_number: int) -> str:
        link = f'http://loveread.ec/read_book.php?id={str(book_id)}&p={str(page_number)}'
        logging.info(f'try get page by url: {link}')
        response = urllib.request.urlopen(link)
        web_page = response.read()
        soup = BeautifulSoup(web_page, 'html.parser')
        book_page = soup.get_text().split('Страница\n')[-2].strip()
        book_page = book_page.replace(' ', '')
        logging.info(f'book page read successfully by url: {link}')
        return book_page

    def read_book(self, book_id: str) -> str:
        first_page = None
        book = ''
        page_number = 1
        while True:
            book_page = self.read_book_page(book_id, page_number)

            if page_number == 1:
                first_page = book_page

            if book_page == first_page and page_number != 1:
                break

            book += book_page
            page_number += 1

        logging.info(f'Successfully read book with id: {book_id}')
        return book

    def get_book(self, book_url: str):
        book_id = self.get_book_id(book_url)
        logging.info(f'start processing book with id: {book_id}')
        book = self.read_book(book_id)
        return book_id, book

    def write_book_to_file(self, book: str, filename):
        with open(filename, mode='w', encoding='UTF-8') as file:
            file.write(book)
            file.write(f'\n\n\nread by {self.bot_name}')

    def read_book_to_file(self, book_url: str, file_format: str):
        book = self.get_book(book_url)
        filename = f'{book[0]}.{file_format}'

        self.write_book_to_file(book[1], filename)
        logging.info(f'book with id {book[0]} successfully wrote to file')
        return filename
