# Fair warning, if you are looking at this I had to remove a significant amount of this script for confidentiality. Anything taken out will be subbed with #[REMOVED]
# This uses out in house FTP to ping the production PCs and pull data or stated any file or folder from the PC. 

import subprocess
import os
import shutil
import csv
from datetime import datetime, timedelta

#[REMOVED]_DIRECTORY = #[REMOVED]
EXP_FILE_BACKUP_LOCATION = #[REMOVED]
EXP_LOCATION = #[REMOVED]
OUTPUT_FOLDER = #[REMOVED]

os.chdir(#[REMOVED]_DIRECTORY)
dataMatrix = [ #[REMOVED] ]


splitCommand = #[REMOVED]
splitCommandTwo = #[REMOVED]



for row in dataMatrix:
    ipAdy = row[1]
    system_name = row[0]  
    


    content = f"""[SOURCE]
    Path=#[REMOVED]

    [TARGET]
    Path=C:#[REMOVED]

    [FILE1]
    NAME=20250722
    """
 
    with open(EXP_LOCATION, 'w') as file:
        file.write(content)
           
    command = splitCommand + ipAdy + splitCommandTwo
    result = subprocess.run(command, shell=True)
    print(result)
    if result.returncode != 0:
        print("Error Message from Console: ")
        continue  # Skip to the next file if there's an error


    retrieved_file_path = os.path.join(OUTPUT_FOLDER, "20250722")
    if os.path.exists(retrieved_file_path):
        new_file_name = f"{system_name.replace(' ', '_')}"  
        new_file_path = os.path.join(OUTPUT_FOLDER,new_file_name)

     
        shutil.move(retrieved_file_path, new_file_path)
        print(f"File renamed and moved to: {new_file_path}")
    else:
        print(f"No file found for system: {system_name}")

print("All files processed successfully.")

