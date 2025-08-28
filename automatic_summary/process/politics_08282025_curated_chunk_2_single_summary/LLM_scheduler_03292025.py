import os
import sys
import glob
import json
import re
import time
import socket
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

PLACEHOLDER = "++++++++++++++++++++Paste Here++++++++++++++++++++++++++"

def error_exit(message):
    print(f"ERROR: {message}")
    sys.exit(1)

def update_subreddit_prompt():
    # Step 1: Locate the unique subreddit file in current directory.
    subreddit_files = glob.glob("subreddit*.txt")
    if len(subreddit_files) != 1:
        error_exit(f"Expected exactly one file starting with 'subreddit', but found {len(subreddit_files)}")
    subreddit_file = subreddit_files[0]
    print(f"Found subreddit file: {subreddit_file}")
    
    # Read the entire subreddit file.
    try:
        with open(subreddit_file, "r", encoding="utf-8") as f:
            subreddit_introduction_string = f.read().strip()
    except Exception as e:
        error_exit(f"Could not read {subreddit_file}: {e}")
    
    # Open the Prompt\Prompt_Step00_introduction.txt file.
    prompt_intro_path = os.path.join("Prompt", "Prompt_Step00_introduction.txt")
    if not os.path.exists(prompt_intro_path):
        error_exit(f"{prompt_intro_path} does not exist.")
    
    try:
        with open(prompt_intro_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        error_exit(f"Could not read {prompt_intro_path}: {e}")
    
    # Search for the placeholder line.
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
            new_lines.append(subreddit_introduction_string + "\n")
            placeholder_found = True
        else:
            new_lines.append(line)
    
    if placeholder_found:
        try:
            with open(prompt_intro_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Updated {prompt_intro_path} with subreddit introduction.")
        except Exception as e:
            error_exit(f"Could not write to {prompt_intro_path}: {e}")
    else:
        print(f"No placeholder found in {prompt_intro_path}; skipping update.")

def process_raw_input():
    # Step 2: Process raw_input.txt.
    raw_input_path = "raw_input.txt"
    if not os.path.exists(raw_input_path):
        error_exit(f"{raw_input_path} does not exist.")
    
    try:
        with open(raw_input_path, "r", encoding="utf-8") as f:
            raw_input_string = f.read().strip()
    except Exception as e:
        error_exit(f"Could not read {raw_input_path}: {e}")
    
    # Split lines and filter out empty ones.
    lines = [line for line in raw_input_string.splitlines() if line.strip()]
    if not lines:
        error_exit("raw_input.txt contains no non-empty lines.")
    
    ids = []
    raw_input_no_url_lines = []
    
    for line in lines:
        try:
            obj = json.loads(line)
        except Exception as e:
            error_exit(f"Error parsing JSON line: {line}\n{e}")
        # Ensure "url" exists.
        if "url" not in obj:
            error_exit(f"Missing 'url' field in JSON: {line}")
        # Ensure "id" exists.
        if "id" not in obj:
            error_exit(f"Missing 'id' field in JSON: {line}")
        ids.append(obj["id"])
        # Remove the url key for the no_url version.
        obj_no_url = obj.copy()
        del obj_no_url["url"]
        # Re-serialize using ensure_ascii=False so that non-ASCII characters remain intact.
        raw_input_no_url_lines.append(json.dumps(obj_no_url, ensure_ascii=False))
    
    # Compute header (Step 2.1).
    min_id = min(ids)
    max_id = max(ids)
    total_articles = max_id - min_id + 1
    input_header_string = f"**ID range is {min_id}-{max_id}, total number of articles is {total_articles}.**\n"
    print(f"Computed header: {input_header_string.strip()}")
    
    # Create raw_input_no_url_string.
    raw_input_no_url_string = "\n".join(raw_input_no_url_lines)
    
    # Save raw_input_no_url_string to file.
    try:
        with open("raw_input_no_url.txt", "w", encoding="utf-8") as f:
            f.write(raw_input_no_url_string)
        print("Saved raw_input_no_url.txt")
    except Exception as e:
        error_exit(f"Could not write to raw_input_no_url.txt: {e}")
    
    # Step 2.3: Prepend header and an empty line.
    header_prepend = input_header_string + "\n"
    raw_input_string = header_prepend + raw_input_string
    raw_input_no_url_string = header_prepend + raw_input_no_url_string
    
    return raw_input_string, raw_input_no_url_string

def update_prompt_file(prompt_path, replacement_text):
    if not os.path.exists(prompt_path):
        error_exit(f"{prompt_path} does not exist.")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        error_exit(f"Could not read {prompt_path}: {e}")
    
    placeholder_found = False
    new_lines = []
    for line in lines:
        if line.strip() == PLACEHOLDER:
            new_lines.append(replacement_text + "\n")
            placeholder_found = True
        else:
            new_lines.append(line)
    
    if placeholder_found:
        try:
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Updated {prompt_path} with new prompt content.")
        except Exception as e:
            error_exit(f"Could not write to {prompt_path}: {e}")
    else:
        print(f"No placeholder found in {prompt_path}; skipping update.")

def is_port_available(port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return False  # Connection succeeded, port is in use.
    except socket.error:
        return True   # Connection failed, port is available.

def launch_streamlit():
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
        "LLM_controller_03292025.py",
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
    print(f"Extracting output from {conv_file}...")
    try:
        with open(conv_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        error_exit(f"Could not read {conv_file}: {e}")
    
    # Use regex to capture blocks between the header pairs.
    pattern = re.compile(
        r"<Code>==Output File Start==<Code>\s*(.*?)\s*<Code>==Output File End==<Code>",
        re.DOTALL
    )
    matches = pattern.findall(content)
    if len(matches) < 2:
        error_exit(f"Expected at least 2 output blocks in {conv_file}, but found {len(matches)}.")
    # The second block is the one we want.
    output_text = matches[1].strip()
    
    try:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
        print("Extracted output saved to output.txt")
    except Exception as e:
        error_exit(f"Could not write to output.txt: {e}")

def main():
    print("LLM_scheduler.py started.")
    
    # Step 1: Update the introduction prompt.
    update_subreddit_prompt()
    
    # Step 2: Process raw_input.txt and update prompt files.
    raw_input_string, raw_input_no_url_string = process_raw_input()
    
    # Step 2.4: Update Prompt_Step01_01_input_writing.txt with no-url version.
    prompt_writing_path = os.path.join("Prompt", "Prompt_Step01_01_input_writing.txt")
    update_prompt_file(prompt_writing_path, raw_input_no_url_string)
    
    # Step 2.5: Update Prompt_Step07_01_input_reasoning.txt with full raw input (with URLs).
    prompt_reasoning_path = os.path.join("Prompt", "Prompt_Step07_01_input_reasoning.txt")
    update_prompt_file(prompt_reasoning_path, raw_input_string)
    
    # Step 3: Launch the LLM controller via Streamlit.
    streamlit_proc = launch_streamlit()
    
    # Step 4: Monitor for a new conversation file.
    # Record any existing conversation_*.txt files.
    existing_conv_files = set(glob.glob("conversation_*.txt"))
    conv_file = wait_for_conversation_file(existing_conv_files)
    
    # Step 5: Extract output from the conversation file.
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
    
    print("LLM_scheduler.py completed successfully.")

if __name__ == '__main__':
    main()
