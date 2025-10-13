# 🚀 QUICK START - Database Setup

**Time to complete:** ~5 minutes  
**Prerequisites:** MySQL installed

---

## ⚡ **ONE-COMMAND SETUP**

```bash
cd /Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai && ./setup_database.sh
```

That's it! This will:
1. ✅ Create `omk-hive1` database
2. ✅ Install Python dependencies
3. ✅ Create all tables
4. ✅ Seed admin & demo users
5. ✅ Configure system settings

---

## 🔐 **CREDENTIALS**

### **Admin Account:**
- **Email:** `king@omakh.io`
- **Password:** `Successtrain2025@@`
- **Role:** ADMIN (full access)

### **Demo Users:**
- **Email:** `demo1@omakh.io` or `demo2@omakh.io`
- **Password:** `demouser1234`
- **Role:** USER
- **Pre-loaded with OMK balance for testing**

---

## 🧪 **TEST IT WORKS**

### **Test 1: Login as Admin**
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "king@omakh.io", "password": "Successtrain2025@@"}'
```

**Expected:** Returns JWT token + user info

### **Test 2: Get Current User**
```bash
# Get token first
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "king@omakh.io", "password": "Successtrain2025@@"}' \
  | jq -r '.access_token')

# Get user info
curl http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Returns current user details

### **Test 3: Check Database**
```bash
mysql -u root -p'Successtrain2025@@' omk-hive1 -e "SELECT email, role FROM users;"
```

**Expected:**
```
+------------------+-------+
| email            | role  |
+------------------+-------+
| king@omakh.io    | admin |
| demo1@omakh.io   | user  |
| demo2@omakh.io   | user  |
+------------------+-------+
```

---

## 🔧 **TROUBLESHOOTING**

### **Problem: MySQL not running**
```bash
# macOS
brew services start mysql

# Or manually
mysql.server start
```

### **Problem: Access denied for root**
```bash
# Reset MySQL root password
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Successtrain2025@@';
FLUSH PRIVILEGES;
EXIT;
```

### **Problem: Database already exists**
```bash
# Drop and recreate (WARNING: deletes all data)
mysql -u root -p'Successtrain2025@@' -e "DROP DATABASE IF EXISTS \`omk-hive1\`;"
./setup_database.sh
```

### **Problem: Python dependencies missing**
```bash
pip install pymysql cryptography passlib python-jose sqlalchemy
```

---

## 📊 **DATABASE SCHEMA**

**8 Tables Created:**
1. **users** - All user accounts (admin, demo, regular)
2. **otc_requests** - OTC purchase requests
3. **system_config** - Dynamic configuration (payment methods, TGE date, etc.)
4. **transactions** - Blockchain transactions
5. **queen_ai_logs** - AI chat logs
6. **properties** - Tokenized real estate
7. **property_investments** - User property investments
8. **analytics** - Event tracking

---

## 🔌 **NEW API ENDPOINTS**

### **Authentication:**
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/register` - Create new account
- `GET /api/v1/auth/me` - Get current user (requires token)
- `POST /api/v1/auth/logout` - Logout

### **Headers for Protected Routes:**
```
Authorization: Bearer <your_jwt_token>
```

---

## 📝 **NEXT STEPS**

### **1. Frontend Integration**
Update login page to use new auth endpoints:
```typescript
// Login
const response = await fetch('http://localhost:8001/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token, user } = await response.json();

// Store token
localStorage.setItem('auth_token', access_token);
localStorage.setItem('user', JSON.stringify(user));

// Use token in requests
fetch('http://localhost:8001/api/v1/admin/config', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
});
```

### **2. Update Existing Endpoints**
All admin endpoints should now:
1. Require JWT authentication
2. Verify user role (admin)
3. Use database instead of JSON files
4. Log to analytics table

### **3. OTC Flow Integration**
When user submits OTC request:
1. Check if user is logged in → Link to user_id
2. Insert into `otc_requests` table
3. Log to `transactions` table
4. Send email confirmation
5. Admin can approve/reject from database

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Database `omk-hive1` created
- [ ] 8 tables exist (`SHOW TABLES;`)
- [ ] 3 users seeded (1 admin, 2 demo)
- [ ] Admin login works (returns JWT token)
- [ ] Demo user login works
- [ ] `/api/v1/auth/me` returns user info with valid token
- [ ] MySQL service running (`brew services list`)
- [ ] Backend starts without errors

---

## 🎯 **SUMMARY**

**You now have:**
- ✅ Production-grade MySQL database
- ✅ JWT authentication system
- ✅ Admin account (king@omakh.io)
- ✅ 2 demo users for testing
- ✅ 8 comprehensive tables
- ✅ Secure password hashing (bcrypt)
- ✅ Role-based access control
- ✅ API endpoints ready to use

**Database is FULLY OPERATIONAL!** 🚀

---

**Full Documentation:** See `DATABASE_IMPLEMENTATION_GUIDE.md`
