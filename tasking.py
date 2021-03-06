import asyncio
import threading


class Tasker:
    def __init__(self, name="tasker"):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(name=name, target=self._run, daemon=True)

    def _run(self):
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def start(self):
        self.thread.start()

    def do(self, func, *args, **kwargs):
        handle = self.loop.call_soon(lambda: func(*args, **kwargs))
        self.loop._write_to_self()

        return handle

    def later(self, func, *args, after=None, **kwargs):
        handle = self.loop.call_later(after, lambda: func(*args, **kwargs))
        self.loop._write_to_self()

        return handle

    def periodic(self, func, *args, interval=None, **kwargs):
        @asyncio.coroutine
        def f():
            while True:
                yield from asyncio.sleep(interval)
                func(*args, **kwargs)

        handle = self.loop.create_task(f())
        self.loop._write_to_self()

        return handle
