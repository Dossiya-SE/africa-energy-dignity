# FIN-001 Mathematical Specification

- Document ID: `AED-FIN-MATH-001`
- Version: `FIN-001.1`
- Status: Frozen deterministic baseline
- Issue: `FIN-001 / #22`
- Data contract: `docs/finance/fin-001-data-contract.md`
- Schema: `schemas/finance.schema.json`

## 1. Scope and determinism

FIN-001.1 defines annual, periodic, deterministic project-finance calculations. Pure calculation functions must satisfy:

```text
same normalized inputs
→ same outputs
→ same statuses
→ same diagnostics
```

The calculation layer contains no database access, timestamps, random values, network access or implicit data transformations.

## 2. Timeline and symbols

The valuation date is `t = 0`. Annual end-of-period values occur at `t = 1, ..., T`.

| Symbol | Definition |
|---|---|
| `r` | annual project discount rate in decimal form |
| `r_D` | annual debt discount rate in decimal form |
| `DF_t` | discount factor at period `t` |
| `C_t` | lifecycle cost in period `t` |
| `R_t` | project operating revenue in period `t` |
| `E_t` | energy delivered in period `t` |
| `TV_t` | terminal or salvage value in period `t` |
| `CF_t` | project net cash flow before financing |
| `CFADS_t` | cash flow available for debt service |
| `D_t` | debt service in period `t` |
| `B_t^open` | opening debt balance in period `t` |
| `B_t^close` | closing debt balance after period-`t` payment |

All rates are decimals. Monetary values combined in one calculation must have compatible currency, price year and real/nominal basis.

## 3. Discounting and basis consistency

For `r > -1`:

```math
DF_t = \frac{1}{(1+r)^t}
```

```math
PV(X) = \sum_{t=0}^{T} X_t DF_t
```

Real cash flows require a real discount rate. Nominal cash flows require a nominal discount rate. FIN-001 never performs an implicit Fisher conversion.

When an explicit conversion is separately authorized:

```math
1+r_n=(1+r_r)(1+\pi)
```

## 4. Lifecycle costs and project cash flow

```math
C_t = CAPEX_t + OPEX_t^{fixed} + OPEX_t^{variable} + Fuel_t
      + Replacement_t + Tax_t + Duty_t + Decommissioning_t
```

```math
CF_t = R_t - C_t + TV_t
```

Events after the declared project horizon are excluded and reported. Negative event times are invalid.

## 5. Net present cost, energy and LCOE

```math
NPC = \sum_{t=0}^{T}(C_t-TV_t)DF_t
```

```math
E_{PV}=\sum_{t=1}^{T}E_tDF_t
```

```math
LCOE=\frac{NPC}{E_{PV}}
```

`E_PV` must be strictly positive. A zero denominator produces a blocking result, never zero or infinity.

## 6. Revenue and NPV

For customer class `h`:

```math
Revenue_{h,t}=N_{h,t}(q_{h,t}\tau_{h,t}+12f_{h,t})
```

Project NPV before financing is:

```math
NPV(r)=\sum_{t=0}^{T}\frac{CF_t}{(1+r)^t}
```

Equity NPV is a separate indicator and requires an explicit equity cash-flow series.

## 7. Internal rate of return policy

IRR is a real root satisfying:

```math
0=\sum_{t=0}^{T}\frac{CF_t}{(1+r)^t}, \qquad r>-1
```

### 7.1 Preconditions

- cash flows are periodic annual values ordered from `t = 0`;
- every value is finite;
- at least one value is negative and at least one is positive;
- no scalar result is returned when those sign conditions fail.

### 7.2 Deterministic solver domain

FIN-001.1 uses the bounded admissible domain:

```text
-0.999999 <= r <= 10
```

The domain corresponds to rates from approximately `-99.9999%` to `1000%`. A root outside the domain is not asserted by this formula version.

The search grid contains `8,192` intervals uniform in `log(1+r)`, plus explicit lower bound, zero and upper bound points. This improves deterministic coverage near `r = -1` while retaining positive-rate coverage.

