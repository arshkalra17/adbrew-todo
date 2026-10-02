import { useCallback, useEffect, useRef, useState } from 'react';

import { createTodo, fetchTodos } from '../api/todos';

export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const inFlightRequest = useRef(null);

  const refresh = useCallback(async () => {
    // Cancel any older request so a stale response can't overwrite a newer one.
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
    return () => inFlightRequest.current?.abort();
  }, [refresh]);

  const addTodo = useCallback(
    async (description) => {
      await createTodo(description);
      await refresh();
    },
    [refresh]
  );

  return { todos, isLoading, error, refresh, addTodo };
}
