from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import threading
import time

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, callback, exts=None):
        super().__init__()
        self.callback = callback
        self.exts = exts or {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).suffix.lower() in self.exts:
            self.callback(event.src_path)

class FileMonitor:
    def __init__(self, folder: Path, callback):
        self.folder = folder
        self.callback = callback
        self.observer = Observer()
        self._thread = None

    def start(self):
        handler = NewFileHandler(self.callback)
        self.observer.schedule(handler, str(self.folder), recursive=False)
        self.observer.start()
        self._thread = threading.Thread(target=self._join, daemon=True)
        self._thread.start()

    def _join(self):
        try:
            while self.observer.is_alive():
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()

    def stop(self):
        self.observer.stop()
