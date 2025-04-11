from typing import TypedDict
from suggestions_pb2 import SuggestionsData

class SuggestionsOrderData(TypedDict):
     data: SuggestionsData
     vector_clock: list[int]