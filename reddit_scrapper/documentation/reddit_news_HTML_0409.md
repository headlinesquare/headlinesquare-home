# reddit_news_HTML_0409.py

# Reddit News Scraper v0.1 (HTML Version)

This script is designed to scrape news posts from a specified subreddit using Reddit’s “old” HTML interface. It fetches recent posts while filtering out stickied or promoted content. It also supports resuming with a checkpoint and can optionally split the output by daily segments.

---

## Table of Contents

1. [Overview](https://platform.openai.com/playground/prompts?models=o3-mini#overview)
2. [Installation & Dependencies](https://platform.openai.com/playground/prompts?models=o3-mini#installation--dependencies)
3. [Usage](https://platform.openai.com/playground/prompts?models=o3-mini#usage)
4. [Command-line Arguments](https://platform.openai.com/playground/prompts?models=o3-mini#command-line-arguments)
5. [Workflow & Architecture](https://platform.openai.com/playground/prompts?models=o3-mini#workflow--architecture)
   - [HTTP Session Setup](https://platform.openai.com/playground/prompts?models=o3-mini#http-session-setup)
   - [Pagination & Checkpointing](https://platform.openai.com/playground/prompts?models=o3-mini#pagination--checkpointing)
   - [Daily Page Output](https://platform.openai.com/playground/prompts?models=o3-mini#daily-page-output)
6. [Function-by-Function Explanation](https://platform.openai.com/playground/prompts?models=o3-mini#function-by-function-explanation)
7. [Error Handling & Logs](https://platform.openai.com/playground/prompts?models=o3-mini#error-handling--logs)
8. [Notes](https://platform.openai.com/playground/prompts?models=o3-mini#notes)

---

## Overview

The script scrapes the “new” posts from a specified subreddit (using the “old” Reddit interface) and extracts key information including the title, selftext (the full text of a post), URL, score, number of comments, publication timestamp, and more. It then outputs the results in JSON Lines (JSONL) format with three variations:

- **Full Output:** All extracted fields.
- **Simple Output:** A subset of key fields with the creation date in US Eastern time.
- **Curated Output:** A minimal “curated” record that contains an ID (incremental), domain, title, and URL.

Optionally, the script can generate separate output files for each 24-hour segment if the user enables the daily page mode.

---

## Installation & Dependencies

Before running the script, ensure you have the following packages installed:

- `requests`
- `pytz`
- `beautifulsoup4`

You can install them using either conda or pip:

Using conda:

```text
conda install requests pytz beautifulsoup4
```

Using pip:

```text
pip install requests pytz beautifulsoup4
```

---

## Usage

Run the script from the command line. Examples:

```text
python reddit_news_HTML_0409.py Conservative --start 2025-03-23T19:00:00-04:00 \
    --cutoff 2025-03-24T19:00:00-04:00 --reset --output conservative_0324.jsonl
```

For daily segmentation:

```text
python reddit_news_HTML_0409.py Conservative --start 2025-03-23T19:00:00-04:00 \
    --cutoff 2025-03-26T19:00:00-04:00 --reset --daily_page --output conservative.jsonl
```

---

## Command-line Arguments

- **subreddit** The name of the subreddit (e.g. “Conservative”) from which posts will be scraped.

- **--start** The ISO formatted start date/time (with timezone) marking the beginning of the coverage window.
  Example: `2025-03-23T19:00:00-04:00`

- **--cutoff** The ISO formatted end date/time marking the end of the coverage window.
  Example: `2025-03-24T19:00:00-04:00`

- **--output** The base filename for the output JSON Lines. Default is “posts.jsonl”.
  In daily mode, different files are generated with date suffixes.

- **--reset** A flag that, if set, resets the scraper's checkpoint so that scraping will start from the first page.

- **--daily_page** If set, the output is split into separate files per each 24-hour segment.
  Note: In this mode, the start and cutoff times must share the same time-of-day.

---

## Workflow & Architecture

### HTTP Session Setup

- **User-Agent & Session:** The script uses a custom user-agent (as recommended by Reddit’s API 
  guidelines) and builds a persistent HTTP session with a retry adapter 
  (up to 3 retries) to increase robustness.

### Pagination & Checkpointing

- **Fetching New Pages:** The script loads pages from `https://old.reddit.com/r/{subreddit}/new/` and uses an “after” parameter to navigate through pagination.
- **Checkpoint File:** A file named `checkpoint.txt` is used to store the “after” parameter from the last successful page fetch so that the scraper can resume if interrupted.
- **Post Time Filtering:**
  - Posts with creation timestamps later than the `cutoff` are ignored.
  - For posts earlier than the `start` time, the script checks nearby posts (and may even fetch an extra page) to decide if the pagination should stop.

### Daily Page Output

- **Daily Segments:** With the `--daily_page` flag enabled (and provided that both 
  start and cutoff times share the same time-of-day), output is split by 
  day. The script creates three different file handles for each daily 
  segment:
  - Full JSON output
  - Simple JSON output
  - Curated JSON output
- **Daily Article ID:** For curated output, each day gets its own incremental ID starting from 1.

---

## Function-by-Function Explanation

### build_session()

- **Purpose:** Creates and returns a persistent `requests.Session` instance.
- **Details:**
  - Configures an HTTP adapter with up to 3 retries.
  - Ensures that subsequent HTTP requests share the same session.

---

### parse_number(text)

- **Purpose:** Converts string representations of numbers (e.g., "45" or "1.2k") into integer values.
- **Details:**
  - Strips the string and returns 0 if empty or equals “•”.
  - Converts strings with “k” (case-insensitive) by multiplying accordingly.
  - Returns 0 in case of errors.

---

### fetch_full_selftext(post_url, sess, timeout=10)

- **Purpose:** If a post’s selftext is abbreviated (not fully loaded and appears as 
  “loading...”), this function fetches the post’s individual page and 
  extracts the complete textual content.
- **Details:**
  - Constructs a full URL if a relative URL is provided.
  - Uses BeautifulSoup to parse the HTML and locate the expando section.
  - Catches timeouts and exceptions; prints error messages if any occur.

---

### fetch_page(sess, subreddit, after=None)

- **Purpose:** Fetches a page of new posts from a subreddit and parses out the relevant post data.
- **Details:**
  - Uses the `after` parameter for pagination if available.
  - Skips posts that are “stickied” or flagged as promoted.
  - For each valid post (wrapped in a `<div class="thing">`):
    - Extracts the title, URL, self text, score, number of comments, domain, permalink, author, and timestamp.
    - Handles the timestamp using either a data attribute (`data-timestamp`) or a `<time>` element.
    - Attempts to get a thumbnail URL if available.
  - Uses BeautifulSoup to locate the “next” button and extract the next “after” identifier from its URL.
  - Returns a tuple: a list of valid posts (each a dictionary) and the new `after` value.

---

### load_checkpoint()

- **Purpose:** Reads the current pagination checkpoint from the `checkpoint.txt` file (if it exists).
- **Returns:** The saved “after” parameter as a string, or `None` if the file does not exist.

---

### save_checkpoint(after)

- **Purpose:** Saves the current pagination checkpoint (`after` parameter) to `checkpoint.txt` so that the scraper can resume from this point later.
- **Details:**
  - Writes the checkpoint value to the file (or an empty string if `after` is `None`).

---

### parse_args()

- **Purpose:** Uses Python‘s `argparse` module to parse and validate the command-line arguments.
- **Details:**
  - Requires the subreddit name, start date, and cutoff date.
  - Provides optional flags: `--reset`, `--daily_page`, and `--output`.
  - Validates that for daily-page splitting, the start and cutoff times share the same time-of-day.

---

### main()

- **Purpose:** The entry point of the script; it sets up the session, initializes pagination and file outputs, then enters the scraping loop.
- **Key Steps:**
  1. **Argument Parsing:** Retrieves user inputs from the command line.
  2. **Session and Checkpoint Initialization:**
     - Builds an HTTP session.
     - Resumes from a checkpoint if the `--reset` flag is not set.
  3. **Time Conversion:** Converts the provided ISO start and cutoff times into UTC for uniform comparison.
  4. **File Handling for Output:**
     - If `--daily_page` is enabled, the script splits the output into files for each 24-hour segment.
     - Three file types are maintained per segment: full, simple, and curated.
     - Otherwise, three general output files are opened.
  5. **Scraping Loop:**
     - Fetches pages using `fetch_page()`.
     - Sleeps for 2 seconds between page requests to be polite to Reddit’s servers.
     - For each post:
       - Skips posts that are outside the desired time window.
       - For posts with “loading...” as selftext, the script attempts to fetch the full post content.
       - Computes the post’s creation time and formats it in US Eastern Time for the simple output.
       - Determines the appropriate output file (or daily segment index) based on creation time.
       - Increments a daily (or overall) counter for the curated post ID.
       - Writes JSON lines to the corresponding files.
  6. **Checkpoint Saving & Pagination Termination:**
     - Saves the “after” checkpoint after processing each page.
     - Stops pagination when there are no further pages (or when posts older than the start time are consistently encountered).
  7. **Closing Files & Final Logging:** All file handles are closed, and the total number of posts processed is printed.

---

## Error Handling & Logs

- The script prints error messages when exceptions occur:
  - In `fetch_full_selftext()`, network timeouts or request exceptions are caught and logged.
  - If the daily-page mode is enabled with mismatched start and cutoff 
    times (different time-of-day), the script prints an error message and 
    exits.
- HTTP errors are propagated via `raise_for_status()` in HTTP requests so that unexpected responses halt execution.

---

## Notes

- **User-Agent:** The script sets a custom user-agent in accordance with Reddit’s guidelines. Replace `"u/YourRedditUsername"` with your actual Reddit username.

- **Rate Limiting & Delays:** A delay (`time.sleep(2)`) is enforced between HTTP requests to avoid hitting Reddit too quickly.

- **Checkpointing:** The checkpoint mechanism (using `checkpoint.txt`) allows you to restart scraping without duplicating already fetched pages, unless you pass the `--reset` flag.

- **Daily Page Splitting:** The `--daily_page` mode assumes that the time window spans exact 24-hour segments (i.e. the start and cutoff have the same time-of-day), which allows it to split posts into discrete daily files.

---

## Summary

This script is a robust Reddit news posts scraper using the HTML interface of “old” Reddit. It allows flexible time-window coverage, supports pagination with checkpointing, and can output three different JSONL views of the data (full, simplified, and curated). Customize the parameters and file outputs as needed for your data collection or analysis workflows.
