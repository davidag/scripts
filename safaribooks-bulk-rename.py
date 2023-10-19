#!/usr/bin/env python3

import argparse
import json
import re
import time
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from collections import namedtuple
from pathlib import Path
from typing import Dict, Optional


Book = namedtuple("Book", ["subdir", "name", "isbn", "year"], defaults=[""]*4)

DIR_RE = re.compile(r"(.+) \((\d+)\)$")


class BookAPI(ABC):
    def __init__(self):
        self.response = None
        self.response_code = None

    def query(self, isbn: str):
        url = self.build_url(isbn)
        try:
            with urllib.request.urlopen(url) as conn:
                self.response_code = conn.getcode()

                if self.response_code == 429:
                    print(f"@ Rate limit hit, waiting...")
                    time.sleep(5)
                    self.query(isbn)

                if self.response_code != 200:
                    print(f"@ URL Response error {self.response_code}")

                self.response = json.loads(conn.read())
        except urllib.error.URLError as exc:
            print(f"@ {type(self).__name__} error: {exc}")

    @abstractmethod
    def build_url(self) -> str:
        pass

    @abstractmethod
    def parse_year(self) -> str:
        pass


class GoogleAPI(BookAPI):
    API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

    def __init__(self):
        super().__init__()

    def build_url(self, isbn: str) -> str:
        return f"{self.API_URL}{isbn}"

    def parse_year(self) -> str:
        try:
            if self.response["totalItems"] == 0:
                print(f"@ GoogleAPI not found")
                return ""

            date = self.response["items"][0]["volumeInfo"]["publishedDate"]
            if (mo := re.search("[0-9]{4}", date)) != None:
                return mo[0]
        except Exception as exc:
            print(f"@ Google parse error: {exc}")
            pass
        return ""


class OpenlibraryAPI(BookAPI):
    API_URL = "https://openlibrary.org/isbn/"

    def __init__(self):
        super().__init__()

    def build_url(self, isbn: str) -> str:
        return f"{self.API_URL}{isbn}.json"

    def parse_year(self) -> str:
        try:
            date = self.response["publish_date"]
            if (mo := re.search("[0-9]{4}", date)) != None:
                return mo[0]
        except Exception:
            pass
        return ""


def get_subdirs(path: Path):
    for p in path.iterdir():
        if not p.is_dir():
            continue
        yield p


def build_book(folder: Path) -> Optional[Dict[str, str]]:
    if (mo := re.match(DIR_RE, folder.name)) != None:
        return Book(folder.name, *mo.group(1, 2))
    return None


def get_new_name(book: Book) -> str:
    # lowercase
    new_name = book.name.lower()

    # special c++ case
    new_name = new_name.replace('c__', 'cpp')

    # remove special characters
    new_name = new_name.translate({ord(i): None for i in "()_"})

    # two or more contiguous spaces
    new_name = re.sub(r'(\s)+', r'\1', new_name)

    # replacif/else spaces by dashes
    new_name = new_name.replace(' ', '-')

    # if isbn available, append it
    if book.year:
        new_name += f"-{book.year}"

    return new_name


def move_and_rename(book: Book, book_path: Path):
    old_path = book_path / book.subdir / f"{book.isbn}.epub"

    new_name = get_new_name(book)
    new_path = book_path / f"{new_name}.epub"

    if old_path.is_file():
        print(f"Renaming '{old_path.name}' to '{new_path.name}'")
        old_path.rename(new_path)
    else:
        print(f"WARNING: Skipping '{old_path}' !!!")


def retrieve_book_year(book: Book) -> str:
    api = OpenlibraryAPI()
    api.query(book.isbn)
    if (year := api.parse_year()):
        return year

    api = GoogleAPI()
    api.query(book.isbn)
    if (year := api.parse_year()):
        return year

    return ""


def main():
    parser = argparse.ArgumentParser(description="Renames epub files downloaded with safaribooks.py")
    parser.add_argument("book_path", type=Path, help="Books folder path")
    args = parser.parse_args()

    if not args.book_path.is_dir():
        print(f"Error: invalid path '{args.book_path}'")
        exit(1)

    for subdir in get_subdirs(args.book_path):
        book = build_book(subdir)
        year = retrieve_book_year(book)
        book = book._replace(year=year)
        move_and_rename(book, args.book_path)


if __name__ == "__main__":
    main()
