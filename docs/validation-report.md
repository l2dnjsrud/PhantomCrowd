# PhantomCrowd Validation Report

Date: 2026-04-04
Engine: Crowd Pulse v1 (rule→LLM feedback loop)
LLM: exaone3.5:7.8b via Ollama (local)
Agents: 100 LLM + 2,000 Rule-based per test

## Test Results

| # | Content | Context | Viral Score | Sentiment | Actions | Time |
|---|---------|---------|-------------|-----------|---------|------|
| 1 | Nike "Just Do It" | Yes (70%+ positive hint) | 85/100 | Strong positive | 9,630 | ~1min |
| 2 | Nike "Just Do It" | None (blind) | 85/100 | Strong positive | 9,546 | ~1min |
| 3 | ZapBrew (fictional product) | None (blind) | 85/100 | Positive, cautious | 9,546 | ~1.5min |
| 4 | EliteGrind (aggressive ad) | None (blind) | 65/100 | Mixed, pricing backlash | 9,546 | ~1.5min |

## Key Findings

### What Works
- Crowd Pulse feedback loop operational: rule-based agent momentum visible in LLM agent responses
- Sentiment direction is correct: good content scores higher than bad content
- Qualitative insights are strong: specific recommendations, segment analysis, influencer identification
- Report sections are detailed and actionable (6 sections per report)
- 10 rounds x 2,100 agents = ~9,500 actions generated reliably

### Issues Found
1. **Score compression**: All scores cluster between 65-85. Expected range: 15-95
2. **Positive bias**: Aggressive/offensive ad copy scored 65 (should be 20-30)
3. **Score stickiness**: Nike with/without context = identical 85 (good AND bad signal)
4. **LLM knowledge leakage**: Nike results may be influenced by LLM's training data

### Root Cause
Report agent's viral score prompt lacks calibration anchors. The LLM defaults to "somewhat high" scores without clear examples of what 20, 50, 80 mean.

## Score Calibration Fix

### What Changed
- Added strict 0-100 calibration scale with 8 anchor ranges to both report_agent.py and simulation_engine.py
- Injected actual sentiment stats (avg_score, positive_ratio, negative_ratio, engagement_rate) into scoring prompt
- Added hard rules: "if avg sentiment < 0.3, score cannot exceed 60"
- Added penalty: "if negative > 20%, subtract 15+ points"
- Added content-aware rule: "offensive/exclusionary content scores below 30 regardless"

### Calibration Results

| Content | Before Fix | After Fix | Change | Expected |
|---------|-----------|-----------|--------|----------|
| Nike "Just Do It" | 85 | **78** | -7 | 70-85 (iconic campaign) |
| EliteGrind (aggressive) | 65 | **16** | **-49** | 15-25 (offensive ad) |

**Score spread: 20 points → 62 points.** Calibration working as intended.

### Calibration Scale Reference
| Range | Meaning | Example |
|-------|---------|---------|
| 0-15 | Actively harmful | Brand-damaging, boycott-worthy |
| 16-30 | Poor | Offensive, tone-deaf |
| 31-45 | Below average | Forgettable, weak |
| 46-55 | Average | OK but nothing special |
| 56-70 | Good | Solid campaign |
| 71-85 | Very good | Strong viral potential |
| 86-95 | Excellent | Cultural moment |
| 96-100 | Legendary | "Just Do It" / "Think Different" level |

## Korean Language Tests

Date: 2026-04-04
LLM: exaone3.5:7.8b (Korean-optimized)
Language: ko

### Test Results (Korean)

