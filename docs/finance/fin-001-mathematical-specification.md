# FIN-001 Mathematical Specification

- Document ID: `AED-FIN-MATH-001`
- Version: `FIN-001.1`
- Status: Frozen deterministic baseline
- Issue: `FIN-001 / #22`
- Data contract: `docs/finance/fin-001-data-contract.md`
- Schema: `schemas/finance.schema.json`

## 1. Symbols and timeline

The valuation date is year `t = 0`. The project horizon is `t = 0, 1, ..., T`, where `T` is the declared operating lifetime in years.

| Symbol | Definition |
|---|---|
| `r` | annual discount rate in decimal form |
| `DF_t` | discount factor at year `t` |
| `C_t` | non-financing lifecycle costs in year `t` |
| `R_t` | operating revenue in year `t` |
| `E_t` | energy delivered in year `t`, converted to the calculation unit |
| `TV_t` | terminal or salvage value in year `t` |
| `CF_t` | project net cash flow before financing in year `t` |
| `D_t` | debt service in year `t` |
| `CADS_t` | cash available for debt service in year `t` |
| `B_t` | debt balance after payment in year `t` |

All rates are decimals. All monetary quantities in one calculation must share the scenario currency, price year and real/nominal basis after explicit transformations.

## 2. Discounting

For annual end-of-period cash flows:

```math
DF_t = \frac{1}{(1+r)^t}
```

The present value of a series `X_t` is:

```math
PV(X) = \sum_{t=0}^{T} X_t DF_t
```

FIN-001 uses discrete annual discounting. Alternative periodicity is outside this formula version.

## 3. Real and nominal consistency

Real cash flows require a real discount rate. Nominal cash flows require a nominal discount rate.

When an explicit conversion is requested and inflation `π` is supplied, the exact Fisher relation is:

```math
1 + r_n = (1 + r_r)(1 + \pi)
```

Therefore:

```math
r_n = (1+r_r)(1+\pi)-1
```

and

```math
r_r = \frac{1+r_n}{1+\pi}-1
```

The engine must not perform this conversion implicitly.

## 4. Lifecycle cost construction

For each year, gross lifecycle costs are:

```math
C_t = CAPEX_t + OPEX^{fixed}_t + OPEX^{variable}_t + Fuel_t
      + Replacement_t + Tax_t + Duty_t + Decommissioning_t
```

Salvage or terminal value is not a negative input. It is recorded as a positive value and deducted in the project cash-flow equation:

```math
CF_t = R_t - C_t + TV_t
```

Cost events with `t > T` are excluded and reported. A cost event with `t < 0` is invalid.

## 5. Net present cost

Net present cost excludes financing transfers and operating revenue. It represents discounted lifecycle resource cost:

```math
NPC = \sum_{t=0}^{T} (C_t - TV_t)DF_t
```

When grants or subsidies are reported, the engine must distinguish:

- economic NPC: before financing transfers;
- sponsor or payer NPC: after explicitly identified grants or subsidies.

FIN-001.1 calculates economic NPC as the canonical `net_present_cost`. Payer-specific NPC must be labelled separately.

## 6. Discounted lifecycle energy and LCOE

All annual energy is converted to the selected calculation unit before discounting:

```math
E_{PV} = \sum_{t=1}^{T} E_t DF_t
```

The levelized cost of energy is:

```math
LCOE = \frac{NPC}{E_{PV}}
```

Preconditions:

```text
E_t >= 0 for all t
E_PV > 0
```

When `E_PV = 0`, LCOE is undefined. The engine returns a blocking validation result rather than infinity or zero.

## 7. Revenue

For customer class `h`:

```math
Revenue_{h,t} = N_{h,t}
\left(q_{h,t}\tau_{h,t} + 12 f_{h,t}\right)
```

where:

- `N_{h,t}` is connected customers;
- `q_{h,t}` is annual energy consumption per customer;
- `τ_{h,t}` is the tariff per energy unit;
- `f_{h,t}` is the monthly fixed charge.

Total operating revenue is:

```math
R_t = \sum_h Revenue_{h,t} + OtherRevenue_t
```

Connection charges are reported separately from recurring energy revenue unless the scenario explicitly classifies them as project revenue.

