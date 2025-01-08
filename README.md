# TurfTool 
Hi!

Firstly, thanks for using my Q1 sog! This project originated from a conversation I had with Matthijs about making his turf tool object-oriented. One week later this is the result! It is a bit more upgraded compared to Matthijs' version, sporting the ability to interpret aliases, being able to auto-calculate solidarity turfs and a more elaborate plotting system. This readme file should give you all the instructions you'll ever need to use it.

Hope you enjoy!

-- Wouter

# Installing the required packages
So some functionalities within the Statistics function require matplotlib and PySide2. I made it easy for you, simply run the included ```requirements.bat``` file and it'll install it for you

# Configuring the settings
This is the main work that you'll need to do, namely filling in all the committee data specific to you as secretary. This is done within the file ```settings.cfg```. There is already some documentation present, but for the sake of clarity, here's an overview of all the lists and objects:

- [names]: Object containing the links between the function of somebody and their name. E.g. for me it would be ```S = Wouter```.
- [aliases]: Object containing the links between the function of somebody and their alias. This is used to make the turfing and inning quicker by providing an alternate name to select their name. I personally chose to input the first letter(s) of somebody's name and their function number. It uses a list format, but string format is not needed. E.g. for me it would be ```S = [2,W]```.
- [groups]: Object containing the links between the name of a group and the people within it. An example of a correctly formatted group would be ```Mannen = [Thijs,Wouter,Meine]```.
- [groupsaliases]: Object containing the links between the name of a group and the people within it. An example would be ```Mannen = [m]```.
- [turfreasons]: One of the two main tasks to input, namely the turf reasons. This is formatted slightly differently to the previous objects, namely ```REASON: [ALIASES], VALUE```. For example, the reason ```Spelling``` which has the aliases ```i1``` and ```s``` and is worth 1 turf would be formatted as ```Spelling = [i1,s], 1```.
- [inningreasons]: Quite similar to turfreasons, this also has the format ```REASON: [ALIASES], VALUE```. For example, the reason ```Bak 25cl``` with aliases ```i1a``` and ```25cl``` and is worth 1 turf would be formatted as ```Bak 25cl = [i1a, 25cl], 1```.
- [turfrules]: Some settings about which turf rules to apply and when. ```solidarity``` can be either ```True``` or ```False``` and determines whether solidarity rules are applied (making it so that nobody can be the only one with the lowest amount of turfs and has turfs auto-applied if they are). ```solidarityday``` specifies at which day this rule is applied and can take any of the following values: ```Mon```, ```Tue```, ```Wed```, ```Thu```, ```Fri```, ```Sat```, ```Sun```. ```solidaritytime``` specifies the time at which solidarity is applied and has format ```HH:MM```. Lastly, ```forcenonegative``` can be either ```True``` or ```False``` and specifies whether negative turfs can exist.
- [plotsettings]: Another set of settings. ```day0``` specifies when the turf plots begin, provided the first turf doesn't begin before this. It has format ```HH:MM DD Monthname YYYY```. ```day0event``` is a string with what event occured on day0. ```graphxticks``` is an integer which specifies how many xticks are present on the turfs over time plot. ```usecolours``` is a boolean which specifies whether to use ```colours```. ```colours``` is a list of HEX colour codes which should be used in the plot if ```usecolours``` equals ```True```. Make sure that this list is at least as long as the amount of people within your committee as otherwise the code starts crying. We also have ```barcolours``` which is a list of two integers which specifies the colours to use within the bar plot. Last but not least there is ```maxreasons``` which limits the amount of turf reasons to display. The reasons that were cut off are grouped into "Other".

That was a lot of text lol

# Using the Turf Tool
You can either run it on your Python interpreter or just double click the TurfTool.bat which also launches the code. It has three main functions, namely ```Turf```, ```Inning``` and ```Statistics``` which all kinda speaks for itself. You also have ```Exit``` but this just closes the program.

# Issues/Questions?
Just shoot me a message!