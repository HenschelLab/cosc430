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

# Download the JSON key
gcloud iam service-accounts keys create key.json \
  --iam-account github-deployer@cosc430deploy.iam.gserviceaccount.com
