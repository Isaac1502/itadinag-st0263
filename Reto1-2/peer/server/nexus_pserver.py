import requests as req

from concurrent import futures
import logging

import grpc
import nexus_transfer_pb2
import nexus_transfer_pb2_grpc


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def format_response(response):
    if response.status_code == 200:
        return nexus_transfer_pb2.Response(
            message=response.text, status=response.status_code
        )
    return nexus_transfer_pb2.Response(
        message="There was an error when loging in.", status=response.status_code
    )


class NexusPServicer(nexus_transfer_pb2_grpc.NexusTransferServicer):
    """Provides methods that implement functionality of file transfering server at PServer level."""

    def __init__(self):
        pass

    def Login(self, request, context):
        print(f"peer {request.peer.url} requested to log in the server.")
        payload = {
            "username": request.username,
            "password": request.password,
            "url": request.peer.url,
            "ip_address": request.peer.ip_address,
            "port": request.peer.port,
        }

        request = req.post(
            f"http://{SERVER_IP}:{SERVER_PORT}/login",
            json=payload,
            verify=False,
            headers={"Connection": "close"},
        )

        response = format_response(request)
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nexus_transfer_pb2_grpc.add_NexusTransferServicer_to_server(
        NexusPServicer(), server
    )
    server.add_insecure_port("[::]:5005")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
