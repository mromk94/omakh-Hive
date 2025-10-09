# Terraform - OMK Hive GCP Infrastructure

Infrastructure as Code for deploying OMK Hive to Google Cloud Platform.

---

## 📋 **Prerequisites**

1. **Install Terraform**
   ```bash
   brew install terraform
   ```

2. **Install Google Cloud SDK**
   ```bash
   brew install google-cloud-sdk
   ```

3. **Authenticate**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Enable Billing**
   - Ensure billing is enabled on your GCP project
   - Apply for Google for Startups ($200K credits)

---

## 🚀 **Quick Start**

### **1. Initialize Terraform**

```bash
cd terraform/
terraform init
```

### **2. Create terraform.tfvars**

```bash
cat > terraform.tfvars <<EOF
project_id  = "omk-hive-prod"
region      = "us-central1"
zone        = "us-central1-a"
environment = "staging"
EOF
```

### **3. Plan Deployment**

```bash
terraform plan
```

Review the changes Terraform will make.

### **4. Deploy Infrastructure**

```bash
terraform apply
```

Type `yes` to confirm.

---

## 📦 **What Gets Created**

### **Networking**
- VPC Network (`omk-hive-vpc-{env}`)
- Subnet with GKE secondary ranges
- Firewall rules

### **Databases**
- Cloud SQL PostgreSQL instance
  - Staging: db-f1-micro ($7.67/month)
  - Production: db-custom-2-8192
- Automated backups (daily, 7-day retention)
- Point-in-time recovery (production only)

### **Cache & Queue**
- Memorystore Redis instance
  - Staging: BASIC tier, 1GB
  - Production: STANDARD_HA, 5GB
- High availability in production

### **Compute**
- GKE Autopilot cluster
  - Auto-scaling
  - Auto-patching
  - Workload Identity enabled
  - Binary Authorization

### **Storage**
- BigQuery dataset (`omk_hive_learning`)
  - 1-year retention
  - Partitioned tables
- Cloud Storage bucket for backups
  - Versioning enabled
  - Lifecycle: 90 days → Coldline, 365 days → Delete

### **Container Registry**
- Artifact Registry repository
  - Docker format
  - Regional storage

### **Security**
- Secret Manager for credentials
- Service accounts with least privilege
- Workload Identity for GKE

---

## 🔧 **Configuration**

### **Environments**

**Staging** (Cost-optimized):
```hcl
environment = "staging"
db_tier     = "db-f1-micro"
redis_memory_size_gb = 1
```

**Production** (High-availability):
```hcl
environment = "production"
db_tier     = "db-custom-2-8192"
redis_memory_size_gb = 5
```

### **Regions**

Recommended regions:
- `us-central1` (Iowa) - Lowest cost, most services
- `us-east1` (South Carolina) - Good latency
- `europe-west1` (Belgium) - EU data residency

---

## 📊 **Outputs**

After deployment, Terraform outputs:

```bash
terraform output
```

**Available outputs**:
- `database_connection_name` - Cloud SQL connection string
- `database_ip` - Database IP address
- `redis_host` - Redis host
- `redis_port` - Redis port
- `gke_cluster_name` - GKE cluster name
- `artifact_registry_url` - Container registry URL
- `bigquery_dataset_id` - BigQuery dataset
- `workload_service_account_email` - Service account email

---

## 🔐 **Secrets Management**

Database password is automatically:
1. Generated (32-character random)
2. Stored in Secret Manager
3. Never exposed in Terraform state

**Access secret**:
```bash
gcloud secrets versions access latest \
  --secret="omk-hive-db-password-staging"
```

---

## 🔄 **Updates & Changes**

### **Modify Infrastructure**

1. Edit `main.tf` or `variables.tf`
2. Plan changes: `terraform plan`
3. Apply changes: `terraform apply`

### **Add New Resources**

Create new `.tf` file in `terraform/` directory:

```hcl
# redis-backup.tf
resource "google_storage_bucket" "redis_backup" {
  name     = "omk-hive-redis-backup"
  location = var.region
}
```

Run `terraform apply`.

---

## 🗑️ **Destroy Infrastructure**

⚠️ **WARNING**: This deletes ALL resources!

```bash
terraform destroy
```

Type `yes` to confirm.

**Note**: Production resources with `deletion_protection = true` cannot be destroyed without manually disabling protection first.

---

## 💰 **Cost Estimation**

### **Staging Environment**
| Resource | Cost/Month |
|----------|------------|
| Cloud SQL (db-f1-micro) | $7.67 |
| Memorystore (1GB Basic) | $35.70 |
| GKE Autopilot (minimal) | $50-100 |
| BigQuery (free tier) | $0 |
| Storage | $5-10 |
| **Total** | **$98-153** |

### **Production Environment**
| Resource | Cost/Month |
|----------|------------|
| Cloud SQL (custom-2-8192) | $158 |
| Memorystore (5GB HA) | $238 |
| GKE Autopilot (scaled) | $300-500 |
| BigQuery | $50-100 |
| Storage | $20-30 |
| **Total** | **$766-1,026** |

**With $200K startup credits**: $0 for ~2 years

---

## 🔍 **Troubleshooting**

### **"APIs not enabled"**

Enable required APIs:
```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com
```

### **"Insufficient permissions"**

Grant yourself Owner role:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/owner"
```

### **"Terraform state locked"**

```bash
terraform force-unlock LOCK_ID
```

### **"Backend bucket doesn't exist"**

Create state bucket:
```bash
gsutil mb gs://omk-hive-terraform-state
gsutil versioning set on gs://omk-hive-terraform-state
```

---

## 🔄 **CI/CD Integration**

Terraform can be run in Cloud Build:

```yaml
# cloudbuild-terraform.yaml
steps:
  - name: 'hashicorp/terraform:latest'
    args: ['init']
  - name: 'hashicorp/terraform:latest'
    args: ['plan']
  - name: 'hashicorp/terraform:latest'
    args: ['apply', '-auto-approve']
```

---

## 📝 **Best Practices**

1. **Use Workspaces** for multiple environments
   ```bash
   terraform workspace new production
   terraform workspace select production
   ```

2. **Remote State** in Cloud Storage
   - Team collaboration
   - State locking
   - Version history

3. **Plan Before Apply**
   - Always review changes
   - Use `-out` flag to save plan

4. **Use Variables**
   - Never hardcode values
   - Use `terraform.tfvars`
   - Environment-specific configs

5. **Tag Resources**
   - Add labels for cost tracking
   - Environment tags
   - Owner tags

---

## 🔗 **Related Files**

- `main.tf` - Main infrastructure definition
- `variables.tf` - Input variables
- `terraform.tfvars` - Variable values (gitignored)
- `outputs.tf` - Output values

---

**Created**: October 9, 2025  
**Terraform Version**: >= 1.0  
**Provider**: google ~> 5.0
