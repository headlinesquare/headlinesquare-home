# LLM_scheduler_03292025.py Documentation

This script is designed to orchestrate an end-to-end workflow for processing raw input data, updating prompt templates, launching a Streamlit-based controller for a language model (LLM), monitoring for conversation output files, extracting the desired output, and cleaning up afterward. It combines file operations, JSON processing, network port handling, and subprocess management.

---

## Table of Contents

1. [Overview](https://platform.openai.com/playground/prompts?models=o3-mini#overview)
2. [Prerequisites and File Structure](https://platform.openai.com/playground/prompts?models=o3-mini#prerequisites-and-file-structure)
3. [Detailed Function Descriptions](https://platform.openai.com/playground/prompts?models=o3-mini#detailed-function-descriptions)
   - [error_exit(message)](https://platform.openai.com/playground/prompts?models=o3-mini#error_exitmessage)
   - [update_subreddit_prompt()](https://platform.openai.com/playground/prompts?models=o3-mini#update_subreddit_prompt)
   - [process_raw_input()](https://platform.openai.com/playground/prompts?models=o3-mini#process_raw_input)
   - [update_prompt_file(prompt_path, replacement_text)](https://platform.openai.com/playground/prompts?models=o3-mini#update_prompt_fileprompt_path-replacement_text)
   - [is_port_available(port, timeout=5)](https://platform.openai.com/playground/prompts?models=o3-mini#is_port_availableport-timeout5)
   - [launch_streamlit()](https://platform.openai.com/playground/prompts?models=o3-mini#launch_streamlit)
   - [wait_for_conversation_file(existing_files)](https://platform.openai.com/playground/prompts?models=o3-mini#wait_for_conversation_fileexisting_files)
   - [extract_output_from_conversation(conv_file)](https://platform.openai.com/playground/prompts?models=o3-mini#extract_output_from_conversationconv_file)
   - [main()](https://platform.openai.com/playground/prompts?models=o3-mini#main)
4. [Execution Flow](https://platform.openai.com/playground/prompts?models=o3-mini#execution-flow)
5. [Usage and Execution](https://platform.openai.com/playground/prompts?models=o3-mini#usage-and-execution)
6. [Notes and Considerations](https://platform.openai.com/playground/prompts?models=o3-mini#notes-and-considerations)

---

## Overview

The script performs the following primary tasks:

1. **Prompt Update:** It searches for a subreddit introduction file (named with a pattern `subreddit*.txt`) and uses its content to update a placeholder in an introduction prompt template (`Prompt/Prompt_Step00_introduction.txt`).

2. **Raw Input Processing:** It reads a `raw_input.txt` file containing JSON-formatted lines. For each JSON object, the script verifies required fields (i.e. `"id"` and `"url"`), creates a version without the URL (for certain prompts), calculates an ID range header, and then writes the results into a new file (`raw_input_no_url.txt`).

3. **Prompt File Updates:** Two prompt template files are updated by replacing a defined placeholder (set in the constant `PLACEHOLDER`) with either a raw input with URLs or the version without URLs.

4. **Streamlit Launch and Monitoring:** The script launches a separate Streamlit process that runs another controller script (`LLM_controller_03292025.py`). It finds an available port (by default scanning ports 8501–8510) and monitors a specified directory for new conversation output files.

5. **Output Extraction:** Once a new conversation file is detected (in the `final_conversation/` folder), the script reads the file and uses regular expressions to extract the second output block delimited by specific header markers. The extracted output is saved in `output.txt`.

6. **Cleanup:** Finally, the script terminates the Streamlit process and invokes a cleanup script (`clear_conversation.py`) to reset the conversation state.

---

## Prerequisites and File Structure

### Prerequisites

- **Python Environment:** The script requires Python 3.

- **Python Modules:** It uses several built-in Python modules including:
  
  - `os`, `sys`, `glob`, `json`, `re`, `time`, `socket`, `subprocess`
  - `pathlib` (for `Path`)

- **Streamlit Installation:** Streamlit must be installed in your environment since the script launches a Streamlit application.

### Expected Files and Directories

- A single subreddit introduction file named similar to: `subreddit*.txt` (e.g., `subreddit.txt`)

- Prompt templates under a folder named `Prompt`:
  
  - `Prompt_Step00_introduction.txt`
  - `Prompt_Step01_01_input_writing.txt`
  - `Prompt_Step07_01_input_reasoning.txt`

- An input file:
  
  - `raw_input.txt` (each line should contain a valid JSON object with at least the keys `"id"` and `"url"`)

- Conversation output files (to be detected when produced):
  
  - The output is monitored in the directory `final_conversation` with a file naming pattern: `conversation_*.txt`

- Cleanup script:
  
  - `clear_conversation.py`

- The controller file for Streamlit:
  
  - `LLM_controller_03292025.py`

---

## Detailed Function Descriptions

### error_exit(message)

- **Purpose:** Print an error message (prefixed with “ERROR:”) and exit the script.

- **Parameters:**
  
  - `message` (string): The error message to display.

- **Logic:** Simply prints the error message and terminates the process using `sys.exit(1)`.

---

### update_subreddit_prompt()

- **Purpose:** Reads the subreddit introduction file and updates the introduction prompt template by replacing a defined placeholder.

- **Workflow:**
  
  1. **Locate the Subreddit File:** Uses `glob.glob("subreddit*.txt")` to find a unique file. It expects exactly one file matching the pattern.
  2. **Read Content:** Reads the entire content (assumed to be a subreddit introduction) from the found file.
  3. **Load the Prompt Template:** Opens `Prompt/Prompt_Step00_introduction.txt`. If the file does not exist, the script aborts.
  4. **Placeholder Replacement:** Iterates over each line of the prompt template. If a line (stripped) 
     exactly matches the placeholder (a constant string), it substitutes that
     line with the subreddit introduction text.
  5. **Write-back:** If the placeholder was found, the file is updated with the new content; 
     otherwise, a message is printed and the update is skipped.

---

### process_raw_input()

- **Purpose:** Processes the `raw_input.txt` file by reading each JSON line, validating required fields, preparing two versions (with and without URLs), and generating an ID range header.

- **Workflow:**
  
  1. **File Reading:** Checks for the existence of `raw_input.txt` and reads its entire content.
  2. **Line Processing:** Splits the content into individual non-empty lines.
  3. **JSON Parsing and Validation:** For each line, parses the JSON object and ensures it has both `"id"` and `"url"` keys. Missing fields cause the script to exit with an error.
  4. **Preparation of Two Versions:**
     - **Full Version:** Keeps all fields.
     - **No-URL Version:** Removes the `"url"` field from each object.
  5. **ID Range Header:** Determines the minimum and maximum IDs from the input and computes total
     articles. The header (formatted in Markdown) is prepended to both 
     versions.
  6. **Writing Processed Output:** Writes the no-URL version to `raw_input_no_url.txt` and returns both the full and no-URL prompt strings for further use.

- **Returns:** A tuple containing:
  
  - `raw_input_string`: The full input with URLs and prepended header.
  - `raw_input_no_url_string`: The URL-removed version with prepended header.

---

### update_prompt_file(prompt_path, replacement_text)

- **Purpose:** Updates a given prompt file by searching for a line that exactly matches the placeholder string. When found, it replaces that line with the provided replacement text.

- **Parameters:**
  
  - `prompt_path` (string): Path to the prompt file to update.
  - `replacement_text` (string): The text that will replace the placeholder.

- **Workflow:**
  
  1. **File Existence Check:** Validates that the target file exists.
  2. **File Read:** Reads the entire file line by line.
  3. **Placeholder Detection:** Iterates through each line; if a line exactly matches the defined placeholder (`PLACEHOLDER`), it is replaced with the `replacement_text` (with an appended newline).
  4. **Write-back:** Rewrites the file with updated content if a placeholder was found. Otherwise, a message indicates no changes were made.

---

### is_port_available(port, timeout=5)

- **Purpose:** Checks whether a specific TCP port on localhost is available for listening.

- **Parameters:**
  
  - `port` (int): The TCP port to test.
  - `timeout` (int, optional): How many seconds to wait before timing out the connection attempt (default is 5).

- **Workflow:**
  
  1. **Socket Connection:** Attempts to connect to `127.0.0.1` on the specified port.
  2. **Availability Determination:** If the connection succeeds, the port is in use (returns False). 
     Otherwise, if an error occurs, the port is considered available (returns
     True).

---

### launch_streamlit()

- **Purpose:** Finds an available port (starting at 8501 and scanning upward until 8510) and then launches the Streamlit-based LLM controller.

- **Workflow:**
  
  1. **Port Scanning:** Iterates through ports 8501 to 8510 using `is_port_available()`. The first available port is selected.
  2. **Command Construction:** Prepares a command list to launch Streamlit with the chosen port and to run `LLM_controller_03292025.py`. The command resembles: `streamlit run LLM_controller_03292025.py --server.port=<chosen_port>`
  3. **Launching Process:** Uses `subprocess.Popen` (without `shell=True`) to start the Streamlit process.
  4. **Error Handling:** If no available port is found or if the process fails to launch, the script terminates with an error.

- **Returns:** The `Popen` process object for the launched Streamlit instance.

---

### wait_for_conversation_file(existing_files)

- **Purpose:** Monitors for the appearance of a new conversation file matching the pattern `final_conversation/conversation_*.txt`.

- **Parameters:**
  
  - `existing_files` (set): A set of file names (or paths) representing conversation files that existed before launching the process.
    (Note: In the main function, the existing files are gathered via a different glob pattern (`conversation_*.txt`). This may be intentional or may require alignment.)

- **Workflow:**
  
  1. **Monitoring Loop:** Every 10 seconds, the script checks the `final_conversation` directory for files matching the conversation pattern.
  2. **Detection:** It compares the set of current files with the `existing_files` to find any new file.
  3. **Validation:** If more than one new file is detected, the script exits with an error. Otherwise, the newly detected file is returned.

- **Returns:** The path to the newly detected conversation file.

---

### extract_output_from_conversation(conv_file)

- **Purpose:** Reads the specified conversation file and extracts the desired output block as indicated by marker strings.

- **Workflow:**
  
  1. **File Reading:** Opens and reads the content of the conversation file.
  2. **Regex Extraction:** Uses a regular expression to capture content between two specific markers:
     - Start marker: `"==========Output File Start=========="`
     - End marker: `"==========Output File End============"`The pattern expects exactly two blocks in the file; the second block is considered the output.
  3. **Validation:** If the number of block matches is not exactly two, an error is thrown.
  4. **Saving the Output:** The script writes the trimmed content of the second block to an `output.txt` file.

---

### main()

- **Purpose:** Serves as the main entry point that orchestrates the overall workflow.

- **Workflow (Step-by-Step):**
  
  1. **Initialization Message:** Prints a start message.
  2. **Subreddit Prompt Update:** Calls `update_subreddit_prompt()` to update the introduction in the prompt template.
  3. **Raw Input Processing:** Invokes `process_raw_input()` to process the `raw_input.txt` file and obtain both versions of the input (full and no-URL).
  4. **Prompt Files Update:**
     - Updates `Prompt/Prompt_Step01_01_input_writing.txt` with the no-URL version.
     - Updates `Prompt/Prompt_Step07_01_input_reasoning.txt` with the full raw input.
  5. **Streamlit Launch:** Launches the Streamlit process by calling `launch_streamlit()` and stores the process object.
  6. **Conversation File Monitoring:** Gathers the set of existing conversation files (though note the glob 
     pattern here differs slightly from later usage) and then calls `wait_for_conversation_file()` to wait for a new conversation file.
  7. **Output Extraction:** Once the new conversation file is detected, `extract_output_from_conversation()` extracts the required output to `output.txt`.
  8. **Shutdown Sequence:**
     - Terminates the Streamlit process gracefully.
     - Runs the cleanup script `clear_conversation.py` using `subprocess.run`.
  9. **Completion Message:** Prints a final message indicating successful completion.

- **Flow Summary:** The main function defines the high-level workflow:
  
  - Update prompts → Process inputs → Launch controller → Wait for conversation → Extract output → Cleanup.

---

## Execution Flow

1. Script starts and prints an initialization message.
2. The introduction prompt is updated using the subreddit file.
3. The raw input file is processed to generate two versions along with an ID header.
4. The appropriate prompt files are updated with these versions.
5. A free port is found, and a new Streamlit process is launched with the controller script.
6. The script monitors for a new conversation file in the `final_conversation` directory.
7. When the new conversation file is found, the script extracts the second output block using regex and saves it to `output.txt`.
8. The Streamlit process is then terminated and a cleanup script is executed.
9. The script exits with a success message.

---

## Usage and Execution

1. **Ensure all Required Files and Directories Are Present:**
   
   - A unique `subreddit*.txt` file.
   - The `raw_input.txt` file containing JSON-formatted lines.
   - The prompt templates in the `Prompt` directory.
   - The controller script (`LLM_controller_03292025.py`) and the cleanup script (`clear_conversation.py`).
   - The directory `final_conversation` (if the conversation files are to be monitored there).

2. **Install Python and Dependencies:** Make sure Python 3 and Streamlit are installed:
   • Example installation for Streamlit:
   pip install streamlit

3. **Run the Script:** From the command line, simply run:
   • python LLM_scheduler_03292025.py

4. **Monitoring and Output:** The script will print logging messages to the console as it processes files, launches Streamlit, and updates content. Once the conversation file is detected and processed, the final extracted output is saved as `output.txt`.

---

## Notes and Considerations

- **Placeholder Matching:** The script looks for an exact match of the placeholder string (defined as the constant `PLACEHOLDER`). Ensure that the placeholder line in the prompt templates matches exactly:

- ```text
  ++++++++++++++++++++Paste Here++++++++++++++++++++++++++
  ```

- **Error Handling:** The script uses a dedicated `error_exit()` function to print messages and terminate execution on any failures (e.g., missing files, parse errors, or port conflicts).

- **Port Scanning:** The port selection logic starts at port 8501 and scans up to 8510. If no free port is found, the script will terminate with an error.

- **Directory Inconsistency:** Note that when gathering existing conversation files before monitoring, the script uses a different glob pattern than when monitoring (i.e. `conversation_*.txt` vs. `final_conversation/conversation_*.txt`). Verify that your file structure aligns with these expectations to avoid mismatches.
