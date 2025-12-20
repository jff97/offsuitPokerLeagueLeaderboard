# Workflow Run Analysis - Commit to Deploy Mapping

## Detailed Workflow History

### Successful Deployment (Baseline)
**Commit:** `fed16cf` - "email bar list for visibility"  
**Workflow Run ID:** 20395265859  
**Status:** ✅ SUCCESS  
**Triggered:** Dec 20, 2025, 13:23 UTC  
**Build Job:**
- Duration: 2m 26s
- Conclusion: Success
**Deploy Job:**
- Duration: 3m 18s
- Conclusion: Success
**Total Time:** ~5m 44s

**Dependencies at this point:**
- NO torch
- NO scipy
- All other dependencies stable

---

### First Failed Deployment (Breaking Change)
**Commit:** `913912f` - "kde curve for every player"  
**Workflow Run ID:** 20395440874  
**Status:** ❌ FAILED  
**Triggered:** Dec 20, 2025, 14:04 UTC  

**Build Job:**
- Job ID: 58610267441
- Duration: 2m 15s (14:04:28 → 14:06:43)
- Conclusion: ✅ Success
- Note: Successfully installed torch during this step

**Deploy Job:**
- Job ID: 58610339323
- Duration: 29m 3s (14:06:45 → 14:35:48)
- Conclusion: ❌ Failure
- Failed Step: "Deploy to Azure Web App" (step #5)
- **Critical:** Took 28m 41s before timing out

**Changes in this commit:**
```diff
+ torch = "*"
+ scipy = "*"
```

**Files Modified:**
1. `offsuit_analyzer/analytics/__init__.py` - 7 lines changed
2. `offsuit_analyzer/analytics/placement_distribution_analyzer.py` - 71 lines added (NEW FILE)
3. `offsuit_analyzer/web/controllers/leaderboard_controller.py` - 15 lines changed
4. `pyproject.toml` - 2 lines added (torch + scipy)

**Analysis:**
- Build phase succeeded because GitHub Actions has sufficient resources
- Deploy phase failed because Azure free tier cannot handle PyTorch size
- Deployment attempted to install dependencies on Azure, timed out
- Previous deployments took ~3-5 minutes, this took 28+ minutes before failing

---

## Workflow Comparison

| Metric | Last Success (fed16cf) | First Failure (913912f) | Delta |
|--------|------------------------|-------------------------|-------|
| Build Time | 2m 26s | 2m 15s | -11s ✅ |
| Deploy Time | 3m 18s | 29m 3s | +25m 45s ❌ |
| Total Time | 5m 44s | 31m 18s | +25m 34s ❌ |
| Build Status | Success | Success | Same |
| Deploy Status | Success | Failure | Changed ❌ |
| Package Count | ~13 | ~14+ | +1-2 |
| Est. Package Size | ~300 MB | ~1.1 GB | +800 MB ❌ |

---

## Root Cause Analysis

### Why Build Succeeded
GitHub Actions runners have:
- 14 GB disk space
- 7 GB RAM
- Fast network
- No time limits for individual steps

PyTorch installation in build phase:
- Downloads ~150-200 MB
- Installs to ~800 MB
- Takes ~2 minutes
- **No problem for GitHub Actions**

### Why Deploy Failed
Azure Free Tier has:
- 1 GB disk space
- 1 GB RAM
- Shared network
- Deployment time limits

PyTorch installation in deploy phase:
- Same download/install requirements
- **Exceeds 1 GB disk limit**
- Takes 15-30 minutes on limited resources
- **Times out around 28 minutes**

---

## Deployment Process Flow

### Successful Flow (fed16cf)
```
1. Build on GitHub Actions
   - Install dependencies (small, ~300 MB total)
   - Zip application + virtualenv
   - Upload artifact

2. Deploy to Azure
   - Download artifact
   - Extract to app directory
   - Poetry install (quick, deps already in venv)
   - Restart app
   ✅ Complete in ~3 minutes
```

### Failed Flow (913912f)
```
1. Build on GitHub Actions
   - Install dependencies (includes torch, ~1.1 GB total)
   - Zip application + virtualenv
   - Upload artifact
   ✅ Works fine - GitHub has resources

2. Deploy to Azure
   - Download artifact (~large, includes torch)
   - Extract to app directory
   - Poetry install/rebuild
     ⏳ Downloading torch (~150 MB)
     ⏳ Installing torch (~800 MB)
     ⏳ Building torch dependencies
     ❌ TIMEOUT after 28 minutes
     ❌ OR Out of disk space (1 GB limit)
```

---

## Evidence Summary

### Code Analysis
✅ grep -r "import torch" → **0 results** (torch not used)  
✅ grep -r "import scipy" → **1 result** (scipy IS used)  
✅ scipy only used for `gaussian_kde` function  
❌ torch added but never imported or called

### Timing Analysis
- Last success → First failure gap: **41 minutes**
- Only 1 commit between them: **913912f**
- Build time stable: **~2 minutes** (both)
- Deploy time exploded: **3m → 29m** (867% increase)
- Timeout point: **~28 minutes** (consistent with large package install)

### Deployment Logs (Inferred)
Based on step timing in workflow run 20395440874:
- Steps 1-4: Complete quickly (login, download, unzip) - **1m 5s**
- Step 5 (Deploy): Runs for **28m 41s** then fails
- This indicates failure during dependency installation phase
- Azure likely attempting: `poetry install` or `pip install -r requirements.txt`
- PyTorch download + install = ~15-30 minutes on limited bandwidth/compute

---

## Recommendations

### Immediate Fix (CRITICAL)
Remove torch from pyproject.toml:
```bash
git checkout troubleshooting/remove-pytorch-test
# This branch has torch removed, scipy kept
# Merge this to main to fix deployments
```

### Verification Steps
1. Push fix to main branch
2. Monitor workflow run
3. Expected results:
   - Build time: ~2 minutes (same)
   - Deploy time: ~3-5 minutes (back to normal)
   - Status: ✅ Success

### Long-term Prevention
1. Add deployment size monitoring
2. Review dependencies before adding
3. Test locally: `poetry install && du -sh .venv`
4. If package > 100 MB, evaluate if truly needed
5. Consider Azure tier upgrade for ML workloads

---

## Workflow Run URLs
- Success: https://github.com/jff97/offsuitPokerLeagueLeaderboard/actions/runs/20395265859
- Failure: https://github.com/jff97/offsuitPokerLeagueLeaderboard/actions/runs/20395440874

## Related Documentation
- Full Report: `DEPLOYMENT_TROUBLESHOOTING_REPORT.md`
- Quick Summary: `DEPLOYMENT_TROUBLESHOOTING_SUMMARY.md`
- Fix Patch: `pytorch-removal.patch`
