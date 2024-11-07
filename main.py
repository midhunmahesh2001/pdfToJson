import fitz
import pdfplumber
import json
import re

pdf_path = 'chapter_14.pdf'
output_json_path = 'output_chapter_14.json'

json_data = {
    "chapter": [
        {
            "content": "",
            "chapternumber": [{"content": "Chapter Fourteen"}],
            "chaptertitle": [{"content": "\\section*{SEMICONDUCTOR ELECTRONICS: MATERIALS, DEVICES AND SIMPLE CIRCUITS}"}],
            "section": []
        }
    ]
}

pdf_text = []
with fitz.open(pdf_path) as pdf:
    for page in pdf:
        pdf_text.append(page.get_text())

full_text = ''.join(pdf_text)

section_pattern = re.compile(r'(\d+\.\d+)\s+([A-Z\s]+)\n')
equation_pattern = re.compile(r'\((.*?)\)')
figure_pattern = re.compile(r'(FIGURE\s+\d+\.\d+)')
bullet_pattern = re.compile(r'^\s*[-•]\s+(.*)', re.MULTILINE)

sections = []
for match in section_pattern.finditer(full_text):
    section_title = match.group(2)
    section_number = match.group(1)
    
    start_index = match.end()
    end_index = section_pattern.search(full_text, start_index)
    if end_index:
        section_content = full_text[start_index:end_index.start()]
    else:
        section_content = full_text[start_index:]
    
    section_content = equation_pattern.sub(r'\\(\1\\)', section_content)
    section_content = figure_pattern.sub(r'<figure>\1</figure>', section_content)

    bullet_points = bullet_pattern.findall(section_content)
    if bullet_points:
        bullet_json = [{"bullet": point.strip()} for point in bullet_points]
        section_json = {
            "sectionnumber": [{"content": section_number}],
            "sectiontitle": [{"content": f"\\subsection*{{{section_number} {section_title}}}"}],
            "content": section_content,
            "bullets": bullet_json
        }
    else:
        section_json = {
            "sectionnumber": [{"content": section_number}],
            "sectiontitle": [{"content": f"\\subsection*{{{section_number} {section_title}}}"}],
            "content": section_content
        }
    
    sections.append(section_json)

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            
            table_json = [{"row": row} for row in table]
            sections.append({"table": table_json})

json_data['chapter'][0]['section'] = sections

with open(output_json_path, 'w') as f:
    json.dump(json_data, f, indent=4)

print("Structured JSON file created.")
