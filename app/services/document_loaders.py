# document_loaders.py
import os
from pdfminer.high_level import extract_text as extract_text_from_pdf
from docx import Document
from bs4 import BeautifulSoup
import markdown

def load_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_md(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    # Convert markdown to HTML then extract plain text
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, 'html.parser')
    print(soup.get_text())
    return soup.get_text()

def load_pdf(file_path: str) -> str:
    return extract_text_from_pdf(file_path)

def load_doc(file_path: str) -> str:
    doc = Document(file_path)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

def load_html(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return load_txt(file_path)
    elif ext == '.md':
        return load_md(file_path)
    elif ext == '.pdf':
        return load_pdf(file_path)
    elif ext in ['.doc', '.docx']:
        return load_doc(file_path)
    elif ext in ['.html', '.htm']:
        return load_html(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
