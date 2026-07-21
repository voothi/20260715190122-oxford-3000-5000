import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Keep only the first comma-separated value in a specific column.")
    parser.add_argument("file", help="Path to TSV file")
    parser.add_argument("--col", type=str, required=True, help="Name of the column header to strip")
    args = parser.parse_args()

    file_path = args.file

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = lines[0].strip('\n').split('\t')
    if args.col not in header:
        print(f"Column '{args.col}' not found.")
        return
    
    col_idx = header.index(args.col)
    rows = [line.strip('\n').split('\t') for line in lines[1:]]

    for row in rows:
        if len(row) > col_idx:
            val = row[col_idx]
            if ',' in val:
                row[col_idx] = val.split(',')[0].strip()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(lines[0]) # write original header with its newline
        for row in rows:
            f.write('\t'.join(row) + '\n')

    print("Done")

if __name__ == "__main__":
    main()
