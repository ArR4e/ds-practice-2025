from verification_pb2 import VerificationRequest
from typing import TypedDict
from threading import Lock

class VerificationOrderData(TypedDict):
    data: VerificationRequest
    vector_clock: list[int]
    lock: Lock