"""
The GDriveHelper file contains the methods that can help in launching the Google Drive desktop client 
so that the backup is as smooth and uninterrupted as possible (Doesn't solve the problem of paused sync yet)

"""

import os
import subprocess
import psutil
import time
import logging as log

class GoogleDriveManager:
    def __init__(self):
        self.google_drive_processes = [
            'googledrivesync.exe',
            'Google Drive.exe',
            'drive_fs.exe',
            'GoogleDriveFS.exe'
        ]
        self.possible_paths = []
        self.find_google_drive_path()

    def find_google_drive_path(self):
        possible_paths = [
            r"C:\Program Files\Google\Drive File Stream\launch.bat",    #works with the 105.0.1.0 version
            r"C:\Program Files\Google\Drive\drive.exe",
            r"C:\Program Files (x86)\Google\Drive\drive.exe",
        ]        
        for path in possible_paths:
            if path and os.path.exists(path):
                self.possible_paths.append(path)
    
        return None

    def is_google_drive_running(self):
        try:
            l = [p.info['name'] for p in psutil.process_iter(['name'])]
            log.info(f"List of processes running: {l}")
            for g_drive_name in self.google_drive_processes:
                if g_drive_name in l:
                    return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log.error(f"GDrive exception occured: {e}")        
        return False

    def launch_google_drive(self):
        if self.possible_paths == []:
            log.error("Could not find Google Drive executable.")
            return False
    
        for drive_path in self.possible_paths:
            try:
                subprocess.Popen(drive_path)
                log.info(f"Launching Google Drive from: {drive_path}")
                time.sleep(10)
                return True
            
            except Exception as e:
                pass
        
        return False

def launch_gdrive():
    gdrive_manager = GoogleDriveManager()
    if not gdrive_manager.is_google_drive_running():
        log.warning("Google Drive is not running. Launching...")
        gdrive_manager.launch_google_drive()

if __name__ == "__main__":
    launch_gdrive()
