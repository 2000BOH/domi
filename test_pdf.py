import fitz
import sys

filename = r"C:\2000\OneDrive\000_Download\domi\고객센터 - 도어락.pdf"
doc = fitz.open(filename)

for page_num, page in enumerate(doc):
    print(f"--- PAGE {page_num} ---")
    
    # Text blocks
    blocks = page.get_text("blocks")
    for b in blocks:
        # b = x0, y0, x1, y1, "text", block_no, block_type
        print(f"Block: x0={b[0]:.1f}, y0={b[1]:.1f}, y1={b[3]:.1f}, type={b[6]}")
        text = b[4].strip()
        print(f"Text: {repr(text[:50])}")
        
    # Images
    images = page.get_images()
    print(f"Images count: {len(images)}")
    for img in images:
        print(f"Image: {img}")

    if page_num > 1:
        break
