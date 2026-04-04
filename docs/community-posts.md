# PhantomCrowd Community Launch Posts

---

## 1. Reddit

### r/marketing (마케팅 실무자)

**Title:** I built an open-source AI that simulates 500+ audience reactions before you publish anything

**Body:**

Hey r/marketing,

I'm an AI R&D engineer — not a marketer. I saw [MiroFish](https://github.com/666ghj/MiroFish) (48K stars), a multi-agent simulation engine that predicts anything, and thought: what if this concept was focused specifically on marketing? Instead of predicting elections or stock markets, what if you could preview how real people would react to your ad copy before spending a dollar?

I'm not a marketing expert, so I'd really appreciate feedback from people who actually do this for a living. Here's what I built: **PhantomCrowd** — an open-source AI audience simulator.

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

I'm an AI R&D engineer. Got inspired by [MiroFish](https://github.com/666ghj/MiroFish) (48K stars) — a multi-agent prediction engine — and built a marketing-focused version.

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

I'm an AI engineer, not a marketer. I saw [MiroFish](https://github.com/666ghj/MiroFish) — a multi-agent simulation engine that hit 48K GitHub stars — and thought: this concept would be perfect for content marketing.

**The problem:** You spend hours crafting content, post it, and... crickets. Or worse, backlash you didn't see coming.

**The solution:** I built **PhantomCrowd** — it summons a crowd of AI personas that react to your content like real people would.

**Features:**
- 🎯 Quick Test — paste content, get 50 persona reactions in minutes
- 🔬 A/B Test — compare two variants head-to-head
- 🌐 Campaign Mode — full multi-agent simulation with knowledge graph
- 📊 Dashboard — sentiment distribution, viral score, engagement metrics
- 🗣️ Simulate in 12 languages (Korean, Japanese, Chinese, Spanish, etc.)
- 🔒 Runs fully local with Ollama

Tech: Python + FastAPI + Vue 3 + LightRAG + camel-ai

https://github.com/l2dnjsrud/PhantomCrowd

---

### r/ClaudeAI

**Title:** I built a multi-agent audience simulator using Claude API — 500 AI personas react to your content before you post it

**Body:**

I'm an AI R&D engineer. Got inspired by [MiroFish](https://github.com/666ghj/MiroFish) (48K stars multi-agent prediction engine) and built a marketing-focused version called **PhantomCrowd**. I'm not a marketing expert — I just thought multi-agent simulation could solve a real problem in content creation.

It's an open-source tool that simulates how real audiences will react to your content.

**Works with any OpenAI-compatible API, including Claude:**
- Use **Haiku** for persona reactions (fast, cheap — handles 500 personas)
- Use **Sonnet** for persona generation, knowledge graph analysis, marketing reports
- Also works with Ollama (free, local), OpenAI, Groq, Together AI — just change the base URL and model name in `.env`

**What it actually does:**
1. You paste content (ad copy, social post, product launch)
2. It generates 10–500 personas with unique demographics, personalities, social media habits
3. Each persona reacts independently — writes comments, decides to like/share/ignore/dislike
4. In Campaign mode: personas interact with *each other* on a simulated social network (up to 100 LLM agents + 2,000 rule-based agents)
5. You get a dashboard with sentiment distribution, viral score, and improvement suggestions

The results are surprisingly realistic. A 19-year-old K-pop fan reacts very differently from a 45-year-old marketing executive — and when they interact, you get emergent behavior you can't predict from individual responses.

MIT licensed, Docker support, simulate in 12 languages.

GitHub: https://github.com/l2dnjsrud/PhantomCrowd

---

### r/LocalLLaMA

**Title:** PhantomCrowd: multi-agent audience simulator that runs 100% locally with Ollama — no paid API needed

**Body:**

I'm an AI engineer, not a marketing person. I saw [MiroFish](https://github.com/666ghj/MiroFish) (48K stars) do multi-agent simulation for general prediction, but it requires Zep Cloud and paid APIs. So I built a marketing-focused version that runs 100% locally.

**Local setup (3 commands):**
```
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
docker compose up --build
```

That's it. No API keys, no cloud services, no Zep Cloud (looking at you, MiroFish).

**What it does:**
- Generate 10–500 AI personas with unique demographics and personalities
- Each persona reacts independently to your content
- Campaign mode: up to 100 LLM agents + 2,000 rule-based agents interact on a simulated social network
- Knowledge graph (LightRAG + NetworkX) built from your content context
- Marketing report with viral score, segment analysis, recommendations

**Models used:**
- `qwen2.5:7b` for persona reactions (fast enough for 500 personas)
- `nomic-embed-text` for knowledge graph embeddings
- Any OpenAI-compatible model works — swap in `llama3.1`, `mistral`, `exaone3.5`, whatever you prefer

Stack: Python/FastAPI, Vue 3, LightRAG, camel-ai, D3.js, ECharts.

MIT licensed. No telemetry. Your data stays on your machine.

https://github.com/l2dnjsrud/PhantomCrowd

---

### r/ollama

