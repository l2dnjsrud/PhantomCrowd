# PhantomCrowd Community Launch Posts

---

## 1. Reddit

### r/marketing (마케팅 실무자)

**Title:** I built an open-source AI that simulates 500+ audience reactions before you publish anything

**Body:**

Hey r/marketing,

I got tired of guessing whether my content would land. So I built **PhantomCrowd** — an open-source AI audience simulator.

**How it works:**
1. Paste your content (ad copy, social post, product launch, whatever)
2. PhantomCrowd generates 10–500 AI personas with unique demographics, personalities, and social media habits
3. Each persona reacts independently — writes comments, decides to like/share/ignore
4. You get a dashboard: sentiment breakdown, viral score (0-100), engagement rate, and actionable suggestions

**What makes it different from a survey:**
- It's instant (no waiting for responses)
- Personas interact with *each other* on a simulated social network (v2 Campaign mode)
- It builds a knowledge graph from your content context, so reactions are grounded in real-world relationships
- Fully local — runs on Ollama, no data leaves your machine

**Example output:**
> "Viral Score 82/100. 18-24 segment drove 70% of shares. Recommendation: add a dance challenge hook."

It's MIT licensed, free, and runs locally. Built with Python + Vue 3.

GitHub: https://github.com/l2dnjsrud/PhantomCrowd

Would love feedback from actual marketers — does this solve a real pain point for you?

---

### r/artificial (AI 커뮤니티)

**Title:** PhantomCrowd: Multi-agent social simulation with knowledge graphs — simulate how content spreads before publishing

**Body:**

Built an open-source multi-agent simulation platform for content marketing.

**Architecture:**
- **Knowledge Graph** (LightRAG + NetworkX) — auto-extracts entities and relationships from content + context
- **Multi-Agent Simulation** (camel-ai) — up to 100 LLM agents with full personalities + 2,000 rule-based agents interact on a simulated social network
- **Report Agent** (ReACT pattern) — uses graph_search, action_search, and sentiment_aggregate tools to generate marketing reports
- **Tiered Agent Model** — LLM agents drive conversation, rule-based agents create realistic crowd dynamics

The simulation runs in rounds. Agents post, reply, share, like, and argue with each other. You can watch it happen live, then interview individual agents afterward ("Why did you share this?").

Stack: Python (FastAPI), Vue 3, D3.js (force-directed graph), ECharts, Ollama (fully local).

GitHub: https://github.com/l2dnjsrud/PhantomCrowd

---

### r/SideProject

**Title:** I built PhantomCrowd — an AI audience simulator that tells you if your content will go viral before you post it

**Body:**

**The problem:** You spend hours crafting content, post it, and... crickets. Or worse, backlash you didn't see coming.

**The solution:** PhantomCrowd summons a crowd of AI personas that react to your content like real people would.

**Features:**
- 🎯 Quick Test — paste content, get 50 persona reactions in minutes
- 🔬 A/B Test — compare two variants head-to-head
- 🌐 Campaign Mode — full multi-agent simulation with knowledge graph
- 📊 Dashboard — sentiment distribution, viral score, engagement metrics
- 🗣️ 12 languages supported
- 🔒 Runs fully local with Ollama

Tech: Python + FastAPI + Vue 3 + LightRAG + camel-ai

https://github.com/l2dnjsrud/PhantomCrowd

---

### r/ChatGPT / r/ClaudeAI

**Title:** I used LLMs to simulate 500 people reacting to content — here's what I learned building PhantomCrowd

**Body:**

Instead of asking one LLM "will this content work?", I made up to 500 LLM-powered personas with different ages, jobs, personalities, and social media habits react independently.

The results are surprisingly realistic. A 19-year-old K-pop fan reacts very differently from a 45-year-old marketing executive — and when they interact with each other on a simulated social network, you get emergent behavior you can't predict from individual responses.

Key insight: **diversity of personas matters more than the number.** 50 well-constructed personas give better signal than 200 generic ones.

Open source, runs locally with Ollama: https://github.com/l2dnjsrud/PhantomCrowd

---

## 2. Hacker News

**Title:** Show HN: PhantomCrowd – Multi-agent audience simulator with knowledge graphs

**Body:**

PhantomCrowd is an open-source platform that simulates how content will be received before you publish it.

Instead of surveys or focus groups, it generates AI personas with distinct demographics and personalities, builds a knowledge graph from your content context, and runs a multi-agent simulation where personas interact with each other on a simulated social network.

Architecture:
- Knowledge graph (LightRAG + NetworkX) for entity/relationship extraction
- Tiered agents: up to 100 LLM agents (camel-ai) + 2,000 rule-based agents
- 5-stage pipeline: Graph Build → Persona Generation → Simulation → Report → Interview
- ReACT-pattern report agent with graph_search and sentiment_aggregate tools

Runs fully local with Ollama. No paid API required.

Stack: Python/FastAPI, Vue 3, D3.js, ECharts.

https://github.com/l2dnjsrud/PhantomCrowd

---

## 3. Twitter/X

### Thread (메인 트윗)

**Tweet 1:**
What if you could test your marketing on 500 AI personas before spending $1?

I built PhantomCrowd — an open-source AI audience simulator.

Paste your content → 👻 phantom personas react → 📊 viral score + suggestions

It's like a focus group that takes 2 minutes instead of 2 weeks.

🔗 github.com/l2dnjsrud/PhantomCrowd

**Tweet 2:**
How it works:

1/ Build a knowledge graph from your content + context
2/ Spawn up to 100 LLM agents + 2,000 rule-based agents
3/ They post, reply, share, argue on simulated social media
4/ Watch it happen live
5/ Get a marketing report with viral score

