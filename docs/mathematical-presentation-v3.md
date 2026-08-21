# Africa Energy Dignity — Mathematical Presentation V3

## Purpose

This document defines how AED displays mathematics, quantitative evidence and systems-engineering relationships. It does not change the current pre-alpha maturity boundary.

## Evidence states

Use:

`[S] source-grounded` · `[D] derived` · `[M] model` · `[C] computed` · `[V] verified` · `[E] empirical` · `[H] hypothesis` · `[T] design target`.

Every major numeric value should additionally remain distinguishable as observed, official/published, derived, model output, expert judgment, scenario, design target, or planned.

## 1. Energy conservation — [M]

```math
P_{gen}+P_{import}+P_{dis}
=
P_{load}+P_{loss}+P_{ch}+P_{export}.
```

A professional display must state the system boundary, timestep, sign convention, and units. A balance equation without those definitions is incomplete.

## 2. Storage accounting — [M]

Where discrete storage is used,

```math
SOC_{t+1}
=
SOC_t
+
\eta_c E_{ch}
-
\frac{E_{dis}}{\eta_d}.
```

A storage plot must declare:

- energy vs power units;
- timestep;
- charging/discharging efficiency;
- SOC limits;
- initial condition;
- degradation assumptions if modeled.

## 3. Spatial evidence field — [E/M]

A spatial-temporal data state may be represented as

```math
z(s,t)
=
\{population,demand,assets,cost,hazard,service,geography\}.
```

Maps must preserve:

- coordinate reference system;
- resolution/support;
- date/time validity;
- source/license;
- missingness/coverage;
- whether the displayed field is observed, interpolated, modeled, or scenario-based.

## 4. Resilience dynamics — [M/C]

```math
\dot x=f(x,u,\eta;\theta),
\qquad
S(t)=w^T x(t).
```

A resilience trajectory must not imply that `w`, `theta`, or the hazard process have been empirically calibrated unless that work is actually complete.

If a service floor is shown, define its physical/social meaning and evidence basis.

## 5. Multiobjective design — [M]

```math
\min_d[C(d),E(d),T(d),Risk(d)],
\qquad
\max_d[Service(d),Resilience(d),Sovereignty(d)].
```

A Pareto plot is scientifically valid only after:

1. decision variables are defined;
2. objectives are computable;
3. constraints are explicit;
4. units/scaling are controlled;
5. infeasible points are excluded;
6. uncertainty/sensitivity are reported where decision-relevant.

Minimum deployment time alone is not the objective.

## 6. Rapid-deployment time — [M/E]

```math
T_{impact}
=
T_{diagnosis}
+
T_{design}
+
T_{approval}
+
T_{finance}
+
T_{procurement}
+
T_{construction}
+
T_{commissioning}.
```

A duration component is `[E]` only when its value is grounded in project/official observations. Otherwise it remains a scenario or target.

## 7. Reliability and uncertainty

Where failure probability is defined,

```math
P_f=\mathbb P[g(X,H)\le0].
```

The limit-state function `g`, random variables, distributional assumptions and sampling/approximation method must accompany any probability visualization.

## 8. Verification versus validation

Use the explicit chain

```text
source
→ provenance
→ canonical variable
→ model input
→ derived/model output
→ uncertainty/sensitivity
→ software verification
→ model validation
→ bounded decision
```

CI can establish `[V]` software/repository consistency. It does not establish `[E]` continental optimization quality, investment effectiveness, field reliability, or causal productive impact.

## 9. Visual semantics

- evidence / official values: cyan/neutral;
- energy physics: gold/green;
- hazard / violation: red;
- resilience / service continuity: green/teal;
- optimization/trade space: gold;
- uncertainty: amber bands or ensembles;
- planned/unvalidated: dashed styling.

No map or chart should encode information only by color.

## 10. V3 reference visual

`docs/assets/aed-mathematical-system.svg` is the current profile-aligned mathematical systems architecture.

It is a scientific architecture visual, not evidence of completed continental optimization or deployment.

## 11. Preferred tools by role

- Python/NumPy/SciPy/Pandas/GeoPandas → numerical, evidence and geospatial workflow;
- PostgreSQL/PostGIS → spatial evidence infrastructure;
- Pyomo/CVX/Julia optimization ecosystems → future optimization where model class requires them;
- Matplotlib/Plotly/D3 → computed data/decision plots;
- SVG/TikZ/PGFPlots → architecture and publication-quality mathematical exposition;
- uncertainty libraries / Monte Carlo → only with recorded distributions, seeds and convergence controls.

## Rigor invariant

```math
\boxed{
\text{decision strength}
\le
\text{evidence quality}
+
\text{model validity}
+
\text{uncertainty characterization}
}
```
