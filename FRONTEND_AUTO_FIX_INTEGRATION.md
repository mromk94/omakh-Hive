# 🎨 Frontend Auto-Fix Integration Guide

**What to add to make the autonomous loop visible in the UI**

---

## 📍 **Where to Add: ProposalDetail Component**

**File:** `/omk-frontend/app/kingdom/components/QueenDevelopmentHub.tsx`

---

## 1️⃣ **Add Auto-Fix Button**

**Location:** In the ProposalDetail component, after test results section

```tsx
// Inside ProposalDetail function
const [autoFixing, setAutoFixing] = useState(false);
const [autoFixProgress, setAutoFixProgress] = useState('');

const triggerAutoFix = async () => {
  setAutoFixing(true);
  setAutoFixProgress('Analyzing failure...');
  
  try {
    const token = localStorage.getItem('auth_token') || 'dev_token';
    const response = await fetch(
      `${BACKEND_URL}/api/v1/admin/proposals/auto-fix/${proposal.id}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    const result = await response.json();
    
    if (result.success && result.fix_applied) {
      toast.success(`✅ Fix applied! Attempt ${result.attempts}/3`);
      setAutoFixProgress(`Fixed: ${result.explanation}`);
      
      // Refresh proposal to show updated code
      onUpdate();
      
      // Suggest re-testing
      toast.info('💡 Ready to re-test! Click "Deploy to Sandbox" again');
    } else {
      toast.error(result.error || 'Auto-fix failed');
    }
  } catch (error: any) {
    toast.error(`❌ ${error.message}`);
  } finally {
    setAutoFixing(false);
  }
};

