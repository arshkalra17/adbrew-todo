import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import App from './App';
import { createTodo, fetchTodos } from './api/todos';

jest.mock('./api/todos');

const todo = (id, description) => ({ id, description, created_at: '2026-10-01T12:00:00+00:00' });

describe('App', () => {
  afterEach(() => jest.resetAllMocks());

  test('shows todos loaded from the API', async () => {
    fetchTodos.mockResolvedValue([todo('1', 'Learn Docker'), todo('2', 'Learn React')]);

    render(<App />);

    expect(await screen.findByText('Learn Docker')).toBeInTheDocument();
    expect(screen.getByText('Learn React')).toBeInTheDocument();
  });

  test('shows an empty state when there are no todos', async () => {
    fetchTodos.mockResolvedValue([]);

    render(<App />);

    expect(await screen.findByText(/no todos yet/i)).toBeInTheDocument();
  });

  test('creates a todo and re-fetches the list from the server', async () => {
    fetchTodos
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([todo('1', 'Write tests')]);
    createTodo.mockResolvedValue(todo('1', 'Write tests'));

    render(<App />);
    await screen.findByText(/no todos yet/i);

    userEvent.type(screen.getByLabelText(/todo/i), 'Write tests');
    userEvent.click(screen.getByRole('button', { name: /add todo/i }));

    expect(await screen.findByText('Write tests')).toBeInTheDocument();
    expect(createTodo).toHaveBeenCalledWith('Write tests');
    expect(fetchTodos).toHaveBeenCalledTimes(2);
  });

  test('shows an error and lets the user retry when loading fails', async () => {
    fetchTodos
      .mockRejectedValueOnce(new Error('The database is currently unavailable.'))
      .mockResolvedValueOnce([todo('1', 'Back online')]);

    render(<App />);

    expect(await screen.findByRole('alert')).toHaveTextContent(/database is currently unavailable/i);

    userEvent.click(screen.getByRole('button', { name: /try again/i }));

    expect(await screen.findByText('Back online')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
  });
});
