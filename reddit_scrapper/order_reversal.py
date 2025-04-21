import sys
import json

def main():
    # Check for proper number of arguments
    if len(sys.argv) != 2:
        print("Usage: python order_reversal.py <jsonl_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read file and validate each non-empty JSON line
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error: line {line_number} is not valid JSON.")
                sys.exit(1)
            # Check that the record contains all required keys
            for key in ["id", "domain", "title", "url"]:
                if key not in record:
                    print(f"Error: line {line_number} does not contain required key '{key}'.")
                    sys.exit(1)
            records.append(record)

    # Reverse the order of records
    reversed_records = list(reversed(records))
    total_records = len(reversed_records)

    # Reassign new ids:
    # According to the instructions, the new id of a record is defined as:
    #    new id = original file count + 1 - original id
    # Since the file is originally sorted with ascending id (1, 2, ..., N)
    # and we have reversed that order, the easiest way is to assign new id sequentially.
    # The record that was originally last (old id = total_records) will get new id = 1,
    # and the one that was originally first (old id = 1) will get new id = total_records.
    for index, record in enumerate(reversed_records):
        record["id"] = index + 1

    # Overwrite the original file with the new reversed output
    with open(file_path, 'w', encoding='utf-8') as f:
        for record in reversed_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    main()
