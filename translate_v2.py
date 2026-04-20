# -*- coding: utf-8 -*-
"""
완전 번역 스크립트 v2
- 기존 패턴 매칭 방식 대신, 줄 단위로 완전한 영어 문장으로 대체
- 매칭 안 되는 잔여 한글은 후처리로 제거/번역
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# ── 전체 문장 단위 번역 (가장 높은 우선순위) ──
FULL_LINE_MAP = {
    # 공통
    '분': 'min',
    '시간': 'hours',
    
    # 냄새/해충
    '🌬️ 냄새 & 🐜 해충 FAQ': '🌬️ Odor & 🐜 Pest FAQ',
    '냄새(악취) Q&A': 'Odor Q&A',
    '해충(벌레) Q&A': 'Pest Q&A',
    '가스 냄새, 타는 냄새, 전기 스파크가 느껴지면 즉시 해당 차수 관리사무소, 입주지원센터 로 연락해주세요.': 'If you smell gas, burning odor, or electrical sparks, immediately contact the management office or Resident Support Center.',
    '몸이 어지럽거나 두통·자극 증상이 있으면 해당 공간 사용을 중지하고 창문 환기 후 대기해 주세요.': 'If you feel dizzy or have headache/irritation symptoms, stop using the space and ventilate by opening windows.',
    'Q1. 욕실에서 냄새가 나요. 🤢': 'Q1. There is a bad smell in the bathroom. 🤢',
    'A. 바닥트랩 건조·배수구 이물·환기 문제일 수 있어요.': 'A. It may be due to dry floor trap, drain debris, or ventilation issues.',
    '바로 해보세요: 배수구에 물 한 컵 붓기 → 환풍기 10분 이상 가동.': 'Quick fix: Pour a cup of water into the drain → Run exhaust fan for 10+ minutes.',
    '입주지원센터 및 호텔 조치: 트랩 급수·배관 세척·환기팬 점검.': 'Support Center / Hotel action: Trap water supply, pipe cleaning, exhaust fan inspection.',
    'Q2. 방 안에서 곰팡이 냄새가 나요. 🏠': 'Q2. There is a mold smell in the room. 🏠',
    'A. 습기가 원인. 환기 부족·결로 가능.': 'A. Moisture is the cause. Possible lack of ventilation or condensation.',
    '바로 해보세요: 창문+환풍기로 공기순환, 옷장·신발장 문 열기.': 'Quick fix: Circulate air with windows + exhaust fan, open closets and shoe cabinets.',
    '입주지원센터 및 호텔 조치: 곰팡이 제거·방습 조치·벽지/실리콘 보수.': 'Support Center / Hotel action: Mold removal, moisture-proofing, wallpaper/silicone repair.',
    'Q3. 복도/다른 방에서 음식 냄새가 심하게 나요. 🍜': 'Q3. Strong food odor from hallway/other rooms. 🍜',
    'A. 공용 환기 불균형 또는 밀폐 부족.': 'A. Common ventilation imbalance or insufficient sealing.',
    '바로 해보세요: 내 방 문·창 밀폐. 강한 조리 중 환풍기 가동.': 'Quick fix: Seal your room door/windows. Run exhaust fan during cooking.',
    '입주지원센터 / 프런트 조치: 환기 시스템 점검·이웃 안내.': 'Support / Front Desk action: Ventilation system inspection, neighbor notification.',
    'Q4. 담배 / 전자담배 냄새가 들어와요. 🚭': 'Q4. Cigarette / e-cigarette smell coming in. 🚭',
    'A. 실내 흡연은 금지입니다(지정 흡연구역 이용).': 'A. Indoor smoking is prohibited (use designated smoking areas).',
    '바로 해보세요: 창 부분 환기, 문 하부 틈 확인.': 'Quick fix: Ventilate near windows, check gap under door.',
    '실내 전 구역 금연입니다(전자담배 포함). 흡연 적발 시 퇴실 조치가 될 수 있습니다.': 'Smoking is prohibited in all indoor areas (including e-cigarettes). Violations may result in eviction.',
    '입주지원센터 / 프런트 : 드레인 트레이 점검, 확인.': 'Support / Front Desk: Drain tray inspection, check.',
    'Q5. 벌레가 보여요(바퀴·개미 등). 🪲': 'Q5. I see bugs (cockroaches, ants, etc.). 🪲',
    'A. 외부 유입 또는 배수구·틈새 통한 진입 가능.': 'A. Possible entry from outside or through drains/gaps.',
    '바로 해보세요: 음식물 밀봉, 쓰레기 즉시 처리, 배수구에 물 부어두기.': 'Quick fix: Seal food, dispose trash immediately, pour water into drains.',
    '입주지원센터 및 호텔 조치: 해충 방제 접수 → 전문 방역 일정 안내.': 'Support Center / Hotel action: Pest control report → Professional pest treatment scheduled.',
    'Q6. 모기가 많아요. 🦟': 'Q6. Too many mosquitoes. 🦟',
    'A. 창문 틈이나 출입 시 유입.': 'A. Entry through window gaps or when opening doors.',
    '바로 해보세요: 방충망 닫힘 확인. 고인 물 제거.': 'Quick fix: Check that screen doors are closed. Remove standing water.',
    '입주지원센터 및 호텔 조치: 방충망 보수, 방역.': 'Support Center / Hotel action: Screen door repair, pest control.',
    'Q7. 벌/말벌이 있어요. 🐝': 'Q7. There are wasps/hornets. 🐝',
    'A. 직접 제거 금지. 알레르기 위험.': 'A. Do not remove yourself. Allergy risk.',
    '바로 해보세요: 자극하지 말고 창문 닫기. 즉시 프런트/입주지원센터에 연락.': 'Quick fix: Do not disturb them, close windows. Contact Front Desk/Support Center immediately.',
    '입주지원센터 및 호텔 조치: 전문 업체 투입 벌집 제거.': 'Support Center / Hotel action: Professional removal of wasp/hornet nest.',
    '음식물은 밀봉, 쓰레기는 바로 처리 → 해충 예방의 기본 🗑️': 'Seal food, dispose trash promptly → Basic pest prevention 🗑️',
    '배수구 '물 마름' 방지 = 악취 차단의 핵심 💧': "Prevent drain 'dry-out' = Key to blocking bad odors 💧",
    '곰팡이 의심 → 환기+건조가 먼저, 확산 전 접수 🌬️': 'Suspect mold → Ventilate + dry first, report before it spreads 🌬️',
    '벌·쏘임 위험 곤충은 절대 직접 제거 금지 🐝': 'Never remove stinging insects yourself 🐝',
    '📞 문의·신고': '📞 Inquiries & Reports',
    '입주지원 / 시설팀: (예: 평일 09:00–18:00, 토요일 10:00~17:00), 각 차수 방재실.': 'Resident Support / Facilities Team: Weekdays 09:00-18:00, Sat 10:00-17:00, Fire Safety Office.',
    
    # 냉난방기
    '❄️🌡️ 냉난방기 FAQ': '❄️🌡️ HVAC / Air Conditioning FAQ',
    '타는 냄새/연기, 전기 스파크, 물과 전기 혼재가 보이면 즉시 사용을 중지하고 각 차수 관리사무소(방재실), 입주지원센터/프런트로 연락해 주세요.': 'If you notice burning smell/smoke, electrical sparks, or water near electrical components, stop use immediately and contact Fire Safety Office / Support Center / Front Desk.',
    'Q1. 냉방(에어컨)이 안 나와요. ❄️': 'Q1. Air conditioning won\'t work. ❄️',
    'A. 전원·모드·온도 설정, 카드키 미투입 등 확인.': 'A. Check power, mode, temperature settings, and key card insertion.',
    '바로 해보세요: 카드키 투입 확인, 리모컨 모드→ "냉방/COOL", 설정온도를 현재 실온보다 낮게.': 'Quick fix: Check key card, set remote to "Cool" mode, set temp lower than room temp.',
    '입주지원센터 / 호텔 조치: 필터 세척, 냉매·실외기 점검.': 'Support / Hotel action: Filter cleaning, coolant & outdoor unit inspection.',
    'Q2. 난방(히터)이 안 나와요. 🔥': 'Q2. Heater won\'t turn on. 🔥',
    'A. 시스템 에어컨은 난방 모드 전환이 필요해요.': 'A. System AC needs mode switch to heating.',
    '바로 해보세요: 리모컨 모드→"난방/HEAT", 설정온도를 현재 실온보다 높게, 바람 방향 하향.': 'Quick fix: Set remote to "Heat" mode, set temp higher than room temp, direct airflow downward.',
    '입주지원센터 / 호텔 조치: 밸브·컨트롤러 확인, 난방 전환기(계절) 점검.': 'Support / Hotel action: Valve/controller check, seasonal heating system inspection.',
    'Q3. 자꾸 꺼지거나 약해졌다 강해져요. ⏱️': 'Q3. It keeps turning off or fluctuating. ⏱️',
    'A. 에코·타이머, 창문 센서, 설정 충돌일 수 있어요.': 'A. May be caused by eco/timer, window sensor, or settings conflict.',
    '바로 해보세요: 타이머/에코 OFF, 리모컨 건전지 교체, 창문 완전 닫힘 확인.': 'Quick fix: Turn off timer/eco, replace remote batteries, ensure windows fully closed.',
    '입주지원센터 / 호텔 조치: 컨트롤러 재설정, 센서 점검.': 'Support / Hotel action: Controller reset, sensor inspection.',
    'Q4. 실내기에서 물방울/물 떨어짐이 있어요. 💧': 'Q4. Water dripping from indoor unit. 💧',
    'A. 응축수 배수(드레인) 막힘·결로 가능.': 'A. Possible drain blockage or condensation.',
    '바로 해보세요: 송풍(팬) 가동 후 재확인.': 'Quick fix: Run fan mode and recheck.',
    '입주지원 / 호텔 조치: 드레인·트레이 흡수·세척/정비·단열·기울기': 'Support / Hotel action: Drain/tray cleaning, maintenance, insulation, leveling.',
    '에어컨 리모컨 안 될 때 → 건전지부터! 🔋': 'When AC remote won\'t work → Check batteries first! 🔋',
    '냉난방 전환에 시간이 걸릴 수 있어요 (기다려 주세요) ⏳': 'Heating/cooling switch may take time (please wait) ⏳',
    '물방울이 보이면 → 아래 수건 깔고 바로 접수 💧': 'If you see water drops → Place towel below and report immediately 💧',

    # 누수
    '💧 누수(물샘) FAQ': '💧 Water Leak FAQ',
    '천장·조명·콘센트 주변 물샘, 바닥 대량 침수는 즉시 각 차수 방재실/프런트로 연락 후 전기 접촉을 피해 주세요.': 'For water leaks near ceiling/lights/outlets or major floor flooding, contact Fire Safety Office/Front Desk immediately and avoid electrical contact.',
    'Q1. 천장에서 물이 떨어져요 / 천장에 얼룩이 생겨요. 💧': 'Q1. Water dripping from ceiling / ceiling stains. 💧',
    'A. 상층 배관·방수층 파손 가능. 천장 마감 손상 여부 확인.': 'A. Possible upper floor pipe/waterproof layer damage. Check ceiling finish.',
    '바로 해보세요: 전자장비를 물 떨어지는 곳에서 이동. 수건/양동이로 물 받기. 함부로 천장 건드리지 않기.': 'Quick fix: Move electronics away from leak. Catch water with towel/bucket. Do not touch ceiling.',
    '입주지원센터 및 호텔 조치: 상층 원인 조사, 배관 수리, 천장 건조·복구.': 'Support Center / Hotel action: Upper floor investigation, pipe repair, ceiling drying/restoration.',
    'Q2. 벽이 축축해요 / 곰팡이가 생겨요. 🧱🦠': 'Q2. Walls are damp / mold is growing. 🧱🦠',
    'A. 환기 부족 또는 외벽 단열 불량 가능.': 'A. Possible insufficient ventilation or poor wall insulation.',
    '바로 해보세요: 환기 자주 하기, 벽에서 가구 약간 띄우기(5cm). 결로면 마른 수건으로 물기 제거.': 'Quick fix: Ventilate frequently, keep furniture 5cm from walls. Wipe condensation with dry towel.',
    '입주지원센터 및 호텔 조치: 누수 원인 확인(배관 vs 결로), 곰팡이 제거·단열 보완.': 'Support Center / Hotel action: Identify cause (pipe vs condensation), mold removal, insulation improvement.',
    'Q3. 세면대/싱크대 아래에서 물이 새요. 🚰': 'Q3. Water leaking under sink/basin. 🚰',
    'A. 배수관 연결부 느슨·패킹 노후 가능.': 'A. Possible loose drain connection or worn gasket.',
    '바로 해보세요: 아래 수건 깔아 피해 최소화. 물 사용 중지 또는 밸브 잠금 (가능 시).': 'Quick fix: Place towel below to minimize damage. Stop water use or close valve if possible.',
    '입주지원센터 및 호텔 조치: 연결부 조임·패킹(가스켓) 교체, 필요 시 트랩 교체.': 'Support Center / Hotel action: Tighten connection, replace gasket, replace trap if needed.',
    'Q4. 변기 주변 바닥이 젖어요 / 탱크에서 물이 새는 것 같아요. 🚽': 'Q4. Floor wet around toilet / tank seems to be leaking. 🚽',
    'A. 베이스 실리콘·탱크 부속(플로트/플러퍼)·급수호스 이슈 가능.': 'A. Possible base silicone, tank parts (float/flapper), or supply hose issue.',
    '바로 해보세요: 변기 주변 물기 닦고, 급수밸브 잠금 시도(변기 아래 벽면).': 'Quick fix: Wipe water around toilet, try closing supply valve (on wall below toilet).',
    '입주지원센터 및 호텔 조치: 실리콘 재시공, 부속 교체, 호스 교체·방수 점검.': 'Support Center / Hotel action: Re-silicone, replace parts, hose replacement, waterproofing inspection.',
    'Q5. 창문 주위로 물이 스며들어요 (비 올 때/태풍). 🌧️': 'Q5. Water seeping around windows (during rain/typhoon). 🌧️',
    'A. 외부 실리콘·창틀 방수 노후, 강풍 시 압력 차이.': 'A. External silicone/frame waterproofing deterioration, pressure difference during strong winds.',
    '바로 해보세요: 수건·비닐로 물 유입부 차단. 창문 잠금(밀착) 재확인.': 'Quick fix: Block water entry with towels/plastic. Recheck window lock (tight seal).',
    '입주지원센터 및 호텔 조치: 하부 물막이·경첩 정렬, 실리콘 재시공.': 'Support Center / Hotel action: Lower water barrier/hinge alignment, re-silicone.',
    'Q6. 온수가 안 나와요 / 수압이 약해요. 🚿': 'Q6. No hot water / Weak water pressure. 🚿',
    'A. 중앙 보일러 일시 중단·감압밸브·배관 스케일 가능.': 'A. Possible central boiler shutdown, pressure reducing valve, or pipe scale.',
    '바로 해보세요: 다른 수전(세면·주방)도 동일한지 확인. 수전 필터망(헤드 끝) 이물 확인.': 'Quick fix: Check if other faucets (sink/kitchen) have same issue. Check faucet filter for debris.',
    '입주지원센터 및 호텔 조치: 보일러·감압밸브·배관 스케일 점검, 필터 청소/교체.': 'Support Center / Hotel action: Boiler, pressure valve, pipe scale inspection, filter cleaning/replacement.',
    '천장 물방울이 보이면 → 전기 접촉 피하고 즉시 접수 ⚡': 'If you see ceiling water drops → Avoid electrical contact and report immediately ⚡',
    '곰팡이 초기엔 "환기+건조"가 최선 🌬️': 'For early mold: "Ventilation + Drying" is best 🌬️',
    '싱크 아래 물기 발견 → 밸브 잠그고 접수 🔧': 'Water found under sink → Close valve and report 🔧',
    '접수 시 사진 & 위치를 보내면 훨씬 빨라요 📸': 'Photo & location in your report speeds things up 📸',
    '신고 시 알려주시면 빨라요': 'Providing this info speeds up service',
    '접수 시 알려주시면 빨라요': 'Providing this info speeds up service',
    '객실 번호 / 위치(천장·벽·바닥·창가) / 물 양(방울·흐름·고임) / 시작 시간 / 사진(가능 시)': 'Room number / Location (ceiling/wall/floor/window) / Water amount (drip/flow/pooling) / Start time / Photo (if possible)',
    '프런트: 24시간 운영': 'Front Desk: Open 24 hours',

    # 도어락
    '🔐 도어락 FAQ': '🔐 Door Lock FAQ',
    '잠금 해제가 안 되어 객실에 못 들어가는 경우, 프런트(24시간) 또는 입주지원센터에 즉시 연락해 주세요.': 'If you cannot unlock and enter your room, contact Front Desk (24hr) or Resident Support Center immediately.',
    'Q1. 비밀번호를 눌러도 문이 안 열려요. 🔒': 'Q1. Door won\'t open even after entering password. 🔒',
    'A. 배터리 부족·입력 오류·잠금 모드 가능.': 'A. Possible low battery, input error, or lock mode.',
    '바로 해보세요: 번호 천천히 재입력. 비상 배터리 단자에 9V 건전지 접촉(하단).': 'Quick fix: Re-enter number slowly. Touch 9V battery to emergency terminal (bottom).',
    '입주지원 / 호텔 조치: 비상 해정 후 배터리 교체·기기 점검.': 'Support / Hotel action: Emergency unlock, battery replacement, device inspection.',
    'Q2. 카드키가 인식이 안 돼요. 💳': 'Q2. Key card not recognized. 💳',
    'A. 카드 손상·자기장 노출·잔고장 가능.': 'A. Possible card damage, magnetic exposure, or malfunction.',
    '바로 해보세요: 카드 표면 이물 제거, 방향 재확인.': 'Quick fix: Clean card surface, recheck orientation.',
    '입주지원 / 호텔 조치: 카드 재발급 / 도어록 리더기 점검.': 'Support / Hotel action: Card reissue / Door lock reader inspection.',
    'Q3. 비밀번호를 변경하고 싶어요. 🔑': 'Q3. I want to change the password. 🔑',
    'A. 자체 변경 가능 기종 / 입주지원센터 요청 기종이 있습니다.': 'A. Some models allow self-change, others require Support Center.',
    '바로 해보세요: "#" 또는 "설정" 버튼 → 기존 비밀번호 → 새 비밀번호 입력 방식(기종마다 상이).': 'Quick fix: Press "#" or "Settings" → Enter old password → Enter new password (varies by model).',
    '입주지원센터 조치: 비밀번호 재설정.': 'Support Center action: Password reset.',
    'Q4. 배터리(건전지) 경고음이 나요. 🔋': 'Q4. Battery warning beep. 🔋',
    'A. 건전지 잔량 부족.': 'A. Low battery level.',
    '바로 해보세요: 곧 교체가 필요합니다. 입주지원센터에 접수.': 'Quick fix: Replacement needed soon. Report to Support Center.',
    '입주지원 / 호텔 조치: 건전지 교체.': 'Support / Hotel action: Battery replacement.',
    'Q5. 문이 잠기지 않아요 / 자동 잠김이 안 돼요. 🚪': 'Q5. Door won\'t lock / Auto-lock not working. 🚪',
    'A. 래치 걸림·프레임 틀어짐·오토락 설정 가능.': 'A. Possible latch jam, frame misalignment, or auto-lock setting issue.',
    '바로 해보세요: 문 손잡이를 들어 올려 수동 잠금. 문틀 걸림 확인.': 'Quick fix: Lift door handle for manual lock. Check frame alignment.',
    '입주지원 / 호텔 조치: 래치/스트라이크 조정, 문짝·힌지 점검.': 'Support / Hotel action: Latch/strike adjustment, door/hinge inspection.',
    'Q6. 도어락에서 이상한 소리가 나요. 🔊': 'Q6. Strange noise from door lock. 🔊',
    'A. 배터리·모터 노후·기어 마모 가능.': 'A. Possible battery, motor aging, or gear wear.',
    '바로 해보세요: 배터리 교체 후 재시도.': 'Quick fix: Replace batteries and try again.',
    '입주지원 / 호텔 조치: 내부 모터/기어 점검·교체.': 'Support / Hotel action: Internal motor/gear inspection/replacement.',
    'Q7. 비밀번호를 분실했어요. 🪪': 'Q7. I forgot my password. 🪪',
    'A. 먼저 입주지원/프런트에 신고해 주세요.': 'A. Please report to Support Center/Front Desk first.',
    '인적사항 확인 후 재설정 .': 'Reset after identity verification.',
    '잠겼을 때 당황하지 마세요 → 프런트는 24시간 🏨': 'Don\'t panic when locked out → Front Desk is 24hr 🏨',
    '도어락 "삐삐" 경고 = 건전지 교체 시기 🔋': 'Door lock "beep beep" warning = Time to change batteries 🔋',
    '비밀번호는 주기적으로 변경 권장 🔐': 'Password change recommended periodically 🔐',

    # 욕실
    '🛁 욕실 FAQ': '🛁 Bathroom FAQ',
    '미끄럼 사고에 주의하세요.': 'Be careful of slipping accidents.',
    'Q1. 욕실에서 냄새가 나요. 🤢': 'Q1. Bad smell in bathroom. 🤢',
    'A. 대부분 바닥트랩 건조나 환기 문제입니다.': 'A. Usually caused by dry floor trap or ventilation issues.',
    '바로 해보세요: 바닥 배수구에 물 한 컵을 부어주세요 → 환풍기를 10분 이상 가동해주세요.': 'Quick fix: Pour a cup of water into the floor drain → Run exhaust fan for 10+ minutes.',
    '입주지원센터 및 호텔 조치: 트랩 급수·배관 세척, 필요 시 팬 점검.': 'Support Center / Hotel action: Trap water supply, pipe cleaning, fan inspection if needed.',
    'Q2. 배수가 안 돼요 / 느려요. 🌀': 'Q2. Drain won\'t work / drains slowly. 🌀',
    'A. 머리카락·이물 걸림, 트랩 막힘 가능.': 'A. Possible hair/debris clog or trap blockage.',
    '바로 해보세요: 배수구 덮개 제거 → 눈에 보이는 이물 제거.': 'Quick fix: Remove drain cover → Remove visible debris.',
    '입주지원센터 및 호텔 조치: 배관 관통 세척(고압), 트랩 교체.': 'Support Center / Hotel action: High-pressure pipe cleaning, trap replacement.',
    'Q3. 샤워헤드에서 물이 잘 안 나와요 / 물줄기가 갈라져요. 🚿': 'Q3. Showerhead has weak flow / water splits. 🚿',
    'A. 석회(스케일) 막힘 또는 필터 이물.': 'A. Limescale blockage or filter debris.',
    '바로 해보세요: 헤드 분리 → 식초 30분 담금 → 잔여물 세척 → 재장착.': 'Quick fix: Detach head → Soak in vinegar 30min → Clean residue → Reattach.',
    '입주지원센터 및 호텔 조치: 헤드 교체, 급수필터 청소.': 'Support Center / Hotel action: Head replacement, water filter cleaning.',
    'Q4. 수압이 약해요. 💧': 'Q4. Water pressure is low. 💧',
    'A. 샤워헤드 석회나 밸브 세팅 문제일 수 있어요.': 'A. May be showerhead limescale or valve setting issue.',
    '바로 해보세요: 샤워호스 꼬임이 없는지 확인.': 'Quick fix: Check for shower hose kinks.',
    '입주지원센터 및 호텔 조치 : 헤드 탈석회· 교체, 밸브 점검.': 'Support Center / Hotel action: Head descaling/replacement, valve inspection.',
    'Q5. 샤워 중 바닥에 물이 안 빠져요. 🛁': 'Q5. Floor won\'t drain during shower. 🛁',
    'A. 배수 속도보다 물 사용량이 많거나 부분 막힘.': 'A. Water usage exceeds drain capacity or partial blockage.',
    '바로 해보세요: 배수구 이물 확인, 물 잠시 멈추고 배수 속도 관찰.': 'Quick fix: Check drain for debris, stop water briefly and observe drain speed.',
    '입주지원센터 및 호텔 조치 : 배관 세척, 바닥 기울기 보정.': 'Support Center / Hotel action: Pipe cleaning, floor slope correction.',
    'Q6. 세면대 물이 잘 안 내려가요. 🪥': 'Q6. Sink drains slowly. 🪥',
    'A. 팝업 밸브·이물·트랩 막힘.': 'A. Pop-up valve, debris, or trap blockage.',
    '바로 해보세요: 팝업 밸브(배수마개) 개방 상태 확인. 이물 제거.': 'Quick fix: Check that pop-up valve (drain stopper) is open. Remove debris.',
    '입주지원센터 및 호텔 조치 : 트랩·팝업 분해 청소, 필요 시 교체.': 'Support Center / Hotel action: Trap/pop-up disassembly cleaning, replacement if needed.',
    'Q7. 변기가 막히거나 물이 계속 흘러요. 🚽': 'Q7. Toilet clogged or keeps running. 🚽',
    'A. 이물 투입·플로트 오작동이 원인일 수 있어요.': 'A. May be caused by flushing foreign objects or float malfunction.',
    '바로 해보세요: 물티슈·생리대 등 변기에 투입하지 말아주세요.': 'Quick fix: Do not flush wet wipes, sanitary products, etc.',
    '입주지원센터 및 호텔 조치 : 압축기/플런저 작업, 부속(플로트·플러퍼) 교체. 탈거 후 재시공.': 'Support Center / Hotel action: Plunger work, parts (float/flapper) replacement. Reinstallation.',
    '바닥이 젖어 있으면 미끄럼 주의 🙏': 'Caution: slippery when floor is wet 🙏',
    '변기에는 물티슈·위생용품 투입 금지 🚫': 'Do not flush wipes or hygiene products 🚫',
    '샤워 후 환풍기 10분 추가 가동 권장 🌬️': 'Run exhaust fan for 10 extra minutes after showering 🌬️',
    '객실 번호 / 위치(샤워·세면·변기·바닥) / 증상(냄새·막힘·소리) / 시작 시점 / 사진·영상(선택)': 'Room number / Location (shower/sink/toilet/floor) / Symptom (smell/clog/noise) / Start time / Photo/video (optional)',

    # 응급상황
    '🆘 기숙사 응급상황 FAQ': '🆘 Dormitory Emergency FAQ',
    '가장 먼저': 'First Priority',
    '생명 위급/화재/폭력: 119(화재·구급) / 112(경찰) 📞': 'Life-threatening/Fire/Violence: 119 (Fire/Ambulance) / 112 (Police) 📞',
    '연락: 입주지원센터(032-15-9640), 야간·보안/ 주말 : 프런트(032-267-5004)': 'Contact: Support Center (032-15-9640), Night/Security/Weekend: Front Desk (032-267-5004)',
    '🔥 화재·연기·경보': '🔥 Fire / Smoke / Alarm',
    'Q. 경보가 울리거나 연기가 보여요.': 'Q. Alarm is sounding or smoke is visible.',
    'A.': 'A.',
    '젖은 수건으로 코·입 가리기, 낮은 자세': 'Cover nose/mouth with wet towel, stay low',
    '계단으로 대피(엘리베이터 금지), 방화문 닫기': 'Evacuate via stairs (no elevators), close fire doors',
    '모이는 장소에서 인원 확인 후 대기': 'Wait at assembly point after headcount',
    '🏥 부상/응급 의료': '🏥 Injury / Emergency Medical',
    'Q. 갑자기 의식을 잃은 사람이 있어요.': 'Q. Someone suddenly lost consciousness.',
    '반응 확인 → 119 신고 → 심폐소생술(CPR) 시작': 'Check response → Call 119 → Start CPR',
    'AED(제세동기)가 있다면 즉시 사용': 'Use AED (defibrillator) if available',
    'Q. 심한 출혈/부상입니다.': 'Q. Severe bleeding/injury.',
    '깨끗한 천으로 강한 압박, 출혈 부위 심장보다 높게, 119 신고': 'Apply strong pressure with clean cloth, elevate wound above heart, call 119',
    '🧯 전기·가스·화학 냄새': '🧯 Electrical / Gas / Chemical Odor',
    'Q. 가스/타는 냄새가 나요.': 'Q. I smell gas or something burning.',
    '스위치·불꽃 사용 금지, 창문 환기, 가스밸브 잠금': 'Do not use switches/flames, ventilate windows, close gas valve',
    '사람을 대피시키고 119 연락 + 상단 연락처 연락': 'Evacuate people and call 119 + contact numbers above',
    'Q. 콘센트 스파크/발열이 심해요.': 'Q. Outlet is sparking/overheating.',
    '해당 차단기 OFF, 절대 물 뿌리지 마세요, 즉시 신고': 'Turn OFF circuit breaker, never spray water, report immediately',
    '⚡ 정전': '⚡ Power Outage',
    '정전 시 손전등 사용(촛불 금지), 고출력 기기 플러그 분리': 'During outage: use flashlight (no candles), unplug high-power devices',
    '🌍 지진(흔들림 체감)': '🌍 Earthquake',
    '엎드리고-가리고-붙잡기(탁자 아래) → 흔들림 멈춘 뒤 계단 대피': 'Drop-Cover-Hold On (under table) → Evacuate via stairs when shaking stops',
    '대피 시 엘리베이터 금지, 낙하물 주의': 'During evacuation: no elevators, watch for falling objects',
    '💧 대량 누수·침수': '💧 Major Leak / Flooding',
    '전기 접점 근처면 접근 금지, 가능 시 차단기 OFF': 'Stay away from electrical contact points, turn OFF breaker if possible',
    '물 피해 최소화(높은 곳으로 이동) → 상단 연락처 연락': 'Minimize water damage (move to higher ground) → Contact numbers above',
    '🧠 심리·건강 위기': '🧠 Psychological / Health Crisis',
    '자해·자살 위험 발언/행동 발견 시 즉시 112/119 +상단 연락처 연락연락': 'If self-harm/suicide risk speech/behavior found, immediately call 112/119 + contact numbers above',
    '자해·자살 위험 발언/행동 발견 시 즉시 112/119 +상단 연락처 연락': 'If self-harm/suicide risk speech/behavior found, immediately call 112/119 + contact numbers above',
    '🔇 소음·분쟁': '🔇 Noise / Disputes',
    '자율조정 시도(정중한 요청) → 해결 안 되면 [상단 연락처 연락] 연락': 'Try self-mediation (polite request) → If unresolved, contact numbers above',
    '폭언·위협은 증거(시간·장소) 남겨 신고': 'Document evidence (time/place) of verbal abuse/threats and report',
    '📞 신고 시 알려주시면 빨라요': '📞 Providing this info speeds up response',
    '📞 접수 시 알려주시면 빨라요': '📞 Providing this info speeds up response',
    '이름·객실 / 상황 유형(화재·의료·소음 등) / 부상자 수·상태 / 현재 위치': 'Name/Room / Situation type (fire/medical/noise etc.) / Number of injured / Current location',
    '🧰 개인 비상 키트(권장)': '🧰 Personal Emergency Kit (Recommended)',
    '손전등·예비배터리, 작은 구급약, 마스크, 생수/간식, 개인 복용약, 호루라기': 'Flashlight, spare batteries, first aid, mask, water/snacks, personal medication, whistle',

    # 전기
    '⚡ 전기·콘센트 FAQ': '⚡ Electrical & Outlet FAQ',
    '스파크/연기/타는 냄새/감전 느낌이 있으면 즉시 각 차수 방재실 및 프런트로 연락하고 사용을 중지해주세요. 젖은 손': 'If you experience sparks/smoke/burning smell/electric shock, immediately contact Fire Safety Office and Front Desk. Stop use. Wet hands—',
    '으로 전기기기를 만지지 말아 주세요.': 'never touch electrical devices with wet hands.',
    'Q1. 전기가 안 켜져요. 🔑': 'Q1. Power won\'t turn on. 🔑',
    'A. 전기 차단 상태일 수 있어요.': 'A. Power may be switched off.',
    '바로 해보세요: 카드키 투입구에 카드 삽입 후 확인해주세요.': 'Quick fix: Insert your key card into the card slot and check.',
    '바로 해보세요: 거실 벽면 차단기 확인.': 'Quick fix: Check the living room wall circuit breaker.',
    '입주지원 / 호텔 조치: 전원 라인 점검, 필요 시 교체.': 'Support / Hotel action: Power line inspection, replacement if needed.',
    'Q2. 일부 콘센트/조명만 안 돼요. 🔌💡': 'Q2. Only some outlets/lights don\'t work. 🔌💡',
    'A. 회로 과부하나 스위치/콘센트 개별 불량일 수 있어요.': 'A. Possible circuit overload or individual switch/outlet malfunction.',
    '바로 해보세요: 해당 스위치 ON 확인, 멀티탭/고출력 기기 분리.': 'Quick fix: Check switch is ON, unplug power strips/high-power devices.',
    '입주지원 / 호텔 조치: 회로 확인, 콘센트/스위치 교체, 과부하 원인 제거.': 'Support / Hotel action: Circuit check, outlet/switch replacement, overload cause removal.',
    'Q3. 콘센트에서 스파크/타는 냄새가 나요. 🔥': 'Q3. Outlet is sparking/burning smell. 🔥',
    'A. 느슨한 접촉·과부하 가능.': 'A. Possible loose contact or overload.',
    '바로 해보세요: 즉시 플러그 분리(전원 OFF 후), 사용 중지.': 'Quick fix: Immediately unplug (after turning OFF power), stop use.',
    '입주지원/호텔조치: 콘센트교체·배선점검필요시객실교체안내': 'Support/Hotel action: Outlet replacement, wiring inspection, room change if needed.',
    'Q4. 조명이 깜박여요. 💡': 'Q4. Lights are flickering. 💡',
    'A. 전구 수명·스위치 접점·전압 변동 영향.': 'A. Light bulb lifespan, switch contact, or voltage fluctuation.',
    '바로 해보세요: 다른 스위치/등기구도 동일한지 확인.': 'Quick fix: Check if other switches/fixtures have the same issue.',
    '입주지원 / 호텔 조치: 전구 교체, 스위치/안정기 점검.': 'Support / Hotel action: Bulb replacement, switch/ballast inspection.',
    'Q5. 멀티탭/드라이기 꽂으면 **차단기(누전차단기)**가 내려가요.': 'Q5. Circuit breaker trips when using power strip/hair dryer.',
    'A. 과부하 또는 누전 감지.': 'A. Overload or ground fault detected.',
    '바로 해보세요: 고출력 기기(히터·인덕션 등) 사용 중지, 플러그 모두 분리 후 연락.': 'Quick fix: Stop using high-power devices (heater, induction, etc.), unplug all, then contact.',
    '입주지원 / 호텔 조치: 회로 복구, 누전 테스트, 안전 확인.': 'Support / Hotel action: Circuit recovery, ground fault test, safety check.',
    'Q6. TV·냉장고 전원이 안 켜져요. 📺🧊💨': 'Q6. TV/Refrigerator won\'t power on. 📺🧊💨',
    'A. 개별 스위치/플러그/절전 모드 영향.': 'A. Individual switch/plug/power-saving mode effect.',
    'TV: 리모컨 전원 → 콘센트 플러그 깊이 확인': 'TV: Remote power → Check outlet plug is fully inserted',
    '냉장고: 전용 상시콘센트 연결 확인 (절전 회로와 분리)': 'Refrigerator: Check dedicated always-on outlet (separate from power-saving circuit)',
    '입주지원 / 호텔 조치: 해당 콘센트·회로 점검, 필요 시 가전 교체.': 'Support / Hotel action: Outlet/circuit inspection, appliance replacement if needed.',
    'Q7. 개인 전열기기(전기히터·전기포트 등) 사용 가능한가요? 🔥🥤': 'Q7. Can I use personal heating appliances (heater, electric kettle, etc.)? 🔥🥤',
    'A. 고출력 난방·취사기기는 화재·과부하 위험으로 반입·사용 제한됩니다.': 'A. High-power heating/cooking appliances are restricted due to fire/overload risk.',
    'Q8. 객실/층 정전이 발생했어요. 🌑': 'Q8. Power outage in my room/floor. 🌑',
    'A. 지역/건물 점검 또는 일시 과부하일 수 있어요.': 'A. May be area/building maintenance or temporary overload.',
    '바로 해보세요: 복도 비상등을 따라 안전 대기, 엘리베이터 이용 자제.': 'Quick fix: Follow corridor emergency lights and wait safely, avoid elevators.',
    '입주지원 / 호텔 조치: 즉시 원인 확인, 단계별 복구·안내방송, 필요 시 객실 이동 지원.': 'Support / Hotel action: Immediate cause identification, step-by-step recovery, room relocation support if needed.',
    '객실 번호 / 증상(불점등·스파크·차단기 트립 등) / 시작 시간 / 사용 중인 기기 종류 / 사진·영상(선택)': 'Room number / Symptom (no light/spark/breaker trip etc.) / Start time / Devices in use / Photo/video (optional)',
    '카드키 먼저 꽂으셨나요? → 전기 공급의 첫 단추 🔑': 'Did you insert the key card first? → First step for power supply 🔑',
    '한 콘센트에 고출력 여러 기기 금지 🔌': 'Do not plug multiple high-power devices into one outlet 🔌',
    '스파크/연기/타는 냄새 = 즉시 중지 & 연락 ⚡': 'Spark/smoke/burning smell = Stop immediately & contact ⚡',
    '젖은 손/바닥에서는 플러그 탈·부착 금지 🖐️💧': 'Do not plug/unplug with wet hands or on wet floor 🖐️💧',

    # 생활수칙
    '🏠 표준 생활수칙': '🏠 Standard Living Rules',
    '1) 기본 원칙 🤝': '1) Basic Principles 🤝',
    '서로 존중·배려하고, 공동체 규칙을 우선합니다.': 'Respect and care for each other; community rules come first.',
    '안전·청결·조용을 생활의 기본으로 지킵니다.': 'Safety, cleanliness, and quiet are basic living principles.',
    '2) 조용 시간 🔇': '2) Quiet Hours 🔇',
    '조용 시간: 입주민을 위해 항상 조용히 해주세요...': 'Quiet hours: Please always keep quiet for fellow residents...',
    '문 닫을 때 살짝, 통화·음악은 이어폰 사용, 공용부는 낮은 목소리.': 'Close doors gently, use earphones for calls/music, keep voice low in common areas.',
    '3) 출입·보안 🔐': '3) Access & Security 🔐',
    '본인 카드키/비밀번호로만 출입'; 비인가 동반·대여 금지.': 'Access only with your key card/password; unauthorized companions/lending prohibited.',
    '외부인 초대 시 사전 승인(프런트/입주지원).': 'Prior approval required for visitors (Front Desk/Support).',
    '4) 객실 관리 🧹': '4) Room Management 🧹',
    '퇴실 시 원상복구, 셀프 청소 유지.': 'Restore room condition at move-out, maintain self-cleaning.',
    '가구 임의 이동·벽 못질·개조 금지.': 'No unauthorized furniture moving, wall nailing, or remodeling.',
    '5) 분리수거·쓰레기 🗑️': '5) Recycling & Waste 🗑️',
    '지정 장소·시간에 분리배출. 음식물 밀봉.': 'Dispose at designated place/time. Seal food waste.',
    '복도·공용부에 쓰레기/세탁물 방치 금지.': 'No leaving trash/laundry in hallways or common areas.',
    '6) 취사·냄새 🍳': '6) Cooking & Odor 🍳',
    '주방에서만 취사 허용, 조리 후 환기·원상복구.': 'Cooking only in kitchen, ventilate and clean after cooking.',
    '강한 냄새(튀김·훈제)는 시간 제한 .': 'Strong odors (frying/smoking) have time restrictions.',
    '7) 금연·주류 🚭': '7) No Smoking & Alcohol 🚭',
    '실내 전 구역 금연. 전자담배 포함.': 'No smoking in all indoor areas. Including e-cigarettes.',
    '음주 후 과음·소란 금지.': 'No excessive drinking or noise after drinking.',
    '8) 전기·가전 ⚡': '8) Electrical Appliances ⚡',
    '고출력 개인 전열기기(히터·전기레인지 등) 사용 금지.': 'High-power personal appliances (heaters, electric stoves, etc.) are prohibited.',
    '멀티탭 과부하·문어발 배선 금지.': 'No overloading power strips or daisy-chaining.',
    '장기 외출 시 불필요 전원 OFF.': 'Turn off unnecessary power when away for extended periods.',
    '9) 물 사용·누수 💧': '9) Water Usage & Leaks 💧',
    '잠자리/외출 전 수전 잠금. 세탁기 사용 후 급수밸브 닫기.': 'Close faucets before sleeping/going out. Close water valve after using washer.',
    '10) 반려동물 🐾': '10) Pets 🐾',
    '반입·사육 전면 금지(예외: 안내견 등 법적 인정 제외).': 'All pets prohibited (exception: guide dogs and legally recognized animals).',
    '11) 택배·배달 📦': '11) Deliveries 📦',
    '수령 후 즉시 회수, 공용부 장기 방치 금지.': 'Pick up immediately after delivery, no long-term storage in common areas.',
    '음식 배달은 공용 픽업존 이용 권장.': 'Food delivery pickup zone recommended.',
    '12) 주차·자전거·PM(킥보드) 🚲': '12) Parking / Bicycle / Scooter 🚲',
    '지정 구역 주차/거치, 실내 반입 금지(오염·안전).': 'Park in designated areas only, no indoor storage (hygiene/safety).',
    '충전은 안전 승인 장소에서만.': 'Charge only in approved safe locations.',
    '13) 개인정보·촬영 📵': '13) Privacy & Recording 📵',
    '타인 무단 촬영/녹음 금지. SNS 업로드 시 동의 필수.': 'Unauthorized photo/recording of others prohibited. Consent required for SNS uploads.',
    '주차등록은 입주시 블루오션 3차 3층 슈퍼파킹으로 방문하셔야 합니다. (첨부서류 차량등록증, 신분증)': 'For parking registration, visit Super Parking on 3F of Blue Ocean Phase 3 upon move-in. (Required: vehicle registration, ID)',
    '매트리스 회수를 원하신다면 기숙사 입실 전 인스파이어 담당자에게 내용을 전달해 주셔야 하며': 'If you want mattress removal, inform the Inspire representative before moving in.',
    '사용 중 매트리스 회수를 원하시면 1,3차는 각 층 화물 엘리베이터 앞 / 2,4차는 2차 1층 106호 로 매트리스': 'For mattress removal during stay, move to: Phase 1,3 → each floor freight elevator area / Phase 2,4 → Phase 2, 1F Room 106.',
    '이동 후 입주지원센터로 연락주세요.': 'Then contact Resident Support Center.',
    '연락 : 032-715-9640': 'Contact: 032-715-9640',

    # 도움말
    '불편사항이나 건의사항이 있으신가요?': 'Any complaints or suggestions?',
    '보다 나은 서비스 제공을 위해 소중한 의견을 기다리고 있습니다.': 'We welcome your valuable feedback for better service.',
    '📱 접수 채널': '📱 Contact Channels',
    '카카오톡 상담:': 'KakaoTalk:',
    'LINE 고객센터:': 'LINE Support:',
    '이메일: help@blueoceanhotel.co.kr': 'Email: help@blueoceanhotel.co.kr',
    '전화문의: 032-715-9640 (09:00~18:00)': 'Phone: 032-715-9640 (09:00~18:00)',
    '도움이 더 필요하신가요?': 'Need more help?',
    '2차 104호로 방문하시면 친절하게 도움드리겠습니다.': 'Visit Phase 2 Room 104 for in-person assistance.',
    '지도 데이터 ©2026 TMap Mobility': 'Map data ©2026 TMap Mobility',
    '입주지원 센터 :': 'Resident Support Center:',
    '[2차] 인천광역시 중구 영종대로 893': '[Phase 2] 893 Yeongjong-daero, Jung-gu, Incheon',
    '1층 104호    032-715-9640': '1F Room 104    032-715-9640',

    # 고객센터_01
    '슬기로운  🎉블루오션  생활': 'Smart 🎉 Blue Ocean Living',
    '어떻게 도와드릴까요?': 'How can we help you?',
    '인스파이어 리조트 임직원 여러분의 슬기로운 블루오션 생활을 위해 ...': 'For a smart Blue Ocean life for Inspire Resort employees...',
    '아래 주제에 대해 간단히 도와드릴 수 있습니다.': 'We can help you with the topics below.',
    'Google Forms를 통해 비밀번호를 제출하지 마세요.': 'Do not submit passwords through Google Forms.',
    '이 콘텐츠는 Google이 만들거나 승인하지 않았습니다.': 'This content is neither created nor endorsed by Google.',
    '비공개': 'Private',
    '페이지': 'Page',
    '선택': 'Select',
    '내용': 'Content',
    '내 답변': 'My Answer',
    '제출': 'Submit',
    '양식 지우기': 'Clear Form',
    '설문지': 'Survey',
    '냄새': 'Odor',
    '응급상항': 'Emergency',
}

def translate_content(text: str) -> str:
    """한국어 텍스트를 영어로 번역 (전체 줄 매칭 우선)"""
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue
        
        # 구분선
        if stripped.startswith('─'):
            result.append(line)
            continue
        
        # 전체 줄 완전 매칭
        if stripped in FULL_LINE_MAP:
            result.append(FULL_LINE_MAP[stripped])
            continue
        
        # 부분 매칭 (긴 것부터)
        translated = stripped
        for ko, en in sorted(FULL_LINE_MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if ko in translated:
                translated = translated.replace(ko, en)
        
        result.append(translated)
    
    return '\n'.join(result)


# ── 메인 ──
data_path = r'C:\Users\user\.gemini\antigravity\scratch\domi-app\src\data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    for section in item['sections']:
        if section['type'] == 'text':
            section['content_en'] = translate_content(section['content'])

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 번역 v2 완료")

# 남은 한글 체크
import re
korean_pattern = re.compile(r'[가-힣]')
total_lines = 0
korean_lines = 0
for item in data:
    for section in item['sections']:
        if section['type'] == 'text' and 'content_en' in section:
            for line in section['content_en'].split('\n'):
                stripped = line.strip()
                if not stripped or stripped.startswith('─'):
                    continue
                total_lines += 1
                if korean_pattern.search(stripped):
                    korean_lines += 1

coverage = ((total_lines - korean_lines) / total_lines * 100) if total_lines > 0 else 0
print(f"📊 전체 {total_lines}줄 중 {total_lines - korean_lines}줄 완역 ({coverage:.1f}% coverage)")
print(f"   미번역 {korean_lines}줄 남음")
