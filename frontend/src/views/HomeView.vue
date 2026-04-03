<template>
  <div class="home">
    <!-- Mode Tabs -->
    <div class="mode-tabs">
      <button :class="{ active: mode === 'single' }" @click="mode = 'single'">Single Test</button>
      <button :class="{ active: mode === 'ab' }" @click="mode = 'ab'">A/B Test</button>
    </div>

    <!-- Single Simulation -->
    <section v-if="mode === 'single'" class="card create-section">
      <h2>New Simulation</h2>
      <p class="subtitle">Test how your content will be received by a phantom audience</p>

      <form @submit.prevent="startSimulation" class="form">
        <div class="form-group">
          <label>Title</label>
          <input v-model="form.title" placeholder="e.g. Summer campaign copy A" required />
        </div>

        <div class="form-row form-row-3">
          <div class="form-group">
            <label>Content Type</label>
            <select v-model="form.content_type">
              <option value="social_post">Social Media Post</option>
              <option value="ad_copy">Ad Copy</option>
              <option value="product_launch">Product Launch</option>
              <option value="blog_post">Blog Post</option>
              <option value="email">Email Campaign</option>
              <option value="text">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>Audience Size</label>
            <select v-model.number="form.audience_size">
              <option :value="10">10 (Quick)</option>
              <option :value="30">30</option>
              <option :value="50">50 (Default)</option>
              <option :value="100">100</option>
              <option :value="200">200 (Deep)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Language</label>
            <select v-model="form.language">
              <option value="en">English</option>
              <option value="ko">Korean</option>
              <option value="ja">Japanese</option>
              <option value="zh">Chinese</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="pt">Portuguese</option>
              <option value="ar">Arabic</option>
              <option value="hi">Hindi</option>
              <option value="vi">Vietnamese</option>
              <option value="th">Thai</option>
            </select>
          </div>
        </div>

        <!-- Target Audience -->
        <div class="form-group">
          <label>
            Target Audience (optional)
            <button type="button" class="toggle-btn" @click="showTarget = !showTarget">
              {{ showTarget ? 'Hide' : 'Configure' }}
            </button>
          </label>
          <div v-if="showTarget" class="target-grid">
            <input v-model="target.age_range" placeholder="Age range (e.g. 20-35)" />
            <input v-model="target.gender" placeholder="Gender (e.g. female)" />
            <input v-model="target.occupation" placeholder="Occupation (e.g. developer)" />
            <input v-model="target.interests" placeholder="Interests (e.g. tech, gaming)" />
          </div>
        </div>

        <div class="form-group">
          <label>Content</label>
          <textarea
            v-model="form.content"
            placeholder="Paste your content here — ad copy, social post, product description..."
            rows="5"
            required
          ></textarea>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Starting...' : '👻 Summon Phantom Audience' }}
        </button>
      </form>
    </section>

    <!-- A/B Test -->
    <section v-if="mode === 'ab'" class="card create-section">
      <h2>A/B Test</h2>
      <p class="subtitle">Compare two content variants with the same phantom audience</p>

      <form @submit.prevent="startABTest" class="form">
        <div class="form-group">
          <label>Test Title</label>
          <input v-model="abForm.title" placeholder="e.g. Summer sale — headline comparison" required />
        </div>

        <div class="form-row form-row-3">
          <div class="form-group">
            <label>Content Type</label>
            <select v-model="abForm.content_type">
              <option value="social_post">Social Media Post</option>
              <option value="ad_copy">Ad Copy</option>
              <option value="product_launch">Product Launch</option>
              <option value="blog_post">Blog Post</option>
              <option value="email">Email Campaign</option>
              <option value="text">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>Audience Size (each)</label>
            <select v-model.number="abForm.audience_size">
              <option :value="10">10 (Quick)</option>
              <option :value="30">30</option>
              <option :value="50">50 (Default)</option>
              <option :value="100">100</option>
            </select>
          </div>
          <div class="form-group">
            <label>Language</label>
            <select v-model="abForm.language">
              <option value="en">English</option>
              <option value="ko">Korean</option>
              <option value="ja">Japanese</option>
              <option value="zh">Chinese</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>
        </div>

        <div class="ab-variants">
          <div class="form-group">
            <label>Variant A</label>
            <textarea v-model="abForm.content_a" placeholder="Content variant A..." rows="4" required></textarea>
          </div>
          <div class="ab-vs">VS</div>
          <div class="form-group">
            <label>Variant B</label>
            <textarea v-model="abForm.content_b" placeholder="Content variant B..." rows="4" required></textarea>
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Starting...' : '👻 Run A/B Test' }}
        </button>
      </form>
    </section>

    <!-- Past Simulations -->
    <section v-if="simulations.length || abTests.length" class="history-section">
      <h3>History</h3>
      <div class="simulation-list">
        <router-link
          v-for="ab in abTests"
          :key="'ab-' + ab.id"
          :to="`/ab-test/${ab.id}`"
          class="card sim-card"
        >
          <div class="sim-header">
            <span class="sim-title">🔀 {{ ab.title }}</span>
            <span :class="`badge badge-${statusColor(ab.status)}`">
              {{ ab.status }}{{ ab.winner ? ` — ${ab.winner} wins` : '' }}
            </span>
          </div>
          <div class="sim-meta">
            <span>A/B Test</span>
            <span>{{ formatDate(ab.created_at) }}</span>
          </div>
        </router-link>
        <router-link
          v-for="sim in simulations"
          :key="sim.id"
          :to="`/simulation/${sim.id}`"
          class="card sim-card"
        >
          <div class="sim-header">
            <span class="sim-title">{{ sim.title }}</span>
            <span :class="`badge badge-${statusColor(sim.status)}`">{{ sim.status }}</span>
          </div>
          <div class="sim-meta">
            <span>{{ sim.audience_size }} personas</span>
            <span v-if="sim.viral_score !== null">Viral: {{ sim.viral_score }}/100</span>
            <span>{{ formatDate(sim.created_at) }}</span>
          </div>
        </router-link>
      </div>

      <router-link v-if="simulations.filter(s => s.status === 'completed').length >= 2" to="/compare" class="compare-link">
        Compare simulations →
      </router-link>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  createSimulation, listSimulations, createABTest, listABTests,
  type Simulation, type ABTest as ABTestType,
} from '../api/client'

