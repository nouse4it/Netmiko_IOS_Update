# netmiko_IOS_Update
Use Netmiko Framework to update IOS of Cisco 2960X Switches and up to 4 Stacks.

Author: nouse4it <github@schlueter-online.net>

IOS_update_threating_w_stack.py
Illustrate the following conecepts:
- Fully automate Update process of IOS on given IOS-based Switch
-- Including 2960x-Stacks (tested with up to 4)
- Process handling happend parallel by threating
- Including MD5-Check after copy of Software to Switch to ensure integrity
- When update finished, reload device

You need to fill the devices-file with the needed information of the switches you want to update.
After this run the main script and put in the name of the update file (needs to be in same location as the script), your username and password, when prompted for.
Leave the rest up to the script.
"""
