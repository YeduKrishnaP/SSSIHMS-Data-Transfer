# SSSIHMS-Data-Transfer
Program to automatically backup contents of directory into given Target directory.

## Current implementation idea:
User enters the Path of the Source and Target folders for the backup program in [GUI for Changing Paths.py](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py), which is stored in a Paths file.

[Main script](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py) is set up as a recurring task using the Windows Task manager, which reads the links from the Paths file and calls a recursive function that copies the files of the previous day into the Target under the same folder name.


Dependencies: Shutil, OS, PySimpleGUI

### To do:
- [x] Happy Path and Minimum Viable Product
  - [x] Basic code to transfer current day files
  - [x] Implementation of GUI for changing Paths
  - [ ] Test it out at SSSIHMS

- [ ] Hardening
  - [ ] Exception handling for other cases (malicious input etc.)
  - [ ] Logic for no. of days to check (Should it be given by user?)
  - [ ] Unit testing, End-to-end testing
  - [ ] Style check
  - [ ] Can the task be setup without the user doing it manually?
  
- [ ] Post GA
  - [ ] Logging facility
  - [ ] REST API
