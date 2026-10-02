# Adbrew Test – TODO App

A small TODO app: a React frontend, a Django REST API, and MongoDB, each in its own Docker container.

- **App** (React dev server): http://localhost:3000
- **API** (Django + DRF): http://localhost:8000/todos
- **Mongo**: localhost:27017

## Running it

```bash
git clone <this repo>
cd <repo>
export ADBREW_CODEBASE_PATH="$(pwd)/src"
docker-compose build
docker-compose up -d
```

The `app` container runs `yarn install` on first start, so it can take a few minutes before http://localhost:3000 responds. `docker logs -f app` shows progress.

If `docker-compose` reports `invalid spec: :/src: empty section between colons`, `ADBREW_CODEBASE_PATH` is not set in the current shell.

### Running the tests

```bash
docker exec api bash -c "cd /src/rest && python manage.py test todos"
docker exec app bash -c "cd /src/app && CI=true yarn test"
```

## Fixes to the Docker setup

The provided setup no longer builds. I kept the same three-container structure and only changed what was broken:

| Problem | Cause | Fix |
|---|---|---|
| `apt-get install mongodb-org` fails | `python:3.8` now resolves to Debian 12. The MongoDB 4.4 packages are built for Debian 10 and depend on `libssl1.1`, which Debian 12 doesn't ship. They also have no ARM64 build, so they can't work on Apple Silicon at all. | The `mongo` service uses the official `mongo:4.4` image (multi-arch). The app image no longer installs a database server it doesn't run. |
| `easy_install pip` fails | `easy_install` has been removed from setuptools. | Removed. pip already ships with the official Python image. |
| React dev server would not start | The Yarn apt package pulls in Debian's Node.js (18 on Debian 12). react-scripts 4 uses webpack 4, which crashes on Node 17+ (`ERR_OSSL_EVP_UNSUPPORTED`). | Node 14 is installed from the official tarball, pinned with a build arg and selected by CPU architecture. Yarn comes from npm. |

I considered pinning the base image to `python:3.8-bullseye` instead, but Debian 11 is past end-of-life and its security packages are already being removed from the mirrors, so that build fails too.

## API

All responses are JSON. Errors always have the same shape:

```json
{ "error": { "message": "Description cannot be empty.", "field": "description" } }
```

### `GET /todos`

Returns every todo, newest first.

```bash
curl http://localhost:8000/todos
```
```json
{ "todos": [ { "id": "6abe…", "description": "Learn Docker", "created_at": "2026-10-01T07:11:55.748000+00:00" } ] }
```

### `POST /todos`

```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"description": "Learn Docker"}'
```

| Status | When |
|---|---|
| `201` | Created. The body is the new todo. |
| `400` | Malformed JSON, a body that isn't a JSON object, or a description that is missing, not a string, blank, or longer than 500 characters. |
| `415` | Content-Type isn't `application/json`. |
| `503` | MongoDB is unreachable. The response comes back within about 3 seconds, and the real error is logged on the server only. |

The trailing slash is optional for both methods. With a plain `todos/` route, Django's `APPEND_SLASH` would try to redirect `POST /todos`, which can't keep a request body.

## How the code is organised

### Backend (`src/rest`)

```
rest/
  settings.py           config, all read from environment variables with defaults
  mongo.py              one shared, lazily created MongoClient
  exceptions.py         InvalidInputError, raised by services, mapped to HTTP 400
  exception_handler.py  the only place exceptions become HTTP error responses
todos/
  entities.py           Todo dataclass, which the rest of the code works with
  repository.py         TodoRepository (interface) + MongoTodoRepository
  service.py            TodoService: validation and business rules
  dependencies.py       wiring: which repository the service gets
  views.py              thin HTTP layer
  tests/                service, repository and API tests
```

A request goes **view → service → repository → MongoDB**, and each layer has one job:

