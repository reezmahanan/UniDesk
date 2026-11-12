export async function apiRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const defaultHeaders: Record<string, string> = {
    'Accept': 'application/json',
  }

  // If not uploading FormData, set Content-Type
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json'
  }

  // Include CSRF token if cookie exists
  const csrfMatch = document.cookie.match(/apex_csrf_token=([^;]+)/)
  if (csrfMatch) {
    defaultHeaders['X-CSRF-Token'] = csrfMatch[1]
  }

  // Check if token exists in localStorage (or rely on HttpOnly cookie)
  const token = localStorage.getItem('apex_token')
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  })

  if (!response.ok) {
    let errorDetail = 'Request failed'
    try {
      const errJson = await response.json()
      errorDetail = errJson.detail || JSON.stringify(errJson)
    } catch {
      errorDetail = response.statusText || String(response.status)
    }
    throw new Error(errorDetail)
  }

  // Handle empty bodies (e.g. 204 or file download)
  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return (await response.json()) as T
  }
  return {} as T
}
