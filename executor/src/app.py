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

election_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/leader_selection'))
sys.path.insert(0, election_path)


from verification_pb2 import VerificationRequest
from queue_service_pb2_grpc import QueueStub
from queue_service_pb2 import OrderRequest
from leader_selection_pb2_grpc import SelectionServicer, SelectionStub, \
    add_SelectionServicer_to_server
from leader_selection_pb2 import HealthDeclaration, OK, VoteRequest, VoteResponse, LeaderDeclare


import grpc
from concurrent import futures
import threading
import logging.config
from pathlib import Path
from json import load
import time
from uuid import uuid4, UUID
import random
import asyncio

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
    def __init__(self, id: UUID, name, peers: dict[str, str], queue_addr, port, is_leader):
        self.id = id
        self.name = name
        self.port = port
        self.peers = peers
        self.term = 0
        self.state = FOLLOWER
        self._lock = threading.Lock()
        self.last_heartbeat = time.time()
        self.time_interval = random.uniform(1.5, 10.0)
        self.votes_received = 0
        self.leader_name = None
        self.leader_uuid = None
        self.queue_addr = queue_addr

        if is_leader:
            self.state = LEADER
            self.leader_name = self.name
            self.leader_uuid = self.id

    async def start(self):
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        add_SelectionServicer_to_server(self,server)
        server.add_insecure_port("[::]:" + self.port)
        await server.start()
        logger.info(f'Queue service started on port {self.port}')
        if self.state == LEADER:
            logger.info(f'executor {self.name} became leader: status = {self.state}')
            await self.send_heart_beats()
        asyncio.create_task(self.timer())
        await server.wait_for_termination()

    async def send_heart_beats(self):
        tasks = [
            asyncio.create_task(self. send_heart_beat_to(name, address))
            for name, address in self.peers.items()
        ]
        await asyncio.gather(*tasks)

    async def send_heart_beat_to(self, name, address):
        try:
            channel = grpc.aio.insecure_channel(f'host.docker.internal:{address}')
            stub = SelectionStub(channel)
            response: OK = await asyncio.wait_for(
                stub.HealthCheck(HealthDeclaration(
                    status=True,
                    msg='SUCCESS'
                )),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.debug(f'heartbeat to {name} timed out.')
        except Exception as e:
            logger.debug(f'Error contacting {name} ({address})')

    async def timer(self):
        while True:
            await asyncio.sleep(0.1)
            with self._lock:
                if self.state == LEADER:
                    logger.info('POLLING QUEUE')
                    await self.send_heart_beats()
                    await self.poll_and_process_order()
                elif time.time() - self.last_heartbeat > self.time_interval:
                    await self.start_election()

    async def poll_and_process_order(self) -> None:
        async with grpc.aio.insecure_channel(self.queue_addr) as channel:
            stub = QueueStub(channel=channel)
            order: VerificationRequest = await stub.Dequeue(OrderRequest())
            if not order.orderId.__eq__('0'):
                logger.info(f'processing order {order.orderId}')

    def HealthCheck(self, request: HealthDeclaration, context) -> OK:
        if request.status:
            self.state = FOLLOWER
            self.last_heartbeat = time.time()
            return OK()

    def GetVoteRequest(self, request: VoteRequest, context) -> VoteResponse:
        with self._lock:
            if request.term > self.term:
                self.term = request.term
                self.STATE = FOLLOWER
                self.votes_received = 0
                self.leader_uuid = UUID(request.senderUUID)
                self.leader_name = request.sender_name
                self.last_heartbeat = time.time()
                return VoteResponse(
                    sender_name=str(self.id),
                    senderUUID=str(self.id),
                    confirmation=True
                )
            else:
                return VoteResponse(
                    sender_name=str(self.id),
                    senderUUID=str(self.id),
                    confirmation=False
                )

    def DeclareLeader(self, request: LeaderDeclare, context):
        self.state = FOLLOWER
        self.term = request.term
        self.leader_name = request.sender_name
        self.leader_uuid = request.senderUUID
        self.last_heartbeat = time.time()
        self.time_interval = random.uniform(1.5, 3.0)
        return OK()

    async def start_election(self):
        self.state = CANDITATE
        self.term += 1
        self.votes_received = 1
        self.last_heartbeat = time.time()

        tasks = [
            asyncio.create_task(self.request_vote_from(name, address))
            for name, address in self.peers.items()
        ]
        await asyncio.gather(*tasks)

        # Check majority
        total_nodes = len(self.peers) + 1
        #if is new leader
        logger.info(f'total votes for {self.name} = {self.votes_received}')
        if self.votes_received > total_nodes // 2:
            self.state = LEADER
            await self.declare_self_as_leader()
            logger.info(f'{self.name} becomes leader for term {self.term}')
        else:
            logger.info(f'{self.name} failed to become leader in term {self.term}')

    async def declare_self_as_leader(self):
        tasks = [
            asyncio.create_task(self. send_leader_declaration_to(name, address))
            for name, address in self.peers.items()
        ]
        await asyncio.gather(*tasks)

    async def request_vote_from(self, name, address):
        try:
            channel = grpc.aio.insecure_channel(f'host.docker.internal:{address}')
            stub = SelectionStub(channel)
            response: VoteResponse = await asyncio.wait_for(
                stub.GetVoteRequest(VoteRequest(
                    senderUUID=str(self.id),
                    sender_name=self.name,
                    term=self.term
                )),
                timeout=5.0
            )
            #TODO check if this is safe
            if response.confirmation:
                with self._lock:
                    self.votes_received += 1
                    logger.debug(f'current votes for {self.name} = {self.votes_received}')
        except asyncio.TimeoutError:
            logger.debug(f'Vote request to {name} timed out.')
        except Exception as e:
            logger.debug(f'Error contacting {name} ({address}) for voting {e}')

    async def send_leader_declaration_to(self, name, address):
        try:
            channel = grpc.aio.insecure_channel(f'host.docker.internal:{address}')
            stub = SelectionStub(channel)
            response: OK = await asyncio.wait_for(
                stub.DeclareLeader(LeaderDeclare(
                    senderUUID=str(self.id),
                    sender_name=str(self.name),
                    term=self.term
                )),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.debug(f'Declaration to {name} timed out.')
        except Exception as e:
            logger.debug(f'Error contacting {name} ({address})')
        
            
#TODO add to docker compose file
NAME = os.getenv('NAME')
PORT = os.getenv('PORT')
QUEUE_ADDR = os.getenv('QUEUE_ADDR')



#
# Change the peers to change the known peers, 
# add all, self will be removed later
# see docker-compose file for peers
#
#
async def server():
    is_new_leader = False
    peers = {
        'executora-1':'50060',
        'executorb-1':'50061',
        'executorc-1':'50062'
    }
    if NAME == 'executora-1':
        is_new_leader = True
    #remove own name from peers
    peers.pop(NAME)
    executor = ExecutorService(
        id=uuid4(), 
        peers= peers, 
        queue_addr=QUEUE_ADDR,
        name=NAME,
        port=PORT,
        is_leader=is_new_leader)
    await executor.start()

if __name__ == '__main__':
    asyncio.run(server())
