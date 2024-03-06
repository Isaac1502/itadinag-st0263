import requests as req

from concurrent import futures
import logging

import grpc
import nexus_transfer_pb2
import nexus_transfer_pb2_grpc


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def format_response(response, valid_status):
    if response.status_code == valid_status:
        return nexus_transfer_pb2.Response(
            message=response.text, status=response.status_code
        )
    return nexus_transfer_pb2.Response(
        message="There was an error doing the operation.", status=response.status_code
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

        query = req.post(
            f"http://{SERVER_IP}:{SERVER_PORT}/login",
            json=payload,
            verify=False,
            headers={"Connection": "close"},
        )

        response = format_response(query, 200)
        return response

    def Logout(self, request, context):
        print(f"peer {request.url} requested to log out the server.")
        payload = {
            "url": request.url,
            "ip_address": request.ip_address,
            "port": request.port,
        }

        query = req.post(
            f"http://{SERVER_IP}:{SERVER_PORT}/logout",
            json=payload,
            verify=False,
            headers={"Connection": "close"},
        )

        response = format_response(query, 200)
        return response

    def Ping(self, request, context):
        print(f"ping from server.")
        return nexus_transfer_pb2.Response(message="Up and running.", status=200)

    def SendDirectory(self, request, context):
        print(
            f"peer {request.peer.url} requested to publish the directory to the server."
        )
        formated_files = []

        for file in request.files:
            file_dict = {
                "title": file.title,
                "album": file.album,
                "duration": file.duration,
                "size_MB": file.size_MB,
            }
            formated_files.append(file_dict)

        payload = {
            "url": request.peer.url,
            "ip_address": request.peer.ip_address,
            "port": request.peer.port,
            "files": formated_files,
        }
        query = req.post(
            f"http://{SERVER_IP}:{SERVER_PORT}/directory",
            json=payload,
            verify=False,
            headers={"Connection": "close"},
        )

        response = format_response(query, 201)
        return response

    def Download(self, request, context):
        print(f"peer requested to download {request.title}")

        payload = {
            "element": request.title,
        }

        query = req.get(
            f"http://{SERVER_IP}:{SERVER_PORT}/search",
            json=payload,
            verify=False,
            headers={"Connection": "close"},
        )

        peers_with_file = query.json()
        for url in peers_with_file:
            process, port = url.split(":")
            yield nexus_transfer_pb2.Peer(url=url, ip_address=process, port=int(port))

    def Upload(self, request, context):
        print(f"peer requested to upload {request.title}")

        query = req.get(
            f"http://{SERVER_IP}:{SERVER_PORT}/available",
            verify=False,
            headers={"Connection": "close"},
        )

        available_peer = query.text
        print(available_peer)
        process, port = available_peer.split(":")
        return nexus_transfer_pb2.Peer(
            url=available_peer, ip_address=process, port=int(port)
        )


def serve():
    print("Server listenning on port: 5005")
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
