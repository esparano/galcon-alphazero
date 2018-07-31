import time
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ratelimit import limits

DATA_PATH = 'C:\\Users\\Evan Sparano\\AppData\\Roaming\\Galcon 2'
CONST_MOD_NAME = 'test'
SLEEP_SECONDS = 0.1


def main():
    observer = Observer()
    observer.schedule(
        TrainingInputHandler(), path=DATA_PATH)
    observer.start()

    try:
        while True:
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class TrainingInputHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if CONST_MOD_NAME + '.bin' in event.src_path:
            with open(event.src_path) as f:
                data = json.load(f)
                TrainingInputHandler.addTrainingData(self, data)

    @limits(calls=1, period=SLEEP_SECONDS, raise_on_limit=False)
    def addTrainingData(self, data):
        with open(DATA_PATH + '\\' + CONST_MOD_NAME + '_data.txt', 'a+') as f:
            json.dump(data, f)
            f.write('\n')
            f.flush()


if __name__ == '__main__':
    main()
