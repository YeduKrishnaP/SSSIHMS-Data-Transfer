# SSSIHMS-Data-Transfer (Outdated Readme, will update soon ;) )
Program to automatically backup contents of directory into given Target directory.

## Current implementation idea (partly scrapped):
User enters the Path of the Source and Target folders for the backup program in [GUI for Changing Paths.py](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py), which is stored in a Paths file.

[Main script](https://github.com/YeduKrishnaP/SSSIHMS-Data-Transfer/blob/main/(latest)%20Tranfer%20Script%20for%20IHMS.py) is set up as a recurring task using the Windows Task manager, which reads the links from the Paths file and calls a recursive function that copies the files of the previous day into the Target under the same folder name.

Dependencies: `Shutil`, `OS`, `PySimpleGUI`

## Ideas

Turns out a scheduled task that runs when the user is not logged in will be run in a separate environment by itself, which is hidden from the user.
So, I came up with a Minimum Program that has no GUI and just executes the code with a logger facility, which sends mails to a given mail list with logs as attachments.

- [x] Need to come up with a solution for GUI
      Could be done with two processes. One that runs silently when the user is logged out, other that is run when the user logs in
      ****But, is a daily GUI even required when the email client sends notifications everyday?****
      
Need to make the installation process user-friendly - Currently, the user needs to schedule the task manually etc. (trying out SCHTASKS)

- [x] Add option to browse and select the folder in EditPaths.py

### To do:
- [x] Happy Path and Minimum Viable Product
  - [x] Basic code to transfer current day files
  - [x] Implementation of GUI for changing Paths
  - [x] Test it out at SSSIHMS (But keeps failing for some reason)

- [ ] Hardening
  - [ ] Exception handling for other cases (malicious input etc.)
  - [x] Logic for no. of days to check (Given by user, Exceptions etc are handled)
  - [ ] Unit testing, End-to-end testing
  - [ ] Style check
  - [x] User Friendly installation (currently trying out SCHTASKS)
  
- [ ] Post GA
  - [x] Logging facility (Need to make it better)
    - [x] Email client for the logs (incase of a critical failure)
  - [ ] REST API
