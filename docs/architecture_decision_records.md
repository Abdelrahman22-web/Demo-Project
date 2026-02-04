# Tech Stack Decision Records (TSDRs)

> Format: One record per decision. Keep them short, explicit, and dated.

---

## TSDR-001 — Frontend Framework
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Framework/Library>** for the frontend.
- **Context / Problem:**
  - Need a UI that supports <key needs: forms, routing, auth, charts, etc.>
  - Team familiarity and delivery speed are priorities.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
  3. <Option C>
- **Decision Drivers:**
  - Developer velocity
  - Learning curve
  - Ecosystem maturity
  - Compatibility with backend/API
  - Maintainability
- **Pros:**
  - <pro 1>
  - <pro 2>
- **Cons / Tradeoffs:**
  - <con 1>
  - <con 2>
- **Consequences:**
  - UI will be structured around <components/pages/state mgmt>.
  - Adds dependency on <build tool/runtime>.
- **Notes / Links:**
  - <docs links, tickets, references>

---

## TSDR-002 — Backend Framework
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Backend Framework>** for server/API.
- **Context / Problem:**
  - Need a CRUD API with validation, auth, and clean routing.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Ease of building REST endpoints
  - Middleware support (auth, logging)
  - Testing support
  - Team familiarity
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Standardizes API structure and error handling.
- **Notes / Links:**
  - <links>

---

## TSDR-003 — Database
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Database>** as the primary data store.
- **Context / Problem:**
  - Need reliable persistence for <entities: users, records, etc.>
  - Must support <transactions? relational constraints?>
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Data model fit (relational vs document)
  - Cost and ease of hosting
  - Migration tooling
  - Backup/restore options
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Schema and migrations become part of CI/CD.
- **Notes / Links:**
  - <links>

---

## TSDR-004 — ORM / Data Access
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<ORM/Query Builder>** for database access.
- **Context / Problem:**
  - Need consistent CRUD patterns, validation, and migrations.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Type safety
  - Migration support
  - Performance and query control
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Data layer follows <repository/service> pattern.
- **Notes / Links:**
  - <links>

---

## TSDR-005 — API Style
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **REST** (JSON over HTTP) for client-server communication.
- **Context / Problem:**
  - Need simple integration between frontend and backend with predictable endpoints.
- **Options Considered:**
  1. REST
  2. GraphQL
  3. gRPC
- **Decision Drivers:**
  - Simplicity
  - Debuggability
  - Tooling (Postman/curl)
- **Pros:**
  - Easy to implement and test
- **Cons / Tradeoffs:**
  - May require multiple endpoints for complex views
- **Consequences:**
  - Define endpoint contracts, request/response schemas, and versioning strategy.
- **Notes / Links:**
  - <API spec link>

---

## TSDR-006 — Authentication
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Auth Method>** (e.g., session cookies, JWT, OAuth2).
- **Context / Problem:**
  - Need secure login and role-based access (student/admin).
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Security
  - Implementation complexity
  - UX
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Adds <token storage / cookie config / middleware>.
- **Notes / Links:**
  - <links>

---

## TSDR-007 — Hosting / Deployment
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Deploy using **<Platform>** (e.g., Render, Railway, Vercel, AWS, on-prem).
- **Context / Problem:**
  - Need simple deployment with minimal DevOps overhead.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Cost
  - Ease of setup
  - Reliability
  - CI/CD support
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Defines environment variables, build steps, and rollback approach.
- **Notes / Links:**
  - <links>

---

## TSDR-008 — Testing Strategy
- **Status:** Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Test Tools>** for unit + integration testing.
- **Context / Problem:**
  - Need confidence in CRUD correctness and regression prevention.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Ease of writing tests
  - Speed in CI
  - Coverage for critical paths
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Add CI step for tests and coverage thresholds (optional).
- **Notes / Links:**
  - <links>

---

## TSDR-009 — Logging & Monitoring (Optional for Class Projects)
- **Status:** Proposed / Accepted
- **Date:** YYYY-MM-DD
- **Decision:** Use **<Logging approach>** (structured logs, console logs + file, etc.).
- **Context / Problem:**
  - Need basic observability to debug failures.
- **Options Considered:**
  1. <Option A>
  2. <Option B>
- **Decision Drivers:**
  - Simplicity
  - Debug usefulness
- **Pros:**
  - <pro 1>
- **Cons / Tradeoffs:**
  - <con 1>
- **Consequences:**
  - Standardize log format and error handling.
- **Notes / Links:**
  - <links>
