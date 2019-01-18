import logging

import grpc

import acquired_pb2
import acquired_pb2_grpc

import random


def run():
    '''
    # nginx config for proxy

    upstream acquired_grpc {
        # https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/
        least_conn;
        server localhost:50051;
        server localhost:50052;
        server localhost:50053 down;
    }

    server {
        listen 50050 http2;
        charset utf-8;
        access_log logs/access_grpc.log;

        location / {
            grpc_pass grpc://acquired_grpc;
            error_page 502 = /error502grpc;
        }

        location = /error502grpc {
        internal;
            default_type application/grpc;
            add_header grpc-status 14;
            add_header grpc-message "unavailable";
            return 204;
        }
    }
    '''
     # localhost:50050 - proxy
    with grpc.insecure_channel('localhost:50050', [("grpc.lb_policy_name", "round_robin",)]) as channel:
        stub = acquired_pb2_grpc.AcquiredStub(channel)
        account_id = random.randint(1, 1000)
        logging.info("Request campaigns for account {}".format(account_id))
        try:
            for c in stub.get_campaigns(acquired_pb2.GetCampaignsRequest(ad_account_id=account_id)):
                logging.info("campaign {} - {}".format(c.app, c.channel))
        except KeyboardInterrupt:
            logging.info("Stop client")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
    