**Title:** Built an audience simulator that uses Ollama to run 500 AI personas locally — PhantomCrowd

**Body:**

I'm an AI R&D engineer. Got inspired by [MiroFish](https://github.com/666ghj/MiroFish) but wanted something that runs fully local without Zep Cloud or paid APIs. So I built **PhantomCrowd** — a marketing-focused multi-agent simulator that runs entirely on Ollama.

**Recommended models:**
- `qwen2.5:7b` — best balance of speed and quality for persona reactions
- `exaone3.5:7.8b` — excellent for Korean language simulations
- `nomic-embed-text` — for knowledge graph embeddings

**What it does:**
- Paste your content (ad copy, social post, etc.)
- Ollama generates 10–500 AI personas that react independently
- Campaign mode: multi-agent simulation where personas argue, share, and debate
- Get a viral score, sentiment breakdown, and improvement suggestions

**Config is simple (.env):**
```
PC_LLM_BASE_URL=http://localhost:11434/v1
PC_LLM_API_KEY=ollama
PC_LLM_MODEL=qwen2.5:7b
PC_LLM_ANALYSIS_MODEL=qwen2.5:7b
```

Works with any model Ollama supports. Also compatible with OpenAI, Groq, Together AI if you want to use cloud APIs.

Docker + Ollama setup guide included. MIT licensed.

https://github.com/l2dnjsrud/PhantomCrowd

---

### r/AI_Agents

**Title:** PhantomCrowd: open-source multi-agent social simulation — 100 LLM agents + 2,000 rule-based agents interact on simulated social media

**Body:**

I'm an AI R&D engineer. Inspired by [MiroFish](https://github.com/666ghj/MiroFish) (48K stars, general-purpose multi-agent prediction), I built a marketing-specific version with a different agent architecture and no external service dependencies.

**Agent Architecture:**

The simulation uses a tiered agent model:
- **LLM Agents (up to 100):** Full personality, graph-grounded context via LightRAG, long-form reasoning. Built with camel-ai ChatAgent. Each agent has age, occupation, interests, personality traits, and social media habits.
- **Rule-Based Agents (up to 2,000):** Probability-driven behavior (share if sentiment > 0.5 AND interests overlap > 2, etc.). Creates realistic crowd dynamics without burning API calls.

**Simulation Flow:**
1. **Knowledge Graph Build** — LightRAG extracts entities and relationships from content + context
2. **Profile Generation** — Ontology-aware persona creation grounded in the knowledge graph
3. **Multi-Round Simulation** — Agents post, reply, share, like, dislike on simulated social media. Each round feeds into the next.
4. **Report Generation** — ReACT-pattern agent uses `graph_search`, `action_search`, `sentiment_aggregate` tools to produce marketing analysis
5. **Agent Interview** — Post-sim Q&A with individual agents ("Why did you share this?")

**Memory System:**
Each LLM agent maintains relationship memory — sentiment toward other agents shifts based on interactions. An agent who got criticized in round 2 might dislike in round 3.

**What makes it different from MiroFish:**
- No Zep Cloud dependency (fully local with Ollama)
- Marketing-specific (A/B testing, viral scoring, segment analysis)
- MIT license (vs AGPL-3.0)

Stack: Python/FastAPI, camel-ai, LightRAG, NetworkX, Vue 3, D3.js.

https://github.com/l2dnjsrud/PhantomCrowd

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

AI R&D 엔지니어입니다. MiroFish(GitHub 48K 스타)를 보고 영감을 받아 마케팅 특화 버전을 만들었습니다. 마케팅 전문가는 아니지만, 멀티에이전트 시뮬레이션이 콘텐츠 마케팅에 잘 맞겠다 싶어서 만들어봤습니다.

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

안녕하세요, AI R&D 엔지니어입니다. 마케팅 전문가는 아닙니다.

GitHub에서 MiroFish(48K 스타)라는 멀티에이전트 시뮬레이션 프로젝트를 보고, "이걸 마케팅에 쓰면 어떨까?" 싶어서 만들어봤습니다.

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
| 1 | r/SideProject | 가장 프로모션 친화적, 안전한 첫 게시 |
| 2 | r/ClaudeAI | Claude API 사용 프로젝트, 높은 관련성 |
| 3 | r/LocalLLaMA | Ollama 로컬 실행 강조, 대형 커뮤니티 |
| 4 | r/AI_Agents | 멀티에이전트 기술 타겟 |
| 5 | r/ollama | Ollama 전용, 니치 타겟 |
| 6 | r/artificial | 넓은 AI 커뮤니티 |
| 7 | Twitter/X thread | 빠른 확산 + 데모 GIF |
| 8 | Hacker News Show HN | 기술 커뮤니티 신뢰도 |
| 9 | GeekNews | 한국 기술 커뮤니티 |
| 10 | DEV.to 아티클 | SEO + 장기 유입 |
| 11 | r/marketing | 실사용자 피드백 |
| 12 | ProductHunt | 런칭 이벤트 |
| 13 | 클리앙 | 한국 일반 커뮤니티 |
