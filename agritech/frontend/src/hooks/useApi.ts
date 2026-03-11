import axios from 'axios'
import { useState, useEffect, useCallback } from 'react'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agritech_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export { api }

export function useApi<T>(url: string, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get<T>(url)
      setData(res.data)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Erreur réseau'
      setError(msg)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, ...deps])

  useEffect(() => { fetch() }, [fetch])

  return { data, loading, error, refetch: fetch }
}
