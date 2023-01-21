# parse book text from html page
# parse link


import logging
import urllib.error
import urllib.request
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup


def get_book_id(url: str) -> str:
    params = parse_qs(urlparse(url).query)
    book_id = params['id'][0]
    return book_id


def read_book_page(book_id: str, page_number: int) -> str:
    link = f'http://loveread.ec/read_book.php?id={str(book_id)}&p={str(page_number)}'
    logging.info(f'try get page by url: {link}')
    response = urllib.request.urlopen(link)
    web_page = response.read()
    soup = BeautifulSoup(web_page, 'html.parser')
    book_page = soup.get_text().split('Страница\n')[-2].strip()
    book_page = book_page.replace(' ', '')
    logging.info(f'book page read successfully by url: {link}')
    return book_page


def read_book(book_id: str) -> str:
    first_page = None
    book = ''
    page_number = 1
    while True:
        book_page = read_book_page(book_id, page_number)

        if page_number == 1:
            first_page = book_page

        if book_page == first_page and page_number != 1:
            break

        book += book_page
        page_number += 1

    logging.info(f'Successfully read book with id: {book_id}')
    return book


def get_book(book_url: str):
    book_id = get_book_id(book_url)
    logging.info(f'start processing book with id: {book_id}')
    book = read_book(book_id)
    return book_id, book


def write_book_to_file(book: str, filename):
    with open(filename, mode='w', encoding='UTF-8') as file:
        file.write(book)
        file.write('\n\n\nread by @lovereadbot')  # todo change bot name, pass it to config


def read_book_to_file(book_url: str, file_format: str):
    book = get_book(book_url)
    filename = f'{book[0]}.{file_format}'

    write_book_to_file(book[1], filename)
    logging.info(f'book with id {book[0]} successfully wrote to file')
    return filename


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname) -s at %(asctime) -s: %(message)s')
    url = 'http://loveread.me/read_book.php?id=8107'

    read_book_to_file(url, 'txt')
    logging.info('book read')


if __name__ == '__main__':
    main()
