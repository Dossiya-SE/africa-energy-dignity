"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useMemo, useReducer, useState, useTransition } from "react";

import { StatusBadge } from "@/components/status-badge";
import styles from "@/components/finance-workspace.module.css";
import {
  collectScenarioLimitations,
  financeStatusTone,
  financeWorkspaceReducer,
  formatExactDecimal,
  humanizeFinanceIdentifier,
  indicatorPeriods,
  indicatorUnit,
  indicatorValue,
  indicatorWarnings,
  initialFinanceWorkspaceState,
  orderFinanceIndicators,
} from "@/lib/finance-presentation";
import type {
  FinanceAffordabilityRecord,
  FinanceIndicatorRecord,
  FinanceScenarioSummary,
  FinanceWorkspaceActionResult,
  FinanceWorkspaceData,
} from "@/lib/types";

interface FinanceWorkspaceProps {
  initialScenarios: FinanceScenarioSummary[];
  initialWorkspace: FinanceWorkspaceData | null;
  initialError: string | null;
  loadScenarioAction: (scenarioRecordId: string) => Promise<FinanceWorkspaceActionResult>;
  calculateScenarioAction: (
    scenarioRecordId: string,
  ) => Promise<FinanceWorkspaceActionResult>;
  registerScenarioAction: (scenarioJson: string) => Promise<FinanceWorkspaceActionResult>;
}

function exact(value: unknown, unit = ""): string {
  const rendered = formatExactDecimal(value);
  return unit ? `${rendered} ${unit}` : rendered;
}

function identityValue(value: unknown): string {
  return value === null || value === undefined || value === "" ? "Not applicable" : String(value);
}

