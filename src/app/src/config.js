// The browser runs outside Docker, so it uses the published port, not the `api` hostname.
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Mirrors MAX_DESCRIPTION_LENGTH in todos/service.py.
export const MAX_DESCRIPTION_LENGTH = 500;
