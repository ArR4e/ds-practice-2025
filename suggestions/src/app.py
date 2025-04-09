import os
import sys

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, fraud_detection_grpc_path)

from suggestions_pb2 import SuggestionsData, InitializeRequestDataResponse, \
    BookSuggestionRequest, BookSuggestionResponse, \
    ClearSuggestionsDataRequest, ClearSuggestionsDataResponse
from suggestions_pb2_grpc import add_SuggestionsServiceServicer_to_server, SuggestionsServiceServicer

from BloomFilterStore import BloomFilterStore
from BookStore import BookStore, Book
from VectorStore import VectorStore

import grpc
from concurrent import futures
from typing import TypeVar, Iterable, Callable
from random import randint
from heapq import nlargest
import logging.config
from pathlib import Path
from json import load

# We want to boost new books (exploration)
RECENT_BOOKS_BOOSTING = float(os.getenv('RECENT_BOOKS_BOOSTING'))
# Popular books have higher chance of being bought, but due to their popularity we reduce their score (relevance)
BESTSELLERS_BOOSTING = float(os.getenv('BESTSELLERS_BOOSTING'))

T = TypeVar('T')
# Currently for POC we use in-memory structures but all these things can later be migrated to external tools or different microservices
bloom_filter = BloomFilterStore()
vector_store = VectorStore()
book_store = BookStore()

global logger
logger = logging.getLogger("suggestions_logger")
path = Path(__file__).parent / "config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)


class SuggestionsService(SuggestionsServiceServicer):
    order_data_store: dict[str, SuggestionsData]

    def __init__(self):
        super().__init__(self)
        self.order_data_store = {}

    def InitializeRequestData(self, request: SuggestionsData, context) -> InitializeRequestDataResponse:
        self.order_data_store[request.orderId] = request
        return InitializeRequestDataResponse()

    def SuggestBooks(self, request: BookSuggestionRequest, context) -> BookSuggestionResponse:
        order_data = self.order_data_store[request.orderId]
        suggested_book_ids = self.calculate_suggested_books_ids(order_data.boughtBookIds, order_data.userId)
        suggested_books = self.get_suggested_books(suggested_book_ids)
        return BookSuggestionResponse(suggestedBooks=suggested_books)

    def calculate_suggested_books_ids(self, book_ids: Iterable[str], user_id: str) -> list[str]:
        scored_similar_books = flatten([vector_store.get_top_similar(book_id, 5) for book_id in book_ids])
        recent_books = get_recently_arrived_books()
        bestselling_books = get_bestselling_books()

        logger.debug(f'Retrieved similar books {scored_similar_books} with similarity scores')
        logger.debug(f'Retrieved bestsellers {bestselling_books}')
        logger.debug(f'Retrieved recent books {recent_books}')

        # We do not recommend what user already bought
        filter_instance = f'books:{user_id}'
        for book_id in book_ids:
            bloom_filter.add(filter_instance, book_id)
        new_scored_similar_books = self.get_new_books(scored_similar_books, filter_instance,
                                                      lambda scored_book: scored_book[0])
        new_recent_books = self.get_new_books(recent_books, filter_instance, lambda book_id: book_id)
        new_bestselling_books = self.get_new_books(bestselling_books, filter_instance, lambda book_id: book_id)

        new_scored_recent_books = self.get_scores(new_recent_books, book_ids)
        new_scored_bestselling_books = self.get_scores(new_bestselling_books, book_ids)

        # Now that we have new books, we re-rank them and pick most similar
        return [*map(lambda scored_book: scored_book[0], nlargest(10, [
            *new_scored_similar_books,
            *[(book_id, score * RECENT_BOOKS_BOOSTING) for (book_id, score) in new_scored_recent_books],
            *[(book_id, score * BESTSELLERS_BOOSTING) for (book_id, score) in new_scored_bestselling_books]
        ],
                                                                  lambda scored_book: scored_book[1]
                                                                  ))]

    def get_scores(self, book_ids: list[str], bought_book_ids: Iterable[str]) -> list[(str, float)]:
        return filter_nones(map(lambda book_id: vector_store.get_score(book_id, bought_book_ids), book_ids))

    def get_new_books(self, books: list[T], filter_instance, key_fn: Callable[[T], str]) -> list[T]:
        return [*filter(lambda book: not bloom_filter.exists(filter_instance, key_fn(book)), books)]

    def get_suggested_books(self, suggested_book_ids: list[str]) -> list[BookSuggestionResponse.SuggestedBook]:
        return [*
                map(
                    self.to_suggested_book,
                    map(book_store.get_book_by_id, suggested_book_ids)
                )
                ]

    def to_suggested_book(self, book: Book) -> BookSuggestionResponse.SuggestedBook:
        print(book)
        return BookSuggestionResponse.SuggestedBook(
            bookId=book["bookId"],
            title=book["title"],
            author=book["author"]
        )

    def ClearData(self, request: ClearSuggestionsDataRequest, context) -> ClearSuggestionsDataResponse:
        self.order_data_store.pop(request.orderId, None)
        return ClearSuggestionsDataResponse()


def score_book(book_id: int) -> [int, float]:
    return vector_store.get_score(book_id)


def get_recently_arrived_books(k=5) -> list[str]:
    return [str(randint(0, 63)) for _ in range(k)]


def get_bestselling_books(k=5) -> list[str]:
    return [str(randint(0, 63)) for _ in range(k)]


def flatten(nested_list: list[list[T]]) -> list[T]:
    return [item for sub_list in nested_list for item in sub_list]


def filter_nones(l: Iterable[T | None]) -> list[T]:
    return [*filter(lambda a: a, l)]


def server() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    port = "50053"
    add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f'Book suggestions service started on port {port}')
    server.wait_for_termination()


if __name__ == '__main__':
    server()
