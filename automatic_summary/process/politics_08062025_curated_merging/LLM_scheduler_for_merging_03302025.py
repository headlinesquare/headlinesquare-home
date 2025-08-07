import os
import sys
import glob
import time
import re
import socket
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

PLACEHOLDER = "++++++++++++++++++++Paste Here++++++++++++++++++++++++++"

def error_exit(message):
    print(f"ERROR: {message}")
    sys.exit(1)

def update_introduction_prompt():
    """
    Step 1:
      - Finds files starting with 'input_' (at least two) and sorts them in ascending order.
      - Merges their content with two newline lines between each file.
      - Updates 'Prompt\\Prompt_Step00_introduction.txt' by replacing the placeholder line with the merged content.
    """
    input_files = glob.glob("input_*.txt")
    if len(input_files) < 2:
        error_exit(f"Expected at least two files starting with 'input_', but found {len(input_files)}")
    
    # Sort file names in ascending order.
    input_files = sorted(input_files)
    print(f"Found input files (sorted): {input_files}")
    
    merged_content_list = []
    file_counter = 0
    for file in input_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                file_counter = file_counter + 1
                content = f.read().strip()
                merged_content_list.append(f"==========Output File {file_counter} Start==========\n\n")
                merged_content_list.append(content)
                merged_content_list.append(f"==========Output File {file_counter} End============\n\n");
        except Exception as e:
            error_exit(f"Could not read {file}: {e}")
    
    # Merge the contents with two newlines between each.
    merged_content = "\n\n".join(merged_content_list)
    
    # Open and update the introduction prompt.
    prompt_intro_path = os.path.join("Prompt", "Prompt_Step01_writing.txt")
    if not os.path.exists(prompt_intro_path):
        error_exit(f"{prompt_intro_path} does not exist.")
    
    try:
        with open(prompt_intro_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        error_exit(f"Could not read {prompt_intro_path}: {e}")
    
    placeholder_found = False
    new_lines = []
    
    # Get current time in US Central Time
    now = datetime.now(ZoneInfo("America/Chicago"))
    # Format the string
    formatted_date = f"Today's Date is {now.strftime('%B')}, {now.day}, {now.year}.\n"
    new_lines.append(formatted_date)
    new_lines.append("\n")
    
    for line in lines:
        if line.strip() == PLACEHOLDER:
            new_lines.append(merged_content + "\n")
            placeholder_found = True
        else:
            new_lines.append(line)
    
    if placeholder_found:
        try:
            with open(prompt_intro_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Updated {prompt_intro_path} with merged input files.")
        except Exception as e:
            error_exit(f"Could not write to {prompt_intro_path}: {e}")
    else:
        print(f"No placeholder found in {prompt_intro_path}; skipping update.")

def is_port_available(port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return False  # Port is in use.
    except socket.error:
        return True   # Port is available.
    
def launch_streamlit():
    """
    Step 2:
      - Tries ports starting from 8501 (up to 10 ports) until an available port is found.
      - Launches the LLM controller via Streamlit in a new process.
    """
    base_port = 8501
    max_attempts = 10
    chosen_port = None
    for i in range(max_attempts):
        port = base_port + i
        if is_port_available(port):
            chosen_port = port
            break
        else:
            print(f"Port {port} is in use, trying next port...")
    if chosen_port is None:
        error_exit("No available port found between 8501 and 8510.")
    
    # Build the command as a list of arguments instead of a string.
    command = [
        "streamlit",
        "run",
        "LLM_Controller_03292025.py",
        f"--server.port={chosen_port}"
    ]
    print(f"Launching Streamlit on port {chosen_port} with command:\n{' '.join(command)}")
    
    try:
        # No need for shell=True here.
        proc = subprocess.Popen(command)
    except Exception as e:
        error_exit(f"Failed to launch Streamlit: {e}")
    
    return proc



def wait_for_conversation_file(existing_files):
    """
    Step 3:
      - Monitors the work folder for new files matching 'conversation_*.txt'.
      - Checks every 10 seconds; errors out if more than one new file appears in one check.
    """
    print("Monitoring for new conversation_*.txt file...")
    while True:
        time.sleep(10)  # check every 10 seconds
        current_files = set(glob.glob("final_conversation/conversation_*.txt"))
        new_files = current_files - existing_files
        if new_files:
            if len(new_files) > 1:
                error_exit(f"Multiple new conversation files detected: {new_files}")
            conv_file = new_files.pop()
            print(f"Detected new conversation file: {conv_file}")
            return conv_file

def extract_output_from_conversation(conv_file):
    """
    Step 4:
      - Reads the conversation file.
      - Searches for exactly two pairs of headers ("==========Output File Start==========" and "==========Output File End============").
      - Extracts the content between the second header pair and saves it to output.txt.
    """
    print(f"Extracting output from {conv_file}...")
    try:
        with open(conv_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        error_exit(f"Could not read {conv_file}: {e}")
    
    pattern = re.compile(
        r"<Code>==Output File Start==<Code>\s*(.*?)\s*<Code>==Output File End==<Code>",
        re.DOTALL
    )
    matches = pattern.findall(content)
        
    if len(matches) < 2:
        error_exit(f"Expected at least 2 output blocks in {conv_file}, but found {len(matches)}.")
    
    output_text = matches[1].strip()
    
    try:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
        print("Extracted output saved to output.txt")
    except Exception as e:
        error_exit(f"Could not write to output.txt: {e}")

def main():
    print("LLM_scheduler_for_merging.py started.")
    
    # Step 1: Update the introduction prompt with merged input files.
    update_introduction_prompt()
    
    # Step 2: Launch the LLM controller via Streamlit.
    streamlit_proc = launch_streamlit()
    
    # Step 3: Monitor for a new conversation file.
    existing_conv_files = set(glob.glob("conversation_*.txt"))
    conv_file = wait_for_conversation_file(existing_conv_files)
    
    # Step 4: Extract output from the conversation file.
    extract_output_from_conversation(conv_file)
    
    # Terminate the Streamlit process.
    print("Terminating Streamlit process...")
    try:
        streamlit_proc.terminate()
        streamlit_proc.wait(timeout=10)
        print("Streamlit process terminated.")
    except Exception as e:
        print(f"Warning: Could not properly terminate Streamlit process: {e}")
        
    # Using subprocess.run to call the clear_conversation.py script
    result = subprocess.run(["python", "clear_conversation.py"], check=True)
    print("clear_conversation.py finished with return code:", result.returncode)
    
    print("LLM_scheduler_for_merging.py completed successfully.")

if __name__ == '__main__':
    main()
