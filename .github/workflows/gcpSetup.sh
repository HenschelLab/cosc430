# Create and Set your project
gcloud projects create cosc430deploy
gcloud config set project cosc430deploy

# Enable required APIs
#gcloud services enable run.googleapis.com containerregistry.googleapis.com --project=cosc430deploy
gcloud services enable run.googleapis.com containerregistry.googleapis.com

# Create the service account
gcloud iam service-accounts create github-deployer \
  --display-name "GitHub Actions Deployer"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding cosc430deploy \
  --member "serviceAccount:github-deployer@cosc430deploy.iam.gserviceaccount.com" \
  --role "roles/run.admin"

# Grant Storage Admin role (needed to push to GCR)
gcloud projects add-iam-policy-binding cosc430deploy \
  --member "serviceAccount:github-deployer@cosc430deploy.iam.gserviceaccount.com" \
  --role "roles/storage.admin"

# Grant Service Account User role (needed for Cloud Run to act as the SA)
gcloud projects add-iam-policy-binding cosc430deploy \
  --member "serviceAccount:github-deployer@cosc430deploy.iam.gserviceaccount.com" \
  --role "roles/iam.serviceAccountUser"

#GCP migrated GCR (gcr.io) to run on Artifact Registry under the hood, so Storage Admin is 
#no longer sufficient. Need to grant the Artifact Registry Writer role:
gcloud projects add-iam-policy-binding cosc430deploy \
  --member "serviceAccount:github-deployer@cosc430deploy.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.writer"
gcloud services enable artifactregistry.googleapis.com

# Download the JSON key
gcloud iam service-accounts keys create key.json \
  --iam-account github-deployer@cosc430deploy.iam.gserviceaccount.com

#The Cloud Run deployment gives you a public URL. Get it with:
gcloud run services describe flask-model-api \
  --region us-central1 \
  --project cosc430deploy \
  --format "value(status.url)"

# pseudo commands
#gcloud services enable apis
#gcloud iam # github-deployer roles
#gcloud run services


