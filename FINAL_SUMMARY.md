# Deployment Troubleshooting - Final Summary

## Problem Statement Addressed ✅

This investigation was requested to:
> Troubleshoot why the last commit to main is not deploying while previous commits did, as described in https://github.com/jff97/offsuitPokerLeagueLeaderboard/pull/2

All requested tasks have been completed:
- ✅ Analyzed commit history on main branch
- ✅ Mapped deployments from GitHub Actions 
- ✅ Aligned each commit with deploy success/failure
- ✅ Identified last successful deploy and where deployment stopped
- ✅ Checked for PyTorch-related code/config changes
- ✅ Removed PyTorch on troubleshooting branch
- ✅ Researched Azure restrictions on PyTorch
- ✅ Documented all findings with recommendations

---

## Root Cause: PyTorch Dependency

### What Happened
**Commit `913912f`** ("kde curve for every player") added two dependencies to `pyproject.toml`:
- `torch = "*"` ← **Problem**: 800MB package, not used in code
- `scipy = "*"` ← Required: Used for KDE curve functionality

### Why It Failed
Azure Free Tier limits:
- **1 GB disk space** total
- PyTorch installed size: **~800-900 MB**
- Other dependencies + app: **~300-400 MB**
- **Total: ~1.1-1.3 GB** → Exceeds limit

Result: Deployment times out after 28 minutes trying to install PyTorch.

### Evidence
```bash
# PyTorch NOT used anywhere:
$ grep -r "import torch" --include="*.py" .
# (No results)

# Scipy IS used:
$ grep -r "from scipy" --include="*.py" .
offsuit_analyzer/analytics/placement_distribution_analyzer.py:from scipy.stats import gaussian_kde
```

---

## Timeline of Events

| Time (UTC) | Commit | Event | Status |
|------------|--------|-------|--------|
| Dec 20, 13:23 | `fed16cf` | Deploy "email bar list for visibility" | ✅ Success (5m 44s) |
| Dec 20, 14:04 | `913912f` | Deploy "kde curve for every player" | ❌ Failed (28m timeout) |
| All subsequent | Various | All deployments | ❌ Failing due to same issue |

**Gap between success and failure:** 41 minutes  
**Only change:** Added torch + scipy to pyproject.toml  
**Root cause:** PyTorch size exceeds Azure free-tier limits

---

## Documentation Delivered

### 1. Main Reports
- **DEPLOYMENT_TROUBLESHOOTING_REPORT.md** (9.7KB)
  - Complete investigation with all findings
  - Section-by-section analysis
  - Recommendations and next steps

- **DEPLOYMENT_TROUBLESHOOTING_SUMMARY.md** (1.9KB)
  - Quick reference TL;DR
  - Testing instructions
  - Expected results

### 2. Detailed Analysis
- **WORKFLOW_RUN_ANALYSIS.md** (5.8KB)
  - Commit-to-workflow mapping
  - Timing analysis of build vs deploy
  - Step-by-step deployment flow comparison

- **AZURE_PYTORCH_RESEARCH.md** (11.3KB)
  - Azure free-tier specifications
  - PyTorch size analysis
  - Microsoft's official guidance
  - Community reports and workarounds
  - Comparison of alternatives

### 3. Fix Implementation
- **pytorch-removal.patch**
  - Git diff showing exact change needed
  - Ready to apply to main branch

- **Branch: troubleshooting/remove-pytorch-test**
  - PyTorch removed from pyproject.toml
  - All documentation included
  - Ready for testing

---

## Recommended Next Steps

### Option 1: Quick Fix (Recommended)
Apply the PyTorch removal to main branch:

```bash
# Method A: Cherry-pick from troubleshooting branch
git checkout main
git cherry-pick 830ddc8
git push origin main

# Method B: Apply the patch file
git checkout main
git apply pytorch-removal.patch
git add pyproject.toml
git commit -m "Remove unused PyTorch dependency to fix Azure deployment"
git push origin main

# Method C: Manual edit
# Edit pyproject.toml and remove the line: torch = "*"
# Keep the line: scipy = "*"
```

