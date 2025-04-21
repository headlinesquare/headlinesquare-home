#!/usr/bin/env python
"""
newsroom_daily_work.py

This script implements a fully automated daily workflow that:
    1. Collects news from Reddit using pre-existing scrapper scripts.
    2. Summarizes the collected news using parallel summarization processes.
    3. Updates the static blog by copying, editing, and renaming summary files,
       and then triggers a blog update (only on Windows).

The script uses dynamic date strings for file naming and time arguments, while
keeping the scrapper/summarizer script names fixed. It also performs sanity
checks (time window, file existence, content validity) and exits immediately
if an error is detected.
"""

import os
import sys
import subprocess
import time
import shutil
import datetime
import platform

##############################
# Helper Functions & Classes #
##############################

def check_execution_time():
    """Check that the local time is later than 6:03 pm and earlier than 11:57 pm."""
    now = datetime.datetime.now().time()
    start_limit = datetime.time(18, 3)
    end_limit = datetime.time(23, 57)
    if not (start_limit <= now <= end_limit):
        raise Exception(f"Current local time {now.strftime('%H:%M:%S')} is out of the allowed window (after 18:03 and before 23:57).")
    print(f"[INFO] Execution time check passed: {now.strftime('%H:%M:%S')} is within the allowed window.")

def run_subprocess(command, cwd, error_msg):
    """Run a command as a subprocess with output to parent's console; raise an exception with a detailed error message if it fails."""
    print(f"[INFO] Running command: {' '.join(command)} in {cwd}")
    # By not setting capture_output, stdout/stderr will inherit the parent's streams.
    result = subprocess.run(command, cwd=cwd, text=True)
    if result.returncode != 0:
        raise Exception(f"{error_msg}\nCommand: {' '.join(command)} returned exit code {result.returncode}")
    return result

def verify_file_exists(file_path, desc="File"):
    """Raise an exception if the given file does not exist or is empty/malformed."""
    if not os.path.isfile(file_path):
        raise Exception(f"{desc} does not exist: {file_path}")
    # Check if the file is not empty and contains at least one non-empty line.
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not any(line.strip() for line in lines):
            raise Exception(f"{desc} is empty or malformed: {file_path}")
    print(f"[INFO] Verified {desc} exists and is non-empty: {file_path}")

def copy_file(src, dst):
    """Copy a file from src to dst; raise an exception if copying fails."""
    if not os.path.isfile(src):
        raise Exception(f"Source file does not exist: {src}")
    dst_dir = os.path.dirname(dst)
    if not os.path.isdir(dst_dir):
        raise Exception(f"Destination directory does not exist: {dst_dir}")
    shutil.copy(src, dst)
    print(f"[INFO] Copied file from {src} to {dst}")

