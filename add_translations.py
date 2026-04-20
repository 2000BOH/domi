# -*- coding: utf-8 -*-
"""
bilingual data generator: 기존 data.json을 읽고 영어 번역을 추가하여 저장
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# ── 도메인 특화 한→영 번역 사전 ──
SENTENCE_MAP = {
    # ── 공통 구조 ──
    '바로 해보세요:': 'Quick fix:',
    '입주지원센터 및 호텔 조치:': 'Support Center / Hotel action:',
    '입주지원센터 조치:': 'Support Center action:',
    '입주지원 / 호텔 조치:': 'Support / Hotel action:',
    '입주지원 / 호텔 조치 :': 'Support / Hotel action:',
    '입주지원센터 및 호텔 조치 :': 'Support Center / Hotel action:',
    '예상 시간:': 'Est. time:',
    '긴급 안내': '⚠️ Emergency Notice',
    '정책:': 'Policy:',
    '운영 안내': 'Operating Hours',
    '프런트: 24시간': 'Front Desk: 24 hours',
    '안전 & 이용 가이드 한 줄 요약': 'Safety & Usage Guide Summary',

    # ── TV, WIFI ──
    'TV , WIFI': 'TV & WiFi',
    'TV, WIFI FAQ': 'TV & WiFi FAQ',
    'WIFI(와이파이) FAQ': 'WiFi FAQ',
    'TV가 안 나와요': "TV won't turn on",
    'TV 채널이 안 바뀌어요': "Can't change TV channels",
    'TV에서 소리가 안 나요': "No sound from TV",
    'WiFi가 안 잡혀요': "Can't connect to WiFi",
    'WiFi가 느려요': 'WiFi is slow',
    'WiFi 비밀번호를 모르겠어요': "I don't know the WiFi password",
    '블루투스로 TV에 연결하고 싶어요': 'I want to connect to TV via Bluetooth',
    'TV에서 넷플릭스/유튜브를 보고 싶어요': 'I want to watch Netflix/YouTube on TV',
    '리모컨이 작동하지 않아요': "Remote control won't work",
    '리모컨 배터리를 교체해 주세요': 'Please replace the remote batteries',

    # ── 냉난방기 ──
    '냉난방기 FAQ': 'HVAC FAQ',
    '에어컨이 안 나와요': "AC won't turn on",
    '히터가 안 나와요': "Heater won't turn on",
    '자꾸 꺼지거나 약해졌다 강해져요': 'It keeps turning off or fluctuating',
    '실내기에서 물방울/물 떨어짐이 있어요': 'Water dripping from indoor unit',
    '냄새가 나요': 'There is a bad smell',
    '리모컨이 안 돼요': "Remote won't work",
    '소음이 심해요': 'Too much noise',
    '에코·타이머, 창문 센서, 설정 충돌일 수 있어요.': 'May be caused by eco-timer, window sensor, or settings conflict.',
    '응축수 배수(드레인) 막힘·결로 가능.': 'Possible drain blockage or condensation.',
    '타이머/에코 OFF, 리모컨 건전지 교체, 창문 완전 닫힘 확인.': 'Turn off timer/eco mode, replace remote batteries, ensure window is fully closed.',
    '송풍(팬) 가동 후 재확인.': 'Run fan mode and recheck.',
    '컨트롤러 재설정, 센서 점검.': 'Reset controller, inspect sensors.',
    '드레인·트레이 흡수·세척/정비·단열·기울기': 'Drain/tray cleaning, maintenance, insulation, leveling',

    # ── 누수 ──
    '누수 FAQ': 'Water Leak FAQ',
    '천장에서 물이 떨어져요': 'Water dripping from ceiling',
    '벽이 축축해요/곰팡이가 생겨요': 'Walls are damp / mold is growing',
    '바닥에 물이 고여요': 'Water pooling on floor',
    '수도(싱크) 아래에서 물이 새요': 'Water leaking under sink',
    '창문 주위로 물이 들어와요': 'Water coming in around window',
    '온수가 안 나와요': "Hot water won't come out",
    '수압이 약해요': 'Water pressure is low',
    '상층 배관·방수층 파손 가능. 천장 마감 손상 여부 확인.': 'Possible upper floor pipe/waterproof layer damage. Check ceiling finish.',
    '환기 부족 또는 외벽 단열 불량 가능.': 'Possible insufficient ventilation or poor wall insulation.',

    # ── 도어락 ──
    '도어락 FAQ': 'Door Lock FAQ',
    '문이 안 열려요': "Door won't open",
    '도어락 비밀번호를 변경하고 싶어요': 'I want to change the door lock password',
    '도어락 배터리가 나갔어요': 'Door lock battery is dead',
    '문이 잠기지 않아요': "Door won't lock",
    '도어락에서 경고음이 나요': 'Door lock is beeping/warning',
    '카드키가 안 돼요': "Key card won't work",
    '비밀번호를 분실했어요': 'I forgot my password',
    '비밀번호 재설정.': 'Password reset.',
    '인적사항 확인 후 재설정': 'Reset after identity verification',

    # ── 욕실 ──
    '욕실 FAQ': 'Bathroom FAQ',
    '욕실에서 냄새가 나요': 'Bathroom smells bad',
    '배수가 안 돼요/느려요': "Drain won't work / drains slowly",
    '변기가 막히거나 물이 계속 흘러요': 'Toilet is clogged or keeps running',
    '샤워 중 바닥에 물이 안 빠져요': "Water won't drain during shower",
    '샤워헤드에서 물이 잘 안 나와요': "Showerhead won't produce enough water",
    '바닥트랩 건조나 환기 문제입니다.': 'Floor trap dryness or ventilation issue.',
    '미끄럼 사고에 주의하세요.': 'Be careful of slipping accidents.',
    '배수구에 물 한 컵을 부어주세요': 'Pour a cup of water into the drain',
    '환풍기를 10분 이상 가동해주세요': 'Run the exhaust fan for at least 10 minutes',
    '물티슈·생리대 등 변기에 투입하지 말아주세요.': 'Do not flush wet wipes or sanitary products.',
    '바닥이 젖어 있으면 미끄럼 주의': 'Caution: slippery when wet',
    '변기에는 물티슈·위생용품 투입 금지': 'Do not flush wipes or hygiene products',
    '샤워 후 환풍기 10분 추가 가동 권장': 'Run exhaust fan 10 min after showering',

    # ── 전기 ──
    '전기·콘센트 FAQ': 'Electrical & Outlet FAQ',
    '전기가 안 켜져요': "Power won't turn on",
    '콘센트가 작동하지 않아요': "Outlet won't work",
    '차단기가 내려갔어요(트립)': 'Circuit breaker tripped',
    '조명이 깜박여요': 'Lights are flickering',
    '멀티탭/드라이기 사용 시 차단기가 내려가요': 'Breaker trips when using power strip/dryer',
    '감전 느낌/정전기가 심해요': 'Feeling electric shock / static',
    '개인 전열기기(전기히터·전기포트 등) 사용 가능한가요?': 'Can I use personal heating appliances?',
    '객실/층 정전이 발생했어요': 'Power outage in room/floor',
    '고출력 난방·취사기기는 화재·과부하 위험으로 반입·사용 제한됩니다.': 'High-power heating/cooking appliances are restricted due to fire/overload risk.',
    '젖은 손/바닥에서는 플러그 탈·부착 금지': 'Do not plug/unplug with wet hands or on wet floor',
    '전기 차단 상태일 수 있어요.': 'Power may be switched off.',
    '카드키 투입구에 카드 삽입 후 확인해주세요.': 'Insert your key card into the card slot and check.',

    # ── 냄새/해충 ──
    '냄새 & 🪲 해충 FAQ': 'Odor & Pest FAQ',
    '냄새(악취) Q&A': 'Odor Q&A',
    '해충(벌레) Q&A': 'Pest Q&A',
    '가스 냄새, 타는 냄새, 전기 스파크가 느껴지면 즉시 해당 차수 관리사무소, 입주지원센터 로 연락해주세요.': 'If you smell gas, burning, or electrical sparks, contact the management office or Support Center immediately.',
    '몸이 어지럽거나 두통·자극 증상이 있으면 해당 공간 사용을 중지하고 창문 환기 후 대기해 주세요.': 'If you feel dizzy or have headache/irritation, stop using the space and ventilate.',
    '곰팡이 냄새가 나요': 'There is a mold/mildew smell',
    '음식·조리 냄새가 복도에 퍼져요': 'Food/cooking odor spreading to hallway',
    '담배 냄새가 들어와요': 'Cigarette smell coming in',
    '벌레가 보여요(바퀴·개미 등)': 'I see bugs (cockroaches, ants, etc.)',
    '모기가 많아요': 'Too many mosquitoes',
    '벌/말벌이 있어요': 'There are wasps/hornets',
    '드레인·배수구 건조 또는 이물 가능.': 'Drain may be dry or blocked with debris.',
    '실내 전 구역 금연입니다(전자담배 포함).': 'Smoking is prohibited indoors (including e-cigarettes).',

    # ── 응급상황 ──
    '기숙사 응급상황 FAQ': 'Dormitory Emergency FAQ',
    '생명 위급/화재/폭력:': 'Life-threatening/Fire/Violence:',
    '경보가 울리거나 연기가 보여요.': 'Alarm is sounding or smoke is visible.',
    '화재·연기·경보': 'Fire / Smoke / Alarm',
    '부상/응급 의료': 'Injury / Emergency Medical',
    '전기·가스·화학 냄새': 'Electrical / Gas / Chemical Odor',
    '정전': 'Power Outage',
    '지진(흔들림 체감)': 'Earthquake',
    '대량 누수·침수': 'Major Leak / Flooding',
    '개인 비상 키트(권장)': 'Personal Emergency Kit (Recommended)',
    '가스/타는 냄새가 나요.': 'I smell gas or something burning.',
    '콘센트 스파크/발열이 심해요.': 'Outlet is sparking/overheating.',
    '스위치·불꽃 사용 금지, 창문 환기, 가스밸브 잠금': 'Do not use switches/flames, ventilate, close gas valve',
    '119(화재·구급) / 112(경찰)': '119 (Fire/Ambulance) / 112 (Police)',
    '엎드리고-가리고-붙잡기(탁자 아래)': 'Drop-Cover-Hold On (under table)',
    '손전등·예비배터리, 작은 구급약, 마스크, 생수/간식, 개인 복용약, 호루라기': 'Flashlight, spare batteries, first aid kit, mask, water/snacks, personal medication, whistle',

    # ── 생활수칙 ──
    '표준 생활수칙': 'Standard Living Rules',
    '기본 원칙': 'Basic Principles',
    '서로 존중·배려하고, 공동체 규칙을 우선합니다.': 'Respect and care for each other; community rules come first.',
    '안전·청결·조용을 생활의 기본으로 지킵니다.': 'Safety, cleanliness, and quiet are basic principles.',
    '조용 시간': 'Quiet Hours',
    '취사·냄새': 'Cooking & Odor',
    '주방에서만 취사 허용, 조리 후 환기·원상복구.': 'Cooking allowed only in kitchen; ventilate and clean up after.',
    '금연·주류': 'No Smoking & Alcohol',
    '실내 전 구역 금연. 전자담배 포함.': 'No smoking in all indoor areas, including e-cigarettes.',
    '음주 후 과음·소란 금지.': 'No excessive drinking or noise after drinking.',
    '전기·가전': 'Electrical Appliances',
    '고출력 개인 전열기기(히터·전기레인지 등) 사용 금지.': 'High-power personal appliances (heaters, electric stoves, etc.) are prohibited.',
    '분리수거·쓰레기': 'Recycling & Waste',
    '택배·배달': 'Deliveries',
    '주차·자전거·PM(킥보드)': 'Parking / Bicycle / Scooter',
    '개인정보·촬영': 'Privacy & Recording',
    '타인 무단 촬영/녹음 금지.': 'Unauthorized photographing/recording of others is prohibited.',
    '주차등록은 입주시 블루오션 3차 3층 슈퍼파킹으로 방문하셔야 합니다.': 'For parking registration, visit Super Parking on 3F of Blue Ocean Phase 3 upon move-in.',

    # ── 도움말 ──
    '불편사항이나 건의사항이 있으신가요?': 'Any complaints or suggestions?',
    '보다 나은 서비스 제공을 위해 소중한 의견을 기다리고 있습니다.': 'We welcome your valuable feedback for better service.',
    '접수 채널': 'Contact Channels',
    '카카오톡 상담:': 'KakaoTalk:',
    '전화문의:': 'Phone inquiry:',
    '도움이 더 필요하신가요?': 'Need more help?',
    '입주지원 센터 :': 'Resident Support Center:',

    # ── 고객센터 ──
    '슬기로운': 'Smart',
    '블루오션  생활': 'Blue Ocean Life',
    '어떻게 도와드릴까요?': 'How can we help you?',
    '인스파이어 리조트 임직원 여러분의 슬기로운 블루오션 생활을 위해 ...': 'For a smart Blue Ocean life for Inspire Resort employees...',
    '아래 주제에 대해 간단히 도와드릴 수 있습니다.': 'We can help you with the topics below.',
}

# 일반 단어 사전 (문장 매칭 안 될 때 단어 단위 치환)
WORD_MAP = {
    '입주지원센터': 'Support Center',
    '입주지원': 'Resident Support',
    '프런트': 'Front Desk',
    '방재실': 'Fire Safety Office',
    '관리사무소': 'Management Office',
    '시설팀': 'Facilities Team',
    '호텔': 'Hotel',
    '객실': 'Room',
    '에어컨': 'Air Conditioner',
    '냉난방기': 'HVAC Unit',
    '리모컨': 'Remote Control',
    '도어락': 'Door Lock',
    '비밀번호': 'Password',
    '차단기': 'Circuit Breaker',
    '콘센트': 'Outlet',
    '멀티탭': 'Power Strip',
    '누수': 'Water Leak',
    '배수구': 'Drain',
    '환풍기': 'Exhaust Fan',
    '건전지': 'Battery',
    '욕실': 'Bathroom',
    '샤워': 'Shower',
    '변기': 'Toilet',
    '세면대': 'Sink',
    '조명': 'Lighting',
    '전구': 'Light Bulb',
    '카드키': 'Key Card',
    '분리수거': 'Recycling',
    '쓰레기': 'Trash',
    '택배': 'Package Delivery',
    '주차': 'Parking',
    '금연': 'No Smoking',
    '전자담배': 'E-cigarette',
    '소란': 'Disturbance',
    '취사': 'Cooking',
    '환기': 'Ventilation',
    '교체': 'Replacement',
    '점검': 'Inspection',
    '접수': 'Submit/Report',
    '연락': 'Contact',
    '확인': 'Check',
    '가동': 'Operate',
    '재설정': 'Reset',
    '평일': 'Weekdays',
    '토요일': 'Saturday',
    '주말': 'Weekend',
    '화재': 'Fire',
    '대피': 'Evacuate',
    '신고': 'Report',
    '즉시': 'Immediately',
    '금지': 'Prohibited',
    '권장': 'Recommended',
    '엘리베이터': 'Elevator',
    '계단': 'Stairs',
    '입주민': 'Residents',
    '입주': 'Move-in',
    '퇴실': 'Move-out',
    '매트리스': 'Mattress',
}

def translate_line(line: str) -> str:
    """한 라인을 영어로 번역"""
    stripped = line.strip()
    if not stripped:
        return line
    
    # 1) 전체 문장 매칭 시도
    for ko, en in SENTENCE_MAP.items():
        if ko in stripped:
            stripped = stripped.replace(ko, en)
    
    # 2) 남은 한국어가 있으면 단어 단위 치환
    for ko, en in WORD_MAP.items():
        if ko in stripped:
            stripped = stripped.replace(ko, en)
    
    return stripped

def translate_content(text: str) -> str:
    """전체 텍스트를 줄 단위로 번역"""
    lines = text.split('\n')
    translated = [translate_line(l) for l in lines]
    return '\n'.join(translated)


# ── 메인 로직 ──
data_path = r"C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json"

with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 타이틀 번역
TITLE_MAP = {
    'TV, WIFI': 'TV & WiFi',
    '냄새_해충': 'Odor & Pest',
    '냉난방기': 'HVAC / Air Conditioning',
    '누수': 'Water Leak',
    '도어락': 'Door Lock',
    '도움말': 'Help & Contact',
    '생활수칙': 'Living Rules',
    '욕실': 'Bathroom',
    '응급상황': 'Emergency',
    '전기': 'Electrical',
    '고객센터_01': 'Customer Center',
}

for item in data:
    item['title_en'] = TITLE_MAP.get(item['title'], item['title'])
    
    for section in item['sections']:
        if section['type'] == 'text':
            section['content_en'] = translate_content(section['content'])

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 영어 번역 추가 완료")

# 결과 샘플 출력
for item in data:
    print(f"\n=== {item['title']} → {item['title_en']} ===")
    for s in item['sections'][:2]:
        if s['type'] == 'text' and 'content_en' in s:
            preview = s['content_en'][:200].replace('\n', ' | ')
            print(f"  EN: {preview}")
