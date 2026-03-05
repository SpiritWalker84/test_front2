export function useApi() {
  const config = useRuntimeConfig()

  function getBase(): string {
    if (import.meta.client && typeof window !== 'undefined') {
      return `${window.location.protocol}//${window.location.hostname}:8000`
    }
    return (config.public.apiBase as string) || 'http://localhost:8000'
  }

  function get<T = unknown>(path: string): Promise<T> {
    return $fetch<T>(`${getBase()}/api/v1${path}`)
  }

  function post<T = unknown>(path: string, body?: unknown): Promise<T> {
    return $fetch<T>(`${getBase()}/api/v1${path}`, { method: 'POST', body })
  }

  function patch<T = unknown>(path: string, body: unknown): Promise<T> {
    return $fetch<T>(`${getBase()}/api/v1${path}`, { method: 'PATCH', body })
  }

  function del(path: string): Promise<void> {
    return $fetch<void>(`${getBase()}/api/v1${path}`, { method: 'DELETE' })
  }

  return { get, post, patch, del, getBase }
}