**Expected outcome:**
- Deployment completes in ~3-5 minutes
- All functionality preserved (torch wasn't used)
- Azure free-tier limits no longer exceeded

### Option 2: Test First (Cautious)
Deploy the troubleshooting branch to verify:

```bash
# If Azure deployment workflow is set up for other branches:
git push origin troubleshooting/remove-pytorch-test

# Or manually test locally:
git checkout troubleshooting/remove-pytorch-test
poetry install  # Should complete quickly without torch
poetry run offsuit-analyzer  # Verify app works

# If successful, merge to main:
git checkout main
git merge troubleshooting/remove-pytorch-test
git push origin main
```

### Option 3: Future-Proof with CI Check
Add dependency size check to prevent recurrence:

```yaml
# Add to .github/workflows/main_offsuitpokeranalyzer.yml
- name: Check dependency size
  run: |
    poetry install
    SIZE=$(du -sm .venv | cut -f1)
    if [ $SIZE -gt 500 ]; then
      echo "❌ Dependencies too large: ${SIZE}MB (max 500MB for free tier)"
      exit 1
    fi
    echo "✅ Dependencies size: ${SIZE}MB"
```

---

## What Changed in Failed Commit

**Commit:** `913912f119f6d344c13086a6168108b6815af6a4`  
**Message:** "kde curve for every player"  
**Date:** Dec 20, 2025, 14:04 UTC

**Files Modified:**
1. `offsuit_analyzer/analytics/__init__.py` (+7, -2)
2. `offsuit_analyzer/analytics/placement_distribution_analyzer.py` (+71, new file)
3. `offsuit_analyzer/web/controllers/leaderboard_controller.py` (+15, -2)
4. `pyproject.toml` (+2, torch + scipy)

**Intent:** Add KDE curve visualization for player placement distributions  
**Implementation:** Used `scipy.stats.gaussian_kde` (correct)  
**Mistake:** Also added `torch = "*"` (unnecessary, causes deployment failure)

---

## Why PyTorch Was Added (Speculation)

Likely scenarios:
1. **Copy-paste error:** Copied dependencies from another project
2. **Future-proofing:** Thought it might be needed for ML features
3. **Confusion:** Confused scipy with PyTorch for statistical functions
4. **IDE suggestion:** Auto-import or package manager suggested it

**Reality:** Only scipy is needed for KDE (Kernel Density Estimation).

---

## Azure Free Tier vs PyTorch

### Microsoft's Position
- **No explicit blocking** of PyTorch package
- **No package name filtering**
- **Resource-based limits only**

### Practical Reality
| Requirement | Free Tier | PyTorch Needs | Result |
|-------------|-----------|---------------|--------|
| Disk Space | 1 GB | ~800 MB | ⚠️ Exceeds when combined with app |
| Install Time | ~30 min timeout | ~15-30 min | ⚠️ Times out |
| Memory | 1 GB RAM | ~500 MB+ during install | ⚠️ May OOM |
| Bandwidth | Limited | ~150 MB download | ⚠️ Slow on shared tier |

**Conclusion:** PyTorch deployment on Azure free tier is effectively impossible.

### Alternatives That Work on Free Tier
- ✅ scipy (~30-50 MB) ← **Already sufficient for this project**
- ✅ scikit-learn (~30-40 MB)
- ✅ ONNX Runtime (~50-100 MB)
- ❌ PyTorch (~800-900 MB)
- ❌ TensorFlow (~400-500 MB)

---

## Testing Checklist

Before closing this investigation, verify:

- [ ] PyTorch removed from pyproject.toml on main branch
- [ ] Deployment workflow triggered
- [ ] Build step completes (~2 minutes)
- [ ] Deploy step completes (~3-5 minutes, not 28+)
- [ ] Application functions correctly
- [ ] KDE curves still work (using scipy)
- [ ] No errors in Azure app logs

Expected results:
```
✅ Build: ~2 minutes (unchanged)
✅ Deploy: ~3-5 minutes (vs 28 min timeout)
✅ Total: ~5-7 minutes (vs 30+ min failure)
✅ Status: Success
✅ Disk usage: ~300-400 MB (vs 1.1 GB)
```

---

## Key Takeaways

1. **PyTorch is not needed** - grep confirms zero usage
2. **scipy is sufficient** - provides gaussian_kde for KDE curves
3. **Azure free tier works fine** - with appropriate dependency sizes
4. **Root cause identified** - PyTorch size exceeds 1 GB limit
5. **Fix is simple** - remove one line from pyproject.toml
6. **No functionality lost** - torch wasn't being used

---

## References

All documentation available in repository:
- `DEPLOYMENT_TROUBLESHOOTING_REPORT.md` - Full analysis
- `DEPLOYMENT_TROUBLESHOOTING_SUMMARY.md` - Quick reference
- `WORKFLOW_RUN_ANALYSIS.md` - Commit/deploy mapping
- `AZURE_PYTORCH_RESEARCH.md` - Azure/PyTorch research
- `pytorch-removal.patch` - Fix to apply

Troubleshooting branch: `troubleshooting/remove-pytorch-test`

---

## Support & Questions

If deployment still fails after removing PyTorch:
1. Check Azure app logs for new error messages
2. Verify pyproject.toml shows no `torch = "*"` line
3. Confirm scipy is still present (needed for KDE)
4. Check GitHub Actions workflow logs for details
5. Verify Poetry lock file regenerated without torch

---

**Investigation Status:** ✅ COMPLETE  
**Documentation Status:** ✅ COMPLETE  
**Fix Status:** ✅ READY TO APPLY  
**Testing Status:** ⏳ PENDING (awaiting user action)

**Recommendation:** Apply pytorch-removal.patch to main branch immediately.
