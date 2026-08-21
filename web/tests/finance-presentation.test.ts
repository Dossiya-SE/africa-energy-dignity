import { describe, expect, it } from "vitest";

import {
  collectScenarioLimitations,
  financeStatusTone,
  financeWorkspaceReducer,
  formatExactDecimal,
  humanizeFinanceIdentifier,
  initialFinanceWorkspaceState,
  orderFinanceIndicators,
} from "@/lib/finance-presentation";
import type {
  FinanceIndicatorRecord,
  FinanceScenarioDetail,
  FinanceScenarioSummary,
  FinanceWorkspaceData,
} from "@/lib/types";

const summary: FinanceScenarioSummary = {
  scenario_record_id: "finance.scenario.sha256.abc",
  scenario_id: "finance.scenario.synthetic.test",
  scenario_version: "1.0.0",
  name: "Synthetic Test Scenario",
  formula_version: "FIN-001.1",
  canonicalization_version: "FIN-CANONICAL-JSON-1",
  input_hash: "sha256:abc",
  geography_id: "geo.bfa",
  project_id: null,
  is_synthetic: true,
  reporting_currency: "XOF",
  price_year: 2026,
  monetary_basis: "real",
  validation_status: "schema_valid",
  recorded_at: "2026-07-31T00:00:00Z",
};

const detail: FinanceScenarioDetail = {
  ...summary,
  scenario: {
    scenario_id: summary.scenario_id,
    name: summary.name,
    scenario_version: summary.scenario_version,
    formula_version: summary.formula_version,
    geography_id: summary.geography_id,
    project_id: null,
    is_synthetic: true,
    reporting_currency: "XOF",
    price_year: 2026,
    monetary_basis: "real",
    discount_rate: "0.08",
    discount_rate_basis: "real",
    inflation_rate: null,
    funding_requirement: {
      amount: "1000000000",
      currency: "XOF",
      price_year: 2026,
      basis: "real",
    },
    project_start_year: 2026,
    project_lifetime_years: 10,
    construction_years: 1,
    cost_items: [
      {
        cost_id: "cost.synthetic.capex",
        category: "capex",
        timing_year: 0,
        value: {
          amount: "1000000000",
          currency: "XOF",
          price_year: 2026,
          basis: "real",
        },
        quantity_driver: null,
        quantity_unit: null,
        evidence: {
          source_id: null,
          evidence_class: "scenario",
          validation_status: "schema_valid",
          responsible_contributor: "Tester",
          limitations: ["Invented value for testing only."],
          uncertainty: null,
        },
      },
    ],
    annual_energy: [],
    financing_components: [],
    customer_classes: [],
    validation_status: "schema_valid",
    responsible_contributor: "Tester",
    created_at: "2026-07-31T00:00:00Z",
    updated_at: "2026-07-31T00:00:00Z",
  },
};

const workspace: FinanceWorkspaceData = {
  scenario: detail,
  execution: null,
  cashFlow: null,
  indicators: [],
  affordability: [],
  validations: [],
};

describe("finance presentation", () => {
  it("groups digits without changing decimal precision", () => {
    expect(formatExactDecimal("1234567890.012300")).toBe("1,234,567,890.012300");
    expect(formatExactDecimal("-0.0000001")).toBe("-0.0000001");
  });

  it("does not reinterpret exponent notation", () => {
    expect(formatExactDecimal("1e-9")).toBe("1e-9");
  });

  it("humanizes stable finance identifiers", () => {
    expect(humanizeFinanceIdentifier("dscr.debt.synthetic")).toBe(
      "Dscr · Debt · Synthetic",
    );
  });

  it("keeps failed and warning states visible", () => {
    expect(financeStatusTone("failed")).toBe("negative");
    expect(financeStatusTone("warning")).toBe("warning");
  });

  it("deduplicates declared evidence limitations", () => {
    const duplicateDetail: FinanceScenarioDetail = {
      ...detail,
      scenario: {
        ...detail.scenario,
        cost_items: [
          {
            ...detail.scenario.cost_items[0],
            evidence: {
              ...detail.scenario.cost_items[0].evidence,
              limitations: [
                "Invented value for testing only.",
                "Invented value for testing only.",
              ],
            },
          },
        ],
      },
    };
    expect(collectScenarioLimitations(duplicateDetail)).toEqual([
      "Invented value for testing only.",
    ]);
  });

  it("orders headline indicators before coverage-series indicators", () => {
    const indicator = (name: string): FinanceIndicatorRecord => ({
      result_id: `result.${name}`,
      execution_id: "execution.test",
      indicator_name: name,
      status: "calculated",
      result: { value: "1", method: "test" },
      lineage: {},
      created_at: "2026-07-31T00:00:00Z",
    });
    expect(
      orderFinanceIndicators([
        indicator("dscr.debt"),
        indicator("lcoe"),
        indicator("npv"),
      ]).map((item) => item.indicator_name),
    ).toEqual(["lcoe", "npv", "dscr.debt"]);
  });

  it("preserves the prior workspace when a load fails", () => {
    const state = initialFinanceWorkspaceState([summary], workspace, null);
    const loading = financeWorkspaceReducer(state, {
      type: "start",
      phase: "loading",
    });
    const failed = financeWorkspaceReducer(loading, {
      type: "loaded",
      result: { data: null, error: "Unavailable" },
      announcement: "Finance scenario could not be loaded.",
    });
    expect(failed.workspace).toBe(workspace);
    expect(failed.error).toBe("Unavailable");
    expect(failed.phase).toBe("idle");
  });
});
