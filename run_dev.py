#!/usr/bin/env python3
import os
import sys
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths to watch for changes
WATCH_PATHS = ['.', 'bot', 'agent']
# File extensions to watch
WATCH_EXTENSIONS = ['.py']
# Files to ignore
IGNORE_FILES = ['__pycache__', '.pyc', '.git']

class SourceCodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_process()
        
    def restart_process(self):
        """Kill the current process and start a new one"""
        if self.process:
            logger.info("Stopping the bot process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        logger.info("Starting the bot process...")
        self.process = subprocess.Popen([sys.executable, 'main.py'])
    
    def should_restart(self, event):
        """Check if we should restart based on the file changed"""
        if event.is_directory:
            return False
        
        # Check if the file has an extension we care about
        file_ext = os.path.splitext(event.src_path)[1].lower()
        if file_ext not in WATCH_EXTENSIONS:
            return False
        
        # Check if the file is in our ignore list
        for ignore in IGNORE_FILES:
            if ignore in event.src_path:
                return False
        
        return True
    
    def on_modified(self, event):
        if self.should_restart(event):
            logger.info(f"Detected change in {event.src_path}")
            self.restart_process()
    
    def on_created(self, event):
        if self.should_restart(event):
            logger.info(f"Detected new file {event.src_path}")
            self.restart_process()

def main():
    """Run the development server with auto-restart"""
    logger.info("Starting development server with auto-restart...")
    event_handler = SourceCodeChangeHandler()
    observer = Observer()
    
    # Watch all directories in WATCH_PATHS
    for path in WATCH_PATHS:
        if os.path.exists(path):
            observer.schedule(event_handler, path=path, recursive=True)
            logger.info(f"Watching directory: {path}")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Development server stopping...")
        if event_handler.process:
            event_handler.process.terminate()
        observer.stop()
    
    observer.join()
    logger.info("Development server stopped")

if __name__ == "__main__":
    main() 