from flask import Flask, request

from db import peers
from utils import ping

app = Flask(__name__)


@app.post("/login")
def login_server():
    request_data = request.get_json()
    url = request_data["url"]
    ip = request_data["ip_address"]
    port = request_data["port"]
    process = f"{ip}:{port}"
    peers[process] = {"status": True, "url": url, "data": []}
    print(peers)

    return {"message": f"peer located at {url} has been logged in."}, 200


@app.post("/logout")
def logout_server():
    request_data = request.get_json()
    url = request_data["url"]
    ip = request_data["ip_address"]
    port = request_data["port"]
    process = f"{ip}:{port}"

    try:
        peer = peers[process]
    except KeyError:
        return {"message": f"peer {url} isn't logged in."}, 404

    if not peer["status"]:
        return {"message": f"peer {url} is already logged out."}, 406

    peers[process]["status"] = False
    print(peers)
    return {"message": f"peer {url} has been logged out."}, 200


@app.post("/directory")
def post_directory():
    request_data = request.get_json()
    url = request_data["url"]
    ip = request_data["ip_address"]
    port = request_data["port"]
    process = f"{ip}:{port}"

    files = request_data["files"]
    for file in files:
        peers[process]["data"].append(file)

    print(peers[process])
    return {"message": "directory updated."}, 201


@app.get("/search")
def get_element():
    request_data = request.get_json()
    element = request_data["element"]

    matched_peers = []

    for peer, val in peers.items():
        for peer_file in val["data"]:
            if peer_file == element:
                matched_peers.append(peer)

    if not len(matched_peers):
        return {"message": f"{element} was not found."}

    return matched_peers


if __name__ == "__main__":
    ping()
    app.run(debug=True)
