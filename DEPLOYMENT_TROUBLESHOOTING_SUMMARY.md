# Deployment Troubleshooting - Quick Reference

## TL;DR
**Problem:** Deployments failing since commit `913912f`  
**Root Cause:** PyTorch dependency (~800MB) exceeds Azure free-tier limits  
**Fix:** Remove PyTorch from pyproject.toml (not used in code)  
**Status:** Fix ready on `troubleshooting/remove-pytorch-test` branch

---

## Timeline
- ✅ Last Success: `fed16cf` - Dec 20, 13:23 UTC
- ❌ First Failure: `913912f` - Dec 20, 14:04 UTC (added torch + scipy)
- ⏱️ Deployment timeout: ~28 minutes during package installation

---

## Evidence
1. ✅ Codebase uses `scipy.stats.gaussian_kde` in `placement_distribution_analyzer.py`
2. ❌ Codebase has ZERO imports of `torch` (verified with grep)
3. 📦 PyTorch size: ~800MB-1GB installed
4. 💾 Azure free tier: 1GB disk limit
5. ⏰ Deployment times out during dependency installation

---

## Fix Applied
**Branch:** `troubleshooting/remove-pytorch-test`  
**Commit:** `830ddc8`

**Change:**
```diff
- torch = "*"
  scipy = "*"
```

---

## Testing Instructions
```bash
# Option 1: Test on troubleshooting branch
git push origin troubleshooting/remove-pytorch-test
# Manually trigger workflow or wait for auto-deploy if enabled

# Option 2: Apply to main
git checkout main
git cherry-pick 830ddc8
git push origin main
```

---

## Expected Results
- ✅ Deployment should complete in ~2-5 minutes (vs 28+ min timeout)
- ✅ Application functionality unchanged (torch wasn't used)
- ✅ Package size reduced by ~800MB
- ✅ Free tier limits no longer exceeded

---

## Azure Free Tier Limits (Why PyTorch Fails)
| Resource | Free Tier Limit | PyTorch Impact |
|----------|----------------|----------------|
| Disk Space | 1 GB | ~800MB-1GB just for torch |
| RAM | 1 GB | Installation requires significant memory |
| Deploy Time | Limited | ~15-30 min just to install torch |

---

## Full Details
See: `DEPLOYMENT_TROUBLESHOOTING_REPORT.md`
