import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import SimulationView from './views/SimulationView.vue'
import ABTestView from './views/ABTestView.vue'
import CompareView from './views/CompareView.vue'
import CampaignView from './views/CampaignView.vue'
import GraphFullView from './views/GraphFullView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/simulation/:id', name: 'simulation', component: SimulationView },
    { path: '/ab-test/:id', name: 'ab-test', component: ABTestView },
    { path: '/compare', name: 'compare', component: CompareView },
    { path: '/campaign/:id', name: 'campaign', component: CampaignView },
    { path: '/campaign/:id/graph', name: 'graph-full', component: GraphFullView },
  ],
})

export default router
