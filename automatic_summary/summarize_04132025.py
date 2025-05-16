import sys
import os
import json
import math
import shutil
import subprocess
import time  # Import time module for delays

def log(msg):
    print(f"[INFO] {msg}")

def error_exit(msg):
    print(f"[ERROR] {msg}")
    sys.exit(1)

def check_input_filename(filename):
    lower_name = filename.lower()
    contains_politics = "politics" in lower_name
    contains_conservative = "conservative" in lower_name
    if contains_politics and contains_conservative:
        error_exit("Input file name contains both 'politics' and 'conservative'.")
    if not (contains_politics or contains_conservative):
        error_exit("Input file name must contain either 'politics' or 'conservative'.")
    return contains_politics, contains_conservative

def read_jsonl_lines(filepath):
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                # We assume the line is a valid JSON record
                try:
                    json.loads(stripped)
                except json.JSONDecodeError as e:
                    error_exit(f"Invalid JSON line encountered: {stripped}")
                lines.append(stripped)
    return lines

def divide_into_chunks(lines, max_chunk_size=100):
    total_lines = len(lines)
    num_chunks = math.ceil(total_lines / max_chunk_size)
    chunks = []
    # Calculate base size and remainder for distribution
    base_size = total_lines // num_chunks
    remainder = total_lines % num_chunks

    start = 0
    for i in range(num_chunks):
        # For the first 'remainder' chunks, add one extra line.
        chunk_size = base_size + (1 if i < remainder else 0)
        chunks.append(lines[start:start+chunk_size])
        start += chunk_size
    return chunks

def prepare_chunk_folder(prefix, chunk_index, chunk_lines, subreddit_keyword):
    # CHANGE: Create folder in "process" subfolder instead of the work folder.
    folder_name = os.path.join("process", f"{prefix}_chunk_{chunk_index}_single_summary")
    
    # CHANGE: Use the template from "process_templates" subfolder.
    template_folder = os.path.join("process_templates", "single_summary_template")
    if not os.path.exists(template_folder):
        error_exit(f"Template folder '{template_folder}' not found in the work directory.")
    # Copy the template folder
    shutil.copytree(template_folder, folder_name)
    log(f"Created folder {folder_name} from template.")

    # Overwrite raw_input.txt with the chunk content
    raw_input_path = os.path.join(folder_name, "raw_input.txt")
    with open(raw_input_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chunk_lines))
    log(f"Wrote {len(chunk_lines)} lines to {raw_input_path}.")

    # Delete the incorrect subreddit file based on the keyword in the input filename.
    if subreddit_keyword == "politics":
        file_to_delete = os.path.join(folder_name, "subreddit_conservative.txt")
    else:
        file_to_delete = os.path.join(folder_name, "subreddit_politics.txt")
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
        log(f"Deleted {file_to_delete}.")
    else:
        log(f"File {file_to_delete} not found (maybe already removed).")
    return folder_name

def launch_llm_scheduler(script_name, working_dir):
    # Launch the scheduler script in its folder.
    log(f"Launching LLM scheduler: {script_name} in {working_dir}")
    process = subprocess.Popen(["python", script_name], cwd=working_dir)
    return process

def copy_file(src, dst):
    if os.path.exists(dst):
        os.remove(dst)  # Explicitly remove the file if it exists
    shutil.copyfile(src, dst)
    log(f"Copied {src} to {dst}.")

