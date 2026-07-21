import urllib.request
import urllib.parse
import json
import time
import os
import sys
import argparse

def translate_batch(words, source_lang, target_lang):
    text = "\n".join(words)
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q=' + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            translated = ""
            for block in data[0]:
                if block[0]:
                    translated += block[0]
            # Strip trailing newlines to avoid extra empty element at the end
            return [w.strip() for w in translated.strip('\n').split('\n')]
    except Exception as e:
        print("Error:", e)
        return ["" for _ in words]

def main():
    parser = argparse.ArgumentParser(description="Translate a column in a TSV file using Google Translate GTX API.")
    parser.add_argument("file", help="Path to TSV file")
    parser.add_argument("--source", default="en", help="Source language code")
    parser.add_argument("--target", default="ru", help="Target language code")
    parser.add_argument("--col", type=int, default=0, help="0-based index of the column to translate")
    parser.add_argument("--out-col", type=str, default="Russian", help="Header name for the output column")
    args = parser.parse_args()

    file_path = args.file
    out_path = file_path + '.gtx.tmp'

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = lines[0].strip('\n').split('\t')
    if args.out_col not in header:
        header.append(args.out_col)
    
    out_col_idx = header.index(args.out_col)

    rows = [line.strip('\n').split('\t') for line in lines[1:]]
    words = []
    for r in rows:
        words.append(r[args.col] if len(r) > args.col else "")

    batch_size = 50
    translated_words = []

    print(f"Starting translation of {len(words)} rows...")
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        res = translate_batch(batch, args.source, args.target)
        
        if len(res) < len(batch):
            res.extend([""] * (len(batch) - len(res)))
        elif len(res) > len(batch):
            res = res[:len(batch)]
            
        translated_words.extend(res)
        sys.stdout.write(f"\rTranslated {min(i+batch_size, len(words))}/{len(words)}")
        sys.stdout.flush()
        time.sleep(0.5)

    print("\nWriting file...")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\t'.join(header) + '\n')
        for i, row in enumerate(rows):
            ru = translated_words[i] if i < len(translated_words) else ""
            if len(row) <= out_col_idx:
                row.extend([''] * (out_col_idx - len(row) + 1))
            row[out_col_idx] = ru
            f.write('\t'.join(row) + '\n')

    os.replace(out_path, file_path)
    print("Done")

if __name__ == "__main__":
    main()
