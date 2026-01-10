
# Multi-Finance User Application  
## Authorization Service (AuthZ) - Requirements Document (OpenAPI-Compliant)

---

## 1. Overview

This document defines the functional and non-functional requirements for the **Authorization Service (AuthZ)** - the central Policy Decision Point (PDP) for the Multi-Finance User Web Application built using a **microservices REST architecture**.  
The service **MUST expose OpenAPI 3.x compliant specifications**.

### Core Responsibility
- **Authorization**: Central policy decision point for access control
- **Policy Management**: RBAC (Role-Based Access Control) and ABAC (Attribute-Based Access Control)
- **Multi-Tenant**: Policy isolation and tenant-aware decisions
- **Ownership Rules**: Resource ownership validation

---

## 2. Architecture Principles

- Microservices with **single responsibility**
- **Database-per-service or use entity-service**
- REST APIs with **OpenAPI 3.0+**
- Stateless authorization decisions
- JWT-based authentication
- Default **DENY** authorization model
- Deterministic policy evaluation
- Fast policy lookups (< 50ms P95)

---

## 3. Authorization Service (AuthZ)

A RESTful microservice for centralized authorization decisions, policy management, and access control with support for RBAC, ABAC, and ownership-based policies.

## Features

- **Authorization Decisions**: Real-time access control decisions with context evaluation
- **RBAC Support**: Role-based access control with role-to-permission mappings
- **ABAC Support**: Attribute-based access control with context attributes
- **Ownership Rules**: Resource ownership validation and enforcement
- **Multi-Tenant**: Tenant isolation for policies and decisions
- **Batch Decisions**: Check multiple permissions in a single request
- **Policy Management**: CRUD operations for roles, permissions, and policies
- **Assignment Management**: User-role and role-permission assignments
- **API Key Authentication**: Service-to-service authentication support
- **RESTful API**: Follows REST and OpenAPI standards
- **Async/Await**: Fully asynchronous operations for high performance
- **Entity Service Integration**: All CRUD operations via entity-service
- **Utils Service Integration**: Shared logging and configuration utilities
- **Type Safety**: Full Pydantic schema validation
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **Caching**: Policy cache for performance optimization
- **OpenAPI Documentation**: Auto-generated interactive documentation

## Architecture

### Multi-Service Design

This service integrates with other microservices for separation of concerns:

