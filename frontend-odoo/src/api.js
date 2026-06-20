// src/api.js
const API_BASE_URL = 'http://localhost:8000'; // Default FastAPI URL

function getTokens() {
  return {
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
  };
}

function setTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  if (refresh) {
    localStorage.setItem('refresh_token', refresh);
  }
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.dispatchEvent(new Event('auth_changed'));
}

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token) {
  refreshSubscribers.map(cb => cb(token));
  refreshSubscribers = [];
}

export async function apiFetch(endpoint, options = {}) {
  const { accessToken } = getTokens();
  const headers = new Headers(options.headers || {});
  
  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const config = {
    ...options,
    headers,
  };

  try {
    let response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Handle 401 Unauthorized (Token Expiry)
    if (response.status === 401) {
      const { refreshToken } = getTokens();
      if (!refreshToken) {
        clearTokens();
        throw new Error('Unauthorized');
      }

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
          });
          if (res.ok) {
            const data = await res.json();
            setTokens(data.access_token, data.refresh_token);
            isRefreshing = false;
            onRefreshed(data.access_token);
          } else {
            clearTokens();
            isRefreshing = false;
            throw new Error('Session expired');
          }
        } catch (e) {
          clearTokens();
          isRefreshing = false;
          throw e;
        }
      }

      // Wait for the token refresh to finish, then retry
      const newAccessToken = await new Promise(resolve => {
        subscribeTokenRefresh(token => {
          resolve(token);
        });
      });

      config.headers.set('Authorization', `Bearer ${newAccessToken}`);
      response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    }

    if (!response.ok) {
      let errorMsg = 'An error occurred';
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch (e) {}
      throw new Error(errorMsg);
    }

    // Handle 204 No Content
    if (response.status === 204) return null;

    const resData = await response.json();
    if (resData && resData.success !== undefined && resData.data !== undefined) {
      return resData.data;
    }
    return resData;
  } catch (error) {
    if (!window.navigator.onLine) {
      throw new Error('Network error: You appear to be offline.');
    }
    throw error;
  }
}
