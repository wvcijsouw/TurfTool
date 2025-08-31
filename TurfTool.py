'''TurfTool der Lustrumcommissie 16 by Secretary Cijsouw'''
'''Based on the TurfTool of Studytour 39 as written by Secretary Van Lent'''

import datetime
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
import sys
import configparser
import difflib




class TurfTool():
    """Main TurfTool class.
    """    
    def __init__(self, config,**kwargs):
        super().__init__(**kwargs)
        
        # Initiate the main loop state
        self.active = True

        # Initiate a debug state
        self.debug = False

        # Read the base settings, files and data
        self._check_filepresence(config)
        self._readconfig(config)

        # Determine current time
        self.currenttime = datetime.datetime.now()





    def _check_filepresence(self,config):
        """This function checks whether the settings cfg file and the Turfjes.csv files are present.\\
            If settings cfg file isn't present, it raises an error since the TurfTool can't function without it. \\
            If the Turfjes.csv file isn't present, it creates a new file.

        Args:
            config (str): Settings cfg file location.
        """

        if self.debug:
            # For debugging: print settings.cfg location
            print(f"Attempting to find the settings file at location {config}...")

        # Check whether settings.cfg is present
        cfgpresent = os.path.exists(config)

        if not cfgpresent:
            # If not present, raise an error
            raise FileNotFoundError("Settings file not found. Either Wouter made an oopsie or the file got deleted along the way.\n"\
                                    "If you don't know where it is or what went wrong, contact Wouter.\n")
        elif self.debug:

            print("Settings file found succesfully")
            print("Checking existence of turf file...")

        # Check whether Turfjes.csv is present
        self.turfpath = os.path.dirname(config) + '\\Turfjes.csv'
        turfpresent = os.path.exists(self.turfpath)

        if not turfpresent:
            if self.debug:
                print("Turf file not found, creating fresh file...")
            # If not present, create a fresh file
            turffile = open(self.turfpath,'x',newline='')
            writer = csv.writer(turffile,delimiter=';')
            writer.writerow(['Category','Name','Time','Day','Month','Year','Reason'])
            turffile.close()
        elif self.debug:
            print("Existing turf file found, proceeding...")

        if self.debug:
            # Print that file checks have been completed
            print(f"File checks completed!\n\n")




    def _readconfig(self,config):
        """Functionally important function that interprets the settings cfg file for further use.

        Args:
            config (str): path to the settings cfg file.
        """
        ConfigParser = configparser.ConfigParser()
        ConfigParser.optionxform = str
        ConfigParser.read(config)

        def listdecoder(string,type=list):
            # Select type 
            if type == list:
                for i in '[]':
                    string = string.replace(i,'')

                # Split it up into separate items
                string = string.split(',')

                # Remove leading spaces and return
                lst = [item.lstrip() for item in string]
                return [item for item in lst if item != '']


        # Read the names
        self.names = {item[0]: item[1] for item in ConfigParser.items('names')}
        # Read the aliases for the names
        self.aliases = {item[0]: listdecoder(item[1]) for item in ConfigParser.items('aliases')}
        # Slightly transform this to be {Name:Aliases}
        self.aliases = {self.names[key]: self.aliases[key] for key in self.aliases.keys()}
        # Read the groups
        self.groups = {item[0]: listdecoder(item[1]) for item in ConfigParser.items('groups')}
        # Read the aliases for the groups
        self.groupsaliases = {item[0]: listdecoder(item[1]) for item in ConfigParser.items('groupsaliases')}
        
        # Read the turf reasons
        self.turfreasons = {item[0]:    {'aliases': listdecoder(item[1].split('],')[0]),
                                        'value': int(item[1].split('],')[1])} for item in ConfigParser.items('turfreasons')}
        # Read the inning reasons
        self.inningreasons = {item[0]:  {'aliases': listdecoder(item[1].split('],')[0]),
                                        'value': int(item[1].split('],')[1])} for item in ConfigParser.items('inningreasons')}
        # Read the turf rules
        self.solidarity = bool(ConfigParser.get('turfrules','solidarity'))
        if self.solidarity:
            self.solidarityday = ConfigParser.get('turfrules','solidarityday')
            self.solidaritytime = ConfigParser.get('turfrules','solidaritytime')
        self.forcenonegative = bool(ConfigParser.get('turfrules','forcenonegative'))

        # Read the plot settings
        self.day0 = datetime.datetime.strptime(ConfigParser.get('plotsettings','day0'),"%H:%M %d %b %Y")
        self.day0event = ConfigParser.get('plotsettings','day0event')
        self.graphxticks = int(ConfigParser.get('plotsettings','graphxticks'))
        self.usecolours = ConfigParser.get('plotsettings','usecolours').lower() == 'true'
        self.colours = [f'#{i}' for i in listdecoder(ConfigParser.get('plotsettings','colours'))]
        self.barcolours = [int(i) for i in listdecoder(ConfigParser.get('plotsettings','barcolours'))]
        self.maxreasons = int(ConfigParser.get('plotsettings','maxreasons'))
        self.anytimeramount = int(ConfigParser.get('plotsettings','anytimeramount'))


    def launch(self):
        """Launches the TurfTool. Also suf launch.
        """        
        # On first launch, print the top line
        self._print_topline(welcomemsg=True)
        # Initiate the main loop
        while self.active:
            # Print the command list
            command = input('\nWhat would you like to do?\n\n'\
                            'Type "Turf" or "T" to turf people\n'\
                            'Type "Inning" or "I" to in turfjes\n'\
                            'Type "Statistics" or "S" to view the turf statistics\n'\
                            'Type "Exit" or "E" to close the program\n\n'\
                            'Pressing Enter also closes the program.\n\n')
            
            # Interpret the commands
            self._interpret_commands(command)
            self._print_topline()



    def _print_topline(self,welcomemsg = False):
        """This command prints the top line (so the TurfTool graphic) and clears the screen. Optionally you can also print the welcome message.

        Args:
            welcomemsg (bool, optional): Whether to print the welcome message. Defaults to False.
        """        
        # Clear the screen (if debug is disabled)
        if not self.debug:
            os.system('cls')

        # Print the top line
        print(      r'==============================================================================================================='+'\n'\
                    r"                                                                                                               "+'\n'\
                    r"                                    _____            __ _____           _                                      "+'\n'\
                    r"                                   |_   _|   _ _ __ / _|_   _|__   ___ | |                                     "+'\n'\
                    r"                                     | || | | | '__| |_  | |/ _ \ / _ \| |                                     "+'\n'\
                    r"                                     | || |_| | |  |  _| | | (_) | (_) | |                                     "+'\n'\
                    r"                                     |_| \__,_|_|  |_|   |_|\___/ \___/|_|                                     "+'\n'\
                    r"                                                                                                               "+'\n'\
                    r"					                                                                                             "+'\n'\
                    r'===============================================================================================================')
        if welcomemsg:
            print(  '                  Welcome to the TurfTool by Secretary Cijsouw of the 16th Lustrum Committee!                  \n'\
                    'This tool is an upgraded version of the TurfTool written by Secretary Van Lent of the 39th Studytour Committee.\n'\
                    '  This file will allow you to keep track of turfjes in an unnecessarily complicated and extensive way. Enjoy!  \n\n'\
                    '===============================================================================================================\n')



    def _interpret_commands(self, command):
        # Because of the way we phrased it we only need to check the first character, make it lowercase in order to give some more input leniency.
        # However, we first need to check for an empty input which corresponds to closing the program, otherwise it gives an error.
        if command == '' or command[0].lower() == 'e':
            self.active = False
            print()

        elif command[0].lower() == 't':
            self._print_topline()
            if not self.debug:
                try:
                    self._Turf()
                except:
                    input('Turfing failed, press Enter to return to the home screen...\n\n')
            else:
                self._Turf()
        
        elif command[0].lower() == 'i':
            self._print_topline()
            if not self.debug:
                try:
                    self._Inning()
                except:
                    input('Inning failed, press Enter to return to the home screen...\n\n')
            else:
                self._Inning()

        elif command[0].lower() == 's':
            self._print_topline()
            if not self.debug:
                try:
                    self._Statistics()
                except:
                    input('Displaying the statistics failed, press Enter to return to the home screen...\n\n')
            else:
                self._Statistics()
        
        elif command.lower() == 'debug':
            self.debug = not self.debug
            self._interpret_commands(input(f"Debug mode {'en'*self.debug}{'dis'*(1-self.debug)}abled\n\n"))

        else:
            self._print_topline()
            print('Unknown command. Please try again.\n')



    def _Turf(self):
        """Open the turf prompt.
        """   
        self._print_topline()

        # Create a state for whether to continue
        turfcontinue = True

        # First step is to ask who the turf is directed to
        nameresponse = input(   'Who earned a turf?\n'\
                                'Either input a name or an alias.\n'\
                                'You can also turf multiple people simultaneously by separating the names/alias using a comma.\n\n'\
                                'If you wish to cancel turfing, type "cancel".\n\n')

        # Check whether to continue
        if nameresponse.lower() == 'cancel':
            turfcontinue = False
        
        else:
            # Separate the targets (or put it in a list if no comma is present) and translate the aliases
            turftargets =   [self._aliastranslate(self.aliases,target.lstrip()) 
                            for target in nameresponse.split(',')]
            
            # Check if there are unknown names
            unknownnames = [name for name in turftargets if name not in self.names.values()]

            # If there are names that are not known, ask for confirmation
            if len(unknownnames) != 0:
                if len(unknownnames) == 1:
                    unknownconfirm = input(f'\n{unknownnames[0]} was not recognized, do you wish to continue? (Y/N)\n\n')
                elif len(unknownnames) == 2:
                    unknownnamestr = ''.join([unknownnames[0],' and ',unknownnames[1]])
                    unknownconfirm = input(f'\n{unknownnamestr} were not recognized, do you wish to continue? (Y/N)\n\n')
                else:
                    unknownnamestr = ''.join(f'{unknownname}, ' for unknownname in unknownnames[:-2])
                    unknownnamestr += f'{unknownnames[-2]} and {unknownnames[-1]}'
                    unknownconfirm = input(f'\n{unknownnamestr} were not recognized, do you wish to continue? (Y/N)\n\n')

                if unknownconfirm[0].lower() != 'y':
                    turfcontinue = False

            # Make a turf targets string for bookkeeping in the tool
            if len(turftargets) == 1:
                turftargetsstr = turftargets[0]
            elif len(turftargets) == 2:
                turftargetsstr = turftargets[0] + ' and ' + turftargets[1]
            else:
                turftargetsstr = ''.join(f'{name}, ' for name in turftargets[:-2])
                turftargetsstr += f'{turftargets[-2]} and {turftargets[-1]}'


        # Second step is to ask what the turf reason is
        if turfcontinue:
            self._print_topline()

            # Compile the reasons in a string
            reasonstr = ''
            for reason in self.turfreasons.keys():
                reasonstr += f'- {reason.ljust(max([len(i) for i in self.turfreasons.keys()]))}'

                # Apply actual grammar
                if len(self.turfreasons[reason]["aliases"]) == 0:
                    reasonstr += '\n'
                elif len(self.turfreasons[reason]["aliases"]) == 1:
                    reasonstr += f'  (also selectable by typing "{self.turfreasons[reason]["aliases"][0]}")\n'
                elif len(self.turfreasons[reason]["aliases"]) == 2:
                    reasonstr += f'  (also selectable by typing "{self.turfreasons[reason]["aliases"][0]}" or "{self.turfreasons[reason]["aliases"][1]}")\n'
                elif len(self.turfreasons[reason]["aliases"]) > 2:
                    dummyreasonstr = ''.join(f'"{alias}", ' for alias in self.turfreasons[reason]["aliases"][:-2])
                    dummyreasonstr += f'"{self.turfreasons[reason]["aliases"][-2]}"' + ' or ' + f'"{self.turfreasons[reason]["aliases"][-1]}"'
                    reasonstr += f'  (also selectable by typing {dummyreasonstr})\n'

            reasonresponse = input( f'Turfed: {turftargetsstr}\n\n'\
                                    'What is the reason for the turfing?\n'\
                                    f'{reasonstr}\n' \
                                    'If there was another reason, please type it out.\n\n' \
                                    'If you wish to cancel turfing, type "cancel".\n\n')
            
            # Check whether to continue
            if reasonresponse.lower() == 'cancel':
                turfcontinue = False

            elif reasonresponse == '':
                turfreason = 'Other'

            else:
                # Decode the reason
                turfreason = self._aliastranslate({reason: self.turfreasons[reason]['aliases'] for reason in self.turfreasons.keys()},
                                                    reasonresponse)


        # Third step is to ask how many turfjes this action is worth
        if turfcontinue:
            self._print_topline()
            if turfreason in self.turfreasons.keys():
                turfvalue = self.turfreasons[turfreason]['value']
            else:
                turfvalue = 1
            turfamount = input( f'Turfed: {turftargetsstr}\n'\
                                f'Reason: {turfreason}\n\n'\
                                f'How many turfs is the turfed action worth? Either input the amount of turfs as an integer or press Enter to input the standard value {turfvalue}.\n\n'\
                                'If you wish to cancel turfing, type "cancel".\n\n')
            
            if turfamount.lower() == 'cancel':
                turfcontinue = False
            elif turfamount == '':
                turfamount = turfvalue
            else:
                try:
                    turfamount = int(turfamount)
                except:
                    turfamount = 1


        # Last step is to ask for the date of the turf
        # Thanks Matthijs for the code
        if turfcontinue:
            self._print_topline()
            date = input(   f'Turfed: {turftargetsstr}\n'\
                            f'Reason: {turfreason}\n'\
                            f'Amount of turfs awarded: {turfamount}\n\n'
                            'What date was the turfed action performed? Press Enter to input the current day. Otherwise use DD/MM/YYYY\n\n'\
                            'If you wish to cancel turfing, type "cancel".\n\n')
            if date.lower() == 'cancel':
                turfcontinue = False

            elif date == '':
                day = time.ctime()[8:10].lstrip(' ')
                month = time.ctime()[4:7]
                year = time.ctime()[-4:]
            else:
                date = date.split('/')
                day = date[0].lstrip('0')
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month = months[int(date[1].lstrip("0")) - 1]
                year = date[2]

        # Then ask for the time, again thanks Matthijs for the code
        if turfcontinue:
            self._print_topline()
            timeturf = input(   f'Turfed: {turftargetsstr}\n'\
                                f'Reason: {turfreason}\n'\
                                f'Amount of turfs awarded: {turfamount}\n'
                                f'Date of turfed action: {day}/{month}/{year}\n\n'\
                                'What time was the turfed action performed? Press Enter to input 12:45 and write "now" to input the current time. \n\n' \
                                'If you wish to cancel turfing, type "cancel".\n\n')
            
            if timeturf.lower() == 'cancel':
                turfcontinue = False
            elif timeturf == 'now':
                timeturf = time.ctime()[11:16]
            elif timeturf == '':
                timeturf = '12:45'


        # After this we can write the turf and ask if the user wants to write another turf
        if turfcontinue:
            self._print_topline()
            for name in turftargets:
                for i in range(turfamount):
                    self.write_TurfFile('turf',
                                        name,
                                        timeturf,
                                        day,
                                        month,
                                        year,
                                        turfreason)
            
            # Write the confirmation message
            print(  'The following turf was written succesfully:\n'\
                    f'Turfed: {turftargetsstr}\n'\
                    f'Reason: {turfreason}\n'\
                    f'Date of turfed action: {day}/{month}/{year}\n'\
                    f'Time of turfed action: {timeturf}\n'\
                    f'Amount of turfs awarded: {turfamount}\n\n')

            repeat = input('Do you want to continue turfing? (Y/N)\n\n')
            if repeat == '':
                pass
            elif repeat[0].lower() == 'y':
                # This can kinda become a memory leak but eh don't really care tbh
                self._Turf()



    def _Inning(self):
        """Open the inning prompt.
        """        
        self._print_topline()
        # All in all the steps are pretty similar to the turf prompt

        # Create a state for whether to continue
        inningcontinue = True

        # First step is to ask who inned a turf
        nameresponse = input(   'Who inned a turf?\n'\
                                'Either input a name or an alias.\n'\
                                'You can also in turfs for multiple people simultaneously by separating the names/alias using a comma.\n\n'\
                                'If you wish to cancel inning turfs, type "cancel".\n\n')

        # Check whether to continue
        if nameresponse.lower() == 'cancel':
            inningcontinue = False
        
        else:
            # Separate the targets (or put it in a list if no comma is present) and translate the aliases
            inningtargets =   [self._aliastranslate(self.aliases,target.lstrip()) 
                            for target in nameresponse.split(',')]
            
            # Check if there are unknown names
            unknownnames = [name for name in inningtargets if name not in [self.names[key] for key in self.names.keys()]] # Jezus wat lelijk gecodeerd

            # If there are names that are not known, ask for confirmation
            if len(unknownnames) != 0:
                if len(unknownnames) == 1:
                    unknownconfirm = input(f'\n{unknownnames[0]} was not recognized, do you wish to continue? (Y/N)\n\n')
                elif len(unknownnames) == 2:
                    unknownnamestr = ''.join([unknownnames[0],' and ',unknownnames[1]])
                    unknownconfirm = input(f'\n{unknownnamestr} were not recognized, do you wish to continue? (Y/N)\n\n')
                else:
                    unknownnamestr = ''.join(f'{unknownname}, ' for unknownname in unknownnames[:-2])
                    unknownnamestr += f'{unknownnames[-2]} and {unknownnames[-1]}'
                    unknownconfirm = input(f'\n{unknownnamestr} were not recognized, do you wish to continue? (Y/N)\n\n')

                if unknownconfirm[0].lower() != 'y':
                    inningcontinue = False

            # Make a inning targets string for bookkeeping in the tool
            if len(inningtargets) == 1:
                inningtargetsstr = inningtargets[0]
            elif len(inningtargets) == 2:
                inningtargetsstr = inningtargets[0] + ' and ' + inningtargets[1]
            else:
                inningtargetsstr = ''.join(f'{name}, ' for name in inningtargets[:-2])
                inningtargetsstr += f'{inningtargets[-2]} and {inningtargets[-1]}'


        # Second step is to ask what the inning reason is
        if inningcontinue:
            self._print_topline()

            # Compile the reasons in a string
            reasonstr = ''
            for reason in self.inningreasons.keys():
                reasonstr += f'- {reason.ljust(max([len(i) for i in self.inningreasons.keys()]))}'

                # Apply actual grammar
                if len(self.inningreasons[reason]) == 0:
                    reasonstr += '\n'
                elif len(self.inningreasons[reason]) == 1:
                    reasonstr += f'  (also selectable by typing "{self.inningreasons[reason]["aliases"][0]}")\n'
                elif len(self.inningreasons[reason]) == 2:
                    reasonstr += f'  (also selectable by typing "{self.inningreasons[reason]["aliases"][0]}" or "{self.inningreasons[reason]["aliases"][1]}")\n'
                elif len(self.inningreasons[reason]) > 2:
                    dummyreasonstr = ''.join(f'"{alias}", ' for alias in self.inningreasons[reason]["aliases"][:-2])
                    dummyreasonstr += f'"{self.turfreasons[reason]["aliases"][-2]}"' + ' or ' + f'"{self.inningreasons[reason]["aliases"][-1]}"'
                    reasonstr += f'  (also selectable by typing {dummyreasonstr})\n'

            reasonresponse = input( f'Inning: {inningtargetsstr}\n\n'\
                                    'What is the reason for the inning turfs?\n'\
                                    f'{reasonstr}\n' \
                                    'If there was another reason, please type it out.\n\n' \
                                    'If you wish to cancel inning turfs, type "cancel".\n\n')
            
            # Check whether to continue
            if reasonresponse.lower() == 'cancel':
                inningcontinue = False

            elif reasonresponse == '':
                inningreason = 'Other'

            else:
                # Decode the reason
                inningreason = self._aliastranslate({reason: self.inningreasons[reason]['aliases'] for reason in self.inningreasons.keys()},
                                                    reasonresponse)

        # Third step is to ask how many turfjes this action is worth
        if inningcontinue:
            self._print_topline()
            if inningreason in self.inningreasons.keys():
                inningvalue = self.inningreasons[inningreason]['value']
            else:
                inningvalue = 1
            inningamount = input( f'Inning: {inningtargetsstr}\n'\
                                f'Reason: {inningreason}\n\n'\
                                f'How many minturfs is the inning action worth? Either enter the amount of minturfs as an integer or press Enter to input the standard value {inningvalue}.\n\n'\
                                'If you wish to cancel turfing, type "cancel".\n\n')
            
            if inningamount.lower() == 'cancel':
                inningcontinue = False
            elif inningamount == '':
                inningamount = inningvalue
            else:
                try:
                    inningamount = int(inningamount)
                except:
                    inningamount = 1


        # Last step is to ask for the date of the turf
        # Thanks Matthijs for the code
        if inningcontinue:
            self._print_topline()
            date = input(   f'Inning: {inningtargetsstr}\n'\
                            f'Reason: {inningreason}\n'\
                            f'Amount of minturfs awarded: {inningamount}\n\n'\
                            'What date was the inning action performed? Press Enter to input the current day. Otherwise use DD/MM/YYYY\n\n'\
                            'If you wish to cancel inning, type "cancel".\n\n')
            if date.lower() == 'cancel':
                inningcontinue = False

            elif date == '':
                day = time.ctime()[8:10].lstrip(' ')
                month = time.ctime()[4:7]
                year = time.ctime()[-4:]
            else:
                date = date.split('/')
                day = date[0].lstrip('0')
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month = months[int(date[1].lstrip("0")) - 1]
                year = date[2]

        # Then ask for the time, again thanks Matthijs for the code
        if inningcontinue:
            self._print_topline()
            timeinning = input( f'Inning: {inningtargetsstr}\n'\
                                f'Reason: {inningreason}\n'\
                                f'Amount of minturfs awarded: {inningamount}\n'\
                                f'Date of inning action: {day}/{month}/{year}\n\n'\
                                'What time was the inning action performed? Press Enter to input 12:45 and write "now" to input the current time. \n\n' \
                                'If you wish to cancel inning, type "cancel".\n\n')
            
            if timeinning.lower() == 'cancel':
                inningcontinue = False
            elif timeinning == 'now':
                timeinning = time.ctime()[11:16]
            elif timeinning == '':
                timeinning = '12:45'


        # After this we can write the turf and ask if the user wants to write another turf
        if inningcontinue:
            self._print_topline()
            for name in inningtargets:
                for i in range(inningamount):
                    self.write_TurfFile('minus',
                                        name,
                                        timeinning,
                                        day,
                                        month,
                                        year,
                                        inningreason)
            
            # Write the confirmation message
            print(  'The following inning action was written succesfully:\n'\
                    f'Inning: {inningtargetsstr}\n'\
                    f'Reason: {inningreason}\n'\
                    f'Amount of minturfs awarded: {inningamount}\n'\
                    f'Date of inning action: {day}/{month}/{year}\n'\
                    f'Time of inning action: {timeinning}\n\n')

            repeat = input('Do you want to continue inning? (Y/N)\n\n')
            if repeat == '':
                pass
            elif repeat[0].lower() == 'y':
                # This can kinda become a memory leak but eh don't really care tbh
                self._Inning()



    def _Statistics(self):
        """Open the statistics prompt.
        """        

        # Start with getting the current turfs
        turfbalance, turfset = self.read_TurfFile()

        # Create a boolean for whether to continue viewing statistics
        statscontinue = True

        # Open the prompt asking who the user wants to view the turfs of
        self._print_topline()

        # Compile the groups in a string
        groupstr = ''
        for group in self.groups.keys():
            groupstr += f'- {group.ljust(max([len(i) for i in self.groups.keys()]))}'

            # Apply actual grammar
            if len(self.groupsaliases[group]) == 0:
                groupstr += '\n'
            elif len(self.groupsaliases[group]) == 1:
                groupstr += f'  (also selectable by typing "{self.groupsaliases[group][0]}")\n'
            elif len(self.groupsaliases[group]) == 2:
                groupstr += f'  (also selectable by typing "{self.groupsaliases[group][0]}" or "{self.groupsaliases[group][1]}")\n'
            elif len(self.groupsaliases[group]) > 2:
                dummygroupstr = ''.join(f'"{alias}", ' for alias in self.groupsaliases[group][:-2])
                dummygroupstr += f'"{self.groupsaliases[group][-2]}"' + ' or ' + f'"{self.groupsaliases[group][-1]}"'
                groupstr += f'  (also selectable by typing {dummygroupstr})\n'
        
        groupresponse = input(  'Which group do you want to want to view the statistics from?\n\n'\
                                f'{groupstr}\n'\
                                'You can also select everyone by pressing Enter.\n'\
                                'Alternatively, you can also select individuals by typing out their names. Separate their names using a comma if you want to select multiple people.\n\n'\
                                'If you wish to quit viewing the statistics, type "cancel".\n\n')

        if groupresponse.lower() == 'cancel':
            statscontinue = False
        
        elif groupresponse.lower() == '':
            group = list(self.names.values())

        # Check if the response is a group alias
        elif self._aliastranslate(self.groupsaliases,groupresponse) in self.groupsaliases.keys():
            group = self.groups[self._aliastranslate(self.groupsaliases,groupresponse)]

        # Else the only usable option left is if the response is a name/group of names
        else:
            # Separate the targets (or put it in a list if no comma is present) and translate the aliases
            group = [self._aliastranslate(self.aliases,target.lstrip()) 
                            for target in groupresponse.split(',')]
            
            # Check if there are unknown names
            unknownnames = [name for name in group if name not in self.names.values()]
        
            if len(unknownnames) > 0:
                input('\n\nInput not recognized. Press Enter to retry...\n\n')
                statscontinue = False
                self._Statistics()


        if statscontinue == False:
            pass
        # If no turfs are present, return to main screen
        elif len(turfset) == 0:
            input(  'No turfs logged yet.\n\n'\
                    'Press Enter to continue...\n\n')
        else:
            # Clear the screen and proceed to showing the statistics
            self._print_topline()

            # Print the turf balance for the selected group
            print('Current turf balance:\n')
            print(''.join([name+': '+str(turfbalance[name])+'\n' for name in group]))

            # Reshape the turf list to a balance-per-event form
            ## Create a time-zero event for plotting reasons
            turfmat = {name:{'alltime':[0],
                            'current':[0]
                            } for name in group}
            turfmat['time'] = [min(turfset[0][0],self.day0)]
            turfmat['event'] = [None]
            turfmat['eventtype'] = [None]
            # From testing the pie chart was pretty slow, so precompile all the turf reason counts
            turfmat['turfeventcount'] = [{}]

            nondisplayedreasons = []
            # Walk through the turf list
            for turf in turfset:
                if turf[1][1] in group:
                    # Add the time, event and event type of the turf to the relevant lists
                    turfmat['time'].append(turf[0])
                    turfmat['eventtype'].append(turf[1][0])
                    turfmat['turfeventcount'].append(turfmat['turfeventcount'][-1].copy())

                    # For the event, make sure it is in the reason list. Otherwise assign it as Other.
                    if turf[1][6] in self.turfreasons.keys() or turf[1][6] in self.inningreasons.keys():
                        turfmat['event'].append(turf[1][6])
                    else:
                        nondisplayedreasons.append(turf[1][6])
                        turfmat['event'].append('Other')

                    # Add 1 to the event count if the event type is 'turf'.
                    if turfmat['eventtype'][-1] != 'turf':
                        pass
                    elif turfmat['event'][-1] in turfmat['turfeventcount'][-1].keys():
                        turfmat['turfeventcount'][-1][turfmat['event'][-1]] += 1
                    else:
                        turfmat['turfeventcount'][-1][turfmat['event'][-1]] = 1

                    # Copy the value over for each person within the group
                    for name in group:
                        turfmat[name]['alltime'].append(turfmat[name]['alltime'][-1])
                        turfmat[name]['current'].append(turfmat[name]['current'][-1])

                    # If it is a inned turf, check for nonzero
                    if turf[1][0] == 'minus' and turfmat[turf[1][1]]['current'][-1] > 0:
                        turfmat[turf[1][1]]['current'][-1] -= 1

                    elif turf[1][0] == 'minus' and self.forcenonegative == False:
                        turfmat[turf[1][1]]['current'][-1] -= 1

                    elif turf[1][0] == 'turf':
                        turfmat[turf[1][1]]['alltime'][-1] += 1
                        turfmat[turf[1][1]]['current'][-1] += 1

            # Do some postprocessing on the turf event count to limit the reasons
            for turfcountid in range(len(turfmat['turfeventcount'])):
                if len(turfmat['turfeventcount'][turfcountid].keys()) > self.maxreasons:
                    # Sort the turf count
                    s_turfcount = dict(sorted(turfmat['turfeventcount'][turfcountid].items(), 
                                                        key=lambda x:x[1], 
                                                        reverse=True))

                    # Add the highest counting turf reasons until the maximum amount of reasons are reached
                    turfcount_disp = {"Other": 0}
                    while len(turfcount_disp.keys()) < self.maxreasons:
                        if list(s_turfcount.keys())[0] == "Other":
                            turfcount_disp["Other"] += s_turfcount["Other"]
                        else:
                            turfcount_disp[list(s_turfcount.keys())[0]] = s_turfcount[list(s_turfcount.keys())[0]]
                        s_turfcount.pop(list(s_turfcount.keys())[0])

                    # Add the remaining reasons to others
                    turfcount_disp["Other"] += sum(s_turfcount.values())

                    # Update the turf matrix
                    turfmat['turfeventcount'][turfcountid] = turfcount_disp


            # Make a last column at the current time for plotting reasons
            for name in group:
                turfmat[name]['alltime'].append(turfmat[name]['alltime'][-1])
                turfmat[name]['current'].append(turfmat[name]['current'][-1])
            

            tend = self.currenttime
            turfmat['time'].append(tend)
            turfmat['event'].append(None)
            turfmat['eventtype'].append(None)
            turfmat['turfeventcount'].append(turfmat['turfeventcount'][-1].copy())

            # Print which turfs are grouped into 'Other'
            print('The following turfing reasons were grouped into "Other" for plotting reasons:\n')
            print(''.join([reason + '\n' for reason in set(nondisplayedreasons)]))

            # Prepare the subplots
            ## Bar chart for all-time/current turf standings
            ax1 = plt.subplot(2,2,1)
            X_axis = list(range(len(group)))
            width = 0.4

            # Pie chart for the turf reasons
            ax2 = plt.subplot(2,2,2)


            # Graph for turfs over time
            ax3 = plt.subplot(2,2,(3,4))
            ## Plot the crossover line for anytimers
            ax3.plot([self.day0, self.currenttime],[self.anytimeramount]*2, color='red')
            ## This can just be pre-plotted since we can just shift the x limit
            colourid = 0
            for name in group:
                if self.usecolours:
                    ax3.step(   turfmat['time'],
                                turfmat[name]['current'],
                                label=name,
                                color=self.colours[colourid],
                                where='post')
                else:
                    ax3.step(   turfmat['time'],
                                turfmat[name]['current'],
                                label=name,
                                where='post')
                colourid += 1
            ax3.set_title('Turfs Over Time')
            ax3.grid()

            # Slider below the bottom graph
            slider_ax = plt.axes([0.05, 0.05, 0.9, 0.03])  # [left, bottom, width, height]
            slider = Slider(slider_ax, '', 0, 1, valinit=1)
            slider.valtext.set_visible(False)


            # Define an internal function which fills the plots based on the slider value
            def updateplots(val):
                # Clear the pie chart and the bar chart
                ax1.clear()
                ax2.clear()

                # Determine the selected time and which index corresponds to that time
                tselect = min(turfmat['time'][0],self.day0) + val*(self.currenttime - min(turfmat['time'][0],self.day0)+datetime.timedelta(minutes=1)) # Beunoplossingen hell yeah
                try:
                    index_t = [tselect <= t for t in turfmat['time']].index(True) - 1
                except:
                    index_t = len(turfmat['time']) - 1
                
                # Update the bar plot
                if self.usecolours:
                    ax1.bar([x - width / 2 for x in X_axis], 
                            [turfmat[name]['current'][index_t] for name in group], 
                            width, 
                            color=self.colours[self.barcolours[0]], 
                            label='Current turfs')
                    ax1.bar([x + width / 2 for x in X_axis], 
                            [turfmat[name]['alltime'][index_t] for name in group], 
                            width, 
                            color=self.colours[self.barcolours[1]], 
                            label='All-time turfs')
                else:
                    ax1.bar([x - width / 2 for x in X_axis], 
                            [turfmat[name]['current'][index_t] for name in group], 
                            width, 
                            label='Current turfs')
                    ax1.bar([x + width / 2 for x in X_axis], 
                            [turfmat[name]['alltime'][index_t] for name in group], 
                            width, 
                            label='All-time turfs')
                    
                ax1.set_xticks(X_axis,group)
                ax1.legend()

                # Update the pie chart
                if self.usecolours:
                    ax2.pie(turfmat['turfeventcount'][index_t].values(),
                            colors=self.colours,
                            startangle=90,
                            autopct=lambda i: int(round((i/100)*sum(turfmat['turfeventcount'][index_t].values()))),
                            pctdistance=1.1
                            )

                else:
                    ax2.pie(turfmat['turfeventcount'][index_t].values(),
                            startangle=90,
                            autopct=lambda i: int(round((i/100)*sum(turfmat['turfeventcount'][index_t].values()))),
                            pctdistance=1.1
                            )


                ax2.legend([f"{key} ({turfmat['turfeventcount'][index_t][key]})" for key in turfmat['turfeventcount'][index_t].keys()],
                        loc='center right', 
                        bbox_to_anchor=(-0.16, 0.5),
                        frameon=False
                        )
                ax2.autoscale()

                # Shift the x limit of the turfs over time graph
                ax3.tick_params(axis='x',labelrotation=-45)
                ax3.set_xticks([min(self.day0,turfmat['time'][0])+(i/(self.graphxticks-1))*(tselect-min(self.day0,turfmat['time'][0]))
                                for i in range(self.graphxticks)])
                ax3.set_xlim(min(self.day0,turfmat['time'][0]),tselect)
                ax3.legend(loc='upper left')

                # Set the titles for ax1 and ax2 because those get deleted on update
                ax1.set_title('All-time and Current Turf Standings')
                ax2.set_title('Turf Reasons')


            # Maximize the window and make some adjustments to the window positions
            updateplots(1)
            # try:
            #     wm = plt.get_current_fig_manager()
            #     wm.window.showMaximized()
            # except:
            #     print('Failed to maximize window, display regular window instead...')
            plt.subplots_adjust(left=0.05,right=0.95,bottom=0.2,top=0.9)

            # Set the title with actual grammar
            if len(group) == 1:
                plt.suptitle(f'Turf Statistics for {group[0]}')
            elif len(group) == 2:
                plt.suptitle(f'Turf Statistics for {group[0]} and {group[1]}')
            elif len(group) > 2:
                titlestr = ''.join(f'{name}, ' for name in group[:-2])
                plt.suptitle(f'Turf Statistics for {titlestr}{group[-2]} and {group[-1]}')

            # Assign the update function to the slider and display the plot
            slider.on_changed(updateplots)
            plt.show()



    def _aliastranslate(self,aliasset,response):
        """"Alias translator.

        Args:
            aliasset (dict): Dictionary with the alias lists keyed by name.
            response (str): Response that needs to be translated from an alias.

        Returns:
            str: Either translated input or the normal input.
        """

        # First we need to convert the alias set to be basically the reverse of its current form,
        # so {alias: true value}
        inv_aliasset = {}
        for key in aliasset.keys():
            if len(aliasset[key]) != 0:
                for alias in aliasset[key]:
                    inv_aliasset[alias] = key


        # After which we can try to match it to an alias key(e.g. a name)
        if response.lower() in [key.lower() for key in aliasset.keys()]:
            TrueResponse = list(aliasset.keys())[[key.lower() for key in aliasset.keys()].index(response.lower())]
            return TrueResponse
        
        # Otherwise we check whether it is an alias
        elif response.lower() in [key.lower() for key in inv_aliasset.keys()]:
            TrueAlias = list(inv_aliasset.keys())[[key.lower() for key in inv_aliasset.keys()].index(response.lower())]
            return inv_aliasset[TrueAlias]
        
        # It can also just be an alias key, throw in a spelling mistake corrector for good measure
        # (not doing the spelling corrector for the aliases since its usually just 1 or 2 chars)
        elif len(difflib.get_close_matches(response,aliasset.keys())) != 0:
            return difflib.get_close_matches(response,aliasset.keys())[0]
        
        # Otherwise it's just plain unreadable, return the input s.t. it can be handled by the function itself
        else:
            return response



    def write_TurfFile( self,
                        Category,
                        Name,
                        Time,
                        Day,
                        Month,
                        Year,
                        Reason):
        """Basic function for making the turf writing a bit quicker.

        Args:
            turfpath (str): Path to the turf file.
            Category (str): Category of the turf. Should be either "turf" or "minus".
            Name (str): Name of the receipient.
            Time (str): Time of the turf event in format HH:MM.
            Day (str): Day of the turf event in format DD.
            Month (str): Month of the turf event in format Mth.
            Year (str): Year of the turf event in format YYYY.
            Reason (str): Reason for the turf event.
        """        
        # Open the turf file
        turffile = open(self.turfpath,'a',newline='')
        turfwriter = csv.writer(turffile,delimiter=';')

        # Write the turf/minus and close the turf file
        turfwriter.writerow([Category,Name,Time,Day,Month,Year,Reason])
        turffile.close()



    def read_TurfFile(self,
                      names=None,
                      forcenonegative=None,
                      solidarity=None):
        """Turf file interpreter which also immediately inserts the solidarity and no-negative-turf rules.

        Args:
            names (list, optional): List of names. Defaults to the names list provided in the settings cfg file.
            forcenonegative (bool, optional): Whether to implement the no-negative-turf rule. Defaults to the setting provided in the settings cfg file.
            solidarity (bool, optional): Whether to implement the solidarity rule. Defaults to the setting provided in the settings cfg file.

        Returns:
            dict: Current turf balance.
            list: List of all turfs and their corresponding time. Formatted as [(t1,turf1),(t2,turf2),...,(tn,turfn)]
        """
        # If no names have been given, get the name list from the settings cfg file
        if names == None:
            names = list(self.names.values())
        # Apply standard values if nothing is selected
        if forcenonegative == None:
            forcenonegative = self.forcenonegative
        if solidarity == None:
            solidarity = self.solidarity

        # Now open the turf file and log the lines sorted by time
        turffile = open(self.turfpath, 'r', newline='')
        turfreader = csv.reader(turffile,delimiter=';')
        
        turffile_sorted = []
        timelst = []
        # Skip over the tile line
        linecount = 1

        for line in turfreader:
            if linecount == 1:
                linecount += 1
            else:
                # eventtime = time.mktime(time.strptime(line[-5] + line[-4] + line[-3] + line[-2], "%H:%M%d%b%Y"))
                eventtime = datetime.datetime.strptime(line[-5] + line[-4] + line[-3] + line[-2], "%H:%M%d%b%Y")
                # Find the location of where the line is supposed to go
                timelst.append(eventtime)
                timelst = sorted(timelst)
                turffile_sorted.insert(timelst.index(eventtime),line)

        # Here it might become apparent that someone turfed into the future, if so change current time
        if timelst[-1] > self.currenttime:
            self.currenttime = timelst[-1]

        # If enabled, we now need to consider solidarity. This is only applied at the user-specified moment as to
        # allow people to work away turfs together
        if solidarity:
            # It's the handiest to set a date to the first occurrence of the specified date and time after day 0
            # Find out what day of the week day0 is
            weekdays = ['mo','tu','we','th','fr','sa','su']
            weekday_day0 = self.day0.isoweekday()
            daysolidarity = weekdays.index(self.solidarityday[:2].lower()) + 1
            timesolidarity = datetime.timedelta(hours=int(self.solidaritytime[0:2]),minutes=int(self.solidaritytime[3:5]))


            deltaday_solidarity = datetime.timedelta(days=(weekday_day0-daysolidarity)%7)
            delta_solidarity = deltaday_solidarity - (datetime.timedelta(hours=self.day0.hour,
                                                        minutes=self.day0.minute) 
                                                        - timesolidarity)                   # I hate datetime
                                                                                            # With a passion

            if delta_solidarity.days < 0:
                delta_solidarity += datetime.timedelta(days=7)

            # Okay that was hellish to code, but now we have a delta until the next moment from day 0 until the
            # next moment solidarity needs to be applied.

            # Now create a time object equal to day 0 we use to track turfs
            timetrack = self.day0

            # Begin with a custom range between day0 and day0+delta solidarity. 
            # Read the amount of turfs and innings and determine whether solidarity needs applying with that balance.
            
            turfbalance_dummy = {name: 0 for name in names}
            sync = False # Create a boolean for determining whether timetrack is already on the solidarity time and day

            while timetrack <= self.currenttime+datetime.timedelta(days=7):
                # Within the sorted list of turfjes, get a window between timetrack and timetrack - 7 days
                turfs_window = [turffile_sorted[i] for i in range(len(turffile_sorted)) 
                                if timetrack - datetime.timedelta(days=7) < timelst[i] and timelst[i] <= timetrack]
                
                # Add up the turfs within the window to the dummy turfbalance
                for turf in turfs_window:
                    if turf[0].lower() == 'turf':
                        turfbalance_dummy[turf[1]] += 1
                    elif turf[0].lower() == 'minus':
                        if turfbalance_dummy[turf[1]] >= 1 and forcenonegative:
                            turfbalance_dummy[turf[1]] -= 1
                        else:
                            turfbalance_dummy[turf[1]] -= 1

                # Check if someone is lonely at the bottom
                balancelist = turfbalance_dummy.values()
                occurrences_minval = 0
                for val in balancelist:
                    if val == min(balancelist):
                        occurrences_minval += 1

                # If the minimum value of the balance list only occurs once, solidarity needs to be applied
                if occurrences_minval == 1:
                    # Determine at which index the solidarity turfs need to be inserted
                    # It's not a bug that solidarity turfs aren't visible in the future it's a feature
                    try:
                        index = [timelst[i] >= timetrack for i in range(len(timelst))].index(True)
                    except:
                        index = -1
                    for i in range(sorted(balancelist)[1] - sorted(balancelist)[0]):
                        solidarityname = [key for key in names if turfbalance_dummy[key] == min(balancelist)][0]

                        turffile_sorted.insert(index,['turf',
                                                solidarityname,
                                                str(timetrack.hour)+':'+str(timetrack.minute),
                                                timetrack.day,
                                                ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][timetrack.month-1],
                                                timetrack.year,
                                                'Solidarity'])
                        timelst.insert(index,timetrack)
                        turfbalance_dummy[solidarityname] += 1


                if sync:
                    timetrack += datetime.timedelta(days=7)
                else:
                    timetrack += delta_solidarity
                    sync = True

            turfbalance = turfbalance_dummy

        # If solidarity is not active, the turf balance needs to be determined still.
        if not solidarity:
            turfbalance = self._calc_Turfbalance(turffile_sorted,names)

        # Create the turf list return object
        turfset = [(timelst[i],turffile_sorted[i]) for i in range(len(turffile_sorted))]

        return turfbalance, turfset



    def _calc_Turfbalance(self,turflist,names,alltime=False):
        """Calculate the turf balance or all-time turf balance (so with no inning considered) from a given turf list.

        Args:
            turflist (dict): Turf list as generated by read_Turffile()
            names (list): List of names for which to generate the turflist. \
                            Only considers these names when generating the balance.
            alltime (bool, optional): Whether to consider inned turfs. Defaults to False.

        Returns:
            _type_: _description_
        """        
        turfbalance = {name: 0 for name in names}
        for turf in turflist:
            if turf[1] not in names:
                pass
            elif turf[0].lower() == 'turf':
                turfbalance[turf[1]] += 1
            elif turf[0].lower() == 'minus' and not alltime:
                if turfbalance[turf[1]] >= 1 and self.forcenonegative:
                    turfbalance[turf[1]] -= 1
                else:
                    turfbalance[turf[1]] -= 1

        return turfbalance




if __name__ == '__main__':
    sys.tracebacklimit = 0
    # Weird thing that happens is that dirname reads two different things depending on whether you run the .py or the .bat file/
    # This should catch all exceptions, let me know if you get the FileNotPresent error if the settings.cfg file is present.
    if os.path.dirname(__file__).lower().startswith('c:'):
        config = os.path.dirname(__file__) + '\\settings.cfg'
    else:
        config = os.getcwd() + os.path.dirname(__file__) + '\\settings.cfg'
    
    Turf = TurfTool(config)
    Turf.launch()