const router = useRouter()

const mode = ref<'single' | 'ab'>('single')
const loading = ref(false)
const showTarget = ref(false)
const simulations = ref<Simulation[]>([])
const abTests = ref<ABTestType[]>([])

const form = reactive({
  title: '',
  content: '',
  content_type: 'social_post',
  audience_size: 50,
  language: 'en',
})

const target = reactive({
  age_range: '',
  gender: '',
  occupation: '',
  interests: '',
})

const abForm = reactive({
  title: '',
  content_a: '',
  content_b: '',
  content_type: 'social_post',
  audience_size: 50,
  language: 'en',
})

onMounted(async () => {
  const [simRes, abRes] = await Promise.all([listSimulations(), listABTests()])
  simulations.value = simRes.data
  abTests.value = abRes.data
})

function buildAudienceConfig() {
  if (!showTarget.value) return undefined
  const config: Record<string, string> = {}
  if (target.age_range) config.age_range = target.age_range
  if (target.gender) config.gender = target.gender
  if (target.occupation) config.occupation = target.occupation
  if (target.interests) config.interests = target.interests
  return Object.keys(config).length ? config : undefined
}

async function startSimulation() {
  loading.value = true
  try {
    const { data } = await createSimulation({
      ...form,
      audience_config: buildAudienceConfig(),
    })
    router.push(`/simulation/${data.id}`)
  } finally {
    loading.value = false
  }
}

async function startABTest() {
  loading.value = true
  try {
    const { data } = await createABTest(abForm)
    router.push(`/ab-test/${data.id}`)
  } finally {
    loading.value = false
  }
}

function statusColor(status: string) {
  if (status === 'completed') return 'positive'
  if (status === 'failed') return 'negative'
  if (status === 'running') return 'mixed'
  return 'neutral'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.mode-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 4px;
  width: fit-content;
}

.mode-tabs button {
  padding: 10px 24px;
  background: transparent;
  color: var(--text-secondary);
  border-radius: 8px;
}

.mode-tabs button.active {
  background: var(--accent);
  color: white;
}

.create-section h2 { font-size: 20px; margin-bottom: 4px; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin-bottom: 24px; }
.form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px;
  display: flex; align-items: center; gap: 8px;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-row-3 { grid-template-columns: 1fr 1fr 1fr; }

.toggle-btn {
  font-size: 11px; padding: 2px 8px; background: var(--bg-secondary);
  color: var(--accent); border-radius: 4px; text-transform: none;
  letter-spacing: 0; font-weight: 500;
}

.target-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px;
}

.ab-variants {
  display: grid; grid-template-columns: 1fr auto 1fr; gap: 16px; align-items: start;
}

.ab-vs {
  color: var(--accent); font-weight: 800; font-size: 18px;
  padding-top: 40px; text-align: center;
}

.history-section h3 { margin-bottom: 16px; font-size: 16px; color: var(--text-secondary); }
.simulation-list { display: flex; flex-direction: column; gap: 8px; }
.sim-card { text-decoration: none; color: inherit; cursor: pointer; padding: 16px 20px; }
.sim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.sim-title { font-weight: 600; }
.sim-meta { display: flex; gap: 16px; font-size: 13px; color: var(--text-secondary); }

.compare-link {
  display: block; margin-top: 12px; color: var(--accent);
  text-decoration: none; font-size: 14px;
}
.compare-link:hover { text-decoration: underline; }
</style>