```
Service Structure:
├── main.py                   (FastAPI app, lifespan, middleware)
├── app/
│   ├── __init__.py
│   ├── config.py            (Configuration loader)
│   ├── middleware.py        (Request context, correlation ID, auth)
│   ├── cache.py             (Policy cache, decision cache)
│   ├── routes/              (API endpoints - thin layer)
│   │   ├── __init__.py
│   │   ├── authz.py         (Authorization decisions)
│   │   ├── roles.py         (Role management)
│   │   ├── permissions.py   (Permission management)
│   │   ├── policies.py      (Policy management)
│   │   └── assignments.py   (Role/permission assignments)
│   ├── services/            (Business logic layer)
│   │   ├── __init__.py
│   │   ├── decision_service.py      (Policy evaluation engine)
│   │   ├── rbac_service.py          (RBAC logic)
│   │   ├── abac_service.py          (ABAC logic)
│   │   ├── ownership_service.py     (Ownership validation)
│   │   ├── policy_service.py        (Policy CRUD)
│   │   ├── role_service.py          (Role CRUD)
│   │   ├── permission_service.py    (Permission CRUD)
│   │   └── assignment_service.py    (Assignment CRUD)
│   ├── models/              (Pydantic schemas)
│   │   ├── __init__.py
│   │   ├── request.py       (Authorization request models)
│   │   ├── response.py      (Authorization response models)
│   │   ├── role.py          (Role schemas)
│   │   ├── permission.py    (Permission schemas)
│   │   ├── policy.py        (Policy schemas)
│   │   └── assignment.py    (Assignment schemas)
│   └── clients/             (External service clients)
│       ├── __init__.py
│       └── entity_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_authz_endpoints.py
│   ├── test_role_endpoints.py
│   ├── test_decision_service.py
│   └── test_policy_evaluation.py
├── reports/
│   ├── junit.xml
│   ├── coverage.xml
│   └── htmlcov/
├── logs/
├── config/
│   ├── app.yaml
│   └── logging.yaml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

**Benefits:**
- ✅ Separation of concerns (authorization logic vs data storage)
- ✅ Reusable utilities across services
- ✅ Scalable architecture
- ✅ Easy to test and maintain
- ✅ Clear service boundaries
- ✅ Fast policy evaluation with caching

---

## 4. Technology Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI (async, OpenAPI native)
- **Data Validation**: Pydantic
- **Policy Engine**: Custom rule-based engine with caching
- **Testing**: pytest with coverage reporting
- **Logging**: Structured JSON logs (via utils-service)
- **Configuration**: Config management (via utils-service)
- **Server**: Uvicorn ASGI
- **Cache**: In-memory cache with TTL for policy decisions

---

## 5. Core APIs/Endpoints

### 5.1 Health Check
- `GET /health` - Service health check
- `GET /healthz` - Kubernetes health probe

### 5.2 Authorization Decision Endpoints

#### Check Authorization
**Endpoint**: `POST /api/v1/authz/check`

**Request Requirements:**
- Must accept user_id (required, UUID format)
- Must accept resource (required, string, resource identifier)
- Must accept action (required, string, action to perform: "create", "read", "update", "delete", "execute")
- Must accept context (optional, object, additional context attributes)
  - tenant_id (string, for multi-tenant isolation)
  - resource_owner_id (UUID, for ownership checks)
  - ip_address (string, for IP-based rules)
  - time (ISO 8601, for time-based rules)
  - custom attributes (flexible schema)

**Response Requirements:**
- Success Status: 200 OK
- Must return decision (enum: "ALLOW" or "DENY")
- Must return reason_codes (array of strings, justification for decision)
- Must return policy_version (string, version of policies evaluated)
- Must return evaluated_policies (array of policy IDs evaluated)
- Must include metadata with timestamp and correlation_id

**Business Logic:**
- Must evaluate RBAC rules first (role-based permissions)
- Must evaluate ABAC rules second (attribute-based conditions)
- Must evaluate ownership rules third (resource owner validation)
- Must use default DENY if no matching policy found
- Must cache decisions for performance (with short TTL)
- Must log all authorization decisions for audit

**Security:**
- Must validate JWT token in Authorization header
- Must support API key authentication
- Must validate tenant_id matches JWT claims
- Must rate limit per user/tenant

**Error Responses:**
- 400 Bad Request: Invalid request format
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Insufficient permissions
- 422 Unprocessable Entity: Validation errors
- 500 Internal Server Error: Policy evaluation failure

---

#### Batch Check Authorization
**Endpoint**: `POST /api/v1/authz/check:batch`

**Request Requirements:**
- Must accept checks (required, array of authorization check objects)
  - Each check contains: user_id, resource, action, context
- Must support up to 100 checks per request

**Response Requirements:**
- Success Status: 200 OK
- Must return decisions (array of decision objects)
  - Each decision contains: decision, reason_codes, policy_version, request_index
- Must preserve request order in response
- Must include metadata with timestamp and correlation_id

**Business Logic:**
- Must evaluate each check independently
- Must continue processing even if one check fails
- Must return partial results on evaluation errors
- Must optimize by batching entity-service calls

**Performance:**
- Must complete batch evaluation within 500ms (P95)
- Must use parallel processing for independent checks
- Must leverage policy cache

---

### 5.3 Role Management Endpoints

#### List Roles
**Endpoint**: `GET /api/v1/authz/roles`

**Query Parameters:**
- tenant_id (optional, filter by tenant)
- page (integer, default: 1)
- page_size (integer, default: 50, max: 100)

**Response Requirements:**
- Success Status: 200 OK
- Must return roles (array of role objects)
- Must include pagination metadata (total, page, page_size)

---

#### Create Role
**Endpoint**: `POST /api/v1/authz/roles`

**Request Requirements:**
- Must accept name (required, unique within tenant, 3-50 characters)
- Must accept description (optional, max 500 characters)
- Must accept tenant_id (required, UUID format)
- Must accept permissions (optional, array of permission IDs)

**Response Requirements:**
- Success Status: 201 Created
- Must return role_id (UUID format)
- Must return complete role object

**Business Logic:**
- Must validate role name uniqueness within tenant
- Must validate all permission IDs exist
- Must create via entity-service
- Must clear policy cache on role creation

---

#### Get Role
**Endpoint**: `GET /api/v1/authz/roles/{role_id}`

**Response Requirements:**
- Success Status: 200 OK
- Must return complete role object with permissions

---

#### Update Role
**Endpoint**: `PATCH /api/v1/authz/roles/{role_id}`

**Request Requirements:**
- Must accept name (optional)
- Must accept description (optional)
- Must accept permissions (optional, replaces all permissions)

**Business Logic:**
- Must validate role exists
- Must validate tenant ownership
- Must clear policy cache on update

---

#### Delete Role
**Endpoint**: `DELETE /api/v1/authz/roles/{role_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Must validate role exists
- Must validate no users assigned to role (or cascade delete assignments)
- Must clear policy cache on deletion

---

### 5.4 Permission Management Endpoints

#### List Permissions
**Endpoint**: `GET /api/v1/authz/permissions`

**Query Parameters:**
- resource_type (optional, filter by resource)
- action (optional, filter by action)
- page (integer, default: 1)
- page_size (integer, default: 50, max: 100)

**Response Requirements:**
- Success Status: 200 OK
- Must return permissions (array of permission objects)
- Must include pagination metadata

---

#### Create Permission
**Endpoint**: `POST /api/v1/authz/permissions`

**Request Requirements:**
- Must accept name (required, unique, 3-100 characters)
- Must accept description (optional, max 500 characters)
- Must accept resource_type (required, string, e.g., "loan", "profile", "document")
- Must accept action (required, string, e.g., "create", "read", "update", "delete")
- Must accept conditions (optional, object, ABAC conditions)

**Response Requirements:**
- Success Status: 201 Created
- Must return permission_id (UUID format)
- Must return complete permission object

**Business Logic:**
- Must validate permission uniqueness (resource_type + action)
- Must validate condition syntax
- Must create via entity-service
- Must clear policy cache

---

#### Get Permission
**Endpoint**: `GET /api/v1/authz/permissions/{permission_id}`

**Response Requirements:**
- Success Status: 200 OK
- Must return complete permission object

---

#### Update Permission
**Endpoint**: `PATCH /api/v1/authz/permissions/{permission_id}`

**Request Requirements:**
- Must accept name (optional)
- Must accept description (optional)
- Must accept conditions (optional)

**Business Logic:**
- Must validate permission exists
- Must clear policy cache on update

---

#### Delete Permission
**Endpoint**: `DELETE /api/v1/authz/permissions/{permission_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Must validate no roles reference this permission (or cascade delete)
- Must clear policy cache on deletion

---

### 5.5 Policy Management Endpoints

#### List Policies
**Endpoint**: `GET /api/v1/authz/policies`

**Query Parameters:**
- tenant_id (optional)
- type (optional, filter by policy type: "rbac", "abac", "ownership")
- active (optional, boolean)
- page (integer, default: 1)
- page_size (integer, default: 50, max: 100)

**Response Requirements:**
- Success Status: 200 OK
- Must return policies (array of policy objects)
- Must include pagination metadata

---

#### Create Policy
**Endpoint**: `POST /api/v1/authz/policies`

**Request Requirements:**
- Must accept name (required, unique within tenant, 3-100 characters)
- Must accept description (optional, max 1000 characters)
- Must accept tenant_id (required, UUID format)
- Must accept policy_type (required, enum: "rbac", "abac", "ownership")
- Must accept rules (required, array of rule objects)
  - effect (enum: "allow", "deny")
  - conditions (object, evaluation conditions)
  - priority (integer, 0-1000)
- Must accept active (required, boolean, default: true)
- Must accept version (required, string, semantic versioning)

**Response Requirements:**
- Success Status: 201 Created
- Must return policy_id (UUID format)
- Must return complete policy object

**Business Logic:**
- Must validate policy syntax
- Must validate rule conditions are evaluable
- Must version policies (increment on update)
- Must clear policy cache on creation

---

#### Get Policy
**Endpoint**: `GET /api/v1/authz/policies/{policy_id}`

**Response Requirements:**
- Success Status: 200 OK
- Must return complete policy object with all rules

---

#### Update Policy
**Endpoint**: `PATCH /api/v1/authz/policies/{policy_id}`

**Request Requirements:**
- Must accept name (optional)
- Must accept description (optional)
- Must accept rules (optional)
- Must accept active (optional)

**Business Logic:**
- Must validate policy exists
- Must increment version on update
- Must preserve old version for audit
- Must clear policy cache on update

---

#### Delete Policy
**Endpoint**: `DELETE /api/v1/authz/policies/{policy_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Must soft delete (mark as inactive) for audit trail
- Must clear policy cache on deletion

---

### 5.6 Assignment Management Endpoints

#### Assign Role to User
**Endpoint**: `POST /api/v1/authz/assignments/users/{user_id}/roles`

**Request Requirements:**
- Must accept role_id (required, UUID format)
- Must accept tenant_id (required, UUID format)
- Must accept valid_from (optional, ISO 8601 datetime)
- Must accept valid_until (optional, ISO 8601 datetime)

**Response Requirements:**
- Success Status: 201 Created
- Must return assignment_id (UUID format)

**Business Logic:**
- Must validate user exists
- Must validate role exists
- Must validate tenant_id matches
- Must prevent duplicate assignments
- Must clear policy cache for user

---

#### List User Roles
**Endpoint**: `GET /api/v1/authz/assignments/users/{user_id}/roles`

**Query Parameters:**
- tenant_id (optional)
- active_only (boolean, default: true)

**Response Requirements:**
- Success Status: 200 OK
- Must return roles assigned to user
- Must filter by validity period if active_only=true

---

#### Revoke Role from User
**Endpoint**: `DELETE /api/v1/authz/assignments/users/{user_id}/roles/{role_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Must soft delete assignment for audit
- Must clear policy cache for user

---

#### Assign Permission to Role
**Endpoint**: `POST /api/v1/authz/assignments/roles/{role_id}/permissions`

**Request Requirements:**
- Must accept permission_id (required, UUID format)

**Response Requirements:**
- Success Status: 201 Created
- Must return assignment_id (UUID format)

**Business Logic:**
- Must validate role exists
- Must validate permission exists
- Must prevent duplicate assignments
- Must clear policy cache

---

#### List Role Permissions
**Endpoint**: `GET /api/v1/authz/assignments/roles/{role_id}/permissions`

**Response Requirements:**
- Success Status: 200 OK
- Must return permissions assigned to role

---

#### Revoke Permission from Role
**Endpoint**: `DELETE /api/v1/authz/assignments/roles/{role_id}/permissions/{permission_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Must clear policy cache

---

## 6. Data Models

### 6.1 Authorization Request
```yaml
AuthorizationRequest:
  user_id: string (UUID)
  resource: string
  action: string (enum: create, read, update, delete, execute)
  context:
    tenant_id: string (UUID, optional)
    resource_owner_id: string (UUID, optional)
    ip_address: string (optional)
    time: string (ISO 8601, optional)
    attributes: object (flexible, optional)
```

### 6.2 Authorization Response
```yaml
AuthorizationResponse:
  decision: string (enum: ALLOW, DENY)
  reason_codes: array of strings
  policy_version: string
  evaluated_policies: array of strings (policy IDs)
  metadata:
    timestamp: string (ISO 8601)
    correlation_id: string (UUID)
```

### 6.3 Role
```yaml
Role:
  role_id: string (UUID)
  name: string
  description: string (optional)
  tenant_id: string (UUID)
  permissions: array of Permission objects
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
```

### 6.4 Permission
```yaml
Permission:
  permission_id: string (UUID)
  name: string
  description: string (optional)
  resource_type: string
  action: string
  conditions: object (ABAC rules, optional)
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)
```

### 6.5 Policy
```yaml
Policy:
  policy_id: string (UUID)
  name: string
  description: string (optional)
  tenant_id: string (UUID)
  policy_type: string (enum: rbac, abac, ownership)
  rules: array of Rule objects
  active: boolean
  version: string
  created_at: string (ISO 8601)
  updated_at: string (ISO 8601)

Rule:
  effect: string (enum: allow, deny)
  conditions: object
  priority: integer
```

### 6.6 Assignment
```yaml
UserRoleAssignment:
  assignment_id: string (UUID)
  user_id: string (UUID)
  role_id: string (UUID)
  tenant_id: string (UUID)
  valid_from: string (ISO 8601, optional)
  valid_until: string (ISO 8601, optional)
  created_at: string (ISO 8601)

RolePermissionAssignment:
  assignment_id: string (UUID)
  role_id: string (UUID)
  permission_id: string (UUID)
  created_at: string (ISO 8601)
```

---

## 7. Business Logic & Rules

### 7.1 Authorization Decision Flow
1. **Authenticate**: Validate JWT token or API key
2. **Extract Context**: Parse user_id, resource, action, context from request
3. **Load User Roles**: Retrieve all active roles for user (with caching)
4. **Evaluate RBAC**: Check if user has permission via role assignments
5. **Evaluate ABAC**: Apply attribute-based conditions if RBAC passes
6. **Evaluate Ownership**: Validate resource ownership if applicable
7. **Apply Default**: Return DENY if no policy matches
8. **Log Decision**: Record decision for audit trail
9. **Return Response**: Deterministic decision with reason codes

### 7.2 Policy Evaluation Priority
1. **Explicit DENY**: Always takes precedence
2. **Explicit ALLOW**: Granted if no DENY exists
3. **Default DENY**: Applied if no explicit rule matches

### 7.3 Multi-Tenant Isolation
- All policies scoped to tenant_id
- User roles validated against tenant_id
- Cross-tenant access forbidden by default
- Tenant admins can only manage their tenant's policies

### 7.4 Ownership Rules
- Resource owner always has full access (unless explicitly denied)
- Ownership validation via resource_owner_id in context
- Ownership checked after RBAC/ABAC evaluation

### 7.5 Caching Strategy
- **Policy Cache**: Cache compiled policies per tenant (TTL: 5 minutes)
- **Role Cache**: Cache user-role mappings (TTL: 2 minutes)
- **Decision Cache**: Cache authorization decisions (TTL: 30 seconds)
- **Cache Invalidation**: Clear on policy/role/assignment updates

---

## 8. Security Requirements

### 8.1 Authentication
- **JWT Validation**: Validate access tokens from auth-service
- **API Key Support**: Service-to-service authentication
- **Token Claims**: Extract user_id, tenant_id, roles from JWT
- **Signature Verification**: Validate JWT signature with shared secret

### 8.2 Authorization
- **Admin Endpoints**: Role/permission/policy management requires admin role
- **User Endpoints**: Authorization checks require valid user authentication
- **Tenant Isolation**: Enforce tenant boundaries in all operations

### 8.3 Rate Limiting
- **Per User**: 1000 requests per minute
- **Per Tenant**: 10000 requests per minute
- **Per IP**: 5000 requests per minute

### 8.4 Audit Logging
- Log all authorization decisions (ALLOW and DENY)
- Log all policy changes (create, update, delete)
- Log all role/permission assignments
- Include correlation_id for request tracing

---

## 9. Performance Requirements

### 9.1 Latency
- **Authorization Check**: P95 < 50ms, P99 < 100ms
- **Batch Check**: P95 < 500ms for 100 checks
- **Policy CRUD**: P95 < 200ms
- **Role CRUD**: P95 < 200ms

### 9.2 Throughput
- **Min**: 10,000 authorization checks per second
- **Peak**: 50,000 authorization checks per second

### 9.3 Caching
- **Cache Hit Rate**: > 90% for authorization checks
- **Cache Latency**: < 5ms for cached decisions

### 9.4 Scalability
- Horizontal scaling via multiple service instances
- Stateless service design
- Load balancing across instances

---

## 10. Error Handling

### 10.1 Standard Error Response
```yaml
ErrorResponse:
  success: false
  error:
    code: string (ERROR_CODE)
    message: string (human-readable)
    details: object (optional)
  data: null
  metadata:
    timestamp: string (ISO 8601)
    correlation_id: string (UUID)
```

### 10.2 Error Codes
- **INVALID_REQUEST**: Malformed request body/parameters
- **UNAUTHORIZED**: Missing or invalid authentication
- **FORBIDDEN**: Insufficient permissions
- **ROLE_NOT_FOUND**: Role does not exist
- **PERMISSION_NOT_FOUND**: Permission does not exist
- **POLICY_NOT_FOUND**: Policy does not exist
- **DUPLICATE_ROLE**: Role name already exists
- **DUPLICATE_PERMISSION**: Permission already exists
- **DUPLICATE_ASSIGNMENT**: Assignment already exists
- **INVALID_POLICY_SYNTAX**: Policy rules contain syntax errors
- **EVALUATION_ERROR**: Policy evaluation failed
- **TENANT_MISMATCH**: Tenant isolation violation
- **CACHE_ERROR**: Cache operation failed (non-critical)
- **ENTITY_SERVICE_ERROR**: Entity service communication failure

---

## 11. External Service Integration

### 11.1 Entity Service
**Purpose**: Data persistence for all authorization entities

**Operations:**
- Create/Read/Update/Delete roles
- Create/Read/Update/Delete permissions
- Create/Read/Update/Delete policies
- Create/Read/Update/Delete assignments

**Error Handling:**
- Retry transient failures (3 attempts)
- Fallback to cached data if available
- Return error to client on persistent failures

### 11.2 Auth Service
**Purpose**: JWT token validation

**Operations:**
- Validate access tokens
- Extract user claims (user_id, tenant_id, roles)

**Error Handling:**
- Return 401 Unauthorized on invalid token
- Support token refresh via auth-service

---

## 12. Testing Requirements

### 12.1 Unit Tests
- Test decision service logic (RBAC, ABAC, ownership)
- Test policy evaluation engine
- Test cache operations
- Test error handling
- Minimum 80% code coverage

### 12.2 Integration Tests
- Test authorization check endpoints
- Test role/permission/policy CRUD endpoints
- Test assignment endpoints
- Test batch operations
- Test entity-service integration
- Test cache invalidation

### 12.3 Performance Tests
- Load test authorization checks (10k+ TPS)
- Stress test batch operations
- Measure cache hit rates
- Validate P95/P99 latency requirements

### 12.4 Security Tests
- Test tenant isolation
- Test authentication bypass attempts
- Test authorization bypass attempts
- Test policy injection attacks
- Test rate limiting

---

## 13. Configuration

### 13.1 Application Configuration
-- Application configuration through app.json
-- Logging configuration through logging.json 
-- Others as needed

### 13.2 Environment Variables
- `JWT_SECRET`: Secret key for JWT validation
- `API_KEY`: Service API key
- `ENTITY_SERVICE_URL`: Entity service base URL
- `REDIS_URL`: Redis connection string (optional, for distributed cache)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)

---

## 14. Deployment

### 14.1 Container
- Docker image with Python 3.10+ and all dependencies
- Health check endpoint: `/healthz`
- Readiness probe: `/health`
- Liveness probe: `/healthz`

### 14.2 Kubernetes (Future scope. not now)
- Minimum 2 replicas for HA
- Resource limits: CPU 1 core, Memory 1GB
- Resource requests: CPU 500m, Memory 512MB
- HPA based on CPU > 70%

### 14.3 Service Discovery
- Service name: `authz-service`
- Port: 8002
- Protocol: HTTP

---

## 15. OpenAPI Requirements

### 15.1 OpenAPI Specification
- Version: OpenAPI 3.0.3
- Title: Authorization Service API
- Version: 1.0.0
- Base Path: `/api/v1`

### 15.2 Security Schemes
```yaml
securitySchemes:
  BearerAuth:
    type: http
    scheme: bearer
    bearerFormat: JWT
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key
```

### 15.3 Response Headers
- `X-Correlation-Id`: Request correlation ID
- `X-Policy-Version`: Evaluated policy version
- `X-Cache-Status`: Cache hit/miss status

### 15.4 Documentation
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- OpenAPI JSON at `/openapi.json`

---

## 16. Monitoring & Observability

### 16.1 Metrics
- **Authorization Decisions**: Count by decision (ALLOW/DENY)
- **Latency**: P50, P95, P99 latency per endpoint
- **Cache Hit Rate**: Policy/role/decision cache hits
- **Error Rate**: Errors by error code
- **Throughput**: Requests per second

### 16.2 Logs
- Structured JSON logs with correlation IDs
- Log levels: DEBUG, INFO, WARN, ERROR
- Log authorization decisions with context
- Log policy changes with user info

### 16.3 Tracing
- Distributed tracing with correlation IDs
- Trace authorization decision flow
- Trace entity-service calls
- Trace cache operations

---

## 17. Project Structure

```
authz-service/
├── main.py                          (Root entry point)
├── app/
│   ├── __init__.py
│   ├── config.py                    (Configuration loader)
│   ├── middleware.py                (Request context, auth, correlation ID)
│   ├── cache.py                     (Policy/role/decision cache)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py               (Authorization request schemas)
│   │   ├── response.py              (Response schemas)
│   │   ├── role.py                  (Role schemas)
│   │   ├── permission.py            (Permission schemas)
│   │   ├── policy.py                (Policy schemas)
│   │   └── assignment.py            (Assignment schemas)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── authz.py                 (Authorization endpoints)
│   │   ├── roles.py                 (Role management endpoints)
│   │   ├── permissions.py           (Permission management endpoints)
│   │   ├── policies.py              (Policy management endpoints)
│   │   └── assignments.py           (Assignment management endpoints)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── decision_service.py      (Policy evaluation engine)
│   │   ├── rbac_service.py          (RBAC logic)
│   │   ├── abac_service.py          (ABAC logic)
│   │   ├── ownership_service.py     (Ownership validation)
│   │   ├── policy_service.py        (Policy CRUD via entity-service)
│   │   ├── role_service.py          (Role CRUD via entity-service)
│   │   ├── permission_service.py    (Permission CRUD via entity-service)
│   │   └── assignment_service.py    (Assignment CRUD via entity-service)
│   └── clients/
│       ├── __init__.py
│       └── entity_service.py        (Entity service HTTP client)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_authz_endpoints.py
│   ├── test_role_endpoints.py
│   ├── test_permission_endpoints.py
│   ├── test_policy_endpoints.py
│   ├── test_assignment_endpoints.py
│   ├── test_decision_service.py
│   ├── test_rbac_service.py
│   ├── test_abac_service.py
│   └── test_ownership_service.py
├── config/
│   ├── app.yaml                     (Application configuration)
│   └── logging.yaml                 (Logging configuration)
├── reports/
│   ├── junit.xml
│   ├── coverage.xml
│   └── htmlcov/
├── logs/
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
├── Dockerfile
├── README.md
└── Requirements.md                  (This document)
```

**Standards:**
- Each directory with Python code MUST have `__init__.py` for clean imports
- Use absolute imports: `from app.services import DecisionService`
- Export commonly used classes/functions in `__init__.py` files
- Follow layered architecture: Routes → Services → Clients → External Services
- Keep routes thin (validation + delegation only)
- Business logic in services layer
- External integrations in clients layer
- Use `from utils import logger` for logging
- Use `from utils import init_app_logging` for logging initialization

---

## 18. Future Enhancements

### 18.1 Advanced Features (Phase 2)
- **Policy Language**: DSL for complex policy definitions
- **Time-Based Policies**: Automatic activation/deactivation
- **Geo-Based Policies**: Location-based access control
- **Risk Scoring**: Risk-based authorization decisions
- **Policy Simulation**: Test policy changes before deployment
- **Policy Versioning**: Rollback to previous policy versions
- **Audit Reports**: Generate compliance reports

### 18.2 Performance Improvements (Phase 2)
- **Distributed Cache**: Redis for shared cache across instances
- **Policy Compilation**: Pre-compile policies for faster evaluation
- **Bloom Filters**: Quick negative lookups for non-existent permissions
- **Query Optimization**: Optimize entity-service queries

### 18.3 Integration Enhancements (Phase 2)
- **Webhook Notifications**: Notify on policy changes
- **Event Publishing**: Publish authorization decisions to event bus
- **External Policy Providers**: Integrate with external policy engines (OPA, Casbin)

---

**End of Document**
