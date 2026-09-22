import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'X-CareWise-Key': 'carewise-demo-secret-2026',
  },
  timeout: 15000,
});

export default api;
