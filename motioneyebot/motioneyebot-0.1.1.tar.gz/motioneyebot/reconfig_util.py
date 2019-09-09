# reconfig_util.py
import re
import os
import pkg_resources

def main():
    config_data = []
    loop_input = True

    print('################ motioneyebot Configuration ################')
    print('\nThank you for using motioneyebot! Please note that this')
    print('\nprocess will reset your current motioneyebot configuration.')

    usr_input = input('\n     Press Enter to continue or \'q\' to quit. >> ')

    if (usr_input.lower() == 'q'):
        exit(0)

    while loop_input:

        print('\n')
        usr_input = input('1) Enter the your GroupMe access token >> ')
        config_data.append(usr_input)

        usr_input = input('2) Now enter your GroupMe bot ID >> ')
        config_data.append(usr_input)

        usr_input = input('3) Now enter your GroupMe group ID >> ')
        config_data.append(usr_input)

        usr_input = input('4) Enter the path to your server\'s index ' +
                            'page >> ')
        config_data.append(usr_input)

        usr_input = input('5) Enter the IP address of your MotionEye ' +
                            'camera >> ')
        config_data.append(usr_input)

        usr_input = input('6) Enter the public IP address of this device >> ')
        config_data.append(usr_input)

        usr_input = input('*Optional* Enter the URL to your camera ' +
                            'uploads >> ')
        if (len(usr_input) == 0):
                usr_input = '-' # Add space so config_data appends something.

        config_data.append(usr_input)

        usr_input = input('*Optional* Enter the name for your Bot (only' +
                        '\ndisplays in this program) >> ')
        if (len(usr_input) == 0):
                usr_input = 'Pops' # Add space so config_data appends something.

        config_data.append(usr_input)

        usr_input = input('*Optional* Enter the name for your Group (only' +
                        '\ndisplays in this program) >> ')
        if (len(usr_input) == 0):
                usr_input = 'motioneye Group' # Add space so config_data appends something.

        config_data.append(usr_input)

        missing_data = False
        for i in range(6):
            if (len(config_data[i]) == 0):
                # tell user first line left blank
                print('\nYou left one or more lines blank starting with' +
                    '\nline ' + str(i + 1) + '\n')
                # clear contents of array if user forgot to enter line
                # don't let code crash if user entered nothing
                if (len(config_data) > 0):
                    del(config_data[:])
                missing_data = True
                break

        if not (missing_data):
            loop_input = False

    configfile = pkg_resources.resource_filename(__name__, 'data/config.txt')
    with open(configfile, 'w') as f:

        f.write('ACCESS_TOKEN = \'' + config_data[0] +
                    '\'     # GROUPME ACCESS TOKEN\n')

        f.write('BOT_ID = \'' + config_data[1] +
                    '\'         # GROUPME BOT ID\n')

        f.write('GROUP_ID = \'' + config_data[2] +
                    '\'       # GROUPME GROUP ID\n')

        f.write('INDEX_LOCATION = \'' + config_data[3] +
                    '\'# PATH TO SERVER INDEX PAGE\n')

        f.write('MOTIONEYE_IP = \'' + config_data[4] +
                    '\'   # IP ADDRESS OF MOTIONEYE CAM\n')

        f.write('PUBLIC_IP = \'' + config_data[5] +
                    '\'      # PUBLIC IP ADDRESS OF THIS DEVICE\n')

        f.write('UPLOADS_URL = \'' + config_data[6] +
                    '\'    # DROPBOX OR DRIVE URL TO UPLOADS\n')

        f.write('BOT_NAME = \'' + config_data[7] +
                    '\'       # GROUPME BOT NAME (ARBITRARY)\n')

        f.write('GROUP_NAME = \'' + config_data[8] +
                    '\'     # GROUPME GROUP NAME (ARBITRARY)')
main()
