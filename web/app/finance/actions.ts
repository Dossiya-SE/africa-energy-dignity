"use server";

import {
  calculateFinanceWorkspaceData,
  loadFinanceWorkspaceData,
  registerFinanceScenarioData,
} from "@/lib/finance-api";
import type { FinanceWorkspaceActionResult } from "@/lib/types";

export async function loadFinanceScenarioAction(
  scenarioRecordId: string,
): Promise<FinanceWorkspaceActionResult> {
  return loadFinanceWorkspaceData(scenarioRecordId);
}

export async function calculateFinanceScenarioAction(
  scenarioRecordId: string,
): Promise<FinanceWorkspaceActionResult> {
  return calculateFinanceWorkspaceData(scenarioRecordId);
}

export async function registerFinanceScenarioAction(
  scenarioJson: string,
): Promise<FinanceWorkspaceActionResult> {
  return registerFinanceScenarioData(scenarioJson);
}
