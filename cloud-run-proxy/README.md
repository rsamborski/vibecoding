# Gemini 3.8 Flash Cloud Run Proxy Service

A high-performance, secure proxy service deployed on Google Cloud Run that forwards authenticated client requests to **Gemini 3.8 Flash** running in the `global` region, while tracking and logging per-user input and output tokens.

---

## 1. Architecture Overview

```
[ Client / Caller ]
        │  1. HTTPS + Google OIDC ID Token (`Authorization: Bearer <ID_TOKEN>`)
        ▼
[ Google Front End (GFE) / Cloud Run ]
        │  2. Cloud IAM enforces `roles/run.invoker`
        ▼
[ FastAPI Proxy Service (Cloud Run) ]
        │  3. Extract User Identity (`email` / `sub`)
        │  4. Forward request to Gemini 3.8 Flash (`location="global"`)
        ├───────────────────────────────────────────────────────┐
        ▼                                                       ▼
[ Gemini 3.8 Flash ]                                    [ Structured Cloud Logging ]
(Returns text + prompt/candidate tokens)               (Emits `gemini_token_usage` JSON)
        │                                                       │
        ▼                                                       ▼
[ Cloud Firestore ]                                    [ BigQuery Sink (Optional) ]
(Atomic token increment: input, output, total)        (Long-term analytics & auditing)
```

---

## 2. Database Recommendation: Why Cloud Firestore?

| Database | Latency | Scalability | Operational Complexity | Cost Model | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cloud Firestore** | **< 10ms** | **Serverless (Auto)** | **Zero (Native IAM, No VPC)** | **Pay per write/read ($0 idle)** | **⭐️ Recommended** |
| **Cloud SQL (PostgreSQL)** | 10–25ms | Fixed instances | High (Requires Serverless VPC Connector + proxy) | Continuous instance cost | Not ideal for lightweight counters |
| **Cloud Spanner** | < 10ms | Enterprise scale | Medium (Requires node provisioning) | High minimum cost | Overkill for token counting |
| **BigQuery** | 1–3s | Infinite | Zero (Append-only) | Cheap storage, slow per-row updates | Excellent for audit sink, not for live counters |

### Why Cloud Firestore is the Best Fit:
1. **Atomic Increments:** Firestore provides native atomic field increments (`firestore.Increment(amount)`), allowing concurrent requests from the same user to safely update token totals without read-modify-write race conditions or distributed locking.
2. **Serverless & Zero-Cost Idle:** Automatically scales to zero when traffic stops and scales to thousands of concurrent requests seamlessly.
3. **No VPC Connector Required:** Connects directly via Google Cloud internal APIs using the Cloud Run runtime Service Account's IAM permissions (`roles/datastore.user`).
4. **Recommended Hybrid Pattern:**
   - **Firestore:** Maintains live, stateful per-user counters for quotas and real-time dashboard lookups.
   - **Cloud Logging + BigQuery Export:** Captures every individual token event for immutable compliance auditing and cost allocation.

---

## 3. Cloud IAM Authentication Architecture

Cloud Run provides infrastructure-level authentication via Google Cloud IAM:

1. **Service Ingress Protection:** The service is deployed with `--no-allow-unauthenticated`. Google Front End automatically drops any unauthenticated or unauthorized traffic with HTTP `401 Unauthorized` or `403 Forbidden` before it reaches the container.
2. **Invoker Authorization:** Only users, groups, or service accounts granted the `roles/run.invoker` role on the Cloud Run service can generate a valid OIDC token to call the proxy.
3. **User Identity Extraction:**
   - Callers supply an OIDC identity token: `Authorization: Bearer <ID_TOKEN>`.
   - The proxy decodes the verified claims (`email` or `sub`) to attribute input and output tokens accurately to that specific user.
   - If accessed via Identity-Aware Proxy (IAP) or Cloud Load Balancer, the service also supports `X-Goog-Authenticated-User-Email`.

---

## 4. Project Structure

