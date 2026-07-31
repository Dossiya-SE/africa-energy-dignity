import type { StatusTone } from "@/lib/presentation";
import type {
  FinanceIndicatorRecord,
  FinanceScenarioDetail,
  FinanceScenarioSummary,
  FinanceWorkspaceActionResult,
  FinanceWorkspaceData,
} from "@/lib/types";

export type FinanceWorkspacePhase =
  | "idle"
  | "loading"
  | "calculating"
  | "registering";

export interface FinanceWorkspaceState {
  scenarios: FinanceScenarioSummary[];
  selectedScenarioId: string | null;
  workspace: FinanceWorkspaceData | null;
  phase: FinanceWorkspacePhase;
  error: string | null;
  announcement: string;
}

export type FinanceWorkspaceEvent =
  | { type: "start"; phase: Exclude<FinanceWorkspacePhase, "idle"> }
  | {
      type: "loaded";
      result: FinanceWorkspaceActionResult;
      announcement: string;
    }
  | {
      type: "registered";
      result: FinanceWorkspaceActionResult;
      announcement: string;
    };

export function initialFinanceWorkspaceState(
  scenarios: FinanceScenarioSummary[],
  workspace: FinanceWorkspaceData | null,
  error: string | null,
): FinanceWorkspaceState {
  return {
    scenarios,
    selectedScenarioId:
      workspace?.scenario.scenario_record_id ?? scenarios[0]?.scenario_record_id ?? null,
    workspace,
    phase: "idle",
    error,
    announcement: workspace
      ? `Loaded ${workspace.scenario.name}.`
      : "No finance scenario is currently selected.",
  };
}

function summaryFromDetail(detail: FinanceScenarioDetail): FinanceScenarioSummary {
  const { scenario: _scenario, ...summary } = detail;
  return summary;
}

function mergeScenario(
  scenarios: FinanceScenarioSummary[],
  detail: FinanceScenarioDetail,
): FinanceScenarioSummary[] {
  const summary = summaryFromDetail(detail);
  const withoutCurrent = scenarios.filter(
    (item) => item.scenario_record_id !== summary.scenario_record_id,
  );
  return [...withoutCurrent, summary].sort((left, right) => {
    const timeOrder = left.recorded_at.localeCompare(right.recorded_at);
    return timeOrder || left.scenario_record_id.localeCompare(right.scenario_record_id);
  });
}

export function financeWorkspaceReducer(
  state: FinanceWorkspaceState,
  event: FinanceWorkspaceEvent,
): FinanceWorkspaceState {
  if (event.type === "start") {
    return {
      ...state,
      phase: event.phase,
      error: null,
      announcement:
        event.phase === "calculating"
          ? "Running deterministic finance calculation."
          : event.phase === "registering"
            ? "Validating and registering canonical finance scenario."
            : "Loading finance scenario.",
    };
  }
  if (event.type === "registered") {
    const nextWorkspace = event.result.data ?? state.workspace;
    return {
      ...state,
      scenarios: event.result.data
        ? mergeScenario(state.scenarios, event.result.data.scenario)
        : state.scenarios,
      selectedScenarioId:
        event.result.data?.scenario.scenario_record_id ?? state.selectedScenarioId,
      workspace: nextWorkspace,
      phase: "idle",
      error: event.result.error,
      announcement: event.announcement,
    };
  }
  return {
    ...state,
    selectedScenarioId:
      event.result.data?.scenario.scenario_record_id ?? state.selectedScenarioId,
    workspace: event.result.data ?? state.workspace,
    phase: "idle",
    error: event.result.error,
    announcement: event.announcement,
  };
}

export function formatExactDecimal(value: unknown): string {
  if (typeof value !== "string") {
    return value === null || value === undefined ? "Not available" : String(value);
  }
  const match = value.match(/^([+-]?)(\d+)(\.\d+)?$/);
  if (!match) return value;
  const [, sign, integer, fraction = ""] = match;
  return `${sign}${integer.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}${fraction}`;
}

