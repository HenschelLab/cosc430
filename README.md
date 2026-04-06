# Flask ML Model API — Docker + GitHub Actions + Google Cloud Run

A minimal end-to-end ML deployment pipeline: a PyTorch neural network served via Flask/Gunicorn,
containerized with Docker, and automatically deployed to Google Cloud Run on every `git push`.

## Architecture

```
Local Development
      |
      v
  GitHub Repo  ── push to main ──►  GitHub Actions
                                          │
                                 Build Docker Image
                                 (includes model.pt)
                                          │
                                 Push to Artifact Registry
                                          │
                                 Deploy to Cloud Run
                                          │
                                          ▼
                                 Public HTTPS API
```

---

## The Model

`IrisNet` is a small MLP (4 → 16 → 3) trained on the
[Iris dataset](https://scikit-learn.org/stable/datasets/toy_dataset.html#iris-dataset):
4 numerical features (sepal/petal length and width), 3 output classes (setosa, versicolor,
virginica). Normalization statistics are baked into the model as buffers so no preprocessing
is needed at inference time.

Training is done locally via `model_dev.py`. The resulting `model.pt` is committed to the repo
and copied into the Docker image at build time — the container only runs inference, not training.

### The `.pt` format

`model.pt` is a binary file produced by `torch.save(model.state_dict(), ...)`. It stores the
model's weights (and normalization buffers) using Python's pickle protocol. Loading with
`weights_only=True` (PyTorch ≥ 2.0) restricts unpickling to tensor data only, preventing
arbitrary code execution.

---

## Repository Structure

```
app.py          Flask API — loads model.pt, serves /predict
model.py        IrisNet class definition
model_dev.py    Training script (run locally, produces model.pt)
model.pt        Trained weights — build artifact, committed to repo
Dockerfile      Builds the production image (python:3.11-slim + Gunicorn)
requirements.txt  flask, gunicorn, torch (CPU)
.github/
  workflows/
    deploy.yml  CI/CD pipeline — build, push, deploy on every push to main
    gcpSetup.sh GCP service account and IAM setup (run once)
```

---

## API

**`POST /predict`**

Accepts a JSON body with a 2D array `X` (one row per sample, 4 features each).
Returns the predicted class index for each row.

```bash
curl -X POST https://<your-cloud-run-url>/predict \
  -H "Content-Type: application/json" \
  -d '{"X": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6], [6.3, 2.7, 4.9, 1.8]]}'
```

```json
{"y": [0, 1, 2]}
```

`0` = setosa, `1` = versicolor, `2` = virginica.

---

## Local Development

### Run Flask dev server

```bash
pip install flask torch scikit-learn
python app.py
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"X": [[5.1, 3.5, 1.4, 0.2]]}'
```

### Run in Docker

```bash
docker build -t flask-model-api .
docker run -p 8080:8080 flask-model-api
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"X": [[5.1, 3.5, 1.4, 0.2]]}'
```

### Retrain the model

```bash
pip install scikit-learn torch
python model_dev.py   # produces model.pt
```

---

## Deployment

### Google Cloud setup (once)

```bash
gcloud config set project your-project-id
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
gcloud artifacts repositories create flask-model-api \
  --repository-format=docker --location=us-central1
```

See `.github/workflows/gcpSetup.sh` for the full service account and IAM setup.

### GitHub Secrets and Variables

In **Settings → Secrets and variables → Actions**:

| Type | Name | Value |
|------|------|-------|
| Secret | `GCP_SA_KEY` | Contents of the service account JSON key |
| Variable | `GCP_PROJECT_ID` | Your GCP project ID |

### CI/CD

The workflow in `.github/workflows/deploy.yml` triggers on every push to `main`:

1. Authenticate to Google Cloud
2. Build Docker image (tagged with commit SHA and `:latest`)
3. Push to Artifact Registry
4. Deploy to Cloud Run (`--allow-unauthenticated`, port 8080)

The workflow can also be triggered manually from the **Actions** tab via **Run workflow**.

### Get your live URL

```bash
gcloud run services describe flask-model-api \
  --region us-central1 --project your-project-id \
  --format "value(status.url)"
```

---

## Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| ML model | PyTorch | Train and run `IrisNet` |
| API server | Flask + Gunicorn | Serve predictions over HTTP |
| Containerization | Docker | Reproducible, portable runtime |
| Image registry | GCP Artifact Registry | Store versioned Docker images |
| CI/CD | GitHub Actions | Automate build and deploy on push |
| Cloud hosting | Google Cloud Run | Serverless, scalable container hosting |
