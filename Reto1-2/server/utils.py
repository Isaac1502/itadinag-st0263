import time
import threading

import grpc
import nexus_transfer_pb2
import nexus_transfer_pb2_grpc

from db import peers

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005


def get_peer_status(stub, flag):
    try:
        ack = stub.Ping(flag)
    except grpc.RpcError:
        return False
    return ack


def check_peers():
    while True:
        for peer, val in peers.items():
            with grpc.insecure_channel(peer) as channel:
                stub = nexus_transfer_pb2_grpc.NexusTransferStub(channel)
                response = get_peer_status(stub, nexus_transfer_pb2.Call(flag=True))
                url = val["url"]
                if not response and val["status"]:
                    print(f"Peer {url} is down.")
                    val["status"] = False
                else:
                    print(f"{url} {response.message} Status: {response.status}")
        time.sleep(1500)


# Background thread to ping every peer logged in.
def ping():
    background_thread = threading.Thread(target=check_peers)
    background_thread.daemon = True
    background_thread.start()
