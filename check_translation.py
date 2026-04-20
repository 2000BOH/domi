# -*- coding: utf-8 -*-
"""번역 누락 확인 스크립트"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open(r'C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json', encoding='utf-8'))

# 한글이 포함된 영어 번역 라인 찾기
korean_pattern = re.compile(r'[가-힣]+')

for item in data:
    for sIdx, section in enumerate(item['sections']):
        if section['type'] != 'text' or 'content_en' not in section:
            continue
        
        lines = section['content_en'].split('\n')
        for lIdx, line in enumerate(lines):
            korean_words = korean_pattern.findall(line)
            if korean_words:
                print(f"[{item['title']}] s{sIdx} L{lIdx}: {line.strip()[:120]}")
                print(f"  Korean words: {', '.join(korean_words[:10])}")
                print()
