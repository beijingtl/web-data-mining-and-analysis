import os
import zipfile
import xml.etree.ElementTree as ET
import glob
import re

def extract_text_from_docx(docx_path):
    text = []
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            for p in tree.findall('.//w:p', namespaces=ns):
                paragraph_text = []
                for t in p.findall('.//w:t', namespaces=ns):
                    if t.text:
                        paragraph_text.append(t.text)
                if paragraph_text:
                    text.append(''.join(paragraph_text))
    except Exception as e:
        print(f"Error reading {docx_path}: {e}")
    return '\n\n'.join(text)

def clean_toc(toc_text):
    cleaned_lines = []
    lines = toc_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove trailing dots and page numbers
        line = re.sub(r'[\.\s]+\d+$', '', line)
        line = re.sub(r'PAGEREF.*', '', line)
        line = re.sub(r'GOTOBUTTON.*', '', line)
        line = re.sub(r'HYPERLINK.*', '', line)
        line = re.sub(r'\s+', ' ', line)
        
        # Simple indentation based on heading numbers if possible, but bullet list is requested
        if line.startswith('第') or line.startswith('附录') or re.match(r'^\d', line) or len(line) > 1:
            cleaned_lines.append("- " + line)
    return '\n'.join(cleaned_lines)

def main():
    base_dir = r"D:\个人\04赚钱项目\02数据常青藤\blog_v2\docs\书籍git仓库\[书籍]网站数据挖掘与分析"
    materials_dir = os.path.join(base_dir, "README物料")
    escaped_materials_dir = glob.escape(materials_dir)

    # 1. Rename cover image
    img_files = glob.glob(os.path.join(escaped_materials_dir, "*.jpg")) + glob.glob(os.path.join(escaped_materials_dir, "*.png"))
    cover_image_name = "[书籍]网站数据挖掘与分析.jpg"
    cover_image_path = os.path.join(materials_dir, cover_image_name)

    for img in img_files:
        if os.path.basename(img) != cover_image_name:
            if not os.path.exists(cover_image_path):
                os.rename(img, cover_image_path)
            else:
                os.remove(img)  # If it already exists, remove duplicate
            break

    # 2. Read preface
    preface_files = glob.glob(os.path.join(escaped_materials_dir, "*前言*.docx"))
    preface_text = ""
    if preface_files:
        preface_text = extract_text_from_docx(preface_files[0])
    else:
        print("Warning: No preface file found!")

    # 3. Read and clean TOC
    toc_files = glob.glob(os.path.join(escaped_materials_dir, "*目录*.docx"))
    if not toc_files:
        toc_files = glob.glob(os.path.join(escaped_materials_dir, "*大纲*.docx"))

    toc_text = ""
    if toc_files:
        raw_toc = extract_text_from_docx(toc_files[0])
        toc_text = clean_toc(raw_toc)
    else:
        print("Warning: No TOC file found!")

    # 4. Generate README.md
    readme_content = f"""![封皮](README物料/{cover_image_name})

# [书籍]网站数据挖掘与分析

## 📖 前言与简介
{preface_text}

## 📑 目录
{toc_text}

## 💻 配套资源与附件
- **随书附件**: 本仓库 `随书附件/` 目录下包含了书中所涉及的所有代码、数据文件和配图。
- **联系与勘误**: 如果您在学习过程中发现任何问题或需要交流，欢迎提交 Issue。
"""

    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("Success: README.md has been generated.")

if __name__ == '__main__':
    main()