function ResultCard({ indicator }: { indicator: FinanceIndicatorRecord }) {
  const warnings = indicatorWarnings(indicator);
  const periods = indicatorPeriods(indicator);
  const unit = indicatorUnit(indicator);
  return (
    <article className={styles.resultCard}>
      <div className={styles.resultHeading}>
        <div>
          <p className={styles.resultLabel}>{humanizeFinanceIdentifier(indicator.indicator_name)}</p>
          <strong className={styles.resultValue}>{exact(indicatorValue(indicator), unit)}</strong>
        </div>
        <StatusBadge tone={financeStatusTone(indicator.status)}>
          {humanizeFinanceIdentifier(indicator.status)}
        </StatusBadge>
      </div>
      <dl className={styles.miniMetadata}>
        <div>
          <dt>Method</dt>
          <dd>{identityValue(indicator.result.method)}</dd>
        </div>
        <div>
          <dt>Result ID</dt>
          <dd className={styles.mono}>{indicator.result_id}</dd>
        </div>
      </dl>
      {periods.length > 0 ? (
        <div className={styles.periodGrid} aria-label={`${indicator.indicator_name} period values`}>
          {periods.map((period) => (
            <div key={`${indicator.result_id}-${period.period}`}>
              <span>Year {period.period}</span>
              <strong>{formatExactDecimal(period.value)}</strong>
            </div>
          ))}
        </div>
      ) : null}
      {warnings.length > 0 ? (
        <ul className={styles.warningList}>
          {warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

function AffordabilityCard({ item }: { item: FinanceAffordabilityRecord }) {
  const result = item.result;
  const currency = typeof result.currency === "string" ? result.currency : "";
  const priceYear = typeof result.price_year === "number" ? result.price_year : null;
  return (
    <article className={styles.affordabilityCard}>
      <div className={styles.resultHeading}>
        <div>
          <p className={styles.resultLabel}>Customer class</p>
          <h3>{humanizeFinanceIdentifier(item.customer_class_id)}</h3>
        </div>
        <StatusBadge tone={financeStatusTone(item.status)}>
          {humanizeFinanceIdentifier(item.status)}
        </StatusBadge>
      </div>
      <dl className={styles.metricStack}>
        <div>
          <dt>Monthly bill</dt>
          <dd>{exact(result.monthly_bill, currency)}</dd>
        </div>
        <div>
          <dt>Monthly energy burden</dt>
          <dd>{exact(result.monthly_energy_burden, "decimal ratio")}</dd>
        </div>
        <div>
          <dt>Connection-cost burden</dt>
          <dd>{exact(result.connection_cost_burden_months, "months of income")}</dd>
        </div>
        <div>
          <dt>Money basis</dt>
          <dd>
            {identityValue(result.basis)}{priceYear ? `, ${priceYear}` : ""}
          </dd>
        </div>
      </dl>
    </article>
  );
}

export function FinanceWorkspace({
  initialScenarios,
  initialWorkspace,
  initialError,
  loadScenarioAction,
  calculateScenarioAction,
  registerScenarioAction,
}: FinanceWorkspaceProps) {
  const [state, dispatch] = useReducer(
    financeWorkspaceReducer,
    initialFinanceWorkspaceState(initialScenarios, initialWorkspace, initialError),
  );
  const [scenarioJson, setScenarioJson] = useState("");
  const [isPending, startTransition] = useTransition();
  const workspace = state.workspace;
  const scenario = workspace?.scenario;
  const orderedIndicators = useMemo(
    () => orderFinanceIndicators(workspace?.indicators ?? []),
    [workspace?.indicators],
  );
  const limitations = useMemo(
    () => (scenario ? collectScenarioLimitations(scenario) : []),
    [scenario],
  );
  const busy = isPending || state.phase !== "idle";

  function loadScenario(scenarioRecordId: string) {
    if (scenarioRecordId === state.selectedScenarioId || busy) return;
    dispatch({ type: "start", phase: "loading" });
    startTransition(async () => {
      const result = await loadScenarioAction(scenarioRecordId);
      dispatch({
        type: "loaded",
        result,
        announcement: result.data
          ? `Loaded ${result.data.scenario.name}.`
          : "Finance scenario could not be loaded.",
      });
    });
  }

  function runCalculation() {
    if (!scenario || busy) return;
    dispatch({ type: "start", phase: "calculating" });
    startTransition(async () => {
      const result = await calculateScenarioAction(scenario.scenario_record_id);
      dispatch({
        type: "loaded",
        result,
        announcement: result.data?.execution
          ? `Calculation ${result.data.execution.status}. Execution ${result.data.execution.execution_id}.`
          : "Finance calculation did not complete.",
      });
    });
  }

  function registerScenario(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!scenarioJson.trim() || busy) return;
    dispatch({ type: "start", phase: "registering" });
    startTransition(async () => {
      const result = await registerScenarioAction(scenarioJson);
      dispatch({
        type: "registered",
        result,
        announcement: result.data
          ? `Registered ${result.data.scenario.name}.`
          : "Finance scenario registration failed.",
      });
      if (result.data) setScenarioJson("");
    });
  }

  return (
    <section
      className={styles.workspace}
      aria-label="FIN-001 finance workspace"
      aria-busy={busy}
    >
      <p className={styles.liveRegion} aria-live="polite" aria-atomic="true">
        {state.announcement}
      </p>

      <aside className={styles.catalogue} aria-label="Finance scenario catalogue">
        <div className={styles.catalogueHeading}>
          <div>
            <p className="eyebrow">Scenario catalogue</p>
            <h2>Immutable versions</h2>
          </div>
          <span>{state.scenarios.length}</span>
        </div>
        {state.scenarios.length > 0 ? (
          <div className={styles.scenarioList}>
            {state.scenarios.map((item) => (
              <button
                className={`${styles.scenarioButton} ${
                  state.selectedScenarioId === item.scenario_record_id ? styles.selected : ""
                }`}
                type="button"
                key={item.scenario_record_id}
                aria-pressed={state.selectedScenarioId === item.scenario_record_id}
                disabled={busy}
                onClick={() => loadScenario(item.scenario_record_id)}
              >
                <span className={styles.scenarioButtonTitle}>{item.name}</span>
                <span className={styles.scenarioButtonMeta}>
                  v{item.scenario_version} · {item.reporting_currency} · {item.price_year}
                </span>
                <span className={styles.scenarioButtonStatus}>
                  {item.is_synthetic ? "Synthetic" : "Project-linked"}
                </span>
              </button>
            ))}
          </div>
        ) : (
          <div className={styles.compactEmpty}>
            <strong>No finance scenarios</strong>
            <p>The Studio will not invent a scenario. Register a complete canonical payload.</p>
          </div>
        )}

        <details className={styles.registration}>
          <summary>Register canonical scenario JSON</summary>
          <form onSubmit={registerScenario}>
            <label htmlFor="finance-scenario-json">Complete FIN-001 scenario payload</label>
            <textarea
              id="finance-scenario-json"
              value={scenarioJson}
              onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setScenarioJson(event.target.value)}
              rows={12}
              spellCheck={false}
              placeholder="Paste one complete canonical FinanceScenario JSON object."
            />
            <p>
              Missing values are rejected. The Studio does not estimate, repair or silently
              complete financial assumptions.
            </p>
            <button
              className={styles.secondaryButton}
              type="submit"
              disabled={busy || !scenarioJson.trim()}
            >
              {state.phase === "registering" ? "Registering…" : "Validate and register"}
            </button>
          </form>
        </details>
      </aside>

      <div className={styles.main}>
        {state.error ? (
          <div className={styles.errorBanner} role="alert">
            <strong>Finance operation incomplete</strong>
            <span>{state.error}</span>
          </div>
        ) : null}

        {!scenario ? (
          <div className="empty-state">
            <h2>No controlled finance scenario is available</h2>
            <p>
              Seed the synthetic fixture or register a complete canonical scenario. AED Studio
              will not display placeholder finance values.
            </p>
          </div>
        ) : (
          <>
            <header className={styles.scenarioHeader}>
              <div>
                <div className={styles.badges}>
                  <StatusBadge tone={scenario.is_synthetic ? "warning" : "positive"}>
                    {scenario.is_synthetic ? "Synthetic scenario" : "Project-linked scenario"}
                  </StatusBadge>
                  <StatusBadge tone={financeStatusTone(scenario.validation_status)}>
                    {humanizeFinanceIdentifier(scenario.validation_status)}
                  </StatusBadge>
                </div>
                <p className="eyebrow">FIN-001 transparent project finance</p>
                <h2>{scenario.name}</h2>
                <p>
                  Version {scenario.scenario_version} · {scenario.reporting_currency} · price year {scenario.price_year} · {scenario.monetary_basis} basis
                </p>
              </div>
              <button
                className={styles.primaryButton}
                type="button"
                onClick={runCalculation}
                disabled={busy}
              >
                {state.phase === "calculating" ? "Calculating…" : "Run deterministic calculation"}
              </button>
            </header>

            {scenario.is_synthetic ? (
              <div className={styles.syntheticWarning} role="alert">
                <strong>Synthetic evidence boundary</strong>
                <p>
                  Every financial and technical value in this scenario is controlled test data.
                  Results are not a Burkina Faso project estimate, approved tariff, lender model
                  or investment recommendation.
                </p>
              </div>
            ) : null}

            <section className={styles.panel} aria-labelledby="finance-scenario-identity">
              <div className={styles.sectionHeading}>
                <div>
                  <p className="eyebrow">Immutable identity</p>
                  <h3 id="finance-scenario-identity">Scenario and calculation lineage</h3>
                </div>
              </div>
              <dl className={styles.identityGrid}>
                <div><dt>Scenario record</dt><dd className={styles.mono}>{scenario.scenario_record_id}</dd></div>
                <div><dt>Scenario ID</dt><dd className={styles.mono}>{scenario.scenario_id}</dd></div>
                <div><dt>Input hash</dt><dd className={styles.mono}>{scenario.input_hash}</dd></div>
                <div><dt>Formula</dt><dd>{scenario.formula_version}</dd></div>
                <div><dt>Canonicalization</dt><dd>{scenario.canonicalization_version}</dd></div>
                <div><dt>Geography</dt><dd>{scenario.geography_id}</dd></div>
                <div><dt>Project</dt><dd>{identityValue(scenario.project_id)}</dd></div>
                <div><dt>Contributor</dt><dd>{scenario.scenario.responsible_contributor}</dd></div>
                {workspace?.execution ? (
                  <>
                    <div><dt>Execution</dt><dd className={styles.mono}>{workspace.execution.execution_id}</dd></div>
                    <div><dt>Calculation run</dt><dd className={styles.mono}>{workspace.execution.calculation_run_id}</dd></div>
                    <div><dt>Software</dt><dd>{workspace.execution.software_version}</dd></div>
                    <div><dt>Execution status</dt><dd><StatusBadge tone={financeStatusTone(workspace.execution.status)}>{humanizeFinanceIdentifier(workspace.execution.status)}</StatusBadge></dd></div>
                  </>
                ) : null}
              </dl>
            </section>

            <section className={styles.assumptionGrid} aria-label="Scenario assumptions">
              <article className={styles.panel}>
                <p className="eyebrow">Capital structure</p>
                <h3>Funding requirement</h3>
                <strong className={styles.largeValue}>
                  {exact(
                    scenario.scenario.funding_requirement.amount,
                    scenario.scenario.funding_requirement.currency,
                  )}
                </strong>
                <dl className={styles.metricStack}>
                  <div><dt>Price year</dt><dd>{scenario.scenario.funding_requirement.price_year}</dd></div>
                  <div><dt>Basis</dt><dd>{scenario.scenario.funding_requirement.basis}</dd></div>
                  <div><dt>Components</dt><dd>{scenario.scenario.financing_components.length}</dd></div>
                </dl>
              </article>
              <article className={styles.panel}>
                <p className="eyebrow">Analysis horizon</p>
                <h3>Declared timing</h3>
                <dl className={styles.metricStack}>
                  <div><dt>Start year</dt><dd>{scenario.scenario.project_start_year}</dd></div>
                  <div><dt>Construction</dt><dd>{scenario.scenario.construction_years} years</dd></div>
                  <div><dt>Project life</dt><dd>{scenario.scenario.project_lifetime_years} years</dd></div>
                  <div><dt>Discount rate</dt><dd>{exact(scenario.scenario.discount_rate, "decimal ratio")}</dd></div>
                </dl>
              </article>
              <article className={styles.panel}>
                <p className="eyebrow">Evidence inventory</p>
                <h3>Declared records</h3>
                <dl className={styles.metricStack}>
                  <div><dt>Cost items</dt><dd>{scenario.scenario.cost_items.length}</dd></div>
                  <div><dt>Energy years</dt><dd>{scenario.scenario.annual_energy.length}</dd></div>
                  <div><dt>Customer classes</dt><dd>{scenario.scenario.customer_classes.length}</dd></div>
                  <div><dt>Unique limitations</dt><dd>{limitations.length}</dd></div>
                </dl>
              </article>
            </section>

            <section className={styles.panel} aria-labelledby="finance-limitations">
              <div className={styles.sectionHeading}>
                <div>
                  <p className="eyebrow">Evidence limitations</p>
                  <h3 id="finance-limitations">Assumptions remain visible</h3>
                </div>
              </div>
              {limitations.length > 0 ? (
                <ul className={styles.limitations}>
                  {limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}
                </ul>
              ) : (
                <p>No limitations were returned. This should be reviewed before use.</p>
              )}
            </section>

            {workspace?.execution?.status === "failed" ? (
              <section className={styles.failurePanel} role="alert">
                <strong>Calculation rejected after execution recording</strong>
                <p>{workspace.execution.error_message ?? "No failure message was returned."}</p>
                <span className={styles.mono}>{workspace.execution.execution_id}</span>
              </section>
            ) : null}

            {workspace?.execution?.status === "succeeded" ? (
              <>
                <section className={styles.resultsSection} aria-labelledby="finance-results">
                  <div className={styles.sectionHeading}>
                    <div>
                      <p className="eyebrow">Deterministic indicators</p>
                      <h3 id="finance-results">Exact results without silent rounding</h3>
                    </div>
                    <span>{orderedIndicators.length} indicators</span>
                  </div>
                  <div className={styles.resultGrid}>
                    {orderedIndicators.map((indicator) => (
                      <ResultCard indicator={indicator} key={indicator.result_id} />
                    ))}
                  </div>
                </section>

                <section className={styles.panel} aria-labelledby="finance-cash-flow">
                  <div className={styles.sectionHeading}>
                    <div>
                      <p className="eyebrow">Project cash flow</p>
                      <h3 id="finance-cash-flow">Annual lifecycle series</h3>
                    </div>
                    <span>
                      {workspace.cashFlow?.currency} · {workspace.cashFlow?.price_year} · {workspace.cashFlow?.monetary_basis}
                    </span>
                  </div>
                  {workspace.cashFlow ? (
                    <div className={styles.tableScroller} tabIndex={0} aria-label="Scrollable exact cash-flow table">
                      <table className={styles.table}>
                        <caption>Exact annual finance values for execution {workspace.cashFlow.execution_id}</caption>
                        <thead>
                          <tr><th>Year</th><th>Lifecycle cost</th><th>Project revenue</th><th>Net cash flow</th><th>Discount factor</th><th>Discounted cash flow</th></tr>
                        </thead>
                        <tbody>
                          {workspace.cashFlow.rows.map((row) => (
                            <tr key={row.year}>
                              <th scope="row">{row.year}</th>
                              <td>{formatExactDecimal(row.lifecycle_cost)}</td>
                              <td>{formatExactDecimal(row.project_revenue)}</td>
                              <td>{formatExactDecimal(row.net_cash_flow)}</td>
                              <td>{formatExactDecimal(row.discount_factor)}</td>
                              <td>{formatExactDecimal(row.discounted_cash_flow)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <p>Cash-flow data was not returned for this execution.</p>}
                </section>

                <section className={styles.resultsSection} aria-labelledby="finance-affordability">
                  <div className={styles.sectionHeading}>
                    <div>
                      <p className="eyebrow">Affordability</p>
                      <h3 id="finance-affordability">Customer-class burdens</h3>
                    </div>
                    <span>{workspace.affordability.length} classes</span>
                  </div>
                  {workspace.affordability.length > 0 ? (
                    <div className={styles.affordabilityGrid}>
                      {workspace.affordability.map((item) => (
                        <AffordabilityCard item={item} key={item.result_id} />
                      ))}
                    </div>
                  ) : (
                    <div className={styles.compactEmpty}>
                      <strong>No affordability records</strong>
                      <p>The scenario declared no customer classes or the result set was unavailable.</p>
                    </div>
                  )}
                </section>
              </>
            ) : null}

            <section className={styles.panel} aria-labelledby="finance-validation-events">
              <div className={styles.sectionHeading}>
                <div>
                  <p className="eyebrow">Validation evidence</p>
                  <h3 id="finance-validation-events">Immutable checks and warnings</h3>
                </div>
                <span>{workspace?.validations.length ?? 0} events</span>
              </div>
              {workspace && workspace.validations.length > 0 ? (
                <ol className={styles.validationList}>
                  {workspace.validations.map((validation) => (
                    <li key={validation.validation_event_id}>
                      <div>
                        <StatusBadge tone={financeStatusTone(validation.status)}>
                          {humanizeFinanceIdentifier(validation.status)}
                        </StatusBadge>
                        <time dateTime={validation.created_at}>{validation.created_at}</time>
                      </div>
                      <strong>{validation.message}</strong>
                      <span className={styles.mono}>{validation.validation_event_id}</span>
                    </li>
                  ))}
                </ol>
              ) : (
                <p>No finance validation event has been recorded for this scenario.</p>
              )}
            </section>
          </>
        )}
      </div>
    </section>
  );
}
