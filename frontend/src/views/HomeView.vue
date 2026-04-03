<template>
  <div class="home">
    <!-- Create Simulation -->
    <section class="card create-section">
      <h2>New Simulation</h2>
      <p class="subtitle">Test how your content will be received by a phantom audience</p>

      <form @submit.prevent="startSimulation" class="form">
        <div class="form-group">
          <label>Title</label>
          <input v-model="form.title" placeholder="e.g. Summer campaign copy A" required />
        </div>

        <div class="form-row">
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
              <option :value="10">10 personas (Quick)</option>
              <option :value="30">30 personas</option>
              <option :value="50">50 personas (Default)</option>
              <option :value="100">100 personas</option>
              <option :value="200">200 personas (Deep)</option>
            </select>
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

        <button type="submit" class="btn-primary" :disabled="store.loading">
          {{ store.loading ? 'Starting...' : '👻 Summon Phantom Audience' }}
        </button>
      </form>
    </section>

    <!-- Past Simulations -->
    <section v-if="store.simulations.length" class="history-section">
      <h3>Past Simulations</h3>
      <div class="simulation-list">
        <router-link
          v-for="sim in store.simulations"
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'

const store = useSimulationStore()
const router = useRouter()

const form = reactive({
  title: '',
  content: '',
  content_type: 'social_post',
  audience_size: 50,
})

onMounted(() => {
  store.fetchList()
})

async function startSimulation() {
  const sim = await store.create(form)
  if (sim) {
    router.push(`/simulation/${sim.id}`)
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
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.create-section h2 {
  font-size: 20px;
  margin-bottom: 4px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 24px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.history-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: var(--text-secondary);
}

.simulation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sim-card {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  padding: 16px 20px;
}

.sim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.sim-title {
  font-weight: 600;
}

.sim-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
