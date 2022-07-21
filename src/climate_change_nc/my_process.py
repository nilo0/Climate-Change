from multiprocessing import Process
import time


class MyProcess:
    def __init__(self, func, args, logger):
        self.logger = logger
        self.process = Process(target=func, args=args)

    def timeout(self, t):
        self.logger.log("Spawning a new process...")
        self.process.start()
        _start_time = time.time()
        while time.time() - _start_time < t:
            if not self.process.is_alive():
                self.logger.log("Process has finished successfully")
                break
        else:
            self.logger.error("Terminating the process...")
            self.process.terminate()
            self.process.join()
