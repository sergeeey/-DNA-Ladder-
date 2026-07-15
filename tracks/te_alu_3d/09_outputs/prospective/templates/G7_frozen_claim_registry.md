# G7 — Frozen claim + PASS/FAIL registry (EMPTY TEMPLATE)

**Status:** `UNFILLED`  
**Rule:** directions and minimum effects must be written **before** outcome data.

```yaml
frozen_claim: >
  In <cell_state>, allele <V> changes <M>, which changes contact(E,P)
  by at least <delta_contact_min> in direction <dir_contact>,
  and expression of <gene> by at least <delta_expr_min> in direction <dir_expr>
  OR expression is explicitly declared a secondary endpoint.
primary_endpoint: contact_change
secondary_endpoints: [occupancy_or_direct_M, expression]
reporter_role: discriminator_not_proof
pass_fail:
  PASS: null
  FAIL: null
  INCONCLUSIVE: null
  NO_GO_FOR_WET_LAB: any of G1-G6 fail before freeze
```
