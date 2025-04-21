This script is designed to process a JSONL (JSON Lines) input file and generate a final summary file by first splitting the input into manageable chunks, processing each chunk using an external “LLM scheduler” script (presumably to leverage large language model functionality), and finally merging the outputs if necessary. Below is a detailed, step‐by‐step analysis:

---

## 1. **Initialization and Helper Functions**

- **Imports and Logging:**  
  The script begins by importing standard Python libraries such as `sys`, `os`, `json`, `math`, `shutil`, `subprocess`, and `time`. It defines two helper functions:
  
  - `log(msg)`: Prints an informational message formatted with `[INFO] …`.
  
  - `error_exit(msg)`: Prints an error message with `[ERROR] …` and exits the program.

- **Filename Validation – `check_input_filename`:**  
  This function inspects the input filename (converted to lowercase) for two keywords:
  
  - It checks if the filename contains the substring `"politics"`.
  
  - It checks if the filename contains `"conservative"`.

  The function has two guard conditions:

- If **both** keywords are present, the script exits with an error.

- If **neither** keyword is found, the script also exits with an error.

  This ensures that the input file is explicitly associated with either a politics-related or a conservative theme, which later drives conditional handling in the folder preparation stage.

---

## 2. **Reading and Validating Input Data**

- **Reading JSONL Lines – `read_jsonl_lines`:**  
  This function opens the input file in UTF-8 mode and reads it line by line. Each non-empty line is expected to be a valid JSON record:
  
  - For each line, it strips whitespace and attempts to parse it with `json.loads()`.
  
  - If any line is not valid JSON, the script terminates immediately with an error.

  The function accumulates valid JSON lines (as raw strings) into a list for further processing.

---

## 3. **Dividing the Input into Chunks**

- **Chunk Creation – `divide_into_chunks`:**  
  Given the list of JSONL lines, this function splits them into “chunks” with a maximum of 120 lines each. The process involves:
  
  - Calculating the number of chunks using `math.ceil(total_lines / max_chunk_size)`.
  
  - Dividing the list into nearly equal parts by computing a base size and distributing any remainder across the first few chunks.

  This step ensures that the processing workload (likely for summarization) is split into smaller units that can be processed in parallel.

---

## 4. **Preparing Processing Folders for Each Chunk**

- **Folder Preparation – `prepare_chunk_folder`:**  
  For every chunk, the script prepares a dedicated folder:
  
  - **Template Copy:**  
    It expects a folder named `single_summary_template` in the working directory. This folder is copied to a new folder whose name is constructed using the file prefix and the chunk index (e.g., `"curated_conservative_0326_chunk_1_single_summary"`).
  
  - **Writing Chunk Data:**  
    Inside this folder, a file named `raw_input.txt` is overwritten with the chunk’s lines (joined with newline characters). This file will serve as the input to the summarization process in that folder.
  
  - **Subreddit File Deletion:**  
    Depending on the keyword inferred from the input filename (`"politics"` or `"conservative"`), the script deletes the file representing the incorrect subreddit. For example, if the input is politics-related, it deletes `subreddit_conservative.txt`, ensuring that only the relevant file remains.

  This careful folder setup ensures that each chunk is isolated with the proper configuration for subsequent processing.

---

## 5. **Launching LLM Processing Subprocesses**

- **Subprocess Execution – `launch_llm_scheduler`:**  
  In each prepared chunk folder, the script expects an external Python script (named `LLM_scheduler_03292025.py`) to be present. This script is launched as a separate process using `subprocess.Popen` with its working directory set to the chunk folder.

- **Parallelism with Delays:**  
  For multiple chunks, the script:
  
  - Launches the scheduler scripts one by one.
  
  - Introduces a 30-second delay between launching each process (except after the last one).  
    This delay may serve to manage resource usage or control request rates to an external LLM service.

- **Process Synchronization:**  
  After launching all processes, the main script waits (using `proc.wait()`) for each subprocess to complete before proceeding further.

---

## 6. **Merging the Outputs (if Needed)**

