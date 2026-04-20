import React, { useState, useMemo } from 'react';
import { Search, Home, Map, BookOpen, ChevronDown, ChevronLeft, Settings, Zap, Droplets, Wind, Wifi, HelpCircle, HardHat, ShieldAlert, Phone, X, Globe } from 'lucide-react';
import manualData from './data.json';

/* ── 타입 정의 ── */
type Lang = 'ko' | 'en';
type LucideIcon = React.FC<{ size?: number; className?: string }>;
interface CategoryStyle { icon: LucideIcon; gradient: string; bgLight: string }

/* ── 카테고리별 스타일 매핑 ── */
const categoryMap: Record<string, CategoryStyle> = {
  'TV, WIFI':    { icon: Wifi,        gradient: 'from-blue-500 to-blue-700',    bgLight: 'bg-blue-50 text-blue-600' },
  '냄새_해충':   { icon: Droplets,    gradient: 'from-emerald-500 to-teal-700',  bgLight: 'bg-emerald-50 text-emerald-600' },
  '냉난방기':    { icon: Wind,        gradient: 'from-sky-400 to-cyan-600',      bgLight: 'bg-sky-50 text-sky-600' },
  '누수':        { icon: Droplets,    gradient: 'from-blue-400 to-indigo-600',   bgLight: 'bg-blue-50 text-blue-500' },
  '도어락':      { icon: HardHat,     gradient: 'from-amber-400 to-orange-600',  bgLight: 'bg-amber-50 text-amber-600' },
  '전기':        { icon: Zap,         gradient: 'from-yellow-400 to-amber-600',  bgLight: 'bg-yellow-50 text-yellow-600' },
  '욕실':        { icon: Droplets,    gradient: 'from-teal-400 to-cyan-600',     bgLight: 'bg-teal-50 text-teal-600' },
  '생활수칙':    { icon: BookOpen,    gradient: 'from-indigo-500 to-purple-700', bgLight: 'bg-indigo-50 text-indigo-600' },
  '응급상황':    { icon: ShieldAlert, gradient: 'from-red-500 to-rose-700',      bgLight: 'bg-red-50 text-red-600' },
  '도움말':      { icon: HelpCircle,  gradient: 'from-gray-400 to-gray-600',     bgLight: 'bg-gray-50 text-gray-500' },
  '고객센터_01': { icon: Phone,       gradient: 'from-brand-vibrant to-brand',   bgLight: 'bg-brand-light text-brand' },
};
const defaultStyle: CategoryStyle = { icon: BookOpen, gradient: 'from-brand-vibrant to-brand', bgLight: 'bg-brand-light text-brand' };
function getStyle(title: string) { return categoryMap[title] || defaultStyle; }
function CategoryIcon({ title, size = 28 }: { title: string; size?: number }) {
  const Icon = getStyle(title).icon;
  return <Icon size={size} />;
}

/* ── 텍스트를 Q&A 블록으로 파싱하는 유틸 ── */
/* Q&A를 하나의 블록으로 묶는 파싱 로직
   - ❓ 질문 시작 → 다음 ❓ 또는 이모지 소제목까지 같은 블록에 포함
   - 💡, ✅, 🔧, ⏱ 등 답변 라인은 질문 블록에 포함 */
function parseContentIntoBlocks(text: string): string[][] {
  const lines = text.split('\n').filter(l => l.trim());
  const blocks: string[][] = [];
  let current: string[] = [];
  let inQA = false; // 현재 Q&A 블록 안에 있는지 추적

  for (const line of lines) {
    const trimmed = line.trim();
    // 구분선은 건너뜀
    if (trimmed.startsWith('─')) continue;

    // 새 질문(Q) 시작 → 이전 블록 저장 후 새 Q&A 블록 시작
    if (trimmed.startsWith('❓')) {
      if (current.length > 0) blocks.push(current);
      current = [trimmed];
      inQA = true;
      continue;
    }

    // Q&A 블록 안에서 답변 관련 라인은 같은 블록에 유지
    if (inQA && /^(💡|✅|🔧|⏱|\d+\.|\d+\))/.test(trimmed)) {
      current.push(trimmed);
      continue;
    }
    // Q&A 블록 안의 일반 텍스트도 같은 블록에 유지 (다른 섹션 시작 전까지)
    if (inQA && !/^[⚠️🔥🧯💧🌍🧰📱🔒🏠📞🚨🆘🛁🌬️🪪⚡🍳🚭🔇🤝🗑️📦🚲📵🎉❄️🌡️🐜🩺🧠🛗🌧️🧹🧯]/.test(trimmed) && !/(?:FAQ|Guide|안내|가이드|수칙|요약|Q&A)/.test(trimmed)) {
      current.push(trimmed);
      continue;
    }

    // Q&A 블록 종료
    inQA = false;

    // 새 이모지 섹션 제목 (FAQ, 안내 등) → 새 블록
    if (/(?:FAQ|Guide|안내|가이드|수칙|요약|Q&A)/.test(trimmed) && /^[^\w\s]/.test(trimmed)) {
      if (current.length > 0) blocks.push(current);
      current = [trimmed];
      continue;
    }
    // 이모지 소제목 시작 → 새 블록
    if (/^[⚠️🔥🧯💧🌍🧰📱🔒🏠📞🚨🆘🛁🌬️🪪⚡🍳🚭🔇🤝🗑️📦🚲📵🎉❄️🌡️🐜🩺🧠🛗🌧️🧹🧯]/.test(trimmed) && !trimmed.startsWith('⏱')) {
      if (current.length > 0) blocks.push(current);
      current = [trimmed];
      continue;
    }
    // 번호 목록이 1)로 시작하면 새 블록
    if (/^\d+\)/.test(trimmed) && current.length > 0 && !current[current.length - 1].match(/^\d+\)/)) {
      if (current.length > 0) blocks.push(current);
      current = [trimmed];
      continue;
    }
    current.push(trimmed);
  }
  if (current.length > 0) blocks.push(current);
  return blocks;
}

/* ── 한 줄을 스타일링하여 렌더링 ── */
function StyledLine({ line, idx }: { line: string; idx: number }) {
  const t = line.trim();

  // FAQ 대제목
  if (/(?:FAQ|Guide|안내|가이드|수칙|요약|Q&A)/.test(t) && /^[^\w\s]/.test(t)) {
    return <h3 key={idx} className="text-[16px] font-bold text-brand border-b-2 border-brand-light pb-2 mb-1">{t}</h3>;
  }
  // 질문 ❓
  if (t.startsWith('❓')) {
    return <p key={idx} className="font-bold text-blue-800 text-[15px] leading-snug">{t.replace('❓ ', '')}</p>;
  }
  // 답변 💡
  if (t.startsWith('💡')) {
    return <p key={idx} className="text-gray-600 mt-1">{t.replace('💡 ', '')}</p>;
  }
  // 실행 가이드 ✅ — "바로 해보세요" / "Quick fix" 접두어 제거 및 내용 없을 시 미노출
  if (t.startsWith('✅')) {
    const cleaned = t.replace(/✅\s*/, '').replace(/^(바로 해보세요\s*[:：]?\s*|Quick fix\s*[:：]?\s*)/i, '').trim();
    if (!cleaned) return null; // 내용이 없으면 렌더링하지 않음 (이미지 2번 케이스)
    
    return (
      <div key={idx} className="flex items-start gap-2 bg-emerald-50 rounded-lg px-3 py-2 text-emerald-700 border border-emerald-100 mt-1.5">
        <span className="shrink-0 mt-0.5">✅</span>
        <p className="font-medium text-[13px]">{cleaned}</p>
      </div>
    );
  }
  // 입주지원 조치 🔧
  if (t.startsWith('🔧')) {
    return (
      <div key={idx} className="flex items-start gap-2 bg-orange-50 rounded-lg px-3 py-2 text-orange-700 border border-orange-100 mt-1.5">
        <span className="shrink-0 mt-0.5">🔧</span>
        <p className="text-[13px]">{t.replace(/🔧\s*/, '')}</p>
      </div>
    );
  }
  // 예상 시간 ⏱
  if (t.startsWith('⏱')) {
    return <span key={idx} className="inline-block bg-purple-50 text-purple-600 rounded-full px-3 py-1 text-[12px] font-medium mt-1">{t}</span>;
  }
  // 이모지 소제목
  if (/^[⚠️🔥🧯💧🌍🧰📱🔒🏠📞🚨🆘🛁🌬️🪪⚡🍳🚭🔇🤝🗑️📦🚲📵🎉❄️🌡️]/.test(t)) {
    return <h4 key={idx} className="text-[15px] font-bold text-gray-800 mt-1">{t}</h4>;
  }
  // 번호 목록
  if (/^\d+[\)\.]/.test(t)) {
    return <p key={idx} className="font-semibold text-gray-800 mt-1">{t}</p>;
  }
  // 일반 텍스트
  return <p key={idx} className="text-gray-600 text-[14px] leading-relaxed">{t}</p>;
}

/* ── 텍스트 블록별 카드 렌더링 ── */
function FormattedContent({ content }: { content: string }) {
  const blocks = parseContentIntoBlocks(content);
  return (
    <div className="space-y-3 px-4 py-3">
      {blocks.map((block, bIdx) => (
        <div key={bIdx} className={`rounded-xl border shadow-sm p-4 space-y-1.5 ${
          block.some(l => l.trim().startsWith('❓'))
            ? 'bg-blue-50/60 border-blue-200'
            : 'bg-white border-gray-100'
        }`}>
          {block.map((line, lIdx) => (
            <StyledLine key={lIdx} line={line} idx={lIdx} />
          ))}
        </div>
      ))}
    </div>
  );
}

/* ── 상세 페이지 ── */
function DetailView({ item, onBack, lang }: { item: any; onBack: () => void; lang: Lang }) {
  const style = getStyle(item.title);
  const displayTitle = lang === 'en' ? (item.title_en || item.title) : item.title;
  
  return (
    <div className="flex flex-col h-full bg-[#F1F3F5]">
      <div className={`bg-gradient-to-br ${style.gradient} text-white pt-8 pb-3 px-5 rounded-b-[1.5rem] shadow-lg shrink-0 relative`}>
        <button onClick={onBack} className="absolute top-8 left-4 bg-white/20 backdrop-blur-md p-1.5 rounded-full hover:bg-white/30 transition-all">
          <ChevronLeft size={20} />
        </button>
        <div className="text-center mt-2 flex flex-col items-center">
          <div className="inline-flex bg-white/20 backdrop-blur-sm p-2 rounded-xl mb-1.5">
            <CategoryIcon title={item.title} size={22} />
          </div>
          <h1 className="text-xl font-extrabold tracking-tight">{displayTitle}</h1>
          <p className="text-white/70 text-[11px] mt-0.5">{item.total_pages} {lang === 'en' ? 'items' : '개 항목'}</p>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto no-scrollbar pb-28 pt-4">
        {item.sections.map((section: any, idx: number) => {
          if (section.type === 'text') {
            const text = lang === 'en' ? (section.content_en || section.content) : section.content;
            return <FormattedContent key={idx} content={text} />;
          }
          if (section.type === 'image') {
            return (
              <div key={idx} className="px-4 mb-3">
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <img src={section.content} alt={`${item.title} ${idx+1}`} className="w-full h-auto" loading="lazy" />
                </div>
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}

/* ── 카테고리 리스트 아이템 ── */
function CategoryListItem({ item, onClick, lang }: { item: any; onClick: () => void; lang: Lang }) {
  const style = getStyle(item.title);
  const displayTitle = lang === 'en' ? (item.title_en || item.title) : item.title;
  return (
    <button onClick={onClick} className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex gap-4 items-center text-left active:scale-[0.98] transition-transform hover:shadow-md">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${style.bgLight}`}>
        <CategoryIcon title={item.title} size={22} />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-bold text-gray-800 text-[15px]">{displayTitle}</h3>
        <p className="text-[11px] text-gray-400 mt-0.5">{item.total_pages} {lang === 'en' ? 'guides' : '개 가이드'}</p>
      </div>
      <ChevronDown size={18} className="text-gray-300 -rotate-90 shrink-0" />
    </button>
  );
}

/* ── 딥서치 결과 타입 ── */
interface SearchResult {
  item: any;
  sectionIdx: number;
  snippet: string;
  matchTitle: boolean;
}

/* ── 메인 앱 ── */
function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [lang, setLang] = useState<Lang>('ko');

  // 딥서치: 한글 2글자 이상 또는 영어 3글자 이상일 때 세부 내용 검색
  const searchResults = useMemo<SearchResult[]>(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase().trim();
    
    // 한글 글자 수 / 영문 글자 수 카운트
    const koreanChars = (q.match(/[가-힣]/g) || []).length;
    const engChars = (q.match(/[a-z]/g) || []).length;
    const isDeepSearch = koreanChars >= 2 || engChars >= 3;
    
    const results: SearchResult[] = [];
    
    for (const item of manualData) {
      const titleKo = item.title.toLowerCase();
      const titleEn = (item.title_en || '').toLowerCase();
      const titleMatch = titleKo.includes(q) || titleEn.includes(q);
      
      if (!isDeepSearch) {
        // 얕은 검색: 제목만
        if (titleMatch) {
          results.push({ item, sectionIdx: -1, snippet: '', matchTitle: true });
        }
        continue;
      }
      
      // 딥 검색: 세부 내용까지
      let hasDetailMatch = false;
      for (let sIdx = 0; sIdx < item.sections.length; sIdx++) {
        const section = item.sections[sIdx];
        if (section.type !== 'text') continue;
        
        const contentKo = (section.content || '').toLowerCase();
        const contentEn = (section.content_en || '').toLowerCase();
        
        if (contentKo.includes(q) || contentEn.includes(q)) {
          // 매칭된 부분 주변 스니펫 추출
          const searchContent = (contentKo.includes(q) ? section.content : section.content_en) || '';
          const matchIdx = searchContent.toLowerCase().indexOf(q);
          const start = Math.max(0, matchIdx - 20);
          const end = Math.min(searchContent.length, matchIdx + q.length + 40);
          let snippet = searchContent.substring(start, end).replace(/\n/g, ' ').trim();
          if (start > 0) snippet = '...' + snippet;
          if (end < searchContent.length) snippet += '...';
          
          results.push({ item, sectionIdx: sIdx, snippet, matchTitle: false });
          hasDetailMatch = true;
        }
      }
      
      // 제목 매치인데 세부 매치가 없었으면 제목 매치로 추가
      if (titleMatch && !hasDetailMatch) {
        results.push({ item, sectionIdx: -1, snippet: '', matchTitle: true });
      }
    }
    
    return results;
  }, [searchQuery]);

  // 카테고리 그룹핑
  const facilityItems = manualData.filter((item: any) => 
    ['TV, WIFI', '냉난방기', '전기', '도어락', '누수', '욕실'].includes(item.title)
  );
  const livingItems = manualData.filter((item: any) => 
    ['생활수칙', '냄새_해충', '도움말'].includes(item.title)
  );
  const emergencyItem = manualData.find((item: any) => item.title === '응급상황');

  // 상세 페이지 모드
  if (selectedItem) {
    return (
      <div className="flex justify-center bg-gray-200 min-h-screen font-sans">
        <div className="w-full max-w-md bg-[#F1F3F5] h-screen flex flex-col relative shadow-2xl overflow-hidden">
          <DetailView item={selectedItem} onBack={() => { setSelectedItem(null); }} lang={lang} />
          <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} onHome={() => { setSelectedItem(null); setSearchQuery(''); setActiveTab('home'); }} lang={lang} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center bg-gray-200 min-h-screen font-sans">
      <div className="w-full max-w-md bg-[#F8F9FA] h-screen flex flex-col relative shadow-2xl overflow-hidden">
        
        {/* 헤더 */}
        <div className="bg-gradient-to-br from-brand-vibrant to-brand text-white pt-10 pb-6 px-6 rounded-b-[2rem] shadow-lg z-10 shrink-0">
          <div className="flex justify-between items-center mb-5">
            <div>
              <h2 className="text-blue-200 text-[13px] font-medium mb-0.5">
                {lang === 'en' ? 'Resident Guide' : '입주자 가이드'}
              </h2>
              <h1 className="text-[22px] font-extrabold tracking-tight">
                {lang === 'en' ? 'Blue Ocean Residence' : '블루오션 레지던스'}
              </h1>
            </div>
            <div className="flex items-center gap-2">
              {/* 언어 토글 */}
              <button 
                onClick={() => setLang(lang === 'ko' ? 'en' : 'ko')}
                className="flex items-center gap-1.5 bg-white/20 px-3 py-2 rounded-full backdrop-blur-md hover:bg-white/30 transition-all text-sm font-bold"
              >
                <Globe size={16} />
                {lang === 'ko' ? 'EN' : '한'}
              </button>

            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <Search className="text-gray-400 group-focus-within:text-brand-vibrant transition-colors" size={20} />
            </div>
            <input 
              type="text" 
              placeholder={lang === 'en' ? 'Search anything (e.g. wifi, leak)' : '무엇이든 검색해 보세요 (예: 와이파이, 누수)'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-10 py-3.5 rounded-2xl text-gray-800 bg-white shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-300/50 transition-all text-sm font-medium placeholder:font-normal placeholder:text-gray-400"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 bg-gray-200 p-1 rounded-full">
                <X size={14} className="text-gray-500" />
              </button>
            )}
          </div>
        </div>

        {/* 메인 스크롤 영역 */}
        <main className="flex-1 overflow-y-auto no-scrollbar pb-24 px-5 pt-5 bg-[#F8F9FA]">
          {searchQuery ? (
            /* ── 검색 결과 ── */
            <div>
              <div className="flex justify-between items-end mb-4 px-1">
                <h2 className="text-lg font-bold text-gray-800">{lang === 'en' ? 'Search Results' : '검색 결과'}</h2>
                <span className="text-sm font-semibold text-brand">{searchResults.length}{lang === 'en' ? ' found' : '건'}</span>
              </div>
              {searchResults.length > 0 ? (
                <div className="space-y-2.5">
                  {searchResults.map((result, rIdx) => {
                    const style = getStyle(result.item.title);
                    const displayTitle = lang === 'en' ? (result.item.title_en || result.item.title) : result.item.title;
                    
                    return (
                      <button 
                        key={rIdx}
                        onClick={() => {
                          setSelectedItem(result.item);
                          setSelectedItem(result.item);
                          // if (result.sectionIdx >= 0) setSelectedSection(result.sectionIdx); // 추후 섹션 이동 기능 필요 시 주석 해제
                        }}
                        className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-left active:scale-[0.98] transition-transform"
                      >
                        <div className="flex gap-3 items-center">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${style.bgLight}`}>
                            <CategoryIcon title={result.item.title} size={20} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-gray-800 text-[14px]">{displayTitle}</h3>
                            {result.snippet && (
                              <p className="text-[12px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">{result.snippet}</p>
                            )}
                            {result.matchTitle && (
                              <p className="text-[11px] text-gray-400 mt-0.5">
                                {lang === 'en' ? `${result.item.total_pages} guides available` : `${result.item.total_pages}개 가이드 보기`}
                              </p>
                            )}
                          </div>
                          <ChevronDown size={16} className="text-gray-300 -rotate-90 shrink-0" />
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-20 flex flex-col items-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <Search className="text-gray-300" size={32} />
                  </div>
                  <p className="text-gray-500 font-semibold text-lg">{lang === 'en' ? 'No results found' : '검색 결과가 없어요'}</p>
                  <p className="text-gray-400 text-sm mt-1">{lang === 'en' ? 'Try another keyword' : '다른 키워드로 검색해 보세요'}</p>
                </div>
              )}
            </div>
          ) : (
            /* ── 홈 화면 ── */
            <div>
              {/* 긴급 배너 */}
              {emergencyItem && (
                <button
                  onClick={() => setSelectedItem(emergencyItem)}
                  className="w-full bg-gradient-to-r from-red-500 to-rose-600 text-white p-4 rounded-2xl flex items-center justify-between mb-7 shadow-md active:scale-[0.98] transition-transform"
                >
                  <div className="flex items-center gap-3">
                    <div className="bg-white/20 p-2 rounded-full"><ShieldAlert size={22} /></div>
                    <div className="text-left">
                      <p className="font-bold text-[15px]">{lang === 'en' ? '🚨 Emergency Response Guide' : '🚨 긴급 상황 시 행동요령'}</p>
                      <p className="text-[11px] text-white/80 mt-0.5">{lang === 'en' ? 'Fire · Water · Emergency' : '화재 · 단수 · 비상 시 즉시 확인'}</p>
                    </div>
                  </div>
                  <ChevronDown size={18} className="-rotate-90" />
                </button>
              )}

              {/* 아이콘 그리드 */}
              <h2 className="text-[18px] font-bold text-gray-800 mb-4 px-1">
                {lang === 'en' ? 'Quick Solutions' : '자주 찾는 해결법'}
              </h2>
              <div className="grid grid-cols-4 gap-y-5 gap-x-2 mb-8">
                {['TV, WIFI', '냉난방기', '도어락', '전기', '누수', '욕실', '냄새_해충', '생활수칙'].map(title => {
                  const style = getStyle(title);
                  const item = manualData.find((m: any) => m.title === title);
                  const displayTitle = lang === 'en' ? (item?.title_en || title) : title;
                  return (
                    <button key={title} onClick={() => item && setSelectedItem(item)} className="flex flex-col items-center gap-2 transition-transform active:scale-90">
                      <div className={`w-14 h-14 bg-gradient-to-br ${style.gradient} rounded-2xl shadow-md flex items-center justify-center text-white`}>
                        <CategoryIcon title={title} size={28} />
                      </div>
                      <span className="text-[11px] font-semibold text-gray-600 text-center leading-tight">
                        {displayTitle.replace('_', '/')}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* 시설 문제 해결 */}
              <h2 className="text-[18px] font-bold text-gray-800 mb-3 px-1">
                {lang === 'en' ? '🔧 Facility Troubleshooting' : '🔧 시설 문제 해결'}
              </h2>
              <div className="space-y-2.5 mb-8">
                {facilityItems.map((item: any) => (
                  <CategoryListItem key={item.filename} item={item} onClick={() => setSelectedItem(item)} lang={lang} />
                ))}
              </div>

              {/* 생활 가이드 */}
              <h2 className="text-[18px] font-bold text-gray-800 mb-3 px-1">
                {lang === 'en' ? '📋 Living Guide' : '📋 생활 가이드'}
              </h2>
              <div className="space-y-2.5 mb-8">
                {livingItems.map((item: any) => (
                  <CategoryListItem key={item.filename} item={item} onClick={() => setSelectedItem(item)} lang={lang} />
                ))}
              </div>
            </div>
          )}
        </main>

        <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} onHome={() => { setSearchQuery(''); setActiveTab('home'); }} lang={lang} />
      </div>
    </div>
  );
}

/* ── 하단 네비게이션 ── */
function BottomNav({ activeTab, setActiveTab, onHome, lang }: { activeTab: string; setActiveTab: (t: string) => void; onHome: () => void; lang: Lang }) {
  const tabs = [
    { id: 'home', icon: Home, label: lang === 'en' ? 'Home' : '홈', action: onHome },
    { id: 'facility', icon: Map, label: lang === 'en' ? 'Facility' : '시설안내', action: () => setActiveTab('facility') },
    { id: 'life', icon: BookOpen, label: lang === 'en' ? 'Rules' : '생활수칙', action: () => setActiveTab('life') },
    { id: 'settings', icon: Settings, label: lang === 'en' ? 'More' : '더보기', action: () => setActiveTab('settings') },
  ];
  return (
    <div className="absolute bottom-0 w-full bg-white/90 backdrop-blur-xl border-t border-gray-100 shadow-[0_-10px_30px_-10px_rgba(0,0,0,0.08)] shrink-0 z-50">
      <div className="flex justify-around items-center h-16 pt-1">
        {tabs.map(tab => {
          const TabIcon = tab.icon;
          return (
            <button key={tab.id} onClick={tab.action} className={`flex flex-col items-center gap-1 w-16 transition-colors ${activeTab === tab.id ? 'text-brand-vibrant' : 'text-gray-400'}`}>
              <TabIcon size={activeTab === tab.id ? 24 : 22} strokeWidth={activeTab === tab.id ? 2.5 : 1.8} />
              <span className={`text-[10px] ${activeTab === tab.id ? 'font-bold' : 'font-medium'}`}>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default App;
