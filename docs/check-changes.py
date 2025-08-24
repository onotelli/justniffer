import time
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger

source_dir = '.'  
destination_dir = 'my-site'  # 

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        abs_source_path = os.path.abspath(os.path.dirname(event.src_path))
        abs_source_dir = os.path.abspath(source_dir)
        logger.info(f'File changed: {event.src_path} ')
        if not event.is_directory and abs_source_dir == abs_source_path:
            src_path = event.src_path
            filename = os.path.basename(src_path)
            dest_path = os.path.join(destination_dir, filename) # type: ignore
            content = None
            if filename.endswith('.md'):
                with open(src_path, 'r') as file:
                    content = file.read()
                with open(dest_path, 'w') as file:
                    file.write('''
---
layout: default
---

''')
                    file.write(content)
            else:
                shutil.copy2(src_path, dest_path)
            logger.info(f'Copied: {filename} to {destination_dir}')

if __name__ == '__main__':
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=source_dir, recursive=False)  # Set recursive=False
    observer.start()
    for filename in os.listdir(source_dir):
        # touch file
        os.utime(os.path.join(source_dir, filename), None)


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
