# MathForge

A web-based math solver and grapher for Calculus and Linear Algebra, built as three services: a Blazor WebAssembly front end, an ASP.NET Core API, and a Python/SymPy compute service.

> **Status:** Phase 1 complete. The compute service supports differentiation, integration, limits, equation solving, simplification and matrix operations. Next: exposing them through the API (Phase 2).

## Architecture

```mermaid
flowchart LR
    B[Blazor WebAssembly client] -->|HTTP| A[ASP.NET Core API]
    A -->|private network| C[FastAPI + SymPy compute]
```

- **Client** (`client/`): Blazor WebAssembly, runs entirely in the browser.
- **API** (`api/`): ASP.NET Core minimal API. The only service the browser can reach; handles validation, CORS, and error handling.
- **Compute** (`compute/`): FastAPI + SymPy. Does the math; not exposed outside the Docker network.

## Tech stack

C# / .NET 10 · Blazor WebAssembly · ASP.NET Core · Python 3.12 · FastAPI · SymPy · Docker Compose · (planned) Azure Container Apps, Static Web Apps, GitHub Actions, Bicep

## Running locally

**Prerequisites:** Docker with Compose, .NET 10 SDK (for the client)

1. Start the backend (API + compute):
   ```bash
   docker compose up --build
   ```
2. In another terminal, start the client:
   ```bash
   cd client
   dotnet watch
   ```
3. Open http://localhost:5090. The home page should show the compute service as **ok**.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | API health |
| GET | `/health/compute` | Checks the compute service through the API; returns 503 if it's down |

### Compute service (internal)

Reachable only by the API on the Docker network, not from outside.

| Method | Path | Does |
| --- | --- | --- |
| POST | `/differentiate` | Derivatives of any order |
| POST | `/integrate` | Indefinite and definite integrals, including improper ones |
| POST | `/limit` | One- and two-sided limits, including at ±∞ |
| POST | `/solve` | Single-variable equations over the reals |
| POST | `/simplify` | Simplify, expand or factor |
| POST | `/matrix` | Determinant, inverse, RREF, eigenvalues, transpose (up to 5×5) |

Interactive docs: run the compute service locally and open http://localhost:8000/docs.

## Security

SymPy's `parse_expr` uses Python's `eval`, so passing user input to it directly allows remote code execution. MathForge defends against this in layers:

1. **Token allowlist:** input is tokenized first; only numbers, basic operators, known math functions and single-letter variables are allowed. Everything else (attribute access, strings, keywords, imports) is rejected before parsing.
2. **Restricted evaluation:** expressions are evaluated with no Python builtins available.
3. **Resource limits:** each computation runs in a separate process with a 3-second deadline and a 1 GB memory cap, and the process is killed if it exceeds them. This prevents inputs like `9^9^9^9` from freezing the service.
4. **Private network and non-root containers:** the compute service isn't exposed outside Docker, and both containers run as unprivileged users.

Every layer is covered by tests, including known injection payloads.

## Running the tests

```bash
cd compute
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Project structure

```
mathforge/
├── api/        ASP.NET Core API
├── client/     Blazor WebAssembly front end
├── compute/    FastAPI + SymPy service
├── infra/      Azure infrastructure (Bicep, planned)
└── docker-compose.yml
```