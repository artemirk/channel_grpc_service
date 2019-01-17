import logging

import grpc

import acquired_pb2
import acquired_pb2_grpc

import random


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = acquired_pb2_grpc.AcquiredStub(channel)
        account_id = random.randint(1, 1000)
        logging.info("Request campaigns for account {}".format(account_id))
        for c in stub.get_campaigns(acquired_pb2.GetCampaignsRequest(ad_account_id=account_id)):
            logging.info("campaign {} - {}".format(c.app, c.channel))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()