- **Handling a Single versus Multiple Chunks:**
  
  - **Single Chunk:**  
    If only one chunk was created, the script directly copies the `output.txt` from that folder to a final summary file named `<prefix>_summary.txt`.
  
  - **Multiple Chunks:**  
    If multiple chunks are processed:
    
    1. The script first prepares a merging folder by copying a `merging_template` folder. The new folder is named `<prefix>_merging`.
    
    2. It then copies each chunk’s `output.txt` into the merging folder, renaming them sequentially as `input_XX.txt` (where `XX` is a two-digit number representing the chunk index).
    
    3. Next, it launches another LLM scheduler, specifically `LLM_scheduler_for_merging_03302025.py`, within the merging folder. This step is responsible for combining the individual summaries into one coherent final summary.
    
    4. After the merging process finishes, the merged `output.txt` in the merging folder is copied to the final summary file.

  This modular approach (individual chunk processing followed by merging) helps in parallelizing the summarization task while ensuring a consolidated output.

---

## 7. **Final Output and Cleanup**

- **Final Summary File:**  
  The final summary is always placed in a file named `<prefix>_summary.txt`. This file is the end product of either a single chunk’s output or the merged result of multiple chunks.

- **Extensive Logging:**  
  Throughout the process, the script logs key events (folder creation, file copy operations, scheduler launches, etc.) to standard output. This logging aids in tracking the progress and debugging if any error occurs.

- **Error Handling:**  
  Throughout the script, error conditions (such as missing files, invalid JSON, or missing template directories) are caught early, and the script exits gracefully with an informative error message.

---

## **Overall Workflow Summary**

1. **Input Validation:**
   
   - The script verifies that the input file’s name contains either “politics” or “conservative” (but not both) and that the file exists.

2. **Reading and Checking Data:**
   
   - It reads the input file line-by-line, ensuring that each line is valid JSON.

3. **Chunking:**
   
   - The valid lines are divided into chunks (with a maximum of 120 lines per chunk) for better manageability.

4. **Folder Setup:**
   
   - For each chunk, a processing folder is created based on a template. The chunk's data is saved, and files irrelevant to the identified theme (politics/conservative) are removed.

5. **LLM Processing:**
   
   - Each folder launches an external “LLM scheduler” script that likely performs summarization or transformation of the data.
   
   - There is a built-in delay to manage resource usage when launching multiple processes.

6. **Merging:**
   
   - If multiple chunks exist, an additional merging phase combines individual outputs.

7. **Final Output:**
   
   - The ultimate output is a single summary file named with the original file prefix, ready for further use or review.

This design supports robust error handling, modularity (through the use of templates and separate scheduler scripts), and parallel processing while ensuring that a large input file is efficiently summarized with consistent thematic filtering.

Feel free to ask if you need further clarifications on any specific component!





There are following changes I want to make. I want to organize the input/output/process/template files better. Originally, all files and folders are laid out in the work folder. Now, I want to put input files, like `conservative_04122025_curated.jsonl` into `input` subfolder, and final output files, like `conservative_04122025_curated_summary.jsonl` into `output` subfolder. And put two templates, including `single_summary_template` and `merging_template` into `process_templates` subfolder. And put all the chunk summary processing folders, like `conservative_04122025_curated_chunk_1_single_summary`, and `politics_04122025_curated_merging`, into `process` subfolder. And only this Python code, summarize_03302025.py, still remains in the work folder. 
The work folder should contain the following:
summarize_03302025.py
input/
output/
process/
process_templates/
That's it. Nothing else should be changed. Please make minimal change.
Please tell me if everything is clear. Do not start coding this time. Start coding after you receive my confirmation.







Everything is clear. To summarize, here are the changes you want to make:

- **Input Files:**  
  Files like `conservative_04122025_curated.jsonl` will now reside in the `input` subfolder.

- **Output Files:**  
  Final output files such as `conservative_04122025_curated_summary.jsonl` will now be placed in the `output` subfolder.

- **Templates:**  
  Both `single_summary_template` and `merging_template` directories will be moved into the `process_templates` subfolder.

- **Processing Folders:**  
  All chunk summary processing folders (e.g., `conservative_04122025_curated_chunk_1_single_summary` and `politics_04122025_curated_merging`) will be created within the `process` subfolder.

- **Remaining File:**  
  The Python script `summarize_03302025.py` remains directly in the work folder.

Thus, the work folder will contain only:

- `summarize_03302025.py`

- `input/`

- `output/`

- `process/`

- `process_templates/`

Everything is clear, and I will proceed with minimal changes after your confirmation. Let me know when you'd like me to start coding this.




