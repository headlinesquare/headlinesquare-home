# Order Reversal Script Documentation

This document describes the functionality, usage, design, and implementation details of the `order_reversal.py` script. The script is designed to process a JSON Lines (JSONL) file containing records, validate them, reverse their order, reassign their IDs accordingly, and then overwrite the original file with the new order.

---

## Table of Contents

1. [Overview](https://platform.openai.com/playground/prompts?models=o3-mini#overview)
2. [Prerequisites](https://platform.openai.com/playground/prompts?models=o3-mini#prerequisites)
3. [Usage](https://platform.openai.com/playground/prompts?models=o3-mini#usage)
4. [Script Workflow](https://platform.openai.com/playground/prompts?models=o3-mini#script-workflow)
   - [Command-Line Arguments](https://platform.openai.com/playground/prompts?models=o3-mini#command-line-arguments)
   - [Reading and Validating the Input File](https://platform.openai.com/playground/prompts?models=o3-mini#reading-and-validating-the-input-file)
   - [Reversing Records and Reassigning IDs](https://platform.openai.com/playground/prompts?models=o3-mini#reversing-records-and-reassigning-ids)
   - [Writing the Output](https://platform.openai.com/playground/prompts?models=o3-mini#writing-the-output)
5. [Error Handling](https://platform.openai.com/playground/prompts?models=o3-mini#error-handling)
6. [Assumptions and Notes](https://platform.openai.com/playground/prompts?models=o3-mini#assumptions-and-notes)
7. [Example](https://platform.openai.com/playground/prompts?models=o3-mini#example)
8. [Conclusion](https://platform.openai.com/playground/prompts?models=o3-mini#conclusion)

---

## Overview

The `order_reversal.py` script serves to reverse the order of records from a JSONL file and update their IDs. It ensures that:

- Each line in the input file is valid JSON.
- Each JSON record contains all the required keys.
- The record order is completely reversed.
- The IDs in the reversed output are reassigned sequentially starting from 1.

The new ID assignment rule is that the record which was originally last (assuming the original records are in ascending order of ID) will have the new ID `1`, the second last record will have the new ID `2`, and so on.

---

## Prerequisites

- **Python Environment:** Python 3.x must be installed.
- **Input File Format:** The input file must be in JSON Lines (JSONL) format, where each non-empty line is a valid JSON object.
- **Required Record Keys:** Each JSON object must contain the following keys:
  - `id`
  - `domain`
  - `title`
  - `url`

---

## Usage

Run the script from the command line by providing the JSONL file path as an argument:

```bash
python order_reversal.py <jsonl_file>
```

For example:

```bash
python order_reversal.py records.jsonl
```

If the number of arguments is incorrect, the script prints the usage instructions and exits.

---

## Script Workflow

### Command-Line Arguments

1. **Argument Validation:**
   - The script checks that exactly one argument (excluding the script name) is provided.
   - If the incorrect number of arguments is supplied, it prints:

1. - ```text
     Usage: python order_reversal.py <jsonl_file>
     ```
     
     and exits with an error code (`sys.exit(1)`).

### Reading and Validating the Input File

1. **File Reading:**
   
   - The script opens the provided file in read mode with `utf-8` encoding.
   - It iterates over each line of the file, keeping track of the line number (starting at 1).

2. **Line-by-Line Processing:**
   
   - **Skip Empty Lines:** Empty lines are ignored.
   - **JSON Parsing:** Each non-empty line is parsed using `json.loads()`.
     - If the line does not contain valid JSON, the script outputs an error message indicating the line number (e.g., `"Error: line 3 is not valid JSON."`) and exits.

3. **Record Validation:**
   
   - For every successfully parsed JSON object, the script checks for the presence of all required keys (`id`, `domain`, `title`, `url`).
   - If any of these keys is missing, an error message is printed (e.g., `"Error: line 4 does not contain required key 'url'."`) and the program exits.

4. **Record Collection:**
   
   - Validated records are appended to a list called `records`.

### Reversing Records and Reassigning IDs

1. **Reversing Order:**
   - The script reverses the order of the collected records using the built-in `reversed()` function, converting the result to a list `reversed_records`.
2. **Reassigning IDs:**
   - The new IDs are reassigned sequentially.
   - The first record in the reversed list is assigned an ID of `1`, the second an ID of `2`, and so on.
   - This is implemented with:
- ```python
  for index, record in enumerate(reversed_records):
      record["id"] = index + 1
  ```

- **Rationale:** The original instruction state that the new id should be computed as:
1. - ```text
     new id = original file count + 1 - original id
     ```
     
     Assuming the file originally holds records in ascending order (i.e., `1, 2, ..., N`), the reversal naturally results in the original last record (with id = N) getting `1`, and the original first record (with id = 1) getting `N`.

### Writing the Output

1. **Overwriting the File:**
   - The script opens the original file in write mode (using `utf-8` encoding). This causes the file to be overwritten.
   - It then writes each record from `reversed_records` as a JSON string with `ensure_ascii=False` to preserve any non-ASCII characters.
   - Each record is terminated with a newline character.
2. **Final Output:**
   - The output file will contain all the records in reversed order with updated IDs as described.

---

## Error Handling

- **Invalid Argument Count:** If the user does not provide exactly one argument, the script prints the usage instructions and exits.

- **File Reading/Parsing Errors:**
  
  - If any line in the file is not valid JSON, an error message specifying the line number is printed and the script exits.

- **Missing Keys in JSON Records:**
  
  - For each record, if any of the required keys (`id`, `domain`, `title`, `url`) is missing, the script prints an error message indicating the problematic line and exits immediately.

All error conditions result in an immediate termination of the script with a non-zero exit status.

---

## Assumptions and Notes

- The script assumes that the JSONL file is originally sorted with ascending IDs.
- The new ID reassignment logic directly maps to the reversal order. 
  The record originally at the end becomes the first (with ID 1) and the 
  record originally at the beginning becomes the last (with an ID equal to
   the total number of records).
- The entire contents of the input file are loaded into memory. This 
  approach is adequate for moderately sized files but may need adjustment 
  for very large datasets.

---

## Example

Given an input file `records.jsonl` with the following content:

```text
{"id": 1, "domain": "example.com", "title": "First Record", "url": "http://example.com/1"}
{"id": 2, "domain": "example.com", "title": "Second Record", "url": "http://example.com/2"}
{"id": 3, "domain": "example.com", "title": "Third Record", "url": "http://example.com/3"}
```

After running:

```bash
python order_reversal.py records.jsonl
```

The file `records.jsonl` will be overwritten with:

```text
{"id": 1, "domain": "example.com", "title": "Third Record", "url": "http://example.com/3"}
{"id": 2, "domain": "example.com", "title": "Second Record", "url": "http://example.com/2"}
{"id": 3, "domain": "example.com", "title": "First Record", "url": "http://example.com/1"}
```

---

## Conclusion

The `order_reversal.py` script offers a straightforward solution to reverse the order of JSONL records while ensuring data validity. By following the detailed steps of argument validation, file reading, record validation, order reversal, and ID reassignment, it ensures that the processed file meets the desired specifications. This documentation should help users understand how the script works and how to effectively use it in their workflows.
