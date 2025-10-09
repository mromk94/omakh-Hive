# OMK Hive - Google Cloud Platform Infrastructure
# Terraform configuration for complete GCP deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Store state in Cloud Storage (recommended for team collaboration)
  backend "gcs" {
    bucket = "omk-hive-terraform-state"
    prefix = "terraform/state"
  }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (staging, production)"
  type        = string
  default     = "staging"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",  # Vertex AI
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])
  
  service = each.value
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "omk-hive-vpc-${var.environment}"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.required_apis]
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "omk-hive-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.1.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "postgres" {
  name             = "omk-hive-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = var.environment == "production" ? "db-custom-2-8192" : "db-f1-micro"
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc.id
      
      authorized_networks {
        name  = "allow-all-temp"
        value = "0.0.0.0/0"  # TODO: Restrict in production
      }
    }
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "production"
      start_time                     = "03:00"
      transaction_log_retention_days = 7
    }
    
    maintenance_window {
      day  = 7  # Sunday
      hour = 3
    }
    
    insights_config {
      query_insights_enabled = true
    }
  }
  
  deletion_protection = var.environment == "production" ? true : false
}

resource "google_sql_database" "database" {
  name     = "omk_hive"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "omk_admin"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store DB password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "omk-hive-db-password-${var.environment}"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Memorystore (Redis)
resource "google_redis_instance" "redis" {
  name               = "omk-hive-redis-${var.environment}"
  tier               = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb     = var.environment == "production" ? 5 : 1
  region             = var.region
  authorized_network = google_compute_network.vpc.id
  redis_version      = "REDIS_7_0"
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }
}

# GKE Autopilot Cluster
resource "google_container_cluster" "primary" {
  name     = "omk-hive-cluster-${var.environment}"
  location = var.region
  
  # Autopilot mode
  enable_autopilot = true
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
  
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  # Binary Authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }
}

# BigQuery Dataset (Learning Function)
resource "google_bigquery_dataset" "learning" {
  dataset_id  = "omk_hive_learning"
  description = "Learning function training data"
  location    = "US"
  
  default_table_expiration_ms = 31536000000  # 1 year
  
  labels = {
    environment = var.environment
    purpose     = "ml-training"
  }
}

# Artifact Registry for containers
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "omk-hive"
  description   = "OMK Hive container images"
  format        = "DOCKER"
}

# Cloud Storage bucket for backups
resource "google_storage_bucket" "backups" {
  name          = "omk-hive-backups-${var.project_id}"
  location      = var.region
  force_destroy = false
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Service Account for Cloud Build
resource "google_service_account" "cloud_build" {
  account_id   = "omk-hive-cloud-build"
  display_name = "OMK Hive Cloud Build Service Account"
}

# IAM roles for Cloud Build
resource "google_project_iam_member" "cloud_build_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/container.developer",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_build.email}"
}

# Service Account for GKE workloads
resource "google_service_account" "gke_workload" {
  account_id   = "omk-hive-gke-workload"
  display_name = "OMK Hive GKE Workload Service Account"
}

# IAM roles for GKE workloads
resource "google_project_iam_member" "gke_workload_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataEditor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

# Outputs
output "database_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL connection name"
}

output "database_ip" {
  value       = google_sql_database_instance.postgres.ip_address.0.ip_address
  description = "Database IP address"
}

output "redis_host" {
  value       = google_redis_instance.redis.host
  description = "Redis host"
}

output "redis_port" {
  value       = google_redis_instance.redis.port
  description = "Redis port"
}

output "gke_cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE cluster name"
}

output "artifact_registry_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
  description = "Artifact Registry URL"
}

output "bigquery_dataset_id" {
  value       = google_bigquery_dataset.learning.dataset_id
  description = "BigQuery dataset ID"
}

output "workload_service_account_email" {
  value       = google_service_account.gke_workload.email
  description = "GKE workload service account email"
}
