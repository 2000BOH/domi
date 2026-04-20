# -*- coding: utf-8 -*-
import fitz
import os
import json
import sys

# 윈도우 콘솔 인코딩 이슈 방지
sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r"C:\2000\OneDrive\000_Download\domi"
output_json = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json"
public_img_dir = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\public\manuals"

os.makedirs(public_img_dir, exist_ok=True)

# 기존 이미지 정리
for f in os.listdir(public_img_dir):
    os.remove(os.path.join(public_img_dir, f))

NAV_CROP_Y = 65  # 상단 네비게이션 메뉴 잘라낼 Y좌표 (pt 단위)
SCALE = 2.5      # 고해상도 렌더링 (모바일에서 선명하게)

results = []

for filename in sorted(os.listdir(pdf_dir)):
    if not filename.endswith(".pdf"):
        continue
    
    filepath = os.path.join(pdf_dir, filename)
    doc = fitz.open(filepath)
    
    name_no_ext = os.path.splitext(filename)[0]
    safe_name = name_no_ext.replace(' ', '_').replace(',', '')
    
    if " - " in name_no_ext:
        parts = name_no_ext.split(" - ")
        category = parts[0].strip()
        title = parts[1].strip()
    else:
        category = "기타"
        title = name_no_ext
    
    sections = []  # 각 페이지별 추출 결과
    
    for page_num, page in enumerate(doc):
        page_w = page.rect.width
        page_h = page.rect.height
        
        # 본문 영역만 클리핑 (상단 메뉴 제거, 하단 약간 여백 제거)
        content_rect = fitz.Rect(0, NAV_CROP_Y, page_w, page_h - 5)
        
        # 해당 영역의 텍스트 추출
        text_in_content = page.get_text("text", clip=content_rect).strip()
        
        # 해당 영역에 이미지가 있는지 확인
        blocks = page.get_text("dict", clip=content_rect)["blocks"]
        has_image_block = any(b["type"] == 1 for b in blocks)
        has_embedded_image = len(page.get_images()) > 0
        
        # 본문에 의미 있는 내용이 있는지 판단
        # 상단 메뉴 텍스트들을 필터링 (반복되는 메뉴 항목 제거)
        menu_keywords = ['홈', 'TV, WIFI', '고객센터', '도어락', '욕실', '누수', 
                         '냄새/해충', '냉난방기', '전기', '생활수칙', '응급상황', '도움말']
        
        clean_lines = []
        for line in text_in_content.split('\n'):
            stripped = line.strip()
            if stripped and stripped not in menu_keywords and len(stripped) > 1:
                clean_lines.append(stripped)
        
        clean_text = '\n'.join(clean_lines).strip()
        
        # 페이지에 실질적 콘텐츠가 있는 경우만 처리
        if has_image_block or has_embedded_image or len(clean_text) > 10:
            # 본문 영역만 이미지로 렌더링
            mat = fitz.Matrix(SCALE, SCALE)
            clip_rect = content_rect
            pix = page.get_pixmap(matrix=mat, clip=clip_rect)
            
            img_filename = f"{safe_name}_p{page_num+1}.png"
            img_filepath = os.path.join(public_img_dir, img_filename)
            pix.save(img_filepath)
            
            section = {
                "page": page_num + 1,
                "text": clean_text if clean_text else None,
                "image": f"/manuals/{img_filename}",
                "has_diagram": has_image_block or has_embedded_image
            }
            sections.append(section)
            print(f"  ✅ {filename} p{page_num+1}: text={len(clean_text)}chars, img={'Y' if has_image_block or has_embedded_image else 'N'}")
        else:
            print(f"  ⏭️ {filename} p{page_num+1}: 빈 페이지 (스킵)")
    
    results.append({
        "filename": filename,
        "category": category,
        "title": title,
        "sections": sections,
        "total_pages": len(sections)
    })
    
    print(f"📄 {title}: {len(sections)}개 섹션 추출 완료")
    doc.close()

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ 전체 {len(results)}개 매뉴얼 처리 완료 → {output_json}")
