import pandas as pd
import html

# Re-read the base German TSV file requested by the user
tsv_filename = '20260716200932-goethe-german-5000.de.tsv'
df = pd.read_csv(tsv_filename, sep='\t')
print("Shape of original dataset:", df.shape)

html_filename = 'goethe_german_5000.html'

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 15mm 15mm 15mm 15mm;
        @bottom-left {{
            content: "© Goethe-Institut";
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
        <div class="title">Goethe German 5000</div>
        <div class="subtitle">The Goethe German 5000 is a core word list for learners of German, organized by frequency, from A1 to C1 level.</div>
        <div class="divider"></div>
    </div>
    <div class="content">
"""

count = 0
for _, row in df.iterrows():
    word = str(row['Annotation']) if pd.notna(row['Annotation']) else str(row['Word']) if pd.notna(row['Word']) else ""
    pos = str(row['Part of Speech']) if pd.notna(row['Part of Speech']) else ""
    lvl = str(row['Level']) if pd.notna(row['Level']) else ""
    
    word_safe = html.escape(word)
    pos_safe = html.escape(pos)
    lvl_safe = html.escape(lvl)
    
    html_content += f'<div class="entry"><span class="word">{word_safe}</span><span class="pos">{pos_safe}</span><span class="level">{lvl_safe}</span></div>\n'
    count += 1

html_content += """
    </div>
</body>
</html>
"""

with open(html_filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML Generated with {count} entries.")
