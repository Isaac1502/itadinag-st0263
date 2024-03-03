import logging

import grpc
import nexus_transfer_pb2
import nexus_transfer_pb2_grpc

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005


def login_request(stub, credentials):
    logged = stub.Login(credentials)

    if logged.status != 200:
        print("Logging in the Server failed")
    else:
        print(logged.message)


def guide_login(stub):
    login_request(
        stub,
        nexus_transfer_pb2.Credentials(
            peer=nexus_transfer_pb2.Peer(
                url="http://127.0.0.4:4004", ip_address="127.0.0.4", port=4004
            ),
            username="itadina",
            password="123",
        ),
    )


def run():
    # pclient implementation
    with grpc.insecure_channel(f"{SERVER_IP}:{SERVER_PORT}") as channel:
        stub = nexus_transfer_pb2_grpc.NexusTransferStub(channel)
        guide_login(stub)


if __name__ == "__main__":
    logging.basicConfig()
    run()
