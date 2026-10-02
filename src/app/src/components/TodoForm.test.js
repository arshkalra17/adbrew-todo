import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { TodoForm } from './TodoForm';

const input = () => screen.getByLabelText(/todo/i);
const submitButton = () => screen.getByRole('button', { name: /add todo|adding/i });

describe('TodoForm', () => {
  test('submits the trimmed description and clears the input', async () => {
    const onSubmit = jest.fn().mockResolvedValue();
    render(<TodoForm onSubmit={onSubmit} />);

    userEvent.type(input(), '  Buy milk  ');
    userEvent.click(submitButton());

    await waitFor(() => expect(input()).toHaveValue(''));
    expect(onSubmit).toHaveBeenCalledWith('Buy milk');
  });

  test('does not submit an empty description', () => {
    const onSubmit = jest.fn();
    render(<TodoForm onSubmit={onSubmit} />);

    userEvent.type(input(), '   ');
    userEvent.click(submitButton());

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent(/please enter a description/i);
  });

  test('disables the form while the request is in flight', async () => {
    let finishRequest;
    const onSubmit = jest.fn(() => new Promise((resolve) => { finishRequest = resolve; }));
    render(<TodoForm onSubmit={onSubmit} />);

    userEvent.type(input(), 'Slow request');
    userEvent.click(submitButton());

    expect(submitButton()).toBeDisabled();
    expect(input()).toBeDisabled();

    finishRequest();
    await waitFor(() => expect(submitButton()).toBeEnabled());
  });

  test('shows the server error and keeps the text for a retry', async () => {
    const onSubmit = jest.fn().mockRejectedValue(new Error('Description cannot be empty.'));
    render(<TodoForm onSubmit={onSubmit} />);

    userEvent.type(input(), 'Will fail');
    userEvent.click(submitButton());

    expect(await screen.findByRole('alert')).toHaveTextContent('Description cannot be empty.');
    expect(input()).toHaveValue('Will fail');
  });
});