### 7.3 Root solver

1. evaluate NPV across the fixed grid;
2. retain exact or tolerance-level sampled roots;
3. identify every sign-changing bracket;
4. solve each bracket by bisection;
5. deduplicate roots within `100 ×` the declared rate tolerance;
6. validate each retained root using its NPV residual.

Default controls:

```text
rate tolerance = 1e-10
maximum bisection iterations per bracket = 256
residual tolerance = max(1e-18, max(|CF_t|) × 1e-12)
period basis = annual
method = deterministic_bracketed_solver
```

No single-start Newton–Raphson method is permitted.

### 7.4 IRR statuses

```text
unique_root       exactly one admissible validated root
no_root           no root found inside the documented domain
multiple_roots    more than one admissible validated root
invalid_cashflows sign or numeric preconditions fail
non_convergent    one or more detected brackets fail to converge
```

A scalar `value` is returned only for `unique_root`. For `multiple_roots`, `value = null` and all validated candidates and residuals are returned in diagnostics.

## 8. Simple payback policy

Cumulative undiscounted project cash flow is:

```math
S_t=\sum_{\tau=0}^{t}CF_\tau
```

The first recovery is the earliest `t` for which cumulative cash flow changes from negative to non-negative.

- If `S_0 >= 0`, payback is exactly `0`.
- If `S_t = 0`, payback is exactly period `t`.
- If `S_{t-1}<0`, `S_t>0` and `CF_t>0`, linear interpolation is:

```math
PB=(t-1)+\frac{-S_{t-1}}{CF_t}
```

- If cumulative cash flow remains negative through the horizon, status is `no_payback`.
- Revenue-only recovery is prohibited; the input is the defined net project cash-flow sequence.

Statuses:

```text
exact
interpolated
no_payback
invalid_cashflows
```

## 9. Discounted payback policy

```math
DCF_t=\frac{CF_t}{(1+r)^t}
```

```math
S_t^{PV}=\sum_{\tau=0}^{t}DCF_\tau
```

Discounted payback uses the same first-crossing and interpolation convention as simple payback, applied to `DCF_t`.

Mandatory controls:

- `r > -1` and finite;
- real cash flows use a real rate;
- nominal cash flows use a nominal rate;
- mixed bases are rejected;
- the exact discount rate and both basis labels are returned;
- recovery absent inside the horizon returns `no_discounted_payback`.

A valid simple payback with no discounted payback is an admissible result.

## 10. Debt schedules

Interest is computed on the opening balance:

```math
Interest_t=iB_t^{open}
```

```math
B_t^{close}=B_t^{open}-Principal_t
```

```math
D_t=Interest_t+Principal_t+Fees_t
```

Consecutive periods must reconcile:

```math
B_{t+1}^{open}=B_t^{close}
```

### 10.1 Level principal

```math
Principal_t=\frac{P}{n-g}
```

after the grace period, with the final payment absorbing any residual.

### 10.2 Annuity

For `i>0` and `m=n-g` amortizing periods:

```math
A=P\frac{i(1+i)^m}{(1+i)^m-1}
```

```math
Principal_t=A-Interest_t
```

For `i=0`, `A=P/m`.

### 10.3 Bullet

Principal is zero before maturity and the full opening balance is repaid at maturity.

## 11. DSCR

```math
DSCR_t=\frac{CFADS_t}{D_t}
```

A numeric DSCR exists only where `D_t>0`.

```math
DSCR_{min}=\min_{t:D_t>0}DSCR_t
```

## 12. LLCR policy

At the start of debt period `t`:

```math
LLCR_t=
\frac{
\displaystyle\sum_{\tau=t}^{T_D}
\frac{CFADS_\tau}{(1+r_D)^{\tau-t}}
}{B_t^{open}}
```

where `T_D` is the final period with debt outstanding at the start of the period.

### 12.1 Timing and denominator

- the calculation date is the start of period `t`;
- `CFADS_t` is included with exponent zero;
- the denominator is `B_t^open`, never the closing balance;
- post-maturity project cash flows are excluded;
- negative CFADS is retained and reduces the numerator.

