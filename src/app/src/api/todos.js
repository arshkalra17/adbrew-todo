import { request } from './client';

export async function fetchTodos({ signal } = {}) {
  const data = await request('/todos/', { signal });
  return data.todos;
}

export function createTodo(description) {
  return request('/todos/', { method: 'POST', body: { description } });
}
