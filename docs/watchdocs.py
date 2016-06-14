import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
import subprocess

class DocsCompiler(PatternMatchingEventHandler):
    """ Compile docs each a *.rst file is changed
    """

    def dispatch(self, event):
        if event.src_path.endswith(".rst"):
            try:
                print("======================================================")
                print("Recompiling docs: \n\t%s changed" % event.src_path)
                print("======================================================")
                p = subprocess.Popen(["make", "html"], cwd="/code/docs/")
                p.wait()
            except Exception as e:
                pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = DocsCompiler(patterns="*.rst", ignore_patterns="_build/*")
    observer = PollingObserver()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()