### 12.2 Controls

- schedule periods are unique, consecutive and annual;
- opening and closing balances are finite and non-negative;
- the balance and debt-service identities reconcile;
- every CFADS period inside the remaining loan life is present;
- `r_D > -1` and is finite;
- CFADS basis matches the debt-rate basis.

### 12.3 Outputs and statuses

The engine returns:

```text
initial_llcr
minimum_llcr
period_values[{period, value}]
discount_rate
formula_version
method
warnings
diagnostics
```

Statuses:

```text
calculated      at least one opening debt balance is positive
not_applicable  no debt exists or debt is already fully repaid
invalid_inputs  timing, basis, rate, balance or CFADS controls fail
```

Zero outstanding debt never produces infinity.

## 13. Break-even tariff and subsidy

For positive discounted billable energy:

```math
\tau^*=\frac{\sum_{t=0}^{T}(C_t-TV_t-F_t)DF_t}
{\sum_{t=1}^{T}Q_tDF_t}
```

For a subsidy paid at year `s`:

```math
RequiredSubsidy_s=
\max\left(0,-\frac{NPV_{without\ subsidy}}{DF_s}\right)
```

## 14. Affordability

```math
Bill_h=\frac{q_h\tau_h}{12}+f_h
```

```math
EnergyBurden_h=\frac{Bill_h}{Income_h}
```

```math
ConnectionBurden_h=\frac{ConnectionCharge_h}{Income_h}
```

Income must be strictly positive. No universal affordability threshold is inferred.

## 15. Financing reconciliation

```math
Residual=\sum_jF_j-FundingRequirement
```

The structure passes when:

```math
|Residual|\le\max(0.01,10^{-9}|FundingRequirement|)
```

All financing amounts must share the scenario currency, price year and basis.

## 16. Typed deterministic result contract

IRR, payback and LLCR do not return unlabelled `float | None` values. Result objects expose indicator-specific values plus:

```text
status
method
formula_version = FIN-001.1
period_basis = annual
warnings
diagnostics
```

IRR additionally records tolerance and iteration count. Discounted payback records the exact rate. LLCR records the complete period series and debt discount rate.

## 17. Decimal and rounding policy

- API and persistence boundaries use decimal-safe monetary values.
- Internal deterministic metrics retain unrounded values.
- Display rounding is separate from calculation precision.
- Final debt principal absorbs residual arithmetic differences.
- Numeric tolerances are returned and cannot change silently.

## 18. Formula lineage

Every persisted result will eventually record:

```text
formula_version
scenario_id
scenario_version
calculation_run_id
input_hash
software_version
warnings
```

Hashing, persistence and run IDs are outside the deterministic-metrics commit and will be implemented in the next FIN-001 stage.

## 19. Blocking conditions

Calculation is blocked or returned with an explicit failure status for:

- missing or non-finite inputs;
- incompatible currency, price year or basis;
- `r <= -1` where discounting is required;
- no positive and negative cash flows for IRR;
- zero discounted energy for LCOE;
- financing reconciliation failure;
- non-consecutive or inconsistent debt schedules;
- missing CFADS inside loan life;
- non-positive affordability denominators;
- inability to preserve formula and input lineage.

## 20. Required deterministic fixtures

FIN-001.1 tests include:

- unique, zero, negative, absent and multiple IRR roots;
- IRR scale invariance and residual verification;
- exact, interpolated and absent simple payback;
- discounted payback basis rejection;
- simple payback with absent discounted payback;
- level-principal, annuity and bullet LLCR;
- no-debt and fully-repaid LLCR;
- negative CFADS;
- exclusion of post-maturity CFADS;
- minimum LLCR and opening-balance denominator;
- existing NPV, LCOE, DSCR and affordability fixtures.

## 21. Change control

Any change to timing, signs, solver domain, tolerances, interpolation, denominator definitions or failure statuses requires:

1. a new formula version;
2. a compatibility note;
3. new hand-calculated fixtures;
4. recalculation guidance for persisted results.
