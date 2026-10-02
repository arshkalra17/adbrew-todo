// The browser runs on the host machine, not inside Docker, so it reaches the
// API through the published port (localhost:8000), not the `api` hostname.
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Mirrors MAX_DESCRIPTION_LENGTH in the backend's todos/service.py. The backend
// is the source of truth; this only gives the user earlier feedback.
export const MAX_DESCRIPTION_LENGTH = 500;
