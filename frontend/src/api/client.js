import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  register: (data) => client.post('/auth/register/', data),
  login: (data) => client.post('/auth/login/', data),
  profile: () => client.get('/auth/profile/'),
}

export const smsAPI = {
  analyze: (message) => client.post('/sms/analyze/', { message }),
  getDetail: (id) => client.get(`/sms/${id}/`),
  history: () => client.get('/sms/history/'),
  feedback: (data) => client.post('/sms/feedback/', data),
}

export const analyticsAPI = {
  dashboard: () => client.get('/analytics/dashboard/'),
  learning: () => client.get('/analytics/learning/'),
}

export const campaignAPI = {
  list: () => client.get('/campaigns/'),
  detect: () => client.post('/campaigns/detect/'),
}

export const chatAPI = {
  send: (message, smsId, history = []) =>
    client.post('/chat/', { message, sms_id: smsId, history }),
  status: () => client.get('/chat/status/'),
}

export const mlAPI = {
  train: (includeFeedback) => client.post('/ml/train/', { include_feedback: includeFeedback }),
}

export default client