```
.
├── Dockerfile                   # Hardened, non-root container for Cloud Run
├── requirements.txt             # Application dependencies
├── .dockerignore
├── app/
│   ├── __init__.py
│   ├── config.py                # Environment & model settings (gemini-3.8-flash, global)
│   ├── auth.py                  # Cloud IAM identity extraction
│   ├── database.py              # Firestore atomic increment repository
│   ├── gemini_client.py         # Google GenAI SDK client for Gemini 3.8 Flash
│   └── main.py                  # FastAPI endpoints & structured JSON logging
└── tests/
    ├── __init__.py
    └── test_proxy.py            # Unit tests verifying auth, validation, and tokens
```

---

## 5. Deployment Instructions

### Prerequisites
- Google Cloud CLI (`gcloud`) installed and authenticated.
- Target GCP project with billing enabled.

### Step 1: Enable Required Google APIs
```bash
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com \
  --project="PROJECT_ID"
```

### Step 2: Create a Dedicated Service Account
```bash
# Create service account for the Cloud Run proxy
gcloud iam service-accounts create gemini-proxy-sa \
  --display-name="Gemini 3.8 Flash Proxy Service Account" \
  --project="PROJECT_ID"

# Grant Vertex AI user (to invoke Gemini 3.8 Flash in global region)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:gemini-proxy-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Grant Firestore user (to maintain per-user token counters)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:gemini-proxy-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# Grant Cloud Logging writer (to emit structured audit logs)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:gemini-proxy-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy gemini-38-flash-proxy \
  --source . \
  --region us-central1 \
  --platform managed \
  --service-account="gemini-proxy-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=PROJECT_ID,GEMINI_LOCATION=global,GEMINI_MODEL=gemini-3.8-flash" \
  --no-allow-unauthenticated \
  --project="PROJECT_ID"
```

### Step 4: Grant Invoker Permissions to Authorized Callers
```bash
# Allow specific user or group to invoke the proxy
gcloud run services add-iam-policy-binding gemini-38-flash-proxy \
  --region us-central1 \
  --member="user:developer@example.com" \
  --role="roles/run.invoker" \
  --project="PROJECT_ID"
```

---

### Deployed Service Details
- **Service Name:** `gemini-38-flash-proxy`
- **Region:** `us-central1`
- **Project:** `PROJECT_ID`
- **Service URL:** `https://gemini-38-flash-proxy-PROJECT_NUMBER.us-central1.run.app`
- **Model:** `gemini-3.8-flash` (Global region)
- **Database:** Cloud Firestore (`nam5` multi-region)
- **Runtime Service Account:** `gemini-proxy-sa@PROJECT_ID.iam.gserviceaccount.com`

---

## 6. How to Invoke the Proxy

### Option A: Using `curl` with `gcloud` Identity Token
```bash
SERVICE_URL="https://gemini-38-flash-proxy-PROJECT_NUMBER.us-central1.run.app"
# Or retrieve automatically via:
# SERVICE_URL=$(gcloud run services describe gemini-38-flash-proxy --region us-central1 --format 'value(status.url)')
ID_TOKEN=$(gcloud auth print-identity-token)

curl -X POST "${SERVICE_URL}/v1/generate" \
  -H "Authorization: Bearer ${ID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the architectural advantages of Gemini 3.8 Flash.",
    "thinking_level": "MEDIUM"
  }'
```

#### Example Response:
```json
{
  "text": "Gemini 3.8 Flash provides substantial improvements across agentic reasoning...",
  "model": "gemini-3.8-flash",
  "user_id": "developer@example.com",
  "usage": {
    "prompt_tokens": 14,
    "candidates_tokens": 128,
    "total_tokens": 142
  }
}
```

### Option B: Check User Usage
```bash
curl -X GET "${SERVICE_URL}/v1/users/me/usage" \
  -H "Authorization: Bearer ${ID_TOKEN}"
```

#### Example Usage Output:
```json
{
  "user_id": "developer@example.com",
  "total_input_tokens": 2850,
  "total_output_tokens": 15420,
  "total_tokens": 18270,
  "last_active": "2026-09-21T11:25:00Z",
  "models": {
    "gemini-3_8-flash": {
      "input_tokens": 2850,
      "output_tokens": 15420,
      "total_tokens": 18270
    }
  }
}
```

---

## 7. Running Tests Locally

```bash
PYTHONPATH=. uv run --with-requirements requirements.txt pytest tests/
```
