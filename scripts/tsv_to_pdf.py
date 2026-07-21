import pandas as pd
from weasyprint import HTML
import html

# --- Configuration ---
tsv_filename = 'your_input_dictionary.tsv'
html_filename = 'dictionary_output.html'
pdf_filename = 'dictionary_output.pdf'
doc_title = "Dictionary Title"
doc_subtitle = "Dictionary description and level information."
copyright_text = "© Your Copyright Info"

# --- Read Data ---
df = pd.read_csv(tsv_filename, sep='\t')

# --- Build HTML & CSS ---
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 15mm;
        @bottom-left {{
            content: "{copyright_text}";
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
        <div class="title">{doc_title}</div>
        <div class="subtitle">{doc_subtitle}</div>
        <div class="divider"></div>
    </div>
    <div class="content">
"""

# --- Process Data Rows ---
for _, row in df.iterrows():
    # Use 'Annotation' if available, fallback to 'Word'
    if 'Annotation' in row and pd.notna(row['Annotation']):
        word = str(row['Annotation'])
    elif 'Word' in row and pd.notna(row['Word']):
        word = str(row['Word'])
    else:
        word = ""
        
    pos = str(row['Part of Speech']) if 'Part of Speech' in row and pd.notna(row['Part of Speech']) else ""
    lvl = str(row['Level']) if 'Level' in row and pd.notna(row['Level']) else ""
    trans = str(row['Russian']) if 'Russian' in row and pd.notna(row['Russian']) else ""
    
    word_safe = html.escape(word)
    pos_safe = html.escape(pos)
    lvl_safe = html.escape(lvl)
    trans_safe = html.escape(trans)
    
    trans_html = f'<span class="trans">{trans_safe}</span>' if trans_safe else ''
    
    html_content += f'<div class="entry"><span class="word">{word_safe}</span><span class="pos">{pos_safe}</span><span class="level">{lvl_safe}</span>{trans_html}</div>\n'

html_content += """
    </div>
</body>
</html>
"""

# --- Save and Render ---
with open(html_filename, "w", encoding="utf-8") as f:
    f.write(html_content)

try:
    HTML(html_filename).write_pdf(pdf_filename)
    print(f"PDF generated successfully: {pdf_filename}")
except Exception as e:
    print(f"Error generating PDF: {e}")
