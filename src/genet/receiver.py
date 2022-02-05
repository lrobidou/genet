from websockets.exceptions import ConnectionClosedError
from websocket import connect
import asyncio
import time
from typing import Any, Tuple, AsyncGenerator
from typing import Generator as G


def iter_over_async(
    ait: AsyncGenerator[Any, None], loop: asyncio.AbstractEventLoop
) -> G[str, None, None]:
    ait = ait.__aiter__()

    async def get_next() -> Tuple[bool, str]:
        # Union[Tuple[Literal[False], str], Tuple[Literal[True], None]
        try:
            obj: str = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, ""

    while True:
        done, obj = loop.run_until_complete(get_next())
        time.sleep(1)
        if done:
            break
        yield obj


async def asynchronous_websockets(
    subdirectory: str, ip: str, port: int
) -> AsyncGenerator[Any, None]:
    async with connect(f"ws://{ip}:{port}/{subdirectory}") as websocket:
        try:
            await websocket.send("")
            async for message in websocket:
                yield message
                await websocket.send("")
        except ConnectionClosedError:
            pass  # TODO handle better the close of the connection


def iterate(
    subdirectory: str, ip: str = "localhost", port: int = 8080
) -> G[str, None, None]:
    async_generator = asynchronous_websockets(subdirectory, ip, port)
    generator = iter_over_async(async_generator, asyncio.get_event_loop())
    yield from generator


class Receiver:
    def __init__(self, ip: str = "0.0.0.0", port: int = 8080):
        self._ip = ip
        self._port = port

    def iterate(self, subdirectory: str) -> G[str, None, None]:
        yield from iterate(subdirectory, self._ip, self._port)
