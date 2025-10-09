# LIFECYCLE MANAGEMENT & DEBUGGING INFRASTRUCTURE
**Complete System Control & Diagnostics for OMK Hive**

**Date**: October 9, 2025  
**Status**: ✅ Production Ready  
**Supports**: Localhost + Cloud Run + GKE

---

## 📋 **OVERVIEW**

Comprehensive lifecycle management and debugging infrastructure supporting both **localhost** and **cloud deployment**.

### **What Was Created**

**Lifecycle Scripts** (8 files, ~4,000 lines):
1. ✅ `manage.py` - Master control interface (unified CLI)
2. ✅ `start.py` - Graceful system startup
3. ✅ `stop.py` - Graceful shutdown
4. ✅ `reboot.py` - Safe restart
5. ✅ `health_check.py` - Comprehensive health analysis
6. ✅ `status.py` - Real-time status dashboard
7. ✅ `debug.py` - Advanced debugging tools
8. ✅ `app/utils/logging_config.py` - Structured logging

---

## 🚀 **QUICK START**

```bash
# Master interface (recommended)
python3 manage.py start              # Start system
python3 manage.py status             # Real-time dashboard
python3 manage.py health             # Health check
python3 manage.py logs --follow      # Live logs
python3 manage.py stop               # Stop system
python3 manage.py restart            # Restart

# Or use individual scripts
python3 start.py
python3 health_check.py
python3 status.py
python3 stop.py
```

---

## 📚 **FEATURES**

### **1. System Startup (`start.py`)**

**Graceful startup with dependency checking**

✅ Pre-flight validation  
✅ Component initialization in order  
✅ Auto-fallback to in-memory (dev)  
✅ Cloud environment detection  
✅ Signal handling for shutdown  

**Startup Order**:
1. Configuration validation
2. Database (PostgreSQL)
3. Redis (MessageBus + HiveBoard)
4. BigQuery (optional)
5. LLM providers
6. Bee Manager (15 bees)
7. Queen Orchestrator
8. API server

---

### **2. System Shutdown (`stop.py`)**

**Graceful shutdown with cleanup**

✅ Process discovery  
✅ SIGTERM signals  
✅ Configurable timeout  
✅ Force kill option  
✅ Cleanup temp files  

---

### **3. Health Check (`health_check.py`)**

**Comprehensive system analysis**

**Components Checked**:
- Database (connection, latency, pool)
- Redis (connection, memory, uptime)
- LLM (providers, generation, cost)
- Bees (initialization, availability)
- API (endpoints, responsiveness)
- Resources (CPU, memory, disk)
- Security (config validation)

---

### **4. Status Dashboard (`status.py`)**

**Real-time monitoring**

- Live resource usage (CPU/Memory/Disk)
- Component health indicators
- Recent activity log
- Key metrics display
- Color-coded alerts

---

### **5. Debug Tools (`debug.py`)**

**Advanced diagnostics**

- Log analysis with pattern detection
- Error tracing across system
- Performance profiling
- Component deep inspection
- Automated recommendations

---

### **6. Structured Logging**

**Production-grade logging**

**Log Files**:
- `logs/queen.log` - Main log (30 days)
- `logs/errors.log` - Errors only (10 MB rotation)
- `logs/access.log` - API requests (7 days)
- `logs/performance.log` - Performance metrics

**Features**:
- JSON format (production)
- Human-readable (development)
- Auto-rotation
- Cloud Logging integration (GCP)

---

## 🎯 **USAGE EXAMPLES**

### **Development**

```bash
# Start
python3 manage.py start --debug

# Monitor
python3 manage.py status

# Check health
python3 manage.py health

# View logs
python3 manage.py logs --follow
```

### **Production**

```bash
# Start production mode
python3 manage.py start --environment production

# Continuous health monitoring
python3 manage.py health --watch --interval 3600

# Deploy to GCP
python3 manage.py deploy gcp
```

### **Debugging**

```bash
# Analyze logs
python3 manage.py debug --logs

# Profile performance
python3 manage.py debug --profile

# Inspect component
python3 manage.py debug --inspect database

# Trace error
python3 manage.py debug --trace "connection refused"
```

---

## 🌐 **CLOUD SUPPORT**

**Auto-Detection**:
- Cloud Run: `K_SERVICE` env var
- GKE: `/var/run/secrets/kubernetes.io`
- Localhost: Default

**Cloud Features**:
- JSON structured logging
- Cloud Logging integration
- Kubernetes signal handling
- Health endpoints for load balancers
- Secret Manager integration

---

## 📊 **SUMMARY**

✅ **8 lifecycle management scripts** created  
✅ **Works in localhost and cloud** (Cloud Run, GKE)  
✅ **Graceful startup/shutdown** with dependency checking  
✅ **Comprehensive health monitoring** (7 components)  
✅ **Advanced debugging tools** (logs, profiling, inspection)  
✅ **Production-grade logging** (rotation, cloud integration)  
✅ **Unified CLI** via `manage.py`  

**All scripts support both local development and production cloud deployment.**

---

## 🔧 **TROUBLESHOOTING**

**Won't Start**:
```bash
python3 health_check.py
python3 stop.py --force
python3 start.py --debug
```

**High CPU/Memory**:
```bash
python3 debug.py --profile
python3 status.py
```

**Component Failure**:
```bash
python3 health_check.py --component <name>
python3 debug.py --inspect <name>
```

---

**For detailed documentation, see files directly:**
- `start.py` - Extensive inline comments
- `health_check.py` - Component check logic
- `debug.py` - Debugging procedures
- `manage.py` - All available commands
