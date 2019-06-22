import glob, shutil, os, hashlib, random, zipfile
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
global state, selection, start_location

start_location = dir_path = os.path.dirname(os.path.realpath(__file__))
local_egps = glob.glob(os.path.join(os.getcwd(),'*.egp'))
local_egps_names = [i.split('\\')[-1] for i in local_egps]   

if len(local_egps) == 0:
    state = 3
else:
    state = 0
    
while True:
    if state == 3:
        print('NO .egp FILES FOUND IN CURRENT LOCATION')
        print('     move egp_scribe.exe to a location containing .egp files')
        input('>>> ')
        break
        
    while state == 0:
        print('found the following .egp files in current location')
        print()
        counter = 1
        for i in local_egps_names:
            print("     " + str(counter) + ": " + i)
            counter += 1
        print()
        print('which file would you like to convert?')
        selection = input('>>> ')
        state = 1

    while state == 1:
        print()
        print('=============================================')
        print('you selected file ' + str(selection))
        try:
            print("     " + str(local_egps_names[int(selection)-1]))
            print()
            print('please confirm')
            confirm = input('     is that what you wanted?  y/n >>> ')
            if confirm.lower() == 'y':
                state = 2
            elif confirm.lower() == 'n':
                print('=============================================')
                print("you responded 'n'")
                print('     USER RESET')
                print()
                state = 0
            else:
                print('=============================================')
                print()
                print("you responded '" + str(confirm) + "'")
                print("     " + "respond only with 'y' or 'n'")
                print()
                state = 1
                break
        except:
            state = 0
            print()
            print('     NOT A VALID SELECTION')
            print("     " + "respond only with a number between 1 and " + str(len(local_egps_names)))
            print()

    if state == 2:
        print()
        print('=============================================')
        print()
        print('WORKING...')

        # create safe name for zip file (random chars)
        safe_name_long = hashlib.sha256(str(local_egps).encode('utf-8')).hexdigest()
        l = list(safe_name_long)
        random.shuffle(l)
        safe_name_short = ''.join(l)[0:11]

        # make zip
        target = glob.glob(os.path.join(os.getcwd(),'*.egp'))[int(selection)-1]
        shutil.copy2(target, safe_name_short+'.zip')

        # unzip
        with zipfile.ZipFile(safe_name_short+'.zip','r') as zip_ref:
             zip_ref.extractall(safe_name_short)                

        # delete zip
        os.remove(safe_name_short+'.zip')

        # move to unzipped folder
        os.chdir(safe_name_short)

        # open the project.xml
        tree = ET.parse('project.xml')
        root = tree.getroot()

        # find the egp sections
        sections = []		      
        for s in iter(root.findall("./External_Objects/ProjectTreeView/EGTreeNode/Label")):
            sections.append(s.text)

        # reconstruct the original workflow into a list
        workflow = []
        for i in range(len(sections)):
                workflow.append('--')
                workflow.append(sections[i].upper())
                for l in root[-1][0][i][-1].iter("Label"):
                        if l.text == "Programs":
                                # don't want the 'Programs' label
                                continue
                        else:
                                workflow.append(l.text)
                for e in root[-1][0][i][-1].iter("ElementID"):
                        workflow.append(e.text)
        # format and clean up the strings in workflow
        workflow_clean = str(workflow).replace("[","").replace("]","").replace(", ","|").replace("'","").strip().split('--')[1:]

        # organize the workflow_clean (list) into a dataframe
        master = pd.DataFrame()
        for i in range(len(workflow_clean)):
            # pull strings one by one out of workflow_clean
            df = pd.DataFrame(list(filter(None,workflow_clean[i].split('|'))))
            df.columns = ['script']
            # create uniform 'section' data element
            df['section'] = df.iloc[0,0]
            # delete the row with section name in the script col
            df = df[df['script']!=df['section']]
            # second half of script col in df should be the CodeTask ids
            # move them to a seperate col (called 'xml_id')
            df['xml_id'] = df.loc[int(len(df)/2)+1:,'script']
            # shift CodeTask ids up to top to their column
            df['xml_id'] = df['xml_id'].shift(-int((len(df)/2)))
            # drop any NaN rows
            df.dropna(inplace=True)
            # append to master df
            master = master.append(df)
        master.reset_index(inplace=True,drop=True)
        
        # make a new folder to put all the newly created files
        new_folder = os.path.join(start_location,(target.replace('.egp','')))
        os.mkdir(new_folder)

        # find the GitSourceControl ID
        GUID = root[-6].attrib.get("GUID")
        
        # index PFD/Git directories created in the .egp to .zip process
        pfd_dirs = []
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(start_location,safe_name_short)):
            if GUID in str(dirpath):
                pfd_dirs.append(os.path.join(dirpath,'code.sas'))
       
        # move .xml and .sas files to new folder
        for xml_id in master['xml_id']:
            for from_path in pfd_dirs:
                if xml_id in from_path:
                    file_name = str(master[master['xml_id']==xml_id].index[0]+1) + ') [' + master.loc[master[master['xml_id']==xml_id].index[0],'section'] + '] [' + master.loc[master[master['xml_id']==xml_id].index[0],'script'] + '.sas].txt'
                    to_path = os.path.join(new_folder,file_name)
                    shutil.move(from_path, to_path)

        xml_location = os.path.join(start_location,safe_name_short,'project.xml')
        shutil.move(xml_location, os.path.join(new_folder,'project.xml'))
            
        # delete unused materials
        os.chdir(start_location)  
        shutil.rmtree(os.path.join(safe_name_short))    

        # write out master df
        master.to_csv(os.path.join(new_folder,'summary.csv'), index=False)

        # add read_me to new folder
        read_me = '''OVERVIEW:
There are two basic ways to construct and save a SAS project: as a .sas file, or as a .egp file.

A .sas file is a single file that contains all the code needed to run a project, from start to finish.  A .sas file is a flat text file, so it can be opened on any computer, even if the SAS program is not installed on that computer.

A .egp file allows the user to break the job up into multiple short .sas files (as opposed to one long one), and specify the order SAS is to run them when the project is executed.  Those .sas files are embedded in the .egp file itself.  The .egp is like one single file containing many short .sas files, and instructions on what order to run them (similar to a zip file).

But a .egp can only be opened and read on a computer that has SAS installed on it.  egp_scribe is an attempt to address this problem.

egp_scribe is an independent exe program that recovers the .sas files contained in an .egp, even when using computers that do not have SAS installed.

=======================================================================

HOW TO USE:
egp_scribe can be used to extract code saved in a SAS .egp file, even if the user does not have a copy of SAS installed on their computer.

To use egp_scribe, create a folder on your laptop.  Name it 'egp scribe'.  Make a copy of egp_scribe, and put it in the 'egp scribe' folder on your laptop (ctrl+c, ctrl+v).  Then put any number of .egp files in the 'egp scribe' folder as well.  Once you have egp_scribe, and all the .egp files you want to convert copied into the folder, double click egp_scribe and follow the prompts.

After egp_scribe successfully runs, it will create a series of txt files, one xml, one csv, and this read_me.

=======================================================================

RESULTS, PLAN A:
Each txt file is the contents of a .sas file egp_scribe managed to extract from the targeted .egp file.  

Naming convention:
Order this script fell in the original .egp project's run order, name of project section (all caps) that used to contain that .sas file, original name of .sas script.

Example:
"2) [DIRECTIONS AND SETUP] [Variables.sas].txt"
In the original .egp, 'Variables.sas' was the second file to be run out of the entire project.  'Variables.sas' was part of a section of the .egp project called 'Directions and Setup.'

If these text files are usable and sufficient, you can ignore the summary.csv and project.xml files.

...

RESULTS, PLAN B: 
If egp_scribe does not correctly extract, label, and sort the .sas files, or if you require additional context or information from the .egp, you still can manually work through the .egp's contents using project.xml and summary.csv.  

project.xml contains any and all information salvageable from the .egp, in raw xml format.  Open project.xml (in Excel or in a text editor) in order to freely browse and search that information.

Or, to research a specific .sas script from the .egp, open summary.csv first, get the script's xml_id, and search the xml for that id (will take you to the parts of the xml pertaining to that .sas file).

=======================================================================

project.xml - xml file that contains all data/info salvageable from original .egp, in raw xml format.  Use this as a back up in case egp_scribe fails to correctly parse the .egp, or for reference in finding additional information about the entire .egp project or the scripts contained in it.

summary.csv - "script" column lists all the .sas files successfully extracted from the .egp, "section" column is the subheading within the .egp project that that script was part of, "xml_id" is the unique xml element tag that corresponds to that .sas script.
        '''

        with open(os.path.join(new_folder,'read_me.txt'),'w') as file:
            file.write(read_me)
        print('ALL DONE!')
        master.index = np.arange(1,len(master)+1)
        print(master.to_string())
        input('>>> ')
        break


    
        
