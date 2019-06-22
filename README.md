# TECHNICAL NOTE
'egp_scribe.py' can be downloaded from this repo.  However, a .exe version of that script is not included in this repo, due to file size limitations.

It is recommended that you download 'egp_scribe.py' from this repo, then use the Python pyinstaller library to create a .exe version of the .py file.

See also "Convert PY to EXE" by PyTutorials: https://www.youtube.com/watch?v=lOIJIk_maO4 

=======================================================================

# OVERVIEW:
There are two basic ways to construct and save a SAS project: as a .sas file, or as a .egp file.

A single .sas file is a single file that contains all the code needed to run a project, from start to finish.  A .sas file is a flat text file, so it can be opened on any computer with a text editor - even if the SAS program is not installed on that computer.

A .egp file allows the user to break up a project into multiple short .sas files (as opposed to one long one), and specify the order SAS is to run them when the project is executed.  Those .sas files are embedded in the .egp file itself.  The .egp is like one single file containing many short .sas files, and instructions on what order to run them (similar to a zip file).

However, an .egp can only be opened and read on a computer that has SAS installed on it.

egp_scribe is an independent program that recovers the .sas files contained in an .egp, even when used on computers that do not have SAS installed.  It allows anyone access to .sas files inside an .egp, something that ordinarily is not possible without SAS software. 

=======================================================================

# HOW TO USE:
To use egp_scribe, create a folder on your computer's desktop.  Name it 'egp scribe'.  Save a copy of egp_scribe (.exe version of egp_scribe is recommended) into the 'egp scribe' folder.  Then put any number of .egp files in the 'egp scribe' folder as well.  Once you have egp_scribe, and the .egp files all copied into the folder, double click egp_scribe and follow the prompts.

After egp_scribe successfully runs, it will create a series of txt files, one xml, one csv, and a read_me.

=======================================================================

# VIEWING RESULTS, PLAN A:
Each txt file is the contents of a .sas file egp_scribe managed to extract from the targeted .egp file.  

Naming convention:
A number corresponding to the ordinal position this script fell in the original .egp project's run order, name of project section (all caps) where that .sas file was contained, original name of the .sas script.

Example:
"2) [DIRECTIONS AND SETUP] [Variables.sas].txt"

In the original .egp, 'Variables.sas' was the second file to be run out of the entire project.  'Variables.sas' was part of a section of the .egp project called 'Directions and Setup.'

If these text files are usable and sufficient for you, you can ignore the summary.csv and project.xml files.

# ...

# RESULTS, PLAN B: 
If egp_scribe does not correctly extract, label, and sort the .sas files, if an error is encountered, or if you require additional context or information, you still can manually work through some of the .egp's contents using project.xml and summary.csv.  

project.xml contains any and all information salvageable from the .egp, in raw xml format.  Open project.xml (in Excel or in a text editor) in order to freely browse and search that information.

Alternatively, to research a specific .sas script, open summary.csv first, get the script's xml_id, and search project.xml for that id (this will take you to the parts of the xml pertaining to that .sas file).

=======================================================================

project.xml - xml file that contains all data/info salvageable from original .egp, in raw xml format.  Use this as a back up in case egp_scribe fails to correctly parse the .egp, or for reference in finding additional information about the entire .egp project or the scripts contained in it.

summary.csv - "script" column lists all the .sas files successfully extracted from the .egp, "section" column is the subheading within the .egp project that that script was part of, "xml_id" is the unique xml element tag that corresponds to that .sas script.