- **The view** reads the request, calls the service and returns a status code. It has no validation and no database code.
- **The service** holds the rules: a description must be a non-blank string, at most 500 characters, and is stored trimmed. It doesn't know about HTTP or Mongo. It receives its repository and clock through its constructor, so tests can pass a fake repository and a fixed time.
- **The repository** is the only code that knows about Mongo, for example `ObjectId`, BSON dates and the collection name. It returns plain `Todo` objects, so nothing above it handles Mongo documents.
- **The exception handler** keeps error handling consistent. Services raise exceptions instead of building responses, and one function decides the status code and response body for all views.

How this applies SOLID:
- **Single responsibility:** each module above has one reason to change.
- **Dependency inversion:** `TodoService` depends on the abstract `TodoRepository`, not on pymongo.
- **Open/closed:** supporting a different store means adding a new repository class, not editing the service.

As the README requires, the backend uses no Django models, serializers or SQLite. `DATABASES` is empty, and the Django apps that need a relational database (admin, sessions, messages) are removed from `INSTALLED_APPS`.

### Frontend (`src/app/src`)

```
config.js               API base URL (overridable via REACT_APP_API_BASE_URL) and limits
api/client.js           fetch wrapper: base URL, JSON, one ApiError type
api/todos.js            fetchTodos(), createTodo()
hooks/useTodos.js       list state, loading, errors, refresh, addTodo
components/TodoList.js  loading, error (with retry), empty and list states
components/TodoForm.js  controlled input, validation, submitting and error states
App.js                  wires the hook to the two components
```

- Everything uses function components and hooks.
- Components never call `fetch`. They get data and callbacks through props, which makes them easy to test and reuse.
- After a successful create, the list is **re-fetched from the server** rather than appended locally, so it always shows what is actually in MongoDB (requirement 3).
- `useTodos` cancels the previous request with `AbortController` when a new one starts or the component unmounts. A slow, stale response can't overwrite a newer one, and nothing updates state after unmount.
- The form trims input, blocks blank submissions, disables itself while a request is in flight (no double submits), clears only on success, and keeps the text on failure so the user can retry.

## Smaller details

- **Timestamps:** stored in UTC, and the Mongo client is created with `tz_aware=True` so datetimes read back still carry their timezone. BSON only stores milliseconds, so the repository truncates `created_at` before inserting. Otherwise the object returned from `POST` would differ from the same todo returned by `GET`.
- **Index:** there is an index on `created_at`, because the list query sorts by it.
- **Fast failure:** `serverSelectionTimeoutMS` is 3s, so with Mongo down the API returns a 503 quickly instead of hanging for pymongo's default 30s.
- **CORS:** restricted to `http://localhost:3000` (configurable through `CORS_ALLOWED_ORIGINS`). The original setting allowed every origin while also allowing credentials.
- **`.gitignore`:** Mongo's data directory is mounted into `src/db/`, so it's ignored to keep database files out of git.

## Tests

- **Backend (15 tests, Django test runner, no database needed):**
  - Service rules, using an in-memory repository.
  - `MongoTodoRepository` against `mongomock`: mapping, sort order, millisecond round-trip, index creation.
  - API tests through DRF's test client: status codes, error shape, malformed JSON, trailing slash, Mongo outage returning 503 without leaking internals.
- **Frontend (12 tests, Jest + React Testing Library):**
  - The fetch wrapper's error handling.
  - The form's behaviour.
  - The full App flow with the API module mocked: load, empty state, create and re-fetch, error and retry.

## What I would do next

- **Pagination** for `GET /todos`. The response is already wrapped in an object, so adding `next`/`limit` fields won't break clients.
- **Update/delete and a `completed` flag:** new service methods and routes on the same layers.
- **Production serving:** run the API under a WSGI server (uWSGI is already in the requirements) with `DEBUG=False` and a real `SECRET_KEY` from the environment. Serve a built React bundle instead of the dev server.
- **Health checks:** a `/health` endpoint and Docker healthchecks, so `api` waits for `mongo` to be ready.
- **Image size:** trim `requirements.txt`. Most of it (Jupyter, pandas, matplotlib, Celery) isn't used and makes the image slow to build.