export function humanizeFinanceIdentifier(value: string): string {
  return value
    .replace(/^affordability\./, "")
    .replace(/\./g, " · ")
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function financeStatusTone(status: string): StatusTone {
  if (["succeeded", "passed", "calculated", "validated", "schema_valid"].includes(status)) {
    return "positive";
  }
  if (["failed", "rejected", "invalid_inputs", "invalid_cashflows"].includes(status)) {
    return "negative";
  }
  if (["warning", "no_root", "no_payback", "no_discounted_payback"].includes(status)) {
    return "warning";
  }
  return "neutral";
}

export function collectScenarioLimitations(detail: FinanceScenarioDetail): string[] {
  const scenario = detail.scenario;
  const collections = [
    ...scenario.cost_items.map((item) => item.evidence.limitations),
    ...scenario.annual_energy.map((item) => item.evidence.limitations),
    ...scenario.financing_components.map((item) => item.evidence.limitations),
    ...scenario.customer_classes.map((item) => item.evidence.limitations),
  ];
  const seen = new Set<string>();
  const limitations: string[] = [];
  for (const collection of collections) {
    for (const limitation of collection) {
      const normalized = limitation.trim();
      if (normalized && !seen.has(normalized)) {
        seen.add(normalized);
        limitations.push(normalized);
      }
    }
  }
  return limitations;
}

export function indicatorValue(indicator: FinanceIndicatorRecord): string {
  const result = indicator.result;
  if (typeof result.value === "string") return result.value;
  if (typeof result.initial_llcr === "string") return result.initial_llcr;
  if (typeof result.minimum_llcr === "string") return result.minimum_llcr;
  if (Array.isArray(result.period_values)) {
    return `${result.period_values.length} periods`;
  }
  return indicator.status;
}

export function indicatorUnit(indicator: FinanceIndicatorRecord): string {
  const unit = indicator.result.unit;
  if (typeof unit === "string" && unit) return unit;
  if (indicator.indicator_name === "irr") return "decimal ratio";
  if (indicator.indicator_name.endsWith("payback")) return "years";
  if (
    indicator.indicator_name.startsWith("dscr.") ||
    indicator.indicator_name.startsWith("llcr.")
  ) {
    return "ratio";
  }
  return "";
}

export function indicatorWarnings(indicator: FinanceIndicatorRecord): string[] {
  const warnings = indicator.result.warnings;
  return Array.isArray(warnings)
    ? warnings.filter((item): item is string => typeof item === "string")
    : [];
}

export function indicatorPeriods(
  indicator: FinanceIndicatorRecord,
): Array<{ period: number; value: string }> {
  const values = indicator.result.period_values;
  if (!Array.isArray(values)) return [];
  return values.flatMap((item) => {
    if (!item || typeof item !== "object") return [];
    const record = item as { period?: unknown; value?: unknown };
    if (typeof record.period !== "number" || typeof record.value !== "string") return [];
    return [{ period: record.period, value: record.value }];
  });
}

const HEADLINE_ORDER = [
  "lcoe",
  "npv",
  "irr",
  "simple_payback",
  "discounted_payback",
  "required_subsidy",
  "break_even_tariff",
  "net_present_cost",
  "discounted_energy",
];

export function orderFinanceIndicators(
  indicators: FinanceIndicatorRecord[],
): FinanceIndicatorRecord[] {
  const rank = new Map(HEADLINE_ORDER.map((name, index) => [name, index]));
  return [...indicators].sort((left, right) => {
    const leftRank = rank.get(left.indicator_name) ?? Number.MAX_SAFE_INTEGER;
    const rightRank = rank.get(right.indicator_name) ?? Number.MAX_SAFE_INTEGER;
    return leftRank - rightRank || left.indicator_name.localeCompare(right.indicator_name);
  });
}