## 8. Net present value

Project NPV before financing is:

```math
NPV(r) = \sum_{t=0}^{T} CF_t DF_t
```

Equity NPV requires an equity cash-flow series that explicitly includes equity contributions, debt drawdowns, debt service and distributions. It must not be labelled project NPV.

## 9. Internal rate of return

IRR is any real root `x > -1` satisfying:

```math
0 = \sum_{t=0}^{T} \frac{CF_t}{(1+x)^t}
```

FIN-001 root policy:

1. detect sign changes in the cash-flow sequence;
2. search a documented bounded interval;
3. report no root when none is found;
4. report multiple roots when more than one admissible root exists;
5. never select one root silently;
6. return the numerical method, tolerance and bracket with the result.

A scenario with no negative and positive cash-flow values does not have a conventional IRR.

## 10. Payback periods

Simple cumulative cash flow is:

```math
S_t = \sum_{k=0}^{t} CF_k
```

Simple payback is the earliest time where `S_t >= 0` after an initially negative cumulative balance. Linear interpolation within the crossing year may be used and must be labelled.

Discounted cumulative cash flow is:

```math
S^{PV}_t = \sum_{k=0}^{t} CF_k DF_k
```

Discounted payback uses the same crossing rule. If no crossing occurs within the horizon, the result is undefined with reason `not_recovered_within_horizon`.

## 11. Debt schedule

Let initial debt principal be `P`, annual interest rate `i`, tenor `n`, and grace period `g`.

Interest in year `t` is calculated on the opening balance:

```math
Interest_t = i B_{t-1}
```

The debt identity is:

```math
B_t = B_{t-1} + Draw_t - Principal_t
```

with:

```text
B_t >= 0
Principal_t >= 0
D_t = Interest_t + Principal_t + Fees_t
```

### 11.1 Level principal

After the grace period:

```math
Principal_t = \frac{P}{n-g}
```

subject to the final payment being adjusted for decimal rounding so that the closing balance is exactly zero within tolerance.

### 11.2 Annuity

For `i > 0`, the constant annual payment is:

```math
A = P\frac{i(1+i)^m}{(1+i)^m-1}
```

where `m = n-g` is the number of amortizing periods. Then:

```math
Principal_t = A - Interest_t
```

For `i = 0`:

```math
A = \frac{P}{m}
```

### 11.3 Bullet

During the tenor:

```math
Principal_t = 0, \quad t < n
```

and at maturity:

```math
Principal_n = P
```

### 11.4 Custom

A custom schedule must provide every draw, principal and fee value explicitly. The engine verifies the balance identity and final balance.

## 12. Cash available for debt service

The default project-finance definition is:

```math
CADS_t = Revenue_t - OperatingCost_t - Tax_t - MaintenanceCAPEX_t
         \pm WorkingCapitalAdjustment_t
```

Initial construction CAPEX and financing flows are excluded from CADS. The exact included line items are returned with the indicator lineage.

## 13. Debt-service coverage ratio

For each debt-service year:

```math
DSCR_t = \frac{CADS_t}{D_t}
```

Precondition:

```text
D_t > 0
```

Years with zero debt service do not receive a numeric DSCR. Minimum DSCR is:

```math
DSCR_{min} = \min_{t:D_t>0} DSCR_t
```

## 14. Loan-life coverage ratio

At calculation year `k`, remaining debt is `B_k`. The present value of CADS over the remaining loan life is discounted at the declared debt discount rate `r_d`:

```math
LLCR_k = \frac{\sum_{t=k+1}^{n} CADS_t(1+r_d)^{-(t-k)}}{B_k}
```

Preconditions:

```text
B_k > 0
remaining CADS horizon covers the remaining loan tenor
```

## 15. Break-even tariff

Let `Q_t` be billable energy and `F_t` all non-energy recurring revenues. The constant break-even tariff `τ*` that gives project NPV equal to zero is:

```math
\tau^* =
\frac{\sum_{t=0}^{T}(C_t-TV_t-F_t)DF_t}
     {\sum_{t=1}^{T}Q_tDF_t}
```

