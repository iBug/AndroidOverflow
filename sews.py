import json
from threading import Thread

import websocket

from utils import log


class StackExchangeWebSocket:
    WS_URL = "wss://qa.sockets.stackexchange.com/"

    def __init__(self):
        self.ws = None
        self.on_action = {}

    def open(self, max_tries=3):
        if self.ws:
            raise ValueError("WebSocket is already open")

        for tries in range(1, 1 + max_tries, 1):
            if tries > 1:
                log('debug', "Trying to open websocket (Attempt {})".format(tries))
            try:
                self.ws = websocket.create_connection(StackExchangeWebSocket.WS_URL)
                log('debug', "Successfully opened websocket")
                return self.ws
            except websocket.WebSocketException:
                pass
        else:
            raise ConnectionError("Failed to open websocket")

    def close(self):
        try:
            self.ws.close()
            self.ws = None
        except Exception as e:
            pass

    def register(self, action, callback=None):
        if not isinstance(action, str):
            raise TypeError("action must be str")
        self.on_action[action] = callback
        self.ws.send(action)

    def unregister(self, action, callback=None):
        if not isinstance(action, str):
            raise TypeError("action must be str")
        del self.on_action[action]
        self.ws.send("-" + action)

    def restore(self):
        try:  # Force cleanup old ws object
            self.ws.close()
        except Exception:
            pass

        self.open()
        for action in self.on_action:
            self.register(action)

    def event_loop(self):
        log('debug', "Starting Stack Exchange WebSocket event loop")
        while True:
            try:
                j = self.ws.recv()
                if not j:
                    raise ValueError("Unexpected socket data: {!r}".format(j))
                j = json.loads(j)
                action = j['action']
                if action == "hb":
                    # log('debug', "Action: hb")
                    self.ws.send("hb")
                    continue
                data = json.loads(j['data'])
                if action not in self.on_action:
                    log('debug', "Action {!r} not registered".format(action))
                    continue
                func = self.on_action[action]
                Thread(target=func, args=(data,)).start()
            except Exception as e:
                log('error', "{}: {}".format(type(e).__name__, str(e)))
                self.restore()
