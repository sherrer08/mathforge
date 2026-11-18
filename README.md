# MathForge

A web-based math solver and grapher for Calculus and Linear Algebra, built as three services: a Blazor WebAssembly front end, an ASP.NET Core API, and a Python/SymPy compute service.

> **Status:** Phase 0 complete — all three services run and talk to each other. Math features are in progress.

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

## Project structure

```
mathforge/
├── api/        ASP.NET Core API
├── client/     Blazor WebAssembly front end
├── compute/    FastAPI + SymPy service
├── infra/      Azure infrastructure (Bicep, planned)
└── docker-compose.yml
```