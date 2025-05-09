import os
import shutil

def process_conversations_folder(folder_path):
    """
    Processes a 'conversations' folder by:
    - Listing and sorting all file names within it.
    - Writing them to a 'conversation_log.txt' file in the parent directory.
    - Deleting the 'conversations' folder.
    """
    # Determine the parent directory of the 'conversations' folder
    parent_folder = os.path.dirname(folder_path)
    log_file_path = os.path.join(parent_folder, 'conversation_log.txt')
    
    # Collect all regular files in the folder and sort them in ascending order
    files = [item for item in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, item))]
    files.sort()
    
    # Write the sorted file names into the log file with formatted rounds
    with open(log_file_path, 'w') as log_file:
        for idx, filename in enumerate(files, start=1):
            log_file.write(f"Round {idx}: {filename}\n")
    
    print(f"Created log file: {log_file_path}")
    
    # Remove the 'conversations' folder and its contents
    shutil.rmtree(folder_path)
    print(f"Deleted folder: {folder_path}")

def main(work_directory):
    """
    Recursively traverse the given work_directory to find any sub-folder named 'conversations',
    process them, and remove them afterward.
    """
    # Walk the directory tree from bottom up to safely remove directories after processing them
    for root, dirs, _ in os.walk(work_directory, topdown=False):
        for dir_name in dirs:
            if dir_name == "conversations":
                folder_path = os.path.join(root, dir_name)
                process_conversations_folder(folder_path)

if __name__ == "__main__":
    # Automatically determine the work directory as the location of this script.
    try:
        work_directory = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # Fallback in case __file__ is not defined (e.g., in an interactive shell)
        work_directory = os.getcwd()
    
    main(work_directory)
    print("Processing complete.")
