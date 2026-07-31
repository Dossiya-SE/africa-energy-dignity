import type { Metadata } from "next";
import { FinanceWorkspace } from "@/components/finance-workspace";
import {
  calculateFinanceScenarioAction,
  loadFinanceScenarioAction,
  registerFinanceScenarioAction,
} from "@/app/finance/actions";
import { getFinanceScenarios, loadFinanceWorkspaceData } from "@/lib/finance-api";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Transparent Finance" };

export default async function FinancePage() {
  const scenarioPage = await getFinanceScenarios();
  const scenarios = scenarioPage.data?.items ?? [];
  const initial = scenarios[0]
    ? await loadFinanceWorkspaceData(scenarios[0].scenario_record_id)
    : { data: null, error: scenarioPage.error };
  return (
    <>
      <header className="page-heading">
        <p className="eyebrow">Finance Studio</p>
        <h1>Transparent project finance.</h1>
        <p>Inspect immutable scenarios, exact results and validation evidence.</p>
      </header>
      <FinanceWorkspace
        initialScenarios={scenarios}
        initialWorkspace={initial.data}
        initialError={scenarioPage.error ?? initial.error}
        loadScenarioAction={loadFinanceScenarioAction}
        calculateScenarioAction={calculateFinanceScenarioAction}
        registerScenarioAction={registerFinanceScenarioAction}
      />
    </>
  );
}
