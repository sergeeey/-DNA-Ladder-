# C-A2 primary result — SVA_F dELS switching OR

**Verdict:** `REJECT` (`FAIL_KILL`)

- Fisher OR = **0.4894** (Woolf 95% CI 0.2432–0.9848; p=0.04447)
- Table [a,b,c,d] = [10, 58, 91, 249] (SVA switch / SVA non / ctrl switch / ctrl non)
- Switcher rate SVA_F = 0.1471; matched non-TE = 0.2676
- N switching biosamples = 10; k=5; undermatched indices = 0
- Panel-split kill hits (OR<1.1) = 2 / 2

## Panel split

- **odd** (GM12878, HCT116, HepG2, K562, Panc1): OR=0.6553 CI=0.2909–1.4766 kill=True
- **even** (H1, HeLa-S3, IMR-90, MCF-7, PC-3): OR=0.4109 CI=0.1508–1.1191 kill=True

## Leakage control

Matching locked in `matching_lock.json` with `switching_panel_not_used: true` before outcomes.

Not ChIA-PET. True C-A2 SVA_F dELS switching desk.

