# Distributed Observability Platform — Technical Interview Revision Guide

---

# 1. Project Summary

* **Project Name**: Microservice Observability & Tracing Engine
* **One-Line Description**: A full-stack, distributed log aggregation, gRPC trace visualization, and real-time alerting engine built for microservices.
* **Problem It Solves**: In microservices architectures (like Google's Online Boutique), debugging issues across multiple isolated container stdout streams and nested gRPC calls is difficult. This platform aggregates logs in real time, visualizes distributed trace trees, and evaluates alert thresholds automatically.
* **Who Uses It**: DevOps engineers, Site Reliability Engineers (SREs), and Backend Developers monitoring distributed cloud services.

---

# 2. Tech Stack

* **Frontend**: Next.js 16 (App Router), TypeScript, React 19, Tailwind CSS, Lucide Icons, Recharts.
* **Backend**: Python 3.11, FastAPI, Uvicorn, Strawberry GraphQL, APScheduler.
* **Database**: MongoDB 6.0 (via `motor` async driver & `pymongo`).
* **Cloud/Deployment**: Docker, Docker Compose, Linux Container Networking (`boutique-net`).
* **Tools**: OpenTelemetry Collector Contrib, Docker Daemon API (`/var/run/docker.sock`), `mongosh`.
* **Libraries**: `pydantic` v2, `PyJWT`, `passlib` (Bcrypt), `docker` SDK, `requests`, `@apollo/client`.

---

# 3. System Architecture

```
User (Browser)
  │
  ▼
Next.js Frontend Dashboard (Port 3000)
  │
  ├──► REST & GraphQL APIs (Port 8000)
  │      │
  │      ├──► MongoDB (Port 27017) ── (Spans, Logs, Alerts, Users, Keys)
  │      │
  │      └──► APScheduler Alert Worker (Background Task)
  │
  └──► External Microservices Stream Sources:
         │
         ├─► Container stdout/stderr ──► Log Shipper Daemon ──────► POST /logs/batch
         │
         └─► OpenTelemetry Spans ─────► OTel Collector (4317) ────► POST /v1/traces
```

### External Services & Integrations:
* **Docker Daemon Socket (`/var/run/docker.sock`)**: Streamed directly by `log-shipper`.
* **OTel Collector (`otel-collector:4317`)**: Receives standard OTLP/gRPC trace spans from services like `checkoutservice`, `productcatalogservice`, `currencyservice`.

---

# 4. Features

* **Real-Time Log Aggregation**: Daemon-driven container log tailing & JSON normalization.
* **Distributed Trace Visualizer**: Recursive call hierarchy tree with latency duration bars and bottleneck highlights (>200ms).
* **Automated Alerting Engine**: Background rule evaluation for log error rates & trace duration thresholds.
* **API Key Security**: One-time raw secret key generation, hashed database storage, and revocation.
* **GraphQL Explorer**: Flexible typed queries for logs and alert rules (`/graphql`).
* **Security Audit Tracking**: Last login timestamp tracking and security alert banner.

---

# 5. Modules

### Module 1: Auth & API Keys
* **Purpose**: Authenticate dashboard users (JWT) and validate API keys (`X-API-Key`) for log/span ingestion.
* **Flow**: User logs in `POST /auth/login` $\rightarrow$ JWT issued $\rightarrow$ API key generated `POST /keys` $\rightarrow$ Hashed secret stored in DB $\rightarrow$ Ingestion endpoints check key via FastAPI `Depends()`.
* **Files**: `backend/app/api/auth.py`, `backend/app/api/keys.py`, `backend/app/core/security.py`.
* **Important APIs**: `POST /auth/login`, `POST /keys`, `GET /keys`, `DELETE /keys/{id}`.
* **Database Collections**: `users`, `api_keys`.

### Module 2: Log Aggregation (`log_shipper`)
* **Purpose**: Tail active Docker containers, parse structured JSON, and stream normalized logs to FastAPI.
* **Flow**: Daemon reads `/var/run/docker.sock` $\rightarrow$ Filters infra containers $\rightarrow$ Streams logs $\rightarrow$ Normalizes level/timestamp/traceId $\rightarrow$ Queues & sends batches (`POST /logs/batch`).
* **Files**: `log_shipper/main.py`, `log_shipper/log_parser.py`, `backend/app/api/logs.py`.
* **Important APIs**: `POST /logs/batch`, `GET /logs/`.
* **Database Collections**: `logs`.

### Module 3: Distributed Tracing & OTel Collector
* **Purpose**: Ingest OpenTelemetry gRPC spans and reconstruct tree structures.
* **Flow**: Microservices export OTLP gRPC spans to `otel-collector:4317` $\rightarrow$ Collector posts batch to `POST /v1/traces` $\rightarrow$ `SpanService` constructs nested `TraceNode` tree $\rightarrow$ UI visualizes duration bars.
* **Files**: `otel-collector-config.yaml`, `backend/app/api/spans.py`, `backend/app/services/span_service.py`.
* **Important APIs**: `POST /v1/traces`, `GET /traces`, `GET /traces/{trace_id}`.
* **Database Collections**: `spans`.

### Module 4: Alert Engine
* **Purpose**: Periodically evaluate rules (error rates, trace latency) and trigger alerts.
* **Flow**: SRE creates rule `POST /alerts/rules` $\rightarrow$ `APScheduler` worker runs every 60s $\rightarrow$ Queries log error counts & span latencies $\rightarrow$ Inserts trigger document into `alert_triggers`.
* **Files**: `backend/app/api/alerts.py`, `backend/app/services/alert_service.py`, `backend/app/workers/alert_worker.py`.
* **Important APIs**: `POST /alerts/rules`, `GET /alerts/rules`, `GET /alerts/triggers`.
* **Database Collections**: `alert_rules`, `alert_triggers`.

### Module 5: Next.js Frontend Dashboard
* **Purpose**: Unified UI for system metrics, live log explorer, trace visualizer, and alerting.
* **Files**: `frontend/app/page.tsx`, `frontend/app/logs/page.tsx`, `frontend/app/traces/page.tsx`, `frontend/app/alerts/page.tsx`, `frontend/app/keys/page.tsx`.

---

# 6. Request Flow

### Request Flow 1: Distributed Trace Ingestion & Rendering
```
Microservices (e.g. checkoutservice)
  │
  ▼ (OTLP / gRPC)
OTel Collector (4317)
  │
  ▼ (HTTP POST /v1/traces)
FastAPI Backend (spans.py)
  │
  ▼ (SpanRepository.insert_batch)
MongoDB ("spans" collection)
  │
  ▼ (User clicks Trace ID in Next.js UI)
Next.js Trace Explorer (`/traces?id=XYZ`)
  │
  ▼ (HTTP GET /traces/XYZ)
SpanService.get_trace_tree() (Reconstructs Parent-Child Tree)
  │
  ▼ (JSON Response)
Recursive TreeNode React Component (Renders Latency Bars)
```

### Request Flow 2: Container Log Streaming
```
Docker Container stdout/stderr
  │
  ▼
Log Shipper Daemon (Docker Socket API)
  │
  ▼
log_parser.py (JSON Extraction & Level Normalization)
  │
  ▼ (Queue Batching)
HTTP POST /logs/batch (Header: X-API-Key)
  │
  ▼
FastAPI Backend ──► MongoDB ("logs" collection)
  │
  ▼
Next.js Logs Explorer (`/logs`) ──► Live Table Stream
```

---

# 7. Database Architecture

* **Database Engine**: MongoDB 6.0 (`observability` database).

### Collections & Schema Design:
1. **`logs`**:
   * Columns: `_id`, `service`, `level` (INFO/WARN/ERROR), `message`, `timestamp`, `trace_id`, `span_id`, `raw` (Dict).
   * Index: `{ service: 1, level: 1, timestamp: -1 }`.
2. **`spans`**:
   * Columns: `_id`, `trace_id`, `span_id`, `parent_span_id`, `service_name`, `operation_name`, `start_time`, `end_time`, `duration_ms`, `status_code`, `attributes`.
   * Index: `{ trace_id: 1 }`, `{ service_name: 1, start_time: -1 }`.
3. **`api_keys`**:
   * Columns: `_id`, `name`, `key_prefix`, `hashed_key`, `created_at`, `revoked`.
   * Index: `{ hashed_key: 1 }`.
4. **`alert_rules`**:
   * Columns: `_id`, `name`, `metric` (error_rate/latency), `service`, `threshold`, `window_minutes`, `enabled`.
5. **`alert_triggers`**:
   * Columns: `_id`, `rule_id`, `rule_name`, `service`, `metric_value`, `threshold`, `timestamp`, `message`.

---

# 8. Core APIs Summary

| Method | Route | Purpose | Auth Required |
|---|---|---|---|
| `POST` | `/auth/login` | Authenticate user & return JWT | No |
| `POST` | `/keys` | Generate new API Key (reveals raw key once) | Bearer JWT |
| `GET` | `/keys` | List active API keys | Bearer JWT |
| `POST` | `/logs/batch` | Ingest log batch from `log-shipper` | `X-API-Key` |
| `GET` | `/logs/` | Query & filter logs (by service/level/search) | Optional |
| `POST` | `/v1/traces` | Ingest OTel spans batch | `X-API-Key` |
| `GET` | `/traces` | Retrieve list of recent trace IDs | Optional |
| `GET` | `/traces/{trace_id}` | Retrieve reconstructed trace call tree | Optional |
| `POST` | `/alerts/rules` | Create alert rule | Bearer JWT |
| `GET` | `/alerts/triggers` | Fetch historical alert incidents | Optional |
| `POST` | `/graphql` | Strawberry GraphQL endpoint for logs & rules | Optional |

---

# 9. Important Classes & Files

* **`backend/app/main.py`**: Lifespan manager, CORS configuration, router inclusion, and GraphQL route mounting.
* **`backend/app/services/span_service.py`**: Contains `get_trace_tree()` algorithm that converts flat span documents into a parent-child `TraceNode` tree.
* **`backend/app/repositories/span_repository.py`**: Motor async MongoDB driver queries for trace spans and distinct trace IDs.
* **`log_shipper/log_parser.py`**: Normalizes varied container log formats (JSON, Log4j, Pino, Python structlog) into unified log models.
* **`backend/app/workers/alert_worker.py`**: Background `AsyncIOScheduler` executing rule evaluations every 60 seconds.
* **`frontend/app/traces/page.tsx`**: React client component utilizing `<Suspense>`, `useCallback`, and recursive `TreeNode` rendering.

---

# 10. Important Concepts Used

### 1. Distributed Tracing & OTLP
* **What**: Tracking a single user request across multiple microservices via a unique `trace_id` and nested `span_id`s.
* **Why**: Pinpoints latency bottlenecks in complex gRPC dependency chains.
* **Alternatives**: Jaeger, Zipkin, AWS X-Ray.

### 2. Async Non-Blocking I/O (Motor & FastAPI)
* **What**: Using Python `async`/`await` with Motor (MongoDB async driver) and Uvicorn.
* **Why**: Prevents I/O blocking during concurrent log and span ingestion under heavy traffic.

### 3. Queue Batching in Log Shipper
* **What**: Accumulating log lines in a thread-safe `queue.Queue` and shipping 50 logs at a time or every 2.0 seconds.
* **Why**: Drastically reduces HTTP connection overhead on the backend.

### 4. React Suspense & Hook Memoization
* **What**: Wrapping Next.js `useSearchParams()` inside `<Suspense>` and memoizing API handlers with `useCallback`.
* **Why**: Prevents hydration bailouts and eliminates infinite re-render loops when updating state.

---

# 11. Challenges & Solutions

### Challenge 1: Log4j Placeholder Strings in Log Outputs
* **Problem**: Java containers (`adservice`) printed raw strings like `${ctx:traceId}` when MDC context was empty.
* **Root Cause**: Log4j pattern string interpolation outputting literal placeholder text when unassigned.
* **Solution**: Updated `log_parser.py` to filter out any `trace_id` or `span_id` values starting with `${`.

### Challenge 2: React `useEffect` Infinite Re-Fetch Loop
* **Problem**: Typing in the Trace Explorer search box triggered infinite backend requests.
* **Root Cause**: `loadTrace` depended on `searchTraceId` in `useCallback`, which re-created `loadRecentTraces` on every single keystroke.
* **Solution**: Decoupled `fetchTraceById` to accept an explicit `id` string parameter and removed `searchTraceId` from `useEffect` dependencies.

### Challenge 3: Next.js `useSearchParams()` Build Error
* **Problem**: App Router threw client-side rendering errors during build.
* **Root Cause**: `useSearchParams()` requires a `<Suspense>` boundary in Next.js 15+.
* **Solution**: Split page into `TraceContent` component wrapped inside `<Suspense>` in `TracesPage`.

---

# 12. Future Improvements

1. **WebSocket / Server-Sent Events (SSE)**: Replace interval polling with SSE for instant log streaming.
2. **OpenSearch / Elasticsearch Backend**: Transition logs collection from MongoDB to OpenSearch for full-text indexing.
3. **Grafana Dashboard Export**: Add Prometheus metrics exporter endpoint.
4. **Log Sampling Rules**: Implement tail-based sampling in OTel Collector to drop 200 OK trace spans and retain error traces.

---

# 13. Top Interview Questions & Prepared Answers

### Q1: Explain your project in 2 minutes.
> "I built a full-stack, distributed microservices observability platform for Google Cloud's Online Boutique architecture. It features a daemon that streams stdout container logs via the Docker API, an OpenTelemetry Collector that ingests gRPC trace spans on port 4317, a FastAPI backend with MongoDB, and a Next.js dashboard that reconstructs trace call trees and evaluates alert thresholds in real time."

### Q2: Why MongoDB instead of PostgreSQL or Elasticsearch?
> "Logs and trace attributes are inherently unstructured and dynamic across different microservices (Node.js, Go, Python, Java). MongoDB's flexible BSON document model allowed storing varied `raw` log attributes and nested trace span tags without complex relational migrations, while Motor provided async non-blocking I/O."

### Q3: How does the trace tree reconstruction algorithm work?
> "When a `trace_id` is queried, `SpanService` fetches all spans matching that ID. It builds a map of `span_id -> TraceNode`. In a second pass, it checks each span's `parent_span_id`. If a parent exists in the map, it appends the child node to `parent.children`; otherwise, that span is designated as the root node."

### Q4: How do you handle API key security?
> "When an API key is created, we return the raw secret to the user once. On the server, we store only a SHA-256 hash of the secret along with a visible key prefix. When an ingestion request arrives with `X-API-Key`, we hash the incoming key and perform a constant-time database lookup to prevent timing attacks."

### Q5: How would you scale this platform to 1 million logs per second?
> "I would replace direct HTTP ingestion with an Apache Kafka or NATS message broker between the `log-shipper` and backend, switch storage from MongoDB to ClickHouse or OpenSearch for columnar log compression, and implement tail-based trace sampling in the OpenTelemetry Collector."
