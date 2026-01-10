# Authorization Service – Implementation Status

## Snapshot (2026-01-10)
- Codebase scaffolding, FastAPI app, routers, middleware, caching, service layer, and Pydantic models are implemented per Requirements.md.
- Tests in `tests/` all pass (see Coverage section). Warnings: pydantic v2 config deprecations and use of `datetime.utcnow()`; functional behavior unaffected.

## Completed
- **Project setup**: requirements, pytest config, logging/app configs, .gitignore.
- **Models**: request/response, role, permission, policy, assignment (Pydantic v2).
- **Cache layer**: TTL LRU caches for policies, roles, decisions.
- **Middleware**: correlation ID, auth (JWT/API key), logging, CORS.
- **Entity client**: async httpx client with retries for CRUD on roles/permissions/policies/assignments.
- **Services**: RBAC, ABAC (basic operators), ownership, decision engine, CRUD services, assignments.
- **Routes**: health, authz check + batch, roles, permissions, policies, assignments.
- **Main app**: FastAPI wiring, lifespan, middleware, routers, health endpoints.
- **Tests**: unit-style endpoint/service coverage; pytest passes.

## Pending / Planned
- **Deprecation cleanup**: replace `datetime.utcnow()` with timezone-aware datetimes; migrate Pydantic configs to `ConfigDict` to silence v2 warnings.
- **Entity-service mocking**: add fakes/mocks for deterministic endpoint tests (currently rely on empty/no backend state, permitting 500 in assertions).
- **Rate limiting**: implement per-user/tenant/IP limits from Requirements.md (currently not enforced).
- **ABAC depth**: expand condition operators and policy-driven condition evaluation (currently basic evaluation and empty condition usage in decision flow).
- **Policy version source**: load real policy versioning from store/config instead of hard-coded `1.0.0`.
- **Observability**: metrics/tracing hooks (latency, cache hit rate, decision counts) not yet implemented.
- **Performance tests**: load/stress tests for latency/throughput and cache hit targets.
- **Security tests**: tenant isolation, JWT verification scenarios, rate-limit bypass, policy injection.
- **Production hardening**: real secret management, API key rotation, graceful shutdown hooks for external clients.

## Coverage
- Command: `pytest` (see reports/junit.xml, reports/coverage.xml, reports/htmlcov/).
- All 32 tests pass; overall coverage ~67% (service and route paths contain unexecuted branches due to lack of full backend mocks).

## How to Run
1) `python3 -m pip install -r requirements-dev.txt`
2) `pytest`

## Notable Files
- App entry: `main.py`
- Config: `config/app.yaml`, `config/logging.yaml`
- Middleware: `app/middleware.py`
- Clients: `app/clients/entity_service.py`
- Services: `app/services/` (rbac, abac, ownership, decision, CRUD, assignments)
- Routes: `app/routes/` (authz, roles, permissions, policies, assignments)
- Models: `app/models/`
- Tests: `tests/`

## Risks / Unknowns
- Entity-service API assumptions may diverge from the actual service; adjust schemas/paths accordingly.
- Rate limiting and observability gaps could impact production readiness.
- Timezone-naive timestamps and pydantic deprecations should be resolved before release.