Not a survey. A simulation.

**Tweet 3:**
The "aha moment":

A simulated 19yo K-pop fan shared the post 3x.
A simulated 45yo exec ignored it.
A simulated 28yo journalist quoted it with criticism.

Each persona has unique personality, interests, and social media habits.

Emergent behavior > individual predictions.

**Tweet 4:**
Tech stack for nerds:
- LightRAG (knowledge graph)
- camel-ai (multi-agent)
- Ollama (fully local, free)
- FastAPI + Vue 3 + D3.js
- ECharts for dashboards

MIT licensed. Run it on your laptop.

---

### One-shot tweets (단독 트윗용)

**Version A (호기심 유발):**
I simulated 500 people reacting to a product launch.

The AI predicted the 18-24 segment would drive 70% of shares.

The suggestion: "add a dance challenge hook."

This is PhantomCrowd — open-source AI audience simulator.
github.com/l2dnjsrud/PhantomCrowd

**Version B (문제 제기):**
Marketers spend $50K on focus groups that take 6 weeks.

PhantomCrowd does it in 2 minutes with AI personas that interact with each other.

Free. Open source. Runs locally.
github.com/l2dnjsrud/PhantomCrowd

---

## 4. DEV.to Article

**Title:** I Built an AI That Simulates 500 People Reacting to Your Content Before You Post It

**Tags:** ai, opensource, marketing, webdev

**Body outline:**

1. **The Problem** — Content creation is a guessing game
2. **The Idea** — What if you had a focus group on demand?
3. **Architecture Deep Dive**
   - Knowledge Graph layer (LightRAG)
   - Multi-Agent Simulation (camel-ai, tiered model)
   - Report Agent (ReACT pattern)
   - Dashboard (Vue 3 + D3.js + ECharts)
4. **Demo walkthrough** with screenshots
5. **Interesting findings** — emergent behavior, persona diversity > quantity
6. **How to run it** — 3 commands, fully local
7. **Roadmap** — what's next
8. **Call to action** — star, contribute, feedback

---

## 5. 한국 커뮤니티

### GeekNews (긱뉴스)

**Title:** PhantomCrowd - 콘텐츠 올리기 전에 AI 가상 관객 반응 미리 보기

**Body:**

오픈소스 AI 오디언스 시뮬레이터입니다.

광고 카피, SNS 포스트, 제품 런칭 문구를 넣으면 AI 페르소나 수백 명이 각자 독립적으로 반응합니다.

v1: 빠른 테스트 (10~500명 반응) + A/B 테스트 + 12개 언어 지원
v2: 지식 그래프(LightRAG) + 멀티에이전트 시뮬레이션(camel-ai) + 마케팅 리포트 자동 생성

특징:
- 에이전트들이 서로 대화하고, 공유하고, 반박하는 소셜 시뮬레이션
- D3.js 지식 그래프 시각화 + 실시간 액션 피드
- Ollama 지원으로 완전 로컬 실행 가능 (무료)
- MIT 라이선스

스택: Python(FastAPI) + Vue 3 + LightRAG + camel-ai

GitHub: https://github.com/l2dnjsrud/PhantomCrowd

---

### 클리앙 (모두의공원)

**Title:** [공유] 콘텐츠 반응 예측하는 AI 시뮬레이터 만들었습니다

**Body:**

안녕하세요, AI 엔지니어입니다.

마케팅할 때 "이 문구가 먹힐까?" 항상 고민되잖아요.
그래서 AI 페르소나 수백 명이 미리 반응해주는 시뮬레이터를 만들었습니다.

**PhantomCrowd**

- 광고 문구, SNS 포스트, 제품 설명 등 아무 콘텐츠나 넣으면
- 나이/성별/직업/관심사/성격이 다른 AI 페르소나들이
- 각자 좋아요/공유/무시/싫어요 + 댓글을 달아줍니다

결과로 바이럴 스코어, 감정 분포, 개선 제안까지 나옵니다.

v2에서는 페르소나들이 서로 대화하고 공유하는 소셜 네트워크 시뮬레이션도 됩니다.

오픈소스(MIT), Ollama로 로컬 실행 가능해서 무료입니다.

GitHub: https://github.com/l2dnjsrud/PhantomCrowd

피드백 주시면 감사하겠습니다 🙏

---

## 6. ProductHunt

**Tagline:** Test your content on 500 AI personas before you post it

**Description:**

PhantomCrowd is an open-source AI audience simulator. Paste your content, and hundreds of AI personas with unique demographics and personalities react independently.

**Key Features:**
- 🎯 Quick Test — instant persona reactions
- 🔬 A/B Testing — compare content variants
- 🧠 Knowledge Graph — context-aware simulation
- 🤖 Multi-Agent — personas interact with each other
- 📊 Viral Score + Marketing Report
- 🔒 Fully local with Ollama

**Who it's for:**
- Content marketers
- Social media managers
- Startup founders
- Product managers
- Anyone who creates content

**Pricing:** Free & Open Source (MIT)

---

## 게시 우선순위

| 순서 | 채널 | 이유 |
|------|------|------|
| 1 | Twitter/X thread | 빠른 확산 + 데모 GIF 첨부 가능 |
| 2 | r/SideProject + r/artificial | 얼리어답터 유입 |
| 3 | Hacker News Show HN | 기술 커뮤니티 신뢰도 |
| 4 | GeekNews | 한국 기술 커뮤니티 |
| 5 | DEV.to 아티클 | SEO + 장기 유입 |
| 6 | ProductHunt | 런칭 이벤트 |
| 7 | r/marketing | 실사용자 피드백 |
| 8 | 클리앙 | 한국 일반 커뮤니티 |
