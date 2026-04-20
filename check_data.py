# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

data = json.load(open('src/data.json', encoding='utf-8'))
for d in data:
    print(f"\n=== {d['title']} ({len(d['sections'])} sections) ===")
    for s in d['sections']:
        txt_len = len(s['text']) if s['text'] else 0
        print(f"  p{s['page']}: text={txt_len}chars, has_diagram={s['has_diagram']}")
        if s['text']:
            preview = s['text'][:150].replace('\n', ' | ')
            print(f"    -> {preview}")
