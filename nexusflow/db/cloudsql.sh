# Create a PostgreSQL instance in Cloud SQL
# Note: This would typically be done through Google Cloud Console or gcloud CLI
gcloud sql instances create nexusflow-db \
    --database-version=POSTGRES_13 \
    --cpu=2 \
    --memory=4GB \
    --region=us-central1

# Create database
gcloud sql databases create nexusflow \
    --instance=nexusflow-db

# Create user
gcloud sql users create nexusflow-user \
    --instance=nexusflow-db \
    --password=SECURE_PASSWORD