The denominator must be strictly positive. Taxes or losses tied to tariff revenue require an extended equation and are outside the closed-form FIN-001.1 expression.

## 16. Required subsidy or viability-gap amount

For a target NPV of zero and a subsidy paid at year `s`:

```math
Subsidy_s = -\frac{NPV_{without\ subsidy}}{DF_s}
```

The reported required subsidy is:

```math
RequiredSubsidy_s = \max(0, Subsidy_s)
```

A negative calculated value means no subsidy is required under the scenario; it is not reported as a negative subsidy.

## 17. Household energy burden

For customer class `h`, monthly recurring electricity expenditure is:

```math
Bill_h = \frac{q_h\tau_h}{12} + f_h
```

Monthly household energy burden is:

```math
EB_h = \frac{Bill_h}{Income_h}
```

Precondition:

```text
Income_h > 0
```

The engine reports the ratio and percentage. It does not impose a universal affordability threshold unless the threshold is supplied with evidence.

## 18. Connection-cost burden

```math
CB_h = \frac{ConnectionCharge_h}{Income_h}
```

The result is expressed in months of disposable income. Any financing of the connection charge must be modelled separately.

## 19. Productive-use affordability

For productive-use class `p`, energy-cost intensity is:

```math
ECI_p = \frac{AnnualElectricityExpenditure_p}{AnnualOperatingRevenue_p}
```

or, when output quantity is available:

```math
UnitEnergyCost_p = \frac{AnnualElectricityExpenditure_p}{AnnualOutput_p}
```

The denominator must be strictly positive and its unit must be returned. FIN-001 does not infer business revenue or output from population data.

## 20. Financing reconciliation

Let `F_j` be financing component amounts and `FundingRequirement` the declared amount to be financed:

```math
Residual = \sum_j F_j - FundingRequirement
```

The financing structure passes when:

```math
|Residual| \le \max(\epsilon_{abs}, \epsilon_{rel}|FundingRequirement|)
```

Default tolerances for FIN-001.1:

```text
ε_abs = 0.01 reporting-currency units
ε_rel = 1e-9
```

The tolerances are formula metadata and may not be changed silently.

## 21. Decimal and rounding policy

- Monetary inputs and outputs use decimal-safe arithmetic at persistence and API boundaries.
- Internal discounting may use high-precision decimal arithmetic or carefully controlled binary floating point with explicit tolerances.
- Debt schedules round displayed monetary values to the reporting-currency precision.
- The final principal payment absorbs accumulated rounding residuals.
- Indicator calculations retain unrounded internal values and record display precision separately.

## 22. Formula lineage

Every result records:

```text
formula_version = FIN-001.1
scenario_id
scenario_version
calculation_run_id
input_hash
calculation timestamp
software version
warnings
```

The input hash is computed over a canonical serialized scenario after validation. The same scenario version, formula version and software version must reproduce the same deterministic result within documented numeric tolerance.

## 23. Blocking validation conditions

Calculation is blocked when any of the following holds:

- missing currency, price year or monetary basis;
- incompatible currencies without explicit FX transformation;
- nominal/real mismatch;
- project lifetime is not positive;
- negative energy delivery;
- zero discounted energy when LCOE is requested;
- financing does not reconcile;
- debt terms are incomplete or invalid;
- debt principal becomes negative beyond tolerance;
- affordability denominator is non-positive;
- observed or published evidence lacks a source identifier;
- a non-synthetic scenario lacks a registered project identifier;
- a result cannot retain formula and input lineage.

## 24. Verification fixtures

Implementation tests must include hand-calculated fixtures for:

- one-period and multi-period NPV;
- lifecycle cost and LCOE;
- terminal value discounting;
- level-principal, annuity and bullet debt schedules;
- DSCR;
- break-even tariff;
- required subsidy;
- household burden and connection burden;
- no-IRR and multiple-IRR conditions;
- zero-energy LCOE rejection;
- currency and basis mismatch rejection.

## 25. Change control

Any change to formulas, timing conventions, sign conventions, root policy, tolerances or rounding policy requires:

1. a new formula version;
2. a compatibility note;
3. new hand-calculated fixtures;
4. migration or recalculation guidance for persisted results.
