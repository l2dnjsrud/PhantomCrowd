<template>
  <div class="home">
    <!-- Mode Tabs -->
    <div class="mode-tabs">
      <button :class="{ active: mode === 'campaign' }" @click="mode = 'campaign'">{{ $t('tabs.campaign') }}</button>
      <button :class="{ active: mode === 'single' }" @click="mode = 'single'">{{ $t('tabs.quickTest') }}</button>
      <button :class="{ active: mode === 'ab' }" @click="mode = 'ab'">{{ $t('tabs.abTest') }}</button>
    </div>

    <!-- Campaign v2 -->
    <section v-if="mode === 'campaign'" class="card create-section">
      <h2>{{ $t('campaign.title') }}</h2>
      <p class="subtitle">{{ $t('campaign.subtitle') }}</p>

      <form @submit.prevent="startCampaign" class="form">
        <div class="form-group">
          <label>{{ $t('campaign.form.title') }}</label>
          <input v-model="campaignForm.title" :placeholder="$t('campaign.form.titlePlaceholder')" required />
        </div>

        <div class="form-row form-row-3">
          <div class="form-group">
            <label>{{ $t('campaign.form.contentType') }}</label>
            <select v-model="campaignForm.content_type">
              <option value="social_post">{{ $t('contentTypes.social_post') }}</option>
              <option value="ad_copy">{{ $t('contentTypes.ad_copy') }}</option>
              <option value="product_launch">{{ $t('contentTypes.product_launch') }}</option>
              <option value="press_release">{{ $t('contentTypes.press_release') }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ $t('campaign.form.llmAgents') }}</label>
            <select v-model.number="campaignForm.llm_agents">
              <option :value="5">5 ({{ $t('common.quick') }})</option>
              <option :value="10">10 ({{ $t('common.default') }})</option>
              <option :value="20">20 ({{ $t('common.deep') }})</option>
              <option :value="50">50</option>
              <option :value="100">100 (Max)</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ $t('campaign.form.language') }}</label>
            <select v-model="campaignForm.language">
              <option value="en">{{ $t('languages.en') }}</option>
              <option value="ko">{{ $t('languages.ko') }}</option>
              <option value="ja">{{ $t('languages.ja') }}</option>
              <option value="zh">{{ $t('languages.zh') }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>{{ $t('campaign.form.content') }}</label>
          <textarea v-model="campaignForm.content" :placeholder="$t('campaign.form.contentPlaceholder')" rows="4" required></textarea>
        </div>

        <div class="form-group">
          <label>{{ $t('campaign.form.context') }}</label>
          <textarea v-model="campaignForm.context_text" :placeholder="$t('campaign.form.contextPlaceholder')" rows="4"></textarea>
        </div>

        <div class="form-group">
          <label>
            {{ contextFileLabel }}
            <span class="file-hint">PDF, MD, TXT (max 10MB)</span>
          </label>
          <div class="file-upload-row">
            <input type="file" ref="fileInput" accept=".pdf,.md,.markdown,.txt,.text,.csv" @change="handleFileSelect" class="file-input" />
            <button type="button" class="btn-upload" @click="($refs.fileInput as HTMLInputElement)?.click()">
              {{ selectedFile ? selectedFile.name : uploadBtnLabel }}
            </button>
            <span v-if="selectedFile" class="file-selected">{{ (selectedFile.size / 1024).toFixed(0) }}KB</span>
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? $t('campaign.form.starting') : $t('campaign.form.submit') }}
        </button>
      </form>
    </section>

    <!-- Single Simulation -->
    <section v-if="mode === 'single'" class="card create-section">
      <h2>{{ $t('simulation.title') }}</h2>
      <p class="subtitle">{{ $t('simulation.subtitle') }}</p>

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
          {{ loading ? $t('simulation.form.starting') : $t('simulation.form.submit') }}
        </button>
      </form>
    </section>

    <!-- A/B Test -->
    <section v-if="mode === 'ab'" class="card create-section">
      <h2>{{ $t('abTest.title') }}</h2>
      <p class="subtitle">{{ $t('abTest.subtitle') }}</p>

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
          {{ loading ? $t('abTest.form.starting') : $t('abTest.form.submit') }}
        </button>
      </form>
    </section>

    <!-- Past Simulations -->
    <section v-if="simulations.length || abTests.length || campaigns.length" class="history-section">
      <h3>{{ $t('nav.history') }}</h3>
      <div class="simulation-list">
        <router-link
          v-for="c in campaigns"
          :key="'camp-' + c.id"
          :to="`/campaign/${c.id}`"
          class="card sim-card"
        >
          <div class="sim-header">
            <span class="sim-title">🎯 {{ c.title }}</span>
            <span :class="`badge badge-${statusColor(c.status)}`">{{ c.status }}</span>
          </div>
          <div class="sim-meta">
            <span>Campaign v2</span>
            <span v-if="c.viral_score !== null">Viral: {{ c.viral_score }}/100</span>
            <span>{{ formatDate(c.created_at) }}</span>
          </div>
        </router-link>
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
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  createSimulation, listSimulations, createABTest, listABTests,
  createCampaign, listCampaigns, uploadCampaignFile,
  type Simulation, type ABTest as ABTestType, type Campaign,
} from '../api/client'

const router = useRouter()

const { t, locale } = useI18n()
const mode = ref<'campaign' | 'single' | 'ab'>('campaign')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const contextFileLabel = computed(() => locale.value === 'ko' ? '컨텍스트 파일 업로드 (선택)' : 'Upload Context File (optional)')
const uploadBtnLabel = computed(() => locale.value === 'ko' ? '파일 선택...' : 'Choose file...')

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}
const loading = ref(false)
const showTarget = ref(false)
const simulations = ref<Simulation[]>([])
const abTests = ref<ABTestType[]>([])
const campaigns = ref<Campaign[]>([])

const campaignForm = reactive({
  title: '',
  content: '',
  content_type: 'social_post',
  context_text: '',
  language: 'en',
  llm_agents: 10,
})

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
  const [simRes, abRes, campRes] = await Promise.all([listSimulations(), listABTests(), listCampaigns()])
  simulations.value = simRes.data
  abTests.value = abRes.data
  campaigns.value = campRes.data
})

async function startCampaign() {
  loading.value = true
  try {
    const { data } = await createCampaign(campaignForm)

    // Upload file if selected
    if (selectedFile.value) {
      try {
        await uploadCampaignFile(data.id, selectedFile.value)
      } catch {
        // File upload failed but campaign still starts
      }
    }

    router.push(`/campaign/${data.id}`)
  } finally {
    loading.value = false
  }
}

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

.file-upload-row { display: flex; align-items: center; gap: 8px; }
.file-input { display: none; }
.btn-upload {
  padding: 8px 16px; background: var(--bg-secondary); color: var(--text-secondary);
  border: 1px dashed var(--border); border-radius: 8px; font-size: 13px; cursor: pointer;
}
.btn-upload:hover { border-color: var(--accent); color: var(--accent); }
.file-selected { font-size: 12px; color: var(--text-secondary); }
.file-hint { font-size: 10px; color: var(--text-secondary); font-weight: 400; text-transform: none; letter-spacing: 0; margin-left: 8px; }

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
