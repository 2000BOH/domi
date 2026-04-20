import fitz
import os

pdf_dir = r"C:\2000\OneDrive\000_Download\domi"

# 모든 PDF 파일의 구조를 상세 분석
for filename in sorted(os.listdir(pdf_dir)):
    if not filename.endswith(".pdf"):
        continue
    filepath = os.path.join(pdf_dir, filename)
    doc = fitz.open(filepath)
    
    print(f"\n{'='*60}")
    print(f"FILE: {filename} ({len(doc)} pages)")
    print(f"{'='*60}")
    
    for page_num, page in enumerate(doc):
        print(f"\n  --- Page {page_num+1} ---")
        print(f"  Page size: {page.rect.width:.0f} x {page.rect.height:.0f}")
        
        # 텍스트 블록 분석
        blocks = page.get_text("dict")["blocks"]
        for b_idx, block in enumerate(blocks):
            if block["type"] == 0:  # text block
                for line in block.get("lines", []):
                    text = "".join([span["text"] for span in line["spans"]])
                    if text.strip():
                        y = line["bbox"][1]
                        font_size = line["spans"][0]["size"] if line["spans"] else 0
                        font_name = line["spans"][0]["font"] if line["spans"] else ""
                        print(f"  TEXT y={y:.0f} size={font_size:.1f} font={font_name}: {text.strip()[:80]}")
            elif block["type"] == 1:  # image block
                bbox = block["bbox"]
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                print(f"  IMAGE y={bbox[1]:.0f} size={w:.0f}x{h:.0f} at ({bbox[0]:.0f},{bbox[1]:.0f})-({bbox[2]:.0f},{bbox[3]:.0f})")
        
        # 임베디드 이미지 분석
        images = page.get_images()
        if images:
            for img in images:
                xref = img[0]
                print(f"  EMBEDDED_IMG xref={xref} w={img[2]} h={img[3]}")
        
        if page_num >= 3:
            print("  ... (이후 페이지 생략)")
            break
    
    doc.close()
