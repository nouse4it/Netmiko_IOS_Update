"""
Category: Python Config Script
Author: Benjamin Schlüter <benjamin.schlueter@hirschvogel.com>

IOS_update_threating_w_stack.py
Illustrate the following conecepts:
- Upload of IOS Software of given IOS-based Switch and reboot
-- Including 2960x-Stacks
- Process handling happend parallel by threating
- Including MD5-Check after copy of Software to Switch to ensure integrity
- New feature, support of Cisco IOS-XE Device like Cat9300L
-- Stacks supported aswell
"""

__author__ = "nouse4it"
__author_email__ = "github@schlueter-online.net"
__copyright__ = "Copyright (c) 2020 nouse4it "

# Importing all needed Modules
import netmiko
from netmiko import SCPConn,ConnectHandler
import os,sys,subprocess,re
from pprint import pprint
import json
import threading
import time
import getpass

#------------------------------------------------------------------------------
def check_md5(filename):
    command = 'md5sum '+filename
    o = subprocess.getoutput(command)
    output = o.split(' ')
    return output[0]
#------------------------------------------------------------------------------
def software_install(net_connect,file):
    net_connect.send_command('wr')
    net_connect.send_command('install add file flash:{} activate commit'.format(file), expect_string='This operation may require a reload of the system', delay_factor = 4)
    net_connect.send_command('y', expect_string=r'#')
#------------------------------------------------------------------------------
def cleanup(net_connect):
    net_connect.send_command('install remove inactive')
    net_connect.send_command('y', expect_string=r'Do you want to remove the above files?')
#------------------------------------------------------------------------------
def set_boot(net_connect,file):
    get_old_vers = net_connect.send_command('sh version | i System image file is')
    old_vers = get_old_vers.split('"')[1]
    net_connect.config_mode()
    net_connect.send_command('boot system switch all flash:{},{} '.format(file,old_vers))
    net_connect.exit_config_mode()
    output = net_connect.send_command('sh boot | i BOOT')
    print('Following Boot String was set: {}', format(output))
    net_connect.send_command('wr')
#------------------------------------------------------------------------------
def reload(net_connect):
    net_connect.send_command('reload',expect_string='')
    #uncomment if you want a plannend reload, no immediately reboot
    # net_connect.send_command('reload at <insert date time f.e. 06:30 1 November IOS-Update>',expect_string='System configuration has been modified')
    # net_connect.send_command('yes\n')
    net_connect.send_command('\n')
#------------------------------------------------------------------------------
def verify_md5(net_connect,file,md5):
    result = net_connect.send_command("verify /md5 flash:{} {}".format(file,md5))
    # close SSH connection
    # net_connect.disconnect()
    reg = re.compile(r'Verified')
    verify = reg.findall(result)
    if verify:
        result = True
    else:
        result = False
    return result
#------------------------------------------------------------------------------
def verify_space_iosxe(net_connect,file):
    result = net_connect.send_command("show flash:")
    # close SSH connection
    # net_connect.disconnect()
    reg = re.compile(r'(\d+)\sbytes\savailable')
    space = int(reg.findall(result)[0])
    reg = re.compile(r'.*-rwx.*({})'.format(file))
    exist = reg.findall(result)
    f_size = os.path.getsize(file)
    if space >= f_size:
        result = 'True'
    if space < f_size:
        result = 'False'
    if exist:
        exist = 'True'
    else:
        exist = 'False'
    return result,exist
#------------------------------------------------------------------------------
def verify_space(net_connect,file):
    result = net_connect.send_command("show flash:")
    # close SSH connection
    # net_connect.disconnect()
    reg = re.compile(r'(\d+)\sbytes\sfree')
    space = int(reg.findall(result)[0])
    reg = re.compile(r'.*-rwx.*({})'.format(file))
    exist = reg.findall(result)
    f_size = os.path.getsize(file)
    if space >= f_size:
        result = 'True'
    if space < f_size:
        result = 'False'
    if exist:
        exist = 'True'
    else:
        exist = 'False'
    return result,exist
#------------------------------------------------------------------------------
def transfer_file(net_connect,file):
    net_connect.config_mode()
    net_connect.send_command('ip scp server enable')
    scp_conn = SCPConn(net_connect)
    s_file = file
    d_file = file
    scp_conn.scp_transfer_file(s_file, d_file)
