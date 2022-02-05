from __future__ import annotations

import bottle  # type: ignore
import time

from threading import Thread
from gevent.pywsgi import WSGIServer  # type: ignore
from geventwebsocket import WebSocketError  # type: ignore
from geventwebsocket.handler import WebSocketHandler  # type: ignore
from typing import Generator as G
from typing import Tuple
from typing import Dict, Set


class Sender:
    def __init__(
        self,
        *generators: Tuple[str, G[str, None, None]],
        terminable: bool = True,
        ip: str = "0.0.0.0",
        port: int = 8080
    ):
        self._app = bottle.Bottle()
        # which subdirectories are already taken ?
        self._subdirectories_bespoke: Dict[str, G[str, None, None]] = {}
        # can I disable the sender when every generators finished ?
        self._terminable = terminable
        self._ip = ip
        self._port = port
        self._server: WSGIServer = None

        for subdirectory, generator in generators:
            self.expose(subdirectory, generator)
        if self._subdirectories_bespoke or not self._terminable:
            Thread(target=self._start, args=[]).start()
        # let's give enough time for the thread be ready
        # TODO change dumb sleep for a cleaner way
        time.sleep(0.1)

    def _start(self) -> None:
        @self._app.route("/<subdirectory>")
        def handle_request(subdirectory: str) -> None:
            if subdirectory not in self._subdirectories_bespoke:
                bottle.abort(
                    404, "generator not found"
                )  # TODO check if the raised error is correctly received client side
            generator = self._subdirectories_bespoke[subdirectory]

            wsock = bottle.request.environ.get("wsgi.websocket")
            if not wsock:
                bottle.abort(400, "Expected WebSocket request.")
            for x in generator:
                try:
                    # message = wsock.receive()  # TODO send messgage to generator
                    wsock.receive()
                    wsock.send(x)
                except WebSocketError:
                    break
            self._subdirectories_bespoke.pop(subdirectory)
            self._stop_if_needed()

        self._server = WSGIServer(
            (self._ip, self._port), self._app, handler_class=WebSocketHandler
        )
        self._server.serve_forever()

    def _stop_if_needed(self) -> None:
        if self._terminable and not self._subdirectories_bespoke:
            self._server.stop()

    def _expose(self, subdirectory: str, generator: G[str, None, None]) -> Sender:
        self._subdirectories_bespoke[subdirectory] = generator
        return self

    def expose(self, subdirectory: str, generator: G[str, None, None]) -> Sender:
        if subdirectory in self._subdirectories_bespoke:
            raise RuntimeError  # TODO change
        return self._expose(subdirectory, generator)

    def terminable(self) -> None:
        self._terminable = True
        self._stop_if_needed()

    def get_subdirectories_bespoke(self) -> Set[str]:
        return {x for x in self._subdirectories_bespoke}
