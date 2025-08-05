// frontend/src/main.js
// Vue 앱 초기화 및 전역 설정

import './styles/main.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Vue 앱 인스턴스 생성
const app = createApp(App)

// Pinia 상태 관리 설정
app.use(createPinia())

// Vue Router 설정
app.use(router)

// 앱을 DOM에 마운트
app.mount('#app')
