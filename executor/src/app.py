import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

queue_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/priority_queue'))
sys.path.insert(0, queue_path)

verification_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/verification'))
sys.path.insert(0, verification_path)

pb_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, pb_path)

election_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/leader_election'))
sys.path.insert(0, election_path)


from verification_pb2 import VerificationRequest
from queue_service_pb2_grpc import QueueStub
from queue_service_pb2 import OrderRequest
from leader_selection_pb2_grpc import SelectionServicer, SelectionStub, \
    add_SelectionServicer_to_server
from leader_selection_pb2 import HealthDeclaration, OK, VoteRequest, VoteResponse


import grpc
from concurrent import futures
import threading
import logging.config
from pathlib import Path
from json import load
import time
from uuid import uuid4, UUID
import random
from asyncio import gather, TaskGroup

global logger
logger = logging.getLogger("queue_logger")
path = Path(__file__).parent/"config.json"
with open(path) as file:
    config = load(file)
logging.config.dictConfig(config=config)


FOLLOWER = 1
CANDITATE = 2
LEADER = 3

#TODO needs a total redo to asyncio and proper multithreding

class ExecutorService(SelectionServicer):
    def __init__(self, id, name, peers: dict[str, (UUID, SelectionStub)], queue_addr):
        self.id = id
        self.name = name
        self.peer_stubs = peers
        self.term = 0
        self.STATE = FOLLOWER
        self._lock = threading.Lock()
        self.last_heartbeat = time.time()
        self.votes_in_favor = 0
        self.leader_name = None
        self.leader_uuid = None
        self.queue_addr = queue_addr

        threading.Thread(target=self.timer, daemon=True).start()


    def sendHeartBeats(self):
        for (peer_id, stub) in self.peer_stubs:
            try: 
                current_stub: SelectionStub = stub
                current_stub.HealthCheck(HealthDeclaration(
                    status=True,
                    msg='SUCCESS'
                ))
            except Exception as e:
                print(f'Heartbeat to {peer_id} failed')

    def timer(self):
        while True:
            time.sleep(0.1)
            with self.lock:
                if self.state == LEADER:
                    self.sendHeartBeats()
                    self.pollAndProcessOrder()
                elif time.time() - self.last_heartbeat > random.uniform(1.5, 3.0):
                    self.start_election()

    async def pollAndProcessOrder(self):
        async with grpc.aio.insecure_channel(self.queue_addr) as channel:
            stub = QueueStub(channel=channel)
            order: VerificationRequest = await stub.Dequeue(OrderRequest())
            logger.info(f'processing order {order.orderId}')

    def HealthCheck(self, request: HealthDeclaration, context):
        if request.status:
            return OK()

    def GetVoteRequest(self, request: VoteRequest, context):
        with self._lock:
            if request.term > self.term:
                self.term = request.term
                self.STATE = FOLLOWER
                self.leader_uuid = UUID(request.senderUUID)
                self.leader_name = request.sender_name
                self.last_heartbeat = time.time()
                return VoteResponse(
                    sender_name=self.id,
                    senderUUID=self.id,
                    confirmation=True
                )
            else:
                return VoteResponse(
                    sender_name=self.id,
                    senderUUID=self.id,
                    confirmation=False
                )



    def start_election(self):
        self.state = CANDITATE
        self.term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        self.last_heartbeat = time.time()

        for peer_id, stub in self.nodes:
            threading.Thread(target=self.GetVoteRequest, args=(VoteRequest(
                senderUUID = self.id,
                sender_name = self.name,
                term = self.term
            ))).start()
        
            



def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_SelectionServicer_to_server(ExecutorService(),server)
    server.add_insecure_port("[::]:" + '50060')
    server.start()
    logger.info(f'Queue service started on port 50060')
    server.wait_for_termination()

if __name__ == '__main__':
    server()
