# LLM_scheduler_for_merging_03302025.py Documentation

This script orchestrates a multi-step workflow in a large language model (LLM) environment. Its primary tasks include:

1. Merging multiple input text files into a single introduction prompt.
2. Launching a Streamlit-based LLM controller.
3. Monitoring for a newly generated conversation file.
4. Extracting specific output sections from the conversation.
5. Cleaning up conversation log files.

The overall design allows for a controlled and automated process where user-provided inputs are merged, processed by an LLM via a web interface, and the results are extracted and stored.

---

## Table of Contents

- [Prerequisites](https://platform.openai.com/playground/prompts?models=o3-mini#prerequisites)
- [Workflow Overview](https://platform.openai.com/playground/prompts?models=o3-mini#workflow-overview)
- [Modules and Dependencies](https://platform.openai.com/playground/prompts?models=o3-mini#modules-and-dependencies)
- [Detailed Function Explanations](https://platform.openai.com/playground/prompts?models=o3-mini#detailed-function-explanations)
  - [error_exit(message)](https://platform.openai.com/playground/prompts?models=o3-mini#error_exit)
  - [update_introduction_prompt()](https://platform.openai.com/playground/prompts?models=o3-mini#update_introduction_prompt)
  - [is_port_available(port, timeout=5)](https://platform.openai.com/playground/prompts?models=o3-mini#is_port_available)
  - [launch_streamlit()](https://platform.openai.com/playground/prompts?models=o3-mini#launch_streamlit)
  - [wait_for_conversation_file(existing_files)](https://platform.openai.com/playground/prompts?models=o3-mini#wait_for_conversation_file)
  - [extract_output_from_conversation(conv_file)](https://platform.openai.com/playground/prompts?models=o3-mini#extract_output_from_conversation)
  - [main()](https://platform.openai.com/playground/prompts?models=o3-mini#main)
- [Execution Flow](https://platform.openai.com/playground/prompts?models=o3-mini#execution-flow)
- [Usage Notes and Considerations](https://platform.openai.com/playground/prompts?models=o3-mini#usage-notes-and-considerations)

---

## Prerequisites

- Python 3.x installed.
- Required Python libraries:
  • os, sys, glob, time, re, socket, subprocess
  (All these are part of the Python standard library.)
- The following files and directories must exist relative to where the script is executed:
  - Input text files with file names starting with `input_` (e.g., input_1.txt, input_2.txt).
  - A prompt file at `Prompt/Prompt_Step01_writing.txt` which must include a **placeholder line** with the text: `++++++++++++++++++++Paste Here++++++++++++++++++++++++++`
  - The LLM controller Python script `LLM_Controller_03292025.py` (used with Streamlit).
  - (Optional) A script named `clear_conversation.py` which clears or resets conversation logs.
  - A directory for conversation outputs (e.g., files matching `final_conversation/conversation_*.txt`).

---

## Workflow Overview

1. **Merge Input Files:** The script searches for at least two files beginning with `input_*.txt`, sorts them, and concatenates their content. Headers and footers are added around each file’s content to delineate them clearly. This merged content is then inserted into the prompt file (`Prompt/Prompt_Step01_writing.txt`) by replacing a placeholder line.

2. **Launch Streamlit Server:** The script then tries to launch a Streamlit application (the LLM controller) by searching for an available port starting from 8501 (up to 10 ports). Once an open port is found, it launches the Streamlit process using `LLM_Controller_03292025.py`.

3. **Monitor for New Conversation File:** Once the controller is running, the script continually monitors a designated folder for a new conversation file (matching the pattern `conversation_*.txt`, typically located in a folder called `final_conversation`). It polls every 10 seconds and ensures that only one new conversation file is created at a time.

4. **Extract LLM Output:** After a new conversation file is detected, the script reads through it and uses regular expressions to locate exactly two output blocks — each delimited by headers `==========Output File Start==========` and `==========Output File End============`. It extracts the content from the second block and writes it out to a file named `output.txt`.

5. **Cleanup and Termination:** Finally, the Streamlit process is gracefully terminated. The script then calls an external script (`clear_conversation.py`) to clear or reset the conversation log, and the execution process is completed.

---

## Modules and Dependencies

The following Python standard libraries are used:

- **os, sys:** For file system operations and system exit handling.
- **glob:** For pattern matching file names to find inputs and outputs.
- **time:** For sleep intervals during the polling process.
- **re:** For regular expressions used when extracting text.
- **socket:** For checking available network ports.
- **subprocess:** For launching external processes (Streamlit and clear conversation script).

A constant `PLACEHOLDER` is defined, which is used as a marker in the prompt file to indicate where the merged input text should be inserted.

---

## Detailed Function Explanations

### error_exit(message)

- **Purpose:** This function prints an error message and then exits the program.
- **Parameters:** • `message` (str): Error message to be printed.
- **Behavior:** Uses `sys.exit(1)` after printing to ensure immediate termination on errors.

---

### update_introduction_prompt()

- **Purpose:** Reads multiple `input_*.txt` files, merges their content, and updates the prompt file.
- **Detailed Steps:**
  1. **Find and Sort Input Files:** Uses `glob.glob("input_*.txt")` to gather files. Expects at least two; otherwise, an error is raised.
  2. **Read and Merge Content:** Iterates over each file, reading its content, and adds a header and 
     footer around each file’s content. The headers (e.g., "==========Output 
     File 1 Start==========") and footers (e.g., "==========Output File 1 
     End============") clearly separate each input.
  3. **Replace Placeholder in Prompt File:** Reads `Prompt/Prompt_Step01_writing.txt` and looks for a line that exactly matches the constant placeholder (`PLACEHOLDER`).
     If found, replaces that line with the merged content. If the 
     placeholder is not found, the script simply prints a message and skips 
     the update.
  4. **Error Handling:** Any file read or write issues invoke `error_exit()` with an appropriate error message.

---

### is_port_available(port, timeout=5)

- **Purpose:** Checks if a specified TCP port on localhost (127.0.0.1) is available.
- **Parameters:** • `port` (int): Port number to check.
  • `timeout` (int, optional): Timeout for the socket connection in seconds (default is 5).
- **Behavior:** Attempts to create a socket connection. If the connection is successful,
   the port is in use (returns False); otherwise, it returns True 
  indicating the port is free.

---

### launch_streamlit()

- **Purpose:** Launches the LLM controller via Streamlit on an available port.
- **Detailed Steps:**
  1. **Select Available Port:** Iterates through 10 ports starting from 8501. Calls `is_port_available()` to find an eligible port.
  2. **Construct and Run Command:** Upon finding an available port, constructs a command list (for subprocess) to launch Streamlit with the controller script (`LLM_Controller_03292025.py`) and specifies the server port.
  3. **Process Creation:** Uses `subprocess.Popen()` to start the Streamlit process.
  4. **Error Handling:** If no port is available within the range or the process fails to start, the function calls `error_exit()`.

---

### wait_for_conversation_file(existing_files)

- **Purpose:** Monitors a folder (specifically the `final_conversation` directory) for new conversation files that match the pattern `conversation_*.txt`.
- **Parameters:** • `existing_files` (set): A set of file paths that existed before launching the Streamlit process.
- **Detailed Steps:**
  1. **Polling:** In an infinite loop, the function sleeps for 10 seconds between checks.
  2. **Detection:** Scans for files in `final_conversation/conversation_*.txt` and compares them to `existing_files`.
  3. **Validation:** If new files are found and more than one appears at the same time, an error is raised.
  4. **Return Value:** Returns the new conversation file’s path once exactly one new file is detected.

---

### extract_output_from_conversation(conv_file)

- **Purpose:** Extracts specific output content from the conversation file and writes it to `output.txt`.

- **Detailed Steps:**
  
  1. **Read File Contents:** Opens the provided conversation file and reads its contents.
  
  2. **Pattern Matching:** Uses a regular expression to search for output blocks enclosed by the headers:
     • "==========Output File Start=========="
     • "==========Output File End============"
     
     It searches for exactly two such blocks. This is because the merged input was wrapped in header/footer markers and the system output is expected in the second block.
  
  3. **Extract Output:** Retrieves the content from the second matched block, trims whitespace, and writes it to a file named `output.txt`.
  
  4. **Error Handling:** If the number of matched output blocks is not exactly two or if there are any file I/O errors, the function calls `error_exit()`.

---

### main()

- **Purpose:** Acts as the main entry point for the script. It coordinates all the preceding functions to execute the full workflow.

- **Execution Steps:**
  
  1. **Announcement:** Prints a start message.
  2. **Update Introduction Prompt:** Invokes `update_introduction_prompt()` to merge input files and update the prompt file.
  3. **Launch Streamlit Process:** Calls `launch_streamlit()` to start the LLM controller. It retains the process handle for later termination.
  4. **Monitor for Conversation File:** Gathers any pre-existing conversation files (though note that the check differs slightly; the monitoring function looks in `final_conversation` while this set is gathered from the root pattern) and then calls `wait_for_conversation_file()` to wait for the new conversation file.
  5. **Extract Output:** Once a new conversation file is detected, it extracts the output by calling `extract_output_from_conversation()`.
  6. **Terminate Streamlit:** Attempts to gracefully terminate the Streamlit process using `terminate()` and `wait()`.
  7. **Cleanup:** Runs the `clear_conversation.py` script via `subprocess.run()` to clear/reset conversation data.
  8. **Completion Message:** Finally prints a success message indicating that the script has completed its tasks.

- **Error Handling:** Any issues encountered along the way (e.g., missing files, port conflicts, multiple conversation files, etc.) will cause the script to exit early via the `error_exit()` utility.

---

## Execution Flow

1. The script starts by invoking `main()` if executed as the main module.
2. Input files are merged and the introduction prompt is updated.
3. A Streamlit server running the LLM controller is started on an available port.
4. The script enters a monitoring loop, waiting for a new conversation file to be generated.
5. Once the conversation file is detected, the LLM output is extracted and saved into `output.txt`.
6. The Streamlit process is terminated, and a cleanup script (`clear_conversation.py`) is executed.
7. A final success message is printed, and the script exits.

---

## Usage Notes and Considerations

- **Input Files Requirement:** Ensure that there are at least two input text files named with the prefix `input_` (e.g., `input_1.txt`, `input_2.txt`, etc.) in the same directory as the script.

- **Prompt Placeholder:** The prompt file (`Prompt/Prompt_Step01_writing.txt`) must contain the placeholder line exactly as specified in the `PLACEHOLDER` constant for the replacement to occur.

- **Port Availability:** The script automatically finds an available port in the range 8501–8510. Make sure these ports are free or adjust the range if necessary.

- **Conversation File Monitoring:** The monitoring function expects new conversation files to appear in the `final_conversation` directory. Verify that the LLM controller properly writes the output file into the correct path.

- **Cleanup Script:** The external script `clear_conversation.py` is assumed to exist in the same directory as this script. It is executed after processing is complete.

- **Error Handling:** Most critical operations are wrapped with error checks. If an error is encountered at any stage, the script prints an error message and exits.

---

This documentation covers the workings and structure of “LLM_scheduler_for_merging_03302025.py”. For any modifications or troubleshooting, refer to the individual function explanations and ensure that all file paths and dependencies are correctly set up in your environment.


