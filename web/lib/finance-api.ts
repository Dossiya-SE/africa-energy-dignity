import "server-only";

import type {
  FinanceAffordabilityPage,
  FinanceCashFlowResponse,
  FinanceExecutionRecord,
  FinanceIndicatorPage,
  FinanceScenarioDetail,
  FinanceScenarioPage,
  FinanceValidationPage,
  FinanceWorkspaceActionResult,
  FinanceWorkspaceData,
} from "@/lib/types";

const API_BASE_URL = (process.env.AED_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

interface FinanceRequestResult<T> {
  data: T | null;
  error: string | null;
  status: number | null;
  executionId: string | null;
}

function errorDetail(payload: unknown): { message: string | null; executionId: string | null } {
  if (!payload || typeof payload !== "object") {
    return { message: null, executionId: null };
  }
  const detail = (payload as { detail?: unknown }).detail;
  if (typeof detail === "string") {
    return { message: detail, executionId: null };
  }
  if (!detail || typeof detail !== "object") {
    return { message: null, executionId: null };
  }
  const record = detail as { message?: unknown; execution_id?: unknown };
  return {
    message: typeof record.message === "string" ? record.message : null,
    executionId: typeof record.execution_id === "string" ? record.execution_id : null,
  };
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<FinanceRequestResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
      signal: AbortSignal.timeout(10000),
    });
    const payload = (await response.json().catch(() => null)) as unknown;
    if (!response.ok) {
      const detail = errorDetail(payload);
      return {
        data: null,
        error: detail.message ?? `AED finance API returned ${response.status} for ${path}.`,
        status: response.status,
        executionId: detail.executionId,
      };
    }
    return {
      data: payload as T,
      error: null,
      status: response.status,
      executionId: null,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown API failure";
    return {
      data: null,
      error: `AED finance service unavailable: ${message}`,
      status: null,
      executionId: null,
    };
  }
}

export async function getFinanceScenarios(): Promise<FinanceRequestResult<FinanceScenarioPage>> {
  return request<FinanceScenarioPage>("/finance/scenarios?limit=100&offset=0");
}

export async function getFinanceScenario(
  scenarioRecordId: string,
): Promise<FinanceRequestResult<FinanceScenarioDetail>> {
  return request<FinanceScenarioDetail>(
    `/finance/scenarios/${encodeURIComponent(scenarioRecordId)}`,
  );
}

export async function getFinanceValidations(
  scenarioRecordId: string,
): Promise<FinanceRequestResult<FinanceValidationPage>> {
  return request<FinanceValidationPage>(
    `/finance/scenarios/${encodeURIComponent(scenarioRecordId)}/validations?limit=100&offset=0`,
  );
}

async function getFinanceExecution(
  executionId: string,
): Promise<FinanceRequestResult<FinanceExecutionRecord>> {
  return request<FinanceExecutionRecord>(
    `/finance/executions/${encodeURIComponent(executionId)}`,
  );
}

async function getFinanceCashFlow(
  executionId: string,
): Promise<FinanceRequestResult<FinanceCashFlowResponse>> {
  return request<FinanceCashFlowResponse>(
    `/finance/executions/${encodeURIComponent(executionId)}/cash-flow`,
  );
}

async function getFinanceIndicators(
  executionId: string,
): Promise<FinanceRequestResult<FinanceIndicatorPage>> {
  return request<FinanceIndicatorPage>(
    `/finance/executions/${encodeURIComponent(executionId)}/indicators?limit=100&offset=0`,
  );
}

async function getFinanceAffordability(
  executionId: string,
): Promise<FinanceRequestResult<FinanceAffordabilityPage>> {
  return request<FinanceAffordabilityPage>(
    `/finance/executions/${encodeURIComponent(executionId)}/affordability?limit=100&offset=0`,
  );
}

async function createFinanceExecution(
  scenarioRecordId: string,
): Promise<FinanceRequestResult<FinanceExecutionRecord>> {
  return request<FinanceExecutionRecord>("/finance/calculations", {
    method: "POST",
    body: JSON.stringify({ scenario_record_id: scenarioRecordId }),
  });
}

async function createFinanceScenario(
  payload: unknown,
): Promise<FinanceRequestResult<FinanceScenarioDetail>> {
  return request<FinanceScenarioDetail>("/finance/scenarios", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function workspace(
  scenario: FinanceScenarioDetail,
  validations: FinanceValidationPage | null,
  execution: FinanceExecutionRecord | null = null,
  cashFlow: FinanceCashFlowResponse | null = null,
  indicators: FinanceIndicatorPage | null = null,
  affordability: FinanceAffordabilityPage | null = null,
): FinanceWorkspaceData {
  return {
    scenario,
    execution,
    cashFlow,
    indicators: indicators?.items ?? [],
    affordability: affordability?.items ?? [],
    validations: validations?.items ?? [],
  };
}

export async function loadFinanceWorkspaceData(
  scenarioRecordId: string,
): Promise<FinanceWorkspaceActionResult> {
  const [scenarioResult, validationResult] = await Promise.all([
    getFinanceScenario(scenarioRecordId),
    getFinanceValidations(scenarioRecordId),
  ]);
  if (!scenarioResult.data) {
    return { data: null, error: scenarioResult.error };
  }
  return {
    data: workspace(scenarioResult.data, validationResult.data),
    error: validationResult.error,
  };
}

export async function calculateFinanceWorkspaceData(
  scenarioRecordId: string,
): Promise<FinanceWorkspaceActionResult> {
  const scenarioResult = await getFinanceScenario(scenarioRecordId);
  if (!scenarioResult.data) {
    return { data: null, error: scenarioResult.error };
  }

  const executionResult = await createFinanceExecution(scenarioRecordId);
  if (!executionResult.data) {
    const [validationResult, failedExecutionResult] = await Promise.all([
      getFinanceValidations(scenarioRecordId),
      executionResult.executionId
        ? getFinanceExecution(executionResult.executionId)
        : Promise.resolve({
            data: null,
            error: null,
            status: null,
            executionId: null,
          }),
    ]);
    return {
      data: workspace(
        scenarioResult.data,
        validationResult.data,
        failedExecutionResult.data,
      ),
      error: executionResult.error,
    };
  }

  const executionId = executionResult.data.execution_id;
  const [cashFlowResult, indicatorResult, affordabilityResult, validationResult] =
    await Promise.all([
      getFinanceCashFlow(executionId),
      getFinanceIndicators(executionId),
      getFinanceAffordability(executionId),
      getFinanceValidations(scenarioRecordId),
    ]);
  const secondaryError =
    cashFlowResult.error ??
    indicatorResult.error ??
    affordabilityResult.error ??
    validationResult.error;
  return {
    data: workspace(
      scenarioResult.data,
      validationResult.data,
      executionResult.data,
      cashFlowResult.data,
      indicatorResult.data,
      affordabilityResult.data,
    ),
    error: secondaryError,
  };
}

export async function registerFinanceScenarioData(
  scenarioJson: string,
): Promise<FinanceWorkspaceActionResult> {
  let payload: unknown;
  try {
    payload = JSON.parse(scenarioJson) as unknown;
  } catch {
    return { data: null, error: "Scenario JSON is not valid JSON." };
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return { data: null, error: "Scenario JSON must contain one object." };
  }
  const scenarioResult = await createFinanceScenario(payload);
  if (!scenarioResult.data) {
    return { data: null, error: scenarioResult.error };
  }
  const validationResult = await getFinanceValidations(
    scenarioResult.data.scenario_record_id,
  );
  return {
    data: workspace(scenarioResult.data, validationResult.data),
    error: validationResult.error,
  };
}
