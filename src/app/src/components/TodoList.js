export function TodoList({ todos, isLoading, error, onRetry }) {
  // Only show the full loading message on the first load. On later refreshes
  // the current list stays visible instead of flashing empty.
  if (isLoading && todos.length === 0) {
    return <p className="muted">Loading TODOs…</p>;
  }

  return (
    <div aria-busy={isLoading}>
      {error && (
        <p className="error" role="alert">
          Could not load TODOs: {error}{' '}
          <button type="button" className="link-button" onClick={onRetry}>
            Try again
          </button>
        </p>
      )}
      {!error && todos.length === 0 ? (
        <p className="muted">No TODOs yet. Add one below.</p>
      ) : (
        <ul className="todo-list">
          {todos.map((todo) => (
            <li key={todo.id}>{todo.description}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
