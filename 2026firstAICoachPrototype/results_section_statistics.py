"""
Reproduces every statistic currently cited in the manuscript's Results section
regarding sleep score and general mood.

Table 1 sentence claims: "42% chance of winning zero of the 9 total slots and
an equal 42% chance of winning exactly one ... (one-sided p = .58 for winning
one or more slots by chance)"

Table 2 sentence claims: "Sleep score ranked 5th of 12 (p = .37) and general
mood ranked 11th of 12 (p = .84)"
"""
import numpy as np
from scipy import stats

# =============================================================================
# TABLE 1 -- does sleep score's single win (of 9 total slots) exceed chance?
# =============================================================================
# Within each body region, 3 winners are selected sequentially WITHOUT
# replacement from the 12 candidate stressors (each residual is orthogonal to
# the stressor just extracted, so it can't be re-selected in that region). A
# specific stressor's chance of being one of those 3 winners is exactly
# 3/12 = 1/4, confirmed two ways: as an unordered set, C(11,2)/C(12,3) = 0.25;
# or as 3 mutually-exclusive sequential stages, 1/12+1/12+1/12 = 0.25.
# Across the 3 regions, total wins ~ Binomial(3, 1/4).

p_region = 3 / 12
p0 = stats.binom.pmf(0, 3, p_region)
p1 = stats.binom.pmf(1, 3, p_region)
p_at_least_1 = 1 - p0

print("TABLE 1")
print(f"  P(wins 0 of 9 slots)         = {p0:.3f}  ({p0*100:.0f}%)")
print(f"  P(wins exactly 1 of 9)       = {p1:.3f}  ({p1*100:.0f}%)   <- observed (sleep)")
print(f"  P(wins >= 1, one-sided)      = {p_at_least_1:.3f}")

# independent check: direct simulation, no formula, draws 3 distinct winners
# per region explicitly
rng = np.random.default_rng(0)
n_sim = 500_000
wins_per_region = np.zeros((n_sim, 3), dtype=bool)
for region in range(3):
    order = np.argsort(rng.random((n_sim, 12)), axis=1)
    wins_per_region[:, region] = (order[:, :3] == 0).any(axis=1)  # stressor 0 = "sleep"
total_wins = wins_per_region.sum(axis=1)
print(f"  [simulation check]            P(0)={np.mean(total_wins==0):.3f}, "
      f"P(1)={np.mean(total_wins==1):.3f}, P(>=1)={np.mean(total_wins>=1):.3f}")

# =============================================================================
# TABLE 2 -- sleep score's and general mood's rank / Mann-Whitney U vs the
#            10 mechanical stressors' 80th-percentile ROC-AUC values
# =============================================================================
auc = {
    "face": {"computer":.88,"sleep":.83,"keyboard":.83,"steps":.76,"driving":.73,
             "up_bpm":.71,"mood":.70,"cyc_bpm":.68,"mobile":.64,"surf_bpm":.61,
             "climb":.56,"riding":.55},
    "knee": {"cyc_bpm":.79,"steps":.75,"keyboard":.71,"mobile":.68,"driving":.66,
             "sleep":.65,"up_bpm":.61,"surf_bpm":.59,"mood":.57,"computer":.56,
             "riding":.50,"climb":.49},
    "arm":  {"surf_bpm":.86,"up_bpm":.83,"climb":.80,"steps":.75,"mobile":.74,
             "driving":.73,"riding":.64,"sleep":.63,"keyboard":.58,"mood":.56,
             "cyc_bpm":.54,"computer":.49},
}
all_stressors = list(auc["face"].keys())                              # 12 total
mechanical = [k for k in all_stressors if k not in ("sleep", "mood")]  # 10

pooled_mean = {k: np.mean([auc[r][k] for r in auc]) for k in all_stressors}
ranked = sorted(pooled_mean, key=lambda k: -pooled_mean[k])
mech_vals = [auc[r][k] for r in auc for k in mechanical]

print("\nTABLE 2")
for var in ["sleep", "mood"]:
    vals = [auc[r][var] for r in auc]
    rank = ranked.index(var) + 1
    mw = stats.mannwhitneyu(vals, mech_vals, alternative="greater", method="exact")
    print(f"  {var}: 3 region AUCs={vals}, mean={pooled_mean[var]:.3f}, "
          f"rank={rank}/12, Mann-Whitney one-sided p={mw.pvalue:.3f}")