// In the JSX, after test results:
{proposal.status === 'tests_failed' && proposal.needs_auto_fix && (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="mt-6 p-6 bg-purple-500/10 border border-purple-500/30 rounded-xl"
  >
    <div className="flex items-start gap-4">
      <AlertTriangle className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-purple-400 mb-2">
          Tests Failed - Auto-Fix Available
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Claude can analyze the failure and automatically generate a fix.
          This may take 30-60 seconds.
        </p>
        
        {autoFixing ? (
          <div className="flex items-center gap-3">
            <Loader className="w-5 h-5 animate-spin text-purple-400" />
            <span className="text-purple-300">{autoFixProgress}</span>
          </div>
        ) : (
          <button
            onClick={triggerAutoFix}
            className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white font-semibold rounded-lg transition-all flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            🤖 Auto-Fix & Retry
          </button>
        )}
      </div>
    </div>
  </motion.div>
)}
```

---

## 2️⃣ **Add Fix History Display**

**Location:** Below the auto-fix button

```tsx
{proposal.auto_fix_history && proposal.auto_fix_history.length > 0 && (
  <div className="mt-6">
    <h3 className="text-lg font-semibold text-white mb-4">
      🔧 Auto-Fix History ({proposal.auto_fix_history.length} attempts)
    </h3>
    
    <div className="space-y-4">
      {proposal.auto_fix_history.map((fix: any, index: number) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-gray-900/50 border border-gray-700 rounded-lg p-4"
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <h4 className="font-semibold text-white">
                Attempt {fix.attempt}
              </h4>
              <p className="text-xs text-gray-500">
                {new Date(fix.timestamp).toLocaleString()}
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              index === proposal.auto_fix_history.length - 1
                ? 'bg-purple-500/20 text-purple-400'
                : 'bg-gray-700 text-gray-400'
            }`}>
              {index === proposal.auto_fix_history.length - 1 ? 'Latest' : 'Previous'}
            </span>
          </div>
          
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-400">Root Cause:</span>
              <span className="ml-2 text-yellow-400">
                {fix.analysis.root_cause}
              </span>
            </div>
            
            <div>
              <span className="text-gray-400">Error Types:</span>
              <span className="ml-2 text-red-400">
                {fix.analysis.error_types.join(', ')}
              </span>
            </div>
            
            {fix.fix.explanation && (
              <div>
                <span className="text-gray-400">Fix Applied:</span>
                <p className="mt-1 text-green-400">
                  {fix.fix.explanation}
                </p>
              </div>
            )}
            
            {fix.fix.changes && fix.fix.changes.length > 0 && (
              <div className="mt-3">
                <span className="text-gray-400">Files Modified:</span>
                <ul className="mt-2 space-y-1">
                  {fix.fix.changes.map((change: any, i: number) => (
                    <li key={i} className="text-xs">
                      <Code className="w-3 h-3 inline mr-1" />
                      <span className="text-blue-400">{change.file}</span>
                      <span className="text-gray-500 ml-2">({change.action})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  </div>
)}
```

---

## 3️⃣ **Add Status Badge**

**Location:** In proposal card header

```tsx
// In ProposalCard component
{proposal.auto_fix_applied && (
  <span className="px-2 py-1 bg-purple-500/20 border border-purple-500/30 text-purple-400 rounded-full text-xs font-medium flex items-center gap-1">
    <Zap className="w-3 h-3" />
    Auto-Fixed
  </span>
)}
```

---

## 4️⃣ **Update Test Results Display**

**Location:** In test results section

```tsx
{testResults.overall_status === 'failed' && testResults.needs_auto_fix && (
  <div className="mt-4 p-4 bg-purple-500/10 border-l-4 border-purple-500 rounded">
    <div className="flex items-center gap-2 text-purple-400 font-semibold">
      <Sparkles className="w-4 h-4" />
      Auto-fix available - Click the button below to let Claude fix this
    </div>
  </div>
)}
```

---

## 5️⃣ **Add Toast Notifications**

```tsx
// Import at top
import toast from 'react-hot-toast';

// When auto-fix starts:
toast.loading('Claude is analyzing the failure...', { id: 'autofix' });

// When fix is generated:
toast.success('✅ Fix generated! Applying changes...', { id: 'autofix' });

// When fix is applied:
toast.success('🎉 Fix applied successfully! Ready to re-test', {
  duration: 4000,
  icon: '🤖'
});

// When fix fails:
toast.error('❌ Could not generate fix. Manual intervention needed', {
  id: 'autofix'
});
```

---

## 📊 **Complete User Flow**

```
1. User creates proposal
   ↓
2. Deploys to sandbox
   ↓
3. Tests run → FAIL
   ↓
4. UI shows: "🤖 Auto-Fix & Retry" button
   ↓
5. User clicks button
   ↓
6. Loading: "Claude is analyzing the failure..."
   ↓
7. Success: "✅ Fix applied! Attempt 1/3"
   ↓
8. UI updates: Code changes visible
   ↓
9. Suggestion: "💡 Ready to re-test!"
   ↓
10. User clicks "Deploy to Sandbox" again
   ↓
11. Tests run → PASS ✅
   ↓
12. User approves → Production deployment
```

---

## 🎨 **Visual States**

### **Failed (Before Auto-Fix):**
```
┌────────────────────────────────────┐
│ ❌ Tests Failed                    │
│                                    │
│ [🤖 Auto-Fix & Retry]             │
└────────────────────────────────────┘
```

### **Auto-Fixing:**
```
┌────────────────────────────────────┐
│ 🔄 Auto-Fixing...                  │
│ ⏳ Claude is analyzing failure...  │
│ Attempt 1/3                        │
└────────────────────────────────────┘
```

### **Fix Applied:**
```
┌────────────────────────────────────┐
│ ✅ Fix Applied!                    │
│                                    │
│ 💡 Ready to re-test                │
│ [Deploy to Sandbox]                │
│                                    │
│ 🔧 Auto-Fix History:               │
│  └─ Attempt 1: Fixed import errors │
└────────────────────────────────────┘
```

---

## ✅ **Integration Checklist**

- [ ] Add `triggerAutoFix()` function
- [ ] Add auto-fix button (conditional render)
- [ ] Add loading state during fix
- [ ] Add fix history display
- [ ] Add "Auto-Fixed" badge to cards
- [ ] Add toast notifications
- [ ] Test the complete flow

**Once added, the autonomous loop will be fully visible and usable! 🚀**
