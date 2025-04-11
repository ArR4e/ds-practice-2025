from threading import Lock
from typing import TypedDict
from fraud_detection_pb2 import FraudDetectionData

class OrderFraudDetectionData(TypedDict):
    data: FraudDetectionData
    vector_clock: list[int]
    lock: Lock
