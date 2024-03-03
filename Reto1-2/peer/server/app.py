import requests as req

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def login():
    payload = {
        "username": "itadina",
        "password": "123",
        "url": "http://127.0.0.4:5000",
        "ip_address": "127.0.0.4",
        "port": 5000,
    }

    request = req.post(
        f"http://{SERVER_IP}:{SERVER_PORT}/login",
        json=payload,
        verify=False,
        headers={"Connection": "close"},
    )
    return request.json()


def logout():
    payload = {
        "username": "itadina",
        "password": "123",
        "url": "http://127.0.0.4:5000",
        "ip_address": "127.0.0.4",
        "port": 5000,
    }

    request = req.post(
        f"http://{SERVER_IP}:{SERVER_PORT}/logout",
        json=payload,
        verify=False,
        headers={"Connection": "close"},
    )
    return request.json()


def send_index():
    pass


def main():
    login_to_server = login()
    print(login_to_server)

    logout_to_server = logout()
    print(logout_to_server)


if __name__ == "__main__":
    main()
