from concurrent import futures
import time
import logging

import grpc

import acquired_pb2
import acquired_pb2_grpc

import string
import random

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_NUM_CAMPAIGNS = 10

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _get_campaign(i: int, ad_account_id: int) -> acquired_pb2.Campaign:
    campaign = acquired_pb2.Campaign()
    campaign.app = "{}_{}".format(i, id_generator())
    campaign.channel = "{}_network".format(ad_account_id)
    return campaign

class AcquiredServer(acquired_pb2_grpc.AcquiredServicer):

    def get_campaigns(self, request: acquired_pb2.GetCampaignsRequest, context):

        def disconected():
            logging.warning("Request campaigns account_id={} stopped. Client disconnected.".format(request.ad_account_id))
        context.add_callback(disconected)

        logging.info("Request campaigns account_id={}".format(request.ad_account_id))
        for i in range(_NUM_CAMPAIGNS):
            c = _get_campaign(i, request.ad_account_id)
            yield c
            logging.info("respond campaign {}. Sent".format(c))

            time.sleep(2) # Emulate delay
        logging.info("respond finished for account_id={}".format(request.ad_account_id))
        return
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    acquired_pb2_grpc.add_AcquiredServicer_to_server(AcquiredServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Started grpc server {}".format(server.__dict__))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()