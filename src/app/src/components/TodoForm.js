import { useState } from 'react';

import { MAX_DESCRIPTION_LENGTH } from '../config';

export function TodoForm({ onSubmit }) {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed) {
      setError('Please enter a description.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(trimmed);
      setDescription('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="todo-description">ToDo:</label>
      <input
        id="todo-description"
        type="text"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        maxLength={MAX_DESCRIPTION_LENGTH}
        disabled={isSubmitting}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? 'todo-form-error' : undefined}
      />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Adding…' : 'Add ToDo!'}
      </button>
      {error && (
        <p id="todo-form-error" className="error" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
