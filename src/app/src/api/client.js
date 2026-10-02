import { API_BASE_URL } from '../config';

export class ApiError extends Error {
  constructor(message, { status = 0, field = null } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.field = field;
  }
}

async function readJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function request(path, { method = 'GET', body, signal } = {}) {
  const options = { method, signal, headers: { Accept: 'application/json' } };
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error;
    }
    throw new ApiError('Could not reach the server. Please check that the API is running.');
  }

  const data = await readJson(response);
  if (!response.ok) {
    const message = data?.error?.message || `Request failed with status ${response.status}.`;
    throw new ApiError(message, { status: response.status, field: data?.error?.field });
  }
  return data;
}
