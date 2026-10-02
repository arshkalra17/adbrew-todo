import { useCallback, useEffect, useRef, useState } from 'react';

import { createTodo, fetchTodos } from '../api/todos';

// Owns the todo list state and how it is loaded, so components only render.
export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const inFlightRequest = useRef(null);

  const refresh = useCallback(async () => {
    // If an older request is still running, cancel it so a slow, stale
    // response can never overwrite a newer one.
    inFlightRequest.current?.abort();
    const controller = new AbortController();
    inFlightRequest.current = controller;

    setIsLoading(true);
    try {
      const items = await fetchTodos({ signal: controller.signal });
      if (controller.signal.aborted) return;
      setTodos(items);
      setError(null);
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(err.message);
    } finally {
      if (!controller.signal.aborted) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    // Cancel the pending request if the component unmounts.
    return () => inFlightRequest.current?.abort();
  }, [refresh]);

  // Re-fetches from the server instead of appending locally, so the list
  // always shows what is actually stored in MongoDB.
  const addTodo = useCallback(
    async (description) => {
      await createTodo(description);
      await refresh();
    },
    [refresh]
  );

  return { todos, isLoading, error, refresh, addTodo };
}