def update_file_header(file_path, new_header_lines, new_filename):
    """
    Open a text file, find and replace the first non-empty line with new_header_lines,
    and save the output in new_filename (in the same folder as file_path).
    """
    if not os.path.isfile(file_path):
        raise Exception(f"Summary file to update not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the index of the first non-empty line.
    idx = None
    for i, line in enumerate(lines):
        if line.strip():
            idx = i
            break
    if idx is None:
        raise Exception(f"File {file_path} is empty or contains no non-empty lines.")

    # Replace the first non-empty line with the new header block.
    new_lines = lines[:idx] + new_header_lines + lines[idx+1:]
    
    # Write the updated content to new_filename in the same directory.
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[INFO] Updated header in file {file_path} and saved new file as {new_file_path}")
    return new_file_path

##############################
# Step-by-Step Implementation #
##############################

def step_collect_news(base_dir, today, today_tag, coverage_start, coverage_cutoff):
    """
    Step 1: Collect news using the reddit scrapper scripts and then run the order reversal.
    """
    reddit_dir = os.path.join(base_dir, 'reddit_scrapper')
    output_dir = os.path.join(reddit_dir, 'output')

    # --- r/politics ---
    # Build command for scraping r/politics.
    politics_scrape_cmd = [
        "python", "reddit_news_HTML_0409.py", "politics",
        "--start", coverage_start,
        "--cutoff", coverage_cutoff,
        "--reset", "--daily_page",
        "--output", r"output\politics.jsonl"
    ]
    run_subprocess(politics_scrape_cmd, reddit_dir, "Error running politics scrapper")

    # Expected output file for politics: output\politics_<today_tag>_curated.jsonl
    politics_curated_file = os.path.join(output_dir, f"politics_{today_tag}_curated.jsonl")
    # Run order reversal.
    politics_order_cmd = [
        "python", "order_reversal.py",
        rf"output\politics_{today_tag}_curated.jsonl"
    ]
    run_subprocess(politics_order_cmd, reddit_dir, "Error running order reversal for r/politics")
    verify_file_exists(politics_curated_file, "r/politics curated file")

    # --- r/Conservative ---
    # Build command for scraping r/Conservative.
    conservative_scrape_cmd = [
        "python", "reddit_news_HTML_0409.py", "Conservative",
        "--start", coverage_start,
        "--cutoff", coverage_cutoff,
        "--reset", "--daily_page",
        "--output", r"output\conservative.jsonl"
    ]
    run_subprocess(conservative_scrape_cmd, reddit_dir, "Error running Conservative scrapper")

    # Expected output file for Conservative: output\conservative_<today_tag>_curated.jsonl
    conservative_curated_file = os.path.join(output_dir, f"conservative_{today_tag}_curated.jsonl")
    # Run order reversal.
    conservative_order_cmd = [
        "python", "order_reversal.py",
        rf"output\conservative_{today_tag}_curated.jsonl"
    ]
    run_subprocess(conservative_order_cmd, reddit_dir, "Error running order reversal for r/Conservative")
    verify_file_exists(conservative_curated_file, "r/Conservative curated file")

    print("[INFO] Step 1 (Collect News) completed successfully.")
    return politics_curated_file, conservative_curated_file

def step_summarize_news(base_dir, today_tag):
    """
    Step 2: Copy news files from reddit_scrapper output to automatic_summary input,
            then launch the summarization processes.
    """
    reddit_output_dir = os.path.join(base_dir, 'reddit_scrapper', 'output')
    summary_dir = os.path.join(base_dir, 'automatic_summary')
    summary_input_dir = os.path.join(summary_dir, 'input')
    summary_output_dir = os.path.join(summary_dir, 'output')

    politics_src = os.path.join(reddit_output_dir, f"politics_{today_tag}_curated.jsonl")
    conservative_src = os.path.join(reddit_output_dir, f"conservative_{today_tag}_curated.jsonl")
    politics_dst = os.path.join(summary_input_dir, os.path.basename(politics_src))
    conservative_dst = os.path.join(summary_input_dir, os.path.basename(conservative_src))

    if not os.path.isdir(summary_input_dir):
        raise Exception(f"Destination input folder does not exist: {summary_input_dir}")

    copy_file(politics_src, politics_dst)
    copy_file(conservative_src, conservative_dst)

    # Change working directory to automatic_summary for running summarization.
    summarizer_script = "summarize_04132025.py"
    
    politics_summary_cmd = [
        "python", summarizer_script, f"politics_{today_tag}_curated.jsonl"
    ]
    conservative_summary_cmd = [
        "python", summarizer_script, f"conservative_{today_tag}_curated.jsonl"
    ]
    
    # Launch the first summarization process (politics).
    print(f"[INFO] Launching summarization for r/politics: {' '.join(politics_summary_cmd)}")
    p1 = subprocess.Popen(politics_summary_cmd, cwd=summary_dir, text=True)
    
    # Wait precisely 135 seconds before launching the second process.
    print("[INFO] Waiting for 135 seconds before starting the second summarization process...")
    time.sleep(135)
    
    # Launch the second summarization process (Conservative).
    print(f"[INFO] Launching summarization for r/Conservative: {' '.join(conservative_summary_cmd)}")
    p2 = subprocess.Popen(conservative_summary_cmd, cwd=summary_dir, text=True)
    
    # Wait for both processes to finish.
    print("[INFO] Waiting for both summarization processes to complete...")
    p1.wait()
    p2.wait()
    
    if p1.returncode != 0:
        raise Exception("Summarization process for r/politics failed with exit code " + str(p1.returncode))
    if p2.returncode != 0:
        raise Exception("Summarization process for r/Conservative failed with exit code " + str(p2.returncode))
    
    politics_summary_file = os.path.join(summary_output_dir, f"politics_{today_tag}_curated_summary.txt")
    conservative_summary_file = os.path.join(summary_output_dir, f"conservative_{today_tag}_curated_summary.txt")
    verify_file_exists(politics_summary_file, "r/politics summary file")
    verify_file_exists(conservative_summary_file, "r/Conservative summary file")
    
    print("[INFO] Step 2 (Summarize News) completed successfully.")
    return politics_summary_file, conservative_summary_file

def step_update_blog(base_dir, today, today_tag):
    """
    Step 3: Copy the summary output files to the Hugo blog posts folder, update their headers,
            rename them, and trigger the blog update command if on Windows.
    """
    summary_output_dir = os.path.join(base_dir, 'automatic_summary', 'output')
    posts_dir = os.path.join(base_dir, 'my-hugo-blog', 'content', 'posts')
    blog_dir = os.path.join(base_dir, 'my-hugo-blog')

    if not os.path.isdir(posts_dir):
        raise Exception(f"Blog posts directory does not exist: {posts_dir}")

    politics_summary_src = os.path.join(summary_output_dir, f"politics_{today_tag}_curated_summary.txt")
    conservative_summary_src = os.path.join(summary_output_dir, f"conservative_{today_tag}_curated_summary.txt")
    
    politics_summary_dst = os.path.join(posts_dir, os.path.basename(politics_summary_src))
    conservative_summary_dst = os.path.join(posts_dir, os.path.basename(conservative_summary_src))

    copy_file(politics_summary_src, politics_summary_dst)
    copy_file(conservative_summary_src, conservative_summary_dst)

    today_iso = today.isoformat()  # "YYYY-MM-DD"
    weekday_month_day = today.strftime("%A, %B %d")  # e.g., "Sunday, April 13"

    politics_header = [
        "+++\n",
        f"date = '{today_iso}T19:30:00-04:00'\n",
        "draft = false\n",
        f"title = '[{weekday_month_day}] US News Headlines from r/politics'\n",
        "+++\n"
    ]
    conservative_header = [
        "+++\n",
        f"date = '{today_iso}T19:15:00-04:00'\n",
        "draft = false\n",
        f"title = '[{weekday_month_day}] US News Headlines from r/Conservative'\n",
        "+++\n"
    ]

    new_politics_filename = f"{today_iso.replace('-', '')}_politics.md"
    new_conservative_filename = f"{today_iso.replace('-', '')}_conservative.md"
    update_file_header(politics_summary_dst, politics_header, new_politics_filename)
    update_file_header(conservative_summary_dst, conservative_header, new_conservative_filename)
    
    # Remove the original files
    os.remove(politics_summary_dst)
    print(f"{politics_summary_dst} has been deleted.")
    os.remove(conservative_summary_dst)
    print(f"{conservative_summary_dst} has been deleted.")

    if platform.system().lower() == "windows":
        blog_update_script = os.path.join(blog_dir, 'blog_update.bat')
        if not os.path.isfile(blog_update_script):
            raise Exception(f"Blog update script does not exist: {blog_update_script}")
        print(f"[INFO] Running blog update script: {blog_update_script}")
        run_subprocess([blog_update_script], blog_dir, "Error running blog update script")
    else:
        print("[INFO] Non-Windows OS detected; skipping blog update step.")

    print("[INFO] Step 3 (Update Blog) completed successfully.")

##############################
# Main Function              #
##############################

def main():
    try:
        # Step 0: Verify current local time.
        check_execution_time()

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        today_tag = today.strftime("%m%d%Y")
        coverage_start = f"{yesterday.isoformat()}T19:00:00-04:00"
        coverage_cutoff = f"{today.isoformat()}T19:00:00-04:00"

        base_dir = os.path.abspath(os.path.dirname(__file__))
        print(f"[INFO] Base working directory: {base_dir}")

        # Step 1: Collect the news.
        step_collect_news(base_dir, today, today_tag, coverage_start, coverage_cutoff)

        # Step 2: Summarize the news.
        step_summarize_news(base_dir, today_tag)

        # Step 3: Update the blog.
        step_update_blog(base_dir, today, today_tag)

        print("[INFO] All steps completed successfully. Exiting.")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
