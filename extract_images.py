import os
import json
import fitz # PyMuPDF

pdf_dir = r"C:\2000\OneDrive\000_Download\domi"
output_json = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json"
public_img_dir = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\public\manuals"

os.makedirs(public_img_dir, exist_ok=True)

results = []

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        filepath = os.path.join(pdf_dir, filename)
        try:
            doc = fitz.open(filepath)
            text_content = []
            image_paths = []
            
            name_no_ext = os.path.splitext(filename)[0]
            
            for page_num, page in enumerate(doc):
                # Render page to image (use a reasonable scaling for mobile readability, e.g. matrix = fitz.Matrix(2, 2))
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                
                img_filename = f"{name_no_ext.replace(' ', '_')}_page{page_num+1}.png"
                img_filepath = os.path.join(public_img_dir, img_filename)
                pix.save(img_filepath)
                image_paths.append(f"/manuals/{img_filename}")
                
                # Get text
                text_content.append(page.get_text())

            full_text = "\n".join(text_content).strip()
            
            if " - " in name_no_ext:
                parts = name_no_ext.split(" - ")
                category = parts[0].strip()
                title = parts[1].strip()
            else:
                category = "기타"
                title = name_no_ext

            results.append({
                "filename": filename,
                "category": category,
                "title": title,
                "raw_content": full_text,
                "images": image_paths
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Extracted pages as images to {public_img_dir}")
