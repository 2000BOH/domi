# -*- coding: utf-8 -*-
"""
PDF 재추출 스크립트 v3
- 텍스트가 있는 섹션: 이미지 제거, 텍스트만 보존
- 이미지만 있는 섹션: 빈 페이지(거의 흰색)인지 검사 → 빈 페이지 삭제
- 텍스트 포매팅 개선
"""
import fitz
import os
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r"C:\2000\OneDrive\000_Download\domi"
output_json = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json"
public_img_dir = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\public\manuals"

os.makedirs(public_img_dir, exist_ok=True)

# 기존 이미지 정리
for f in os.listdir(public_img_dir):
    os.remove(os.path.join(public_img_dir, f))

NAV_CROP_Y = 65
SCALE = 2.5

# 메뉴 키워드 (상단 네비게이션에서 반복되는 텍스트)
MENU_KEYWORDS = {
    '홈', 'TV, WIFI', '고객센터', '도어락', '욕실', '누수',
    '냄새/해충', '냉난방기', '전기', '생활수칙', '응급상황', '도움말',
    '생활수', '냄새', '해충'
}

def clean_text(raw_text: str) -> str:
    """텍스트를 깔끔하게 포매팅"""
    lines = raw_text.split('\n')
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        # 메뉴 키워드, 1글자 이하 무의미 텍스트 필터링
        if not stripped or stripped in MENU_KEYWORDS or len(stripped) <= 1:
            continue
        clean_lines.append(stripped)
    
    if not clean_lines:
        return ""
    
    # 줄들을 문단으로 재구성
    formatted = format_paragraphs(clean_lines)
    return formatted


def format_paragraphs(lines: list) -> str:
    """Q&A, 제목, 안내문 등의 구조를 파악하여 포매팅"""
    result_parts = []
    
    for line in lines:
        # 이모지 제목 라인 (예: "🛁 욕실 FAQ", "⚡ 전기·콘센트 FAQ")
        if re.match(r'^[^\w\s].*(?:FAQ|안내|가이드|수칙|요약)', line):
            result_parts.append(f"\n{'─' * 30}\n{line}\n{'─' * 30}")
            continue
        
        # Q/A 패턴
        if re.match(r'^Q\d*[\.\)]', line) or line.startswith('Q.'):
            result_parts.append(f"\n❓ {line}")
            continue
        if re.match(r'^A[\.\)]', line) or line.startswith('A.'):
            result_parts.append(f"💡 {line}")
            continue
        
        # 섹션 제목 (이모지로 시작하는 줄)
        if re.match(r'^[⚠️🔥🧯💧🌍🧰📱⏱️🔒🏠📞🚨🆘]', line):
            result_parts.append(f"\n{line}")
            continue
        
        # 번호 매기기 패턴 (1), 2), 등)
        if re.match(r'^\d+[\)\.]', line):
            result_parts.append(f"\n{line}")
            continue
        
        # "바로 해보세요:" 등 액션 가이드
        if '바로 해보세요' in line:
            result_parts.append(f"  ✅ {line}")
            continue
        
        # "입주지원" 관련 조치
        if '입주지원' in line and '조치' in line:
            result_parts.append(f"  🔧 {line}")
            continue
        
        # "예상 시간" 라인
        if '예상 시간' in line:
            result_parts.append(f"  ⏱ {line}")
            continue
        
        # 일반 텍스트
        result_parts.append(line)
    
    return '\n'.join(result_parts).strip()


def is_blank_image(pix) -> bool:
    """이미지가 거의 흰색(빈 페이지)인지 확인"""
    # 이미지 샘플링하여 평균 밝기 체크
    samples = pix.samples
    total = len(samples)
    if total == 0:
        return True
    
    # 전체 픽셀의 평균값 계산 (빠른 방법: 일부만 샘플링)
    step = max(1, total // 10000)  # 최대 10000개 샘플
    bright_count = 0
    sample_count = 0
    
    for i in range(0, total, step * pix.n):
        if i + pix.n <= total:
            # RGB 평균값
            avg = sum(samples[i:i+min(3, pix.n)]) / min(3, pix.n)
            if avg > 245:  # 거의 흰색
                bright_count += 1
            sample_count += 1
    
    if sample_count == 0:
        return True
    
    white_ratio = bright_count / sample_count
    return white_ratio > 0.95  # 95% 이상이 흰색이면 빈 페이지


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
    
    sections = []
    
    for page_num, page in enumerate(doc):
        page_w = page.rect.width
        page_h = page.rect.height
        content_rect = fitz.Rect(0, NAV_CROP_Y, page_w, page_h - 5)
        
        # 텍스트 추출 및 정리
        raw_text = page.get_text("text", clip=content_rect).strip()
        clean = clean_text(raw_text)
        
        # 이미지 포함 여부 확인
        blocks = page.get_text("dict", clip=content_rect)["blocks"]
        has_image_block = any(b["type"] == 1 for b in blocks)
        has_embedded = len(page.get_images()) > 0
        has_visual = has_image_block or has_embedded
        
        # === 핵심 로직 ===
        # 케이스 1: 텍스트가 충분히 있는 경우 → 텍스트만, 이미지 불필요
        if len(clean) > 20:
            sections.append({
                "page": page_num + 1,
                "type": "text",
                "content": clean
            })
            print(f"  📝 {filename} p{page_num+1}: 텍스트 섹션 ({len(clean)}자)")
            continue
        
        # 케이스 2: 텍스트 없고 이미지만 있을 때 → 빈 페이지인지 체크
        if has_visual and len(clean) <= 20:
            mat = fitz.Matrix(SCALE, SCALE)
            pix = page.get_pixmap(matrix=mat, clip=content_rect)
            
            if is_blank_image(pix):
                print(f"  ⬜ {filename} p{page_num+1}: 빈 이미지 → 삭제")
                continue
            
            img_filename = f"{safe_name}_p{page_num+1}.png"
            img_filepath = os.path.join(public_img_dir, img_filename)
            pix.save(img_filepath)
            
            sections.append({
                "page": page_num + 1,
                "type": "image",
                "content": f"/manuals/{img_filename}"
            })
            print(f"  🖼️ {filename} p{page_num+1}: 이미지 섹션")
            continue
        
        # 케이스 3: 아무 내용도 없음 → 스킵
        print(f"  ⏭️ {filename} p{page_num+1}: 콘텐츠 없음 → 스킵")
    
    if sections:
        results.append({
            "filename": filename,
            "category": category,
            "title": title,
            "sections": sections,
            "total_pages": len(sections)
        })
        print(f"✅ {title}: {len(sections)}개 섹션 저장\n")
    
    doc.close()

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n🎉 전체 {len(results)}개 매뉴얼 처리 완료")
