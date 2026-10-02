import { ApiError, request } from './client';

const jsonResponse = (status, body) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
});

describe('request', () => {
  afterEach(() => {
    delete global.fetch;
  });

  test('sends JSON and returns the parsed body', async () => {
    global.fetch = jest.fn().mockResolvedValue(jsonResponse(201, { id: '1' }));

    const data = await request('/todos/', { method: 'POST', body: { description: 'x' } });

    expect(data).toEqual({ id: '1' });
    const [url, options] = global.fetch.mock.calls[0];
    expect(url).toBe('http://localhost:8000/todos/');
    expect(options.headers['Content-Type']).toBe('application/json');
    expect(options.body).toBe(JSON.stringify({ description: 'x' }));
  });

  test('turns an API error body into an ApiError', async () => {
    global.fetch = jest.fn().mockResolvedValue(
      jsonResponse(400, { error: { message: 'Description cannot be empty.', field: 'description' } })
    );

    const promise = request('/todos/', { method: 'POST', body: {} });

    await expect(promise).rejects.toBeInstanceOf(ApiError);
    await expect(promise).rejects.toMatchObject({
      message: 'Description cannot be empty.',
      status: 400,
      field: 'description',
    });
  });

  test('falls back to a generic message when the error body is not JSON', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: () => Promise.reject(new SyntaxError('Unexpected token <')),
    });

    await expect(request('/todos/')).rejects.toMatchObject({
      message: 'Request failed with status 502.',
      status: 502,
    });
  });

  test('reports a friendly message when the server cannot be reached', async () => {
    global.fetch = jest.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(request('/todos/')).rejects.toMatchObject({
      message: expect.stringMatching(/could not reach the server/i),
    });
  });
});
