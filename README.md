# SSSIHMS-Data-Transfer
Program to automatically backup contents of directory into given Target directory.

## Current implementation idea:
User enters the Path of the Source and Target folders for the backup program in [GUI for Changing Paths.py](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py), which is stored in a Paths file.

[Main script](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py) is set up as a recurring task using the Windows Task manager, which reads the links from the Paths file and calls a recursive function that copies the files of the previous day into the Target under the same folder name.


Dependencies: `Shutil`, `OS`, `PySimpleGUI`

Turns out a scheduled task that runs when the user is not logged in will be run in a separate environment by itself, which is hidden from the user.
So, I came up with a Minimum Program that has no GUI and just executes the code with a logger facility.

- [ ] Need to come up with a solution for GUI T_T

### To do:
- [x] Happy Path and Minimum Viable Product
  - [x] Basic code to transfer current day files
  - [x] Implementation of GUI for changing Paths
  - [ ] Test it out at SSSIHMS

- [ ] Hardening
  - [ ] Exception handling for other cases (malicious input etc.)
  - [x] Logic for no. of days to check (Given by user, Exceptions etc are handled)
  - [ ] Unit testing, End-to-end testing
  - [ ] Style check
  - [ ] Can the task be setup without the user doing it manually?
  
- [ ] Post GA
  - [x] Logging facility (Need to make it better)
  - [ ] REST API