def main():
    if len(sys.argv) != 2:
        error_exit("Usage: python summarize_03302025.py <input_file.jsonl>")
    
    # CHANGE: Prepend "input" folder to the input file.
    input_file = os.path.join("input", sys.argv[1])
    if not os.path.exists(input_file):
        error_exit(f"Input file {input_file} does not exist.")

    # Step 1: Validate input file name and read lines
    contains_politics, contains_conservative = check_input_filename(input_file)
    subreddit_keyword = "politics" if contains_politics else "conservative"
    
    # Extract prefix (remove .jsonl extension)
    prefix = os.path.splitext(os.path.basename(input_file))[0]
    log(f"Processing file: {input_file} with prefix: {prefix}")

    lines = read_jsonl_lines(input_file)
    total_lines = len(lines)
    log(f"Total valid JSON lines: {total_lines}")

    chunks = divide_into_chunks(lines, max_chunk_size=100)
    log(f"Divided input into {len(chunks)} chunk(s).")

    chunk_folders = []
    # Step 2: Prepare chunk folders
    for idx, chunk in enumerate(chunks, start=1):
        folder = prepare_chunk_folder(prefix, idx, chunk, subreddit_keyword)
        chunk_folders.append(folder)

    # If more than one chunk, create the merging folder from merging_template
    merging_folder = None
    if len(chunks) > 1:
        # CHANGE: Use the merging template from "process_templates" subfolder.
        merging_template = os.path.join("process_templates", "merging_template")
        # CHANGE: Create the merging folder inside the "process" subfolder.
        merging_folder = os.path.join("process", f"{prefix}_merging")
        if not os.path.exists(merging_template):
            error_exit(f"Merging template folder '{merging_template}' not found.")
        shutil.copytree(merging_template, merging_folder)
        log(f"Created merging folder: {merging_folder} from template.")

    # Step 3: Run LLM processing scripts in parallel for each chunk folder
    processes = []
    for idx, folder in enumerate(chunk_folders, start=1):
        scheduler_script_name = "LLM_scheduler_03292025.py"
        scheduler_full_path = os.path.join(folder, scheduler_script_name)
        if not os.path.exists(scheduler_full_path):
            error_exit(f"Scheduler script {scheduler_full_path} not found in folder {folder}.")
        proc = launch_llm_scheduler(scheduler_script_name, folder)
        processes.append((folder, proc))
        # Add a 30-second delay before launching the next scheduler, if not the last one
        if idx < len(chunk_folders):
            log("Waiting 30 seconds before launching next LLM scheduler...")
            time.sleep(30)

    log("Waiting for all chunk processes to finish...")
    for folder, proc in processes:
        proc.wait()
        log(f"LLM scheduler in {folder} has finished.")

    # Step 4: Collect outputs and run merging (if needed)
    # CHANGE: Final summary output file will be placed in the "output" subfolder with a .txt extension.
    final_summary_name = os.path.join("output", f"{prefix}_summary.txt")
    if len(chunk_folders) == 1:
        # Single chunk: copy output.txt to work folder with final name.
        output_src = os.path.join(chunk_folders[0], "output.txt")
        if not os.path.exists(output_src):
            error_exit(f"Expected output file {output_src} not found.")
        copy_file(output_src, final_summary_name)
    else:
        # Multiple chunks: copy each output.txt into the merging folder with the name input_XX.txt
        for idx, folder in enumerate(chunk_folders, start=1):
            output_src = os.path.join(folder, "output.txt")
            if not os.path.exists(output_src):
                error_exit(f"Expected output file {output_src} not found.")
            dst_filename = f"input_{idx:02d}.txt"
            dst_path = os.path.join(merging_folder, dst_filename)
            copy_file(output_src, dst_path)
        
        # Now run the merging scheduler
        merging_scheduler_name = "LLM_scheduler_for_merging_03302025.py"
        merging_scheduler = os.path.join(merging_folder, merging_scheduler_name)
        if not os.path.exists(merging_scheduler):
            error_exit(f"Merging scheduler script {merging_scheduler} not found.")
        log("Launching merging LLM scheduler...")
        merge_proc = subprocess.Popen(["python", merging_scheduler_name], cwd=merging_folder)
        merge_proc.wait()
        log("Merging process has finished.")

        merged_output = os.path.join(merging_folder, "output.txt")
        if not os.path.exists(merged_output):
            error_exit(f"Merged output file {merged_output} not found.")
        copy_file(merged_output, final_summary_name)

    log(f"Final summary output created: {final_summary_name}")

if __name__ == "__main__":
    main()
