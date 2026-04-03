# 👻 PhantomCrowd

**AI Audience Simulator** — Preview how your content will be received before publishing.

PhantomCrowd summons a crowd of AI-powered personas that react to your content like real people would. Get sentiment analysis, engagement predictions, viral scores, and actionable suggestions — all before you hit "Post".

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Vue](https://img.shields.io/badge/Vue-3-green)
![Claude](https://img.shields.io/badge/Powered%20by-Claude-blueviolet)
![License](https://img.shields.io/badge/License-MIT-yellow)

## How It Works

```
Your Content → 👻 Phantom Personas Generated → 💬 Each Reacts Independently → 📊 Analysis Dashboard
```

1. **Input** your content (ad copy, social post, product launch, email campaign...)
2. **PhantomCrowd generates** 10–500 diverse AI personas with unique demographics and personalities
3. **Each persona reacts** independently — comments, sentiment, engagement decisions
4. **Dashboard shows** sentiment distribution, viral score, engagement rate, and improvement suggestions

## Features

- **Multi-Persona Simulation** — Each phantom has age, occupation, interests, personality, and social media habits
- **Real-Time Progress** — Watch personas react one by one
- **Sentiment Analysis** — Positive / Negative / Neutral / Mixed breakdown with scores
- **Viral Score** — 0-100 prediction of content spread potential
- **Engagement Metrics** — Like / Share / Ignore / Dislike distribution
- **AI Suggestions** — Actionable improvements based on audience reactions
- **Dark UI** — Built for focus

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- [Anthropic API Key](https://console.anthropic.com/)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/YOUR_USERNAME/PhantomCrowd.git
cd PhantomCrowd

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 2. Setup Frontend

```bash
cd ../frontend
npm install
```

### 3. Run

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open http://localhost:5173

### Docker

```bash
export PC_ANTHROPIC_API_KEY=your-key-here
docker compose up --build
```

Open http://localhost:8000

## Architecture

```
PhantomCrowd/
├── backend/
│   └── app/
│       ├── api/            # FastAPI endpoints
│       ├── core/           # Config, database
│       ├── models/         # SQLAlchemy models
│       ├── schemas/        # Pydantic schemas
│       └── services/       # Persona generator, simulation engine
├── frontend/
│   └── src/
│       ├── api/            # API client
│       ├── components/     # ECharts visualizations
│       ├── stores/         # Pinia state management
│       └── views/          # Home + Simulation dashboard
└── docker-compose.yml
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simulations/` | Create & start simulation |
| GET | `/api/simulations/` | List all simulations |
| GET | `/api/simulations/{id}` | Get simulation with reactions |
| GET | `/api/simulations/{id}/progress` | Poll simulation progress |
| DELETE | `/api/simulations/{id}` | Delete simulation |

## Cost Estimation

PhantomCrowd uses Claude Haiku for persona reactions (cheap & fast) and Claude Sonnet for analysis (high quality).

| Audience Size | Estimated Cost |
|---------------|---------------|
| 10 personas | ~$0.02 |
| 50 personas | ~$0.08 |
| 100 personas | ~$0.15 |
| 200 personas | ~$0.30 |

## Roadmap

- [ ] Image content analysis (upload screenshots, ads)
- [ ] A/B testing — compare multiple content versions
- [ ] Custom persona templates (target specific demographics)
- [ ] Export reports (PDF, CSV)
- [ ] Ollama support for local/free inference
- [ ] Multi-language audience simulation
- [ ] Historical trend analysis

## License

MIT

---

Built with Claude API by Anthropic
