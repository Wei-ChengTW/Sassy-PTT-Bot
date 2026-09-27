import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Chart as ChartJS } from 'chart.js'
import App from './App.vue'
import router from './router'
import { CHART_FONT, CHART_TEXT, CHART_GRID } from './constants/chartColors'
import './style.css'

// 圖表全域樣式：與介面同字體、灰階格線，折線走直線段
ChartJS.defaults.font.family = CHART_FONT
ChartJS.defaults.font.size = 11
ChartJS.defaults.color = CHART_TEXT
ChartJS.defaults.borderColor = CHART_GRID
ChartJS.defaults.set('elements.line', { tension: 0 })
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) ChartJS.defaults.animation = false
ChartJS.defaults.set('elements.bar', { borderRadius: 2 })
ChartJS.defaults.set('plugins.tooltip', {
  backgroundColor: '#1E3A2F',
  cornerRadius: 4,
  titleFont: { family: CHART_FONT, weight: 'bold' },
  bodyFont: { family: CHART_FONT },
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
