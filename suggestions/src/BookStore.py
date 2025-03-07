from typing import TypedDict
import json

class Book(TypedDict):
    bookId: str
    title: str
    author: str
    subjects: list[str]
    summary: str

class BookStore:

    def __init__(self):
        with open('suggestions/data/data.json') as f:
            self.data = json.load(f)

    def get_book_by_id(self, book_id) -> Book:
        return self.data[book_id]