#------------------------------------------------------------------------------
def stack_check(net_connect,file):
    output = net_connect.send_command("sh run | i GigabitEthernet")
    intf = output.splitlines()
    if 'interface GigabitEthernet4/0/1' in intf:
        print('It´s a 4-Switch Stack')
        print('Copying Image to flash4:')
        net_connect.send_command('copy flash:%s flash4:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)
        
        print('Copying Image to flash3:')
        net_connect.send_command('copy flash:%s flash3:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)

        print('Copying Image to flash2:')
        net_connect.send_command('copy flash:%s flash2:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)

    elif 'interface GigabitEthernet3/0/1' in intf:
        print('It´s a 3-Switch Stack')
        print('Copying Image to flash3:')
        net_connect.send_command('copy flash:%s flash3:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)

        print('Copying Image to flash2:')
        net_connect.send_command('copy flash:%s flash2:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)

    elif 'interface GigabitEthernet2/0/1' in intf:
        print('It´s a 2-Switch Stack')
        print('Copying Image to flash2:')
        net_connect.send_command('copy flash:%s flash2:' %(file), expect_string='Destination filename')
        net_connect.send_command('\n', expect_string=r'#', delay_factor=5)

    elif 'interface GigabitEthernet1/0/1' in intf:
        print('It´s not a Stack besides quoted! No additional copy needed')

    return
#------------------------------------------------------------------------------
def read_devices( devices_filename ):

    devices = {}  # create our dictionary for storing devices and their info
    
    with open( devices_filename ) as devices_file:

        for device_line in devices_file:

            device_info = device_line.strip().split(',')  #extract device info from line

            device = {'ipaddr': device_info[0],
                      'type':   device_info[1],
                      'name':   device_info[2]} # create dictionary of device objects ...

            devices[device['ipaddr']] = device  # store our device in the devices dictionary
                                                # note the key for devices dictionary entries is ipaddr

    print ('\n----- devices --------------------------')
    pprint( devices )

    return devices

#------------------------------------------------------------------------------
def command_worker( device, creds ):

#---- Connect to the device ----
    if   device['type'] == 'cisco-ios': device_type = 'cisco_ios'
    elif device['type'] == 'cisco-xe': device_type = 'cisco_xe'
    else:                              device_type = 'cisco_ios'   # attempt Cisco IOS as default

    print ('---- Connecting to device {0}, username={1}, password={2}'.format( device['ipaddr'],
                                                                                creds[0], creds[1] ))
    # ---- Connect to the device
    session = ConnectHandler(device_type=device_type, ip=device['ipaddr'],
                             username=creds[0], password=creds[1])

    if device_type == 'cisco_xe':
        #verify if there is enough free space on device to upload ios file
        net_connect = session
        ver = verify_space_iosxe(net_connect,file_s)
        print("\n\n Verifying sufficient space available on the file system ... %s\n\n" %(device['ipaddr']))

        if ver[0] == 'True' and ver[1] == 'False':
            print("\n\n Success! - proceed with image upload")
            print ("\n\nUploading file : %s ...\n\n" %(file_s))
            #transferring file to device
            net_connect = session
            transfer_file(net_connect,file_s)
            print ("\n\nSuccess! - upload file: %s to device: %s was successfull ... \n\n" % (file_s,device['ipaddr']))

            #veryfing md5
            net_connect.exit_config_mode()
            md5 = check_md5(file_s)
            print ("\n\nVerifying md5 checksum on device ... %s\n\n" %(device['ipaddr']))
            net_connect = session
            v_md5 = verify_md5(net_connect,file_s,md5)
            if v_md5 == True:
                print("\n\n MD5 Check... Success! - Starting installing, activating and commiting new Image. Reload will follow!")
                net_connect.exit_config_mode()
                try:
                    software_install(net_connect,file_s)
                except:
                    print("Reloading! Please check if device comes up again as disired ... ")
                else:
                    print("\n\n Abort !!!\n\n")
            else:
                print("\n\n Error veryfing md5 checksum on device, quitting !!!\n\n")

        elif ver[0] == 'False' and ver[1] == 'False':
            print("\n\n Not enough free space on device ... %s \n\n" %(device['ipaddr']))

        elif ver[1] == 'True':
            print ("\n\nFile already uploaded on device ... %s \n\n" %(device['ipaddr']))
    
    if device_type == 'cisco_ios':
        #verify if there is enough free space on device to upload ios file
        net_connect = session
        ver = verify_space(net_connect,file_s)
        print("\n\n Verifying sufficient space available on the file system ... %s\n\n" %(device['ipaddr']))

        if ver[0] == 'True' and ver[1] == 'False':
            print("\n\n Success! - proceed with image upload")
            print ("\n\nUploading file : %s ...\n\n" %(file_s))
            #transferring file to device
            net_connect = session
            transfer_file(net_connect,file_s)
            print ("\n\nSuccess! - upload file: %s to device: %s was successfull ... \n\n" % (file_s,device['ipaddr']))

            #veryfing md5
            net_connect.exit_config_mode()
            md5 = check_md5(file_s)
            print ("\n\nVerifying md5 checksum on device ... %s\n\n" %(device['ipaddr']))
            net_connect = session
            v_md5 = verify_md5(net_connect,file_s,md5)
            if v_md5 == True:
                print("\n\n MD5 Check... Success! - Starting check how many Switches in Stack")
                net_connect.exit_config_mode()
                stack_check(net_connect,file_s)
                set_boot(net_connect,file_s)
                print("\n\n Inserting Boot System Command... Success! - proceed with set reload time")
                try:
                    reload(net_connect)
                except:
                    print("Reload Time Set ... ")
                else:
                    print("\n\n Abort !!!\n\n")
            else:
                print("\n\n Error veryfiing md5 checksum on device, quitting !!!\n\n")

        elif ver[0] == 'False' and ver[1] == 'False':
            print("\n\n Not enough free space on device ... %s \n\n" %(device['ipaddr']))

        elif ver[1] == 'True':
            print ("\n\nFile already uploaded on device ... %s \n\n" %(device['ipaddr']))
      
    session.disconnect()

    return

#==============================================================================
# ---- Main: Run Commands
#==============================================================================

file_s = input("Enter Image Filename: ")
username = input("Enter Usernamen: ")
password = getpass.getpass(prompt ="Enter Password: ")
devices_file = input("Enter devices_file location: ")

devices = read_devices( devices_file )
creds   = (username, password)

config_threads_list = []

for ipaddr,device in devices.items():
    print('Creating thread for: ', device)
    config_threads_list.append(threading.Thread(target=command_worker, args=(device, creds)))

print('\n---- Begin running command threading ----\n')
for config_thread in config_threads_list:
    config_thread.start()

for config_thread in config_threads_list:
    config_thread.join()
