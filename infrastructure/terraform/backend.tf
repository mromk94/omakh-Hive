# Backend configuration for Terraform state
# Uncomment and configure after creating the GCS bucket

# terraform {
#   backend "gcs" {
#     bucket  = "omk-hive-terraform-state"
#     prefix  = "terraform/state"
#   }
# }

# To create the bucket:
# gsutil mb -p PROJECT_ID -c STANDARD -l REGION gs://omk-hive-terraform-state
# gsutil versioning set on gs://omk-hive-terraform-state
