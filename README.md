[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/nouse4it/netmiko_IOS_Update)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

# netmiko_IOS_Update
Use Netmiko Framework to update IOS of Cisco 2960X Switches (incl. up to 4 Stacks) and IOS-XE Switches (f.e. Cat9300L)

Author: nouse4it <github@schlueter-online.net>

## IOS_update_threating_w_stack.py
Illustrate the following conecepts:
- Fully automate Update process of IOS on given IOS-based Switch
-- Including 2960x-Stacks (tested with up to 4)
- Process handling happend parallel by threating
- Including MD5-Check after copy of Software to Switch to ensure integrity
- When update finished, reload device

## Use Case Description

The script is intended to automatically update IOS and IOS-XE based devices.
The script is able to perform the update on multiple devices in parallel. This makes it possible to run an OS update on many devices at once and ensures that the update process is automated and therefore always runs the same.

## Installation
Please use Netmiko at least 2.4.2 ---> pip install netmiko
Netmiko has the following requirements (which pip will install for you)

    Netmiko >= 2.4.2
    Paramiko >= 2.4.3
    scp >= 0.13.2
    pyserial
    textfsm
For more informations see ---> https://pypi.org/project/netmiko/

Python Version must be at least v3.6

I also added you requirements.txt, where you can find all dependencies --> [REQUIREMENTS](https://github.com/nouse4it/netmiko_IOS_Update/blob/master/REQUIREMENTS.txt)

PLEASE MAKE NOTE THAT THIS SCRIPT ONLY LEVERAGES NETMIKO! THERE IS NO NORNIR OR OTHER FRAMEWORK IN USE!

## Usage
Modifiy the variable `<devices = read_devices('path-to-devices_file')>`

After done so, you need to update the devices_file with the needed information of the switches you want to update.
Use `<IP-Address>,<device-type (f.e. cisco-ios or cisco-xe)>,<hostname>`

When this files are prepared, run the main script and put in the asked infos:
* Filename (file needs to be located in same file as script)
* Username
* Password

Leave the rest up to the script ;-)

## Getting help

For more help about netmiko please go to https://pynet.twb-tech.com/blog/automation/netmiko.html or https://github.com/ktbyers/netmiko

## Credits and references
1. @ktbyers and the Netmiko Library
2. Cisco DevNet Course of @hpreston
3. David Bombals Network Automation Course on Udemy

## Licensing info

Please see [LICENSE](https://github.com/nouse4it/netmiko_IOS_Update/blob/master/LICENSE)
