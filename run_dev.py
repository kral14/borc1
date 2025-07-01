import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    """Fayl dəyişikliklərini izləyir və proqramı yenidən başladır."""
    def __init__(self):
        self.process = None
        self.start_process()

    def start_process(self):
        """main.py faylını yeni bir prosesdə işə salır."""
        print(">>> Proqram başladılır...")
        self.process = subprocess.Popen([sys.executable, 'main.py'])

    def restart_process(self):
        """Mövcud prosesi dayandırır və yenisini başladır."""
        print(">>> Fayllarda dəyişiklik aşkarlandı. Proqram yenidən başladılır...")
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.start_process()

    def on_modified(self, event):
        """Yalnız .py faylları dəyişdirildikdə proqramı yenidən başladır."""
        if event.is_directory:
            return
        
        # DƏYİŞİKLİK BURADADIR: Yalnız .py fayllarını yoxlayırıq
        if event.src_path.endswith('.py'):
            # run_dev.py faylının özü dəyişdikdə reaksiya verməmək üçün yoxlama (optional)
            if "run_dev.py" in event.src_path:
                return
            self.restart_process()

if __name__ == "__main__":
    path = '.'
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(">>> Development server aktivdir. Fayl dəyişiklikləri izlənilir...")
    print(">>> Proqramı tam dayandırmaq üçün terminalda CTRL+C basın.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()
    observer.join()
    print(">>> Development server dayandırıldı.")