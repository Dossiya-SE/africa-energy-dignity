import "server-only";

import type {
  ApiResult,
  AssetRecord,
  GeographyRecord,
  InstitutionRecord,
  ServiceStatus,
  SourceRecord,
} from "@/lib/types";

const API_BASE_URL = (process.env.AED_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

async function request<T>(path: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return {
        data: null,
        error: `AED API returned ${response.status} for ${path}.`,
      };
    }

    return { data: (await response.json()) as T, error: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown API failure";
    return { data: null, error: `AED registry unavailable: ${message}` };
  }
}

export function getHealth(): Promise<ApiResult<ServiceStatus>> {
  return request<ServiceStatus>("/health");
}

export function getReadiness(): Promise<ApiResult<ServiceStatus>> {
  return request<ServiceStatus>("/ready");
}

export function getSources(): Promise<ApiResult<SourceRecord[]>> {
  return request<SourceRecord[]>("/sources");
}

export function getSource(sourceId: string): Promise<ApiResult<SourceRecord>> {
  return request<SourceRecord>(`/sources/${encodeURIComponent(sourceId)}`);
}

export function getInstitutions(): Promise<ApiResult<InstitutionRecord[]>> {
  return request<InstitutionRecord[]>("/institutions");
}

export function getGeographies(): Promise<ApiResult<GeographyRecord[]>> {
  return request<GeographyRecord[]>("/geographies");
}

export function getAssets(): Promise<ApiResult<AssetRecord[]>> {
  return request<AssetRecord[]>("/assets");
}
