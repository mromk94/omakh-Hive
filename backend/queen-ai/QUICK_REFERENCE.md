# OMK HIVE - QUICK REFERENCE CARD
**System Control & Debugging Commands**

---

## 🚀 **BASIC COMMANDS**

```bash
# Start system
python3 manage.py start

# Stop system
python3 manage.py stop

# Restart system
python3 manage.py restart

# System status (live dashboard)
python3 manage.py status

# Health check
python3 manage.py health

# View logs
python3 manage.py logs

# View logs live
python3 manage.py logs --follow
```

---

## 🔍 **MONITORING**

```bash
# Real-time dashboard (refresh every 2s)
python3 status.py

# Continuous health monitoring
python3 health_check.py --watch

# Check specific component
python3 health_check.py --component database
python3 health_check.py --component redis
python3 health_check.py --component llm
```

---

## 🐛 **DEBUGGING**

```bash
# Analyze logs (last 1 hour)
python3 debug.py --logs

# Trace specific error
python3 debug.py --trace "connection timeout"

# Performance profiling
python3 debug.py --profile

# Inspect component
python3 debug.py --inspect database
python3 debug.py --inspect redis
python3 debug.py --inspect llm
python3 debug.py --inspect bees

# Run all debugging tools
python3 debug.py --all
```

---

## 🧪 **TESTING**

```bash
# Run full pipeline test (27 tests)
python3 manage.py test

# Run private sale tests (46 tests)
python3 manage.py test --type private_sale

# Run integration tests
python3 manage.py test --type integration
```

---

## 💾 **DATABASE**

```bash
# Initialize database
python3 manage.py db setup

# Run migrations
python3 manage.py db migrate

# Check migration status
python3 manage.py db status

# Rollback last migration
python3 manage.py db rollback
```

---

## 🚢 **DEPLOYMENT**

```bash
# Deploy locally
python3 manage.py deploy local

# Deploy to GCP with Terraform
python3 manage.py deploy gcp

# Build Docker image
python3 manage.py deploy docker
```

---

## 📊 **LOG FILES**

```
logs/queen.log          # Main application log
logs/errors.log         # Errors only
logs/access.log         # API requests
logs/performance.log    # Performance metrics
```

---

## 🔧 **TROUBLESHOOTING**

```bash
# System won't start
python3 health_check.py
python3 stop.py --force
python3 start.py --debug

# High CPU/Memory
python3 debug.py --profile
python3 status.py

# Component failure
python3 health_check.py --component <name>
python3 debug.py --inspect <name>

# Error investigation
python3 debug.py --logs
python3 debug.py --trace "<error_message>"
```

---

## 📝 **COMMON OPTIONS**

```bash
--environment production    # Production mode
--debug                     # Debug mode
--force                     # Force operation
--watch                     # Continuous monitoring
--follow                    # Live tail logs
--component <name>          # Specific component
--refresh 5                 # Update every 5 seconds
```

---

## 🌐 **ENVIRONMENTS**

- `development` - Local development (default)
- `staging` - Staging environment
- `production` - Production environment

---

## 💡 **PRO TIPS**

```bash
# Start with live monitoring
python3 manage.py start && python3 manage.py status

# Health check before deploying
python3 manage.py health && python3 manage.py deploy gcp

# Debug with all tools
python3 manage.py debug --all

# Watch logs for errors
python3 manage.py logs --file errors.log --follow
```

---

**For full documentation**: See `LIFECYCLE_MANAGEMENT.md`
