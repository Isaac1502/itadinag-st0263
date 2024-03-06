import logging
import time

import grpc
import nexus_transfer_pb2
import nexus_transfer_pb2_grpc

from peer.server.pserver_db import files

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
LOADING = 5


def login_request(stub, credentials):
    logged = stub.Login(credentials)

    print(logged.message)


def logout_request(stub, peer):
    logged_out = stub.Logout(peer)

    print(logged_out.message)


def send_dir_request(stub, dir):
    response = stub.SendDirectory(dir)

    print(response.message)


def download_request(stub, file_request):
    print(f"Peers with {file_request.title}")
    peers = stub.Download(file_request)

    for peer in peers:
        print(f"    {peer.url}")


def download(stub, file):
    print(f"{file.title} downloaded")

    file_downloaded = stub.ConnPeerDownload(file)
    formated_file = {
        "title": file_downloaded.title,
        "artist": file_downloaded.artist,
        "album": file_downloaded.album,
        "duration": file_downloaded.duration,
        "size_MB": file_downloaded.size_MB,
    }
    files.append(formated_file)

    # Update directory on server
    guide_send_dir(stub)


def upload_request(stub, file_request):
    peer = stub.Upload(file_request)

    print(f"Available peer: {peer.url}")


def upload(stub, file):
    response = stub.ConnPeerUpload(file)

    print(response.message)


def guide_login(stub):
    print("Requesting log in from server.")
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


def guide_logout(stub):
    print("Requesting log out from server.")
    logout_request(
        stub,
        nexus_transfer_pb2.Peer(
            url="http://127.0.0.4:4004", ip_address="127.0.0.4", port=4004
        ),
    )


def guide_send_dir(stub):
    print("Requesting publish directory to the server.")
    send_dir_request(
        stub,
        nexus_transfer_pb2.Dir(
            peer=nexus_transfer_pb2.Peer(
                url="http://127.0.0.4:4004", ip_address="127.0.0.4", port=4004
            ),
            files=files,
        ),
    )


def guide_download_request(stub, title):
    print(f"Requesting download {title}")
    download_request(stub, nexus_transfer_pb2.FileRequest(title=title))


def guide_upload_request(stub, title):
    print(f"Requesting upload {title}")
    upload_request(stub, nexus_transfer_pb2.FileRequest(title=title))


def guide_download(stub, title):
    print(f"Downloading {title}")
    download(stub, nexus_transfer_pb2.FileRequest(title=title))


def guide_upload(stub, file):
    title = file["title"]
    print(f"Uploading {title}")

    upload(stub, nexus_transfer_pb2.File(**file))


def run():
    # pclient implementation
    with grpc.insecure_channel(f"{SERVER_IP}:{SERVER_PORT}") as channel:
        stub = nexus_transfer_pb2_grpc.NexusTransferStub(channel)
        guide_login(stub)
        time.sleep(LOADING)

        guide_send_dir(stub)
        time.sleep(LOADING)

        guide_download_request(stub, "Bohemian Rhapsody")
        time.sleep(LOADING)

        guide_download(stub, "Imagine")
        time.sleep(LOADING)

        guide_upload_request(stub, files[0]["title"])
        time.sleep(LOADING)

        guide_upload(stub, files[0])
        time.sleep(LOADING)

        guide_logout(stub)
        time.sleep(LOADING)


if __name__ == "__main__":
    logging.basicConfig()
    run()
