# scripts/generate_html.py
import pandas as pd
import html
import argparse
import sys

def generate_html(input_tsv, output_html, doc_title, doc_subtitle):
    try:
        df = pd.read_csv(input_tsv, sep='\t')
        print(f"Shape of dataset '{input_tsv}':", df.shape)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Auto-detect if the Russian translation column exists
    has_russian = 'Russian' in df.columns

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 15mm 15mm 15mm 15mm;
        @bottom-left {{
            content: "© Oxford University Press";
            font-size: 7pt;
            color: #666;
            font-family: "DejaVu Sans", "Liberation Sans", "Helvetica Neue", Arial, sans-serif;
            margin-bottom: 5mm;
        }}
        @bottom-right {{
            content: counter(page) " / " counter(pages);
            font-size: 7pt;
            color: #666;
            font-family: "DejaVu Sans", "Liberation Sans", "Helvetica Neue", Arial, sans-serif;
            margin-bottom: 5mm;
        }}
    }}
    body {{
        font-family: "DejaVu Sans", "Liberation Sans", "Helvetica Neue", Arial, sans-serif;
        font-size: 7.5pt;
        color: #333;
        line-height: 1.15;
        margin: 0;
        padding: 0;
    }}
    .header {{
        margin-bottom: 3mm;
    }}
    .title {{
        color: #195b98;
        font-size: 26pt;
        font-weight: normal;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
        font-family: "DejaVu Serif", "Liberation Serif", Georgia, serif;
    }}
    .subtitle {{
        color: #555;
        font-size: 9pt;
        font-style: italic;
        margin: 0 0 10px 0;
    }}
    .divider {{
        border-top: 1.5px solid #000;
        margin-bottom: 12px;
    }}
    .content {{
        column-count: 3;
        column-gap: 20px;
    }}
    .entry {{
        margin-bottom: 1.5px;
        page-break-inside: avoid;
        text-indent: -10px;
        padding-left: 10px;
    }}
    .word {{
        color: #000;
        font-weight: bold;
    }}
    .pos {{
        color: #555;
        font-style: italic;
        margin-left: 3px;
    }}
    .level {{
        color: #777;
        margin-left: 3px;
    }}
    .trans {{
        color: #195b98;
        margin-left: 3px;
    }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">{html.escape(doc_title)}</div>
        <div class="subtitle">{html.escape(doc_subtitle)}</div>
        <div class="divider"></div>
    </div>
    <div class="content">
"""

    count = 0
    for _, row in df.iterrows():
        # Prefer Annotation over Word if available
        if 'Annotation' in row and pd.notna(row['Annotation']):
            word = str(row['Annotation'])
        elif 'Word' in row and pd.notna(row['Word']):
            word = str(row['Word'])
        else:
            word = ""
            
        pos = str(row['Part of Speech']) if 'Part of Speech' in row and pd.notna(row['Part of Speech']) else ""
        lvl = str(row['Level']) if 'Level' in row and pd.notna(row['Level']) else ""
        
        word_safe = html.escape(word)
        pos_safe = html.escape(pos)
        lvl_safe = html.escape(lvl)
        
        entry_html = f'<span class="word">{word_safe}</span> <span class="pos">{pos_safe}</span> <span class="level">{lvl_safe}</span>'
        
        # Append translation only if applicable
        if has_russian:
            trans = str(row['Russian']) if pd.notna(row['Russian']) else ""
            if trans:
                entry_html += f' <span class="trans">{html.escape(trans)}</span>'
        
        html_content += f'        <div class="entry">{entry_html}</div>\n'
        count += 1

    html_content += """    </div>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML generated successfully with {count} entries -> {output_html}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Oxford HTML dictionary from TSV.")
    parser.add_argument("input_tsv", help="Input TSV file path")
    parser.add_argument("output_html", help="Output HTML file path")
    parser.add_argument("--title", default="Oxford 3000", help="Title of the document")
    parser.add_argument("--subtitle", 
                        default="The Oxford 3000 is a core word list for learners of English.",
                        help="Subtitle of the document")
    
    args = parser.parse_args()
    generate_html(args.input_tsv, args.output_html, args.title, args.subtitle)
