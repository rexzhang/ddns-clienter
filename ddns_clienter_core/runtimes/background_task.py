import asyncio
import queue
import threading

from simple_background_task import BackgroundTask

from ddns_clienter_core.runtimes.check_and_update import check_and_update


async def test():
    pass


_loop = asyncio.new_event_loop()
# _loop.run_forever()


# _loop = None
#
#
def call_task(task):
    global _loop

    # _loop.call_soon(task)
    asyncio.to_thread(task)


# def call_task(task):
#     with asyncio.Runner() as runner:
#         runner.run(task())


# class BTask:
#     _t: threading.Thread
#     running = threading.Event()
#     queue = queue.Queue()
#
#     def __init__(self):
#         self.running.set()
#         self._t = threading.Thread(target=self.worker, daemon=True)
#         self._t.start()
#         self._t.join()
#
#     def stop_all(self, signum, frame):
#         print("\n  program stopping...")
#         self.running.clear()
#         return
#
#     def worker(self):
#         while True:
#             with asyncio.Runner() as runner:
#                 runner.run(check_and_update())
#
#
# b_task = BTask()
