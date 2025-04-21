# Documentation for newsroom_daily_work.py

This script automates a daily workflow that involves collecting news data from Reddit, summarizing the collected data, and updating a Hugo-based static blog. The entire process is scheduled to run within a specific time window to ensure that the latest news has been collected and is ready for publication.

---

## Table of Contents

1. [Overview](https://platform.openai.com/playground/prompts?models=o3-mini#overview)
2. [Prerequisites and Assumptions](https://platform.openai.com/playground/prompts?models=o3-mini#prerequisites-and-assumptions)
3. [Workflow Description](https://platform.openai.com/playground/prompts?models=o3-mini#workflow-description)
   - [Time Check](https://platform.openai.com/playground/prompts?models=o3-mini#time-check)
   - [Step 1: Collect News](https://platform.openai.com/playground/prompts?models=o3-mini#step-1-collect-news)
   - [Step 2: Summarize News](https://platform.openai.com/playground/prompts?models=o3-mini#step-2-summarize-news)
   - [Step 3: Update Blog](https://platform.openai.com/playground/prompts?models=o3-mini#step-3-update-blog)
4. [Helper Functions](https://platform.openai.com/playground/prompts?models=o3-mini#helper-functions)
5. [Execution and Error Handling](https://platform.openai.com/playground/prompts?models=o3-mini#execution-and-error-handling)
6. [Usage Notes](https://platform.openai.com/playground/prompts?models=o3-mini#usage-notes)

---

## Overview

The purpose of “newsroom_daily_work.py” is to run a daily job that:

1. **Collects News:** Uses pre-existing Reddit “scrapper” scripts to collect news data from specific subreddits such as **r/politics** and **r/Conservative**. After scraping, an order reversal step is executed to reformat the data.

2. **Summarizes News:** Copies the newly collected data from the scrapper output, hands it off to a summarization process (using parallel subprocesses) and then verifies that summary files are generated correctly.

3. **Updates the Blog:** Copies the summary files to the Hugo blog’s content folder, updates the front matter (header) information for each summary (such as date, title, and publication time), renames each file appropriately, and triggers a blog update script (only if running on Windows).

The script is organized into logical steps with helper functions that ensure each part of the process runs correctly. If any error occurs (out-of-window time, missing files, or subprocess failure), the script exits immediately with an error message.

---

## Prerequisites and Assumptions

- **Python Environment:** The script must run in a Python environment with access to standard libraries such as os, sys, subprocess, time, shutil, datetime, and platform.

- **Directory Structure:** The script expects a specific directory layout:
  
  - A `reddit_scrapper` folder containing the scraping scripts and an `output` folder.
  - An `automatic_summary` folder with `input` and `output` subfolders for the summarization process.
  - A `my-hugo-blog` folder containing a Hugo static blog with its posts under `content/posts` and a blog update script (`blog_update.bat`).

- **External Scripts:**
  
  - Reddit scraper scripts (e.g., `reddit_news_HTML_0409.py` and `order_reversal.py`) are located in the `reddit_scrapper` folder.
  - A summarization script named `summarize_04132025.py` is located in the `automatic_summary` folder.
  - A blog update script (`blog_update.bat`) is required in the Hugo blog folder for triggering a rebuild (only executed on Windows).

- **Time Window:** The workflow must run between 18:03 (6:03 PM) and 23:57 (11:57 PM) local time. This check ensures that the data collection and summarization processes operate on the appropriate news cycle.

---

## Workflow Description

### Time Check

Before any other action is taken, the script verifies that the current local time is within the allowed window:

- **Allowed Window:** After 18:03 (6:03 PM) and before 23:57 (11:57 PM).
  If the condition is not met, the script raises an exception and exits immediately.

### Step 1: Collect News

The script collects news data from Reddit using the following sub-steps:

1. **Define Directories:** The base directory is determined from the script’s location. The `reddit_scrapper` directory and its `output` folder are used for storing scraped files.

2. **Scrape r/politics:**
   
   - A command is built for `reddit_news_HTML_0409.py` with arguments specifying the subreddit, a start time (`coverage_start`), and a cutoff time (`coverage_cutoff`). It is also passed a few flags such as `--reset` and `--daily_page`.
   - The output is directed to a JSONL file (e.g., `output\politics.jsonl`).
   - After the scrape, the script initiates an "order reversal" by running `order_reversal.py` on the output file. This step reorders or transforms the data as needed.
   - The resulting curated file (with the dynamic naming format including the current date tag) is verified to exist and be valid.

3. **Scrape r/Conservative:**
   
   - A similar process is followed for the subreddit r/Conservative.
   - The scrapper and order reversal steps are executed, and the output file (e.g., `output\conservative_<today_tag>_curated.jsonl`) is similarly verified.

### Step 2: Summarize News

This step involves preparing the collected data for summarization and then executing the summarization process:

1. **File Copying:**
   
   - The curated files from the `reddit_scrapper/output` directory (for r/politics and r/Conservative) are copied to the `automatic_summary/input` folder.
   - This is accomplished using the `copy_file` helper function that checks both source and destination.

2. **Running Summarization:**
   
   - The summarization script (`summarize_04132025.py`) is run twice using subprocesses:
     - First for r/politics.
     - Then, after a deliberate wait of exactly 135 seconds, for r/Conservative.
   - This wait ensures that the summarization processes do not compete for system resources simultaneously.
   - The script waits for both processes to complete and confirms that each subprocess exits successfully.

3. **Verification:**
   
   - Once the subprocesses complete, the script checks that both summary files (e.g., `politics_<today_tag>_curated_summary.txt` and `conservative_<today_tag>_curated_summary.txt`) exist and are non-empty.

### Step 3: Update Blog

In the final stage, the script updates a Hugo blog with the new related summaries:

1. **Copy Summary Files:**
   
   - The generated summary files are copied from `automatic_summary/output` to the blog’s posts folder: `my-hugo-blog/content/posts`.

2. **Update Blog Post Headers:**
   
   - For each summary file, the script modifies the file header (front matter) using the `update_file_header` function:
     - The header includes the publication date (in ISO format), a 
       specified publication time (either 19:30:00 or 19:15:00 with a fixed 
       offset), and a dynamic title that includes the current date in a 
       human-friendly format.
     - The updated file is renamed according to a convention, e.g., `YYYYMMDD_politics.md` or `YYYYMMDD_conservative.md`.

3. **Triggering the Blog Update:**
   
   - If the script is running on Windows, it will execute a batch file (`blog_update.bat`) located in the Hugo blog directory to trigger a blog rebuild.
   - On non-Windows systems, this step is skipped (with a log message indicating the same).

---

## Helper Functions

The following helper functions are used throughout the script:

1. **check_execution_time()**
   
   - Ensures that the current local time is between 18:03 and 23:57.
   - Raises an exception if the script is run outside this time window.

2. **run_subprocess(command, cwd, error_msg)**
   
   - Executes a given command (as a list of arguments) in a specified working directory.
   - Inherits the parent process’s stdout/stderr.
   - Checks the command’s return code and raises an exception if it fails with a detailed error message.

3. **verify_file_exists(file_path, desc="File")**
   
   - Confirms that a given file exists and is not empty/malformed (contains at least one non-empty line).
   - If checks fail, it raises an exception.

4. **copy_file(src, dst)**
   
   - Copies a file from a source to a destination.
   - Verifies the existence of the source file and the destination directory before copying.

5. **update_file_header(file_path, new_header_lines, new_filename)**
   
   - Opens a given text file and finds the first non-empty line.
   - Replaces that line with a block of new header lines (front matter).
   - Saves the modified content as a new file with the specified new filename in the same directory.

---

## Execution and Error Handling

- **Main Function:** The `main()` function orchestrates the overall process:
  
  1. It first validates the execution time.
  2. It calculates the dates needed (today and yesterday) and constructs 
     dynamic date strings used for file naming and time parameters.
  3. It calls the three main steps sequentially:
     - News collection (Step 1)
     - News summarization (Step 2)
     - Blog update (Step 3)
  4. If all steps complete successfully, the script logs a success 
     message; otherwise, it catches exceptions, logs the error, and exits 
     with a non-zero status.

- **Error Handling:** Each helper and step function contains detailed checks. When an error is encountered (e.g., out-of-time window, missing files, subprocess failures), an exception is raised with a clear message, and the process stops. This ensures that faulty or incomplete data does not propagate through later stages.

---

## Usage Notes

- **Scheduling:** Ensure that the script is scheduled to run within the allowed time window (after 18:03 and before 23:57 local time).

- **Platform Consideration:** The blog update step is only executed on Windows. On other operating systems, this step is skipped, so plan accordingly if using a non-Windows environment.

- **Dependencies:** Make sure that all dependent scripts (scrappers, order reversal, summarization, and blog update) are available in the correct subdirectories as expected by the script.

- **Logging:** The script prints informational messages at each significant step (e.g., starting subprocesses, copying files, verifying files) to the console. This makes it easier to diagnose issues based on console logs.

---

## Summary

The “newsroom_daily_work.py” script provides a robust, fully automated workflow for:

- Collecting Reddit news data from designated subreddits.
- Summarizing the collected data using parallel processes.
- Updating a Hugo static blog by modifying, copying, and renaming files while inserting appropriate front matter.

By following these steps with detailed file and time validations, the script ensures that only valid and complete news content is published to the blog. Any errors encountered trigger immediate termination with appropriate error messages, facilitating early detection of issues in the workflow.


