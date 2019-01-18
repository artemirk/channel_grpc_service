from concurrent import futures
import time
import logging

import grpc
import multiprocessing

import acquired_pb2
import acquired_pb2_grpc

import string
import random
import sys

import argparse

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_NUM_CAMPAIGNS = 10

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _get_campaign(i: int, ad_account_id: int, elapsed, port: int) -> acquired_pb2.Campaign:
    campaign = acquired_pb2.Campaign()
    campaign.app = "{}_{}_port:{}".format(i, id_generator(), port)
    campaign.channel = "{}_network_elapsed: {}".format(ad_account_id, elapsed)
    return campaign

def get_context_time(context):
    # The huge value means +Inf timeout
    remaining = context.time_remaining()
    if remaining and remaining < sys.maxsize:
        return sys.maxsize - remaining
    return 0

class AcquiredServer(acquired_pb2_grpc.AcquiredServicer):

    def __init__(self, num_workers: int, port:int):
        self._num_workers = num_workers
        self._port = port

    def get_campaigns(self, request: acquired_pb2.GetCampaignsRequest, context):

        def disconected():
            logging.info("account_id={}. Client disconnected.".format(request.ad_account_id))
        context.add_callback(disconected)

        logging.info("Request campaigns account_id={}".format(request.ad_account_id))
        
        for i in range(_NUM_CAMPAIGNS):
            elapsed_time = time.time() - get_context_time(context)
            c = _get_campaign(i, request.ad_account_id, elapsed_time, self._port)
            yield c
            logging.info("respond campaign {} duration={}. Sent".format(c, elapsed_time))
            time.sleep(2) # Emulate delay
        return
        
def serve(num_workers: int = 1, port:int = 50051, graceful_shutdown_timeout:int = 0):
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=num_workers))
    acquired_pb2_grpc.add_AcquiredServicer_to_server(AcquiredServer(num_workers, port), server)
    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    logging.info("Started grpc server port={} graceful_shutdown_timeout={}".format(port, graceful_shutdown_timeout))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(graceful_shutdown_timeout)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_workers', dest='num_workers', type=int, default=2)
    parser.add_argument('--port', required=True, dest='port', choices=(50051, 50052, 50053), type=int)
    parser.add_argument('--graceful_shutdown_timeout', dest='graceful_shutdown_timeout', type=int, default=0)
    args = parser.parse_args()
    serve(num_workers=args.num_workers, port=args.port, graceful_shutdown_timeout=args.graceful_shutdown_timeout)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
    