| # | Content | Context | Viral Score | Language | Key Finding |
|---|---------|---------|-------------|----------|-------------|
| 5 | 삼성 Galaxy S25 (영어 리포트) | Yes | 78 | Report: EN, Comments: KO | 리포트 언어 미지원 시점 |
| 6 | 삼성 Galaxy S25 (한국어 리포트) | Yes | 80 | **All KO** | 리포트 한국어 정상 작동 |
| 7 | 배달의민족 Quick Test | None | 57 | **All KO** | Quick Test 한국어 정상 |
| 8 | 쿠팡 로켓배송 (성공 사례) | Yes | 65 | **All KO** | 긍정적, 품질 불만 감지 |
| 9 | 성차별 도시락 광고 (실패 사례) | Yes (논란 context) | **67** | **All KO** | **문제 발견** |

### Korean Test: What Works

- 에이전트 댓글 한국어 자연스러움: "와오! 갤럭시 S25 울트라의 AI 기능 정말 멋지네요!"
- 한국어 이름 생성: 이지은, 강하은, 정시우, 김상훈 등
- 리포트 전체 한국어: 섹션 제목("감성 분석 심층 탐구"), 요약, 추천사항
- 세그먼트 분석 정확: "26-45세 긍정적, 15-25세 기대치 불일치" (Galaxy S25)
- 쿠팡 테스트: 제품 품질 불만, 피크 시간대 프로모션 등 한국 시장 맥락 반영

### Korean Test: Critical Issue Found

**Test #9: 성차별 도시락 광고 — 점수 보정 실패**

- Content: "남자라면 이 정도는 먹어야지. 여자들은 모르는 그 맛. 사나이 전용."
- Context: "성별 고정관념 마케팅 논란, 불매운동 사례" 명시적 제공
- Expected Score: 15-25 (한국 사회에서 불매운동 수준의 논란)
- **Actual Score: 67** (쿠팡 65보다 높음)

**Agent reaction sample:**
> @김상훈 [positive]: "와 대박! 진짜 사나이 도시락이라니 진짜 남자들 입맛에 딱 맞는 거 같아요."

**Root Cause Analysis:**
1. **페르소나 다양성 부족**: 여성 페르소나, 젠더 이슈 민감 페르소나가 비판적으로 반응하지 않음
2. **LLM 한계 (exaone3.5:7.8b)**: 7B 모델이 한국 사회의 젠더 감수성 맥락을 충분히 반영하지 못함
3. **Calibration 규칙 미작동**: "offensive/exclusionary content scores below 30" 규칙이 있으나, LLM이 이 콘텐츠를 offensive로 인식하지 못한 것으로 추정
4. **Context 무시**: "불매운동" 정보를 context로 줬으나 시뮬레이션 결과에 반영되지 않음

**Implication:**
- 현재 시스템은 **명시적 공격(욕설, 차별 발언)은 감지**하나 (EliteGrind → 16점)
- **문화적 맥락에 따른 미묘한 논란**은 감지 실패 (성별 고정관념 → 67점)
- 더 큰 모델(70B+)이나 문화적 감수성 프롬프트 강화 필요
- 또는 별도의 "controversy detector" 레이어 추가 검토

**Honest Assessment:**
이 결과는 PhantomCrowd의 현재 한계를 보여줍니다. 직접적이고 명백한 공격적 콘텐츠(EliteGrind)는 잘 감지하지만, 사회문화적 맥락에서의 미묘한 논란(성차별 마케팅)은 7B 로컬 모델로는 정확하게 평가하기 어렵습니다. 이는 향후 개선 과제입니다.

## Summary of All Tests

| Test Type | Score Range | Calibrated? | Language? | Notes |
|-----------|-----------|-------------|-----------|-------|
| English good vs bad | 78 vs 16 | **Yes (62pt spread)** | EN | Calibration working |
| Korean good vs controversial | 65 vs 67 | **No (2pt, wrong direction)** | KO | Cultural sensitivity gap |
| Korean report language | - | - | **Full KO** | All outputs in Korean |
| Quick Test Korean | 57 | Yes | **Full KO** | Reasonable score |

**Overall: PhantomCrowd produces actionable marketing insights with correct directional signals for explicit content quality differences. Cultural/contextual sensitivity remains a known limitation with small local models.**
