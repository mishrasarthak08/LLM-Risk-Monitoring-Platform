/**
 * VERITAS AI — Type-Safe API Client
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error [${response.status}]: ${errorBody || response.statusText}`);
  }

  return response.json();
}

// API Methods
export const api = {
  getProjects: () => fetchApi<any[]>("/projects"),
  getTraces: (feature?: string, status?: string) => {
    const query = new URLSearchParams();
    if (feature) query.append("feature", feature);
    if (status) query.append("status", status);
    return fetchApi<any[]>(`/traces?${query.toString()}`);
  },
  getTraceDetail: (id: string) => fetchApi<any>(`/traces/${id}`),
  getPrompts: () => fetchApi<any[]>("/prompts"),
  getPromptDetail: (id: string) => fetchApi<any>(`/prompts/${id}`),
  diffPrompts: (versionAId: string, versionBId: string) =>
    fetchApi<any>("/prompts/diff", {
      method: "POST",
      body: JSON.stringify({ version_a_id: versionAId, version_b_id: versionBId }),
    }),
  getDatasets: () => fetchApi<any[]>("/datasets"),
  getDatasetDetail: (id: string) => fetchApi<any>(`/datasets/${id}`),
  getRegressions: () => fetchApi<any[]>("/regressions"),
  getRegressionDetail: (id: string) => fetchApi<any>(`/regressions/${id}`),
  triggerRegression: (data: {
    baseline_prompt_version_id: string;
    candidate_prompt_version_id: string;
    dataset_version_id: string;
    evaluator_version_id: string;
    trigger?: string;
  }) =>
    fetchApi<any>("/regressions/run", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getDriftEvents: (status?: string) => {
    const query = new URLSearchParams();
    if (status) query.append("status", status);
    return fetchApi<any[]>(`/drift/events?${query.toString()}`);
  },
  triageDriftEvent: (id: string, new_status: string, notes: string) =>
    fetchApi<any>(`/drift/events/${id}/triage`, {
      method: "PATCH",
      body: JSON.stringify({ new_status, notes }),
    }),
  getCalibrationHistory: () => fetchApi<any[]>("/calibration/history"),
  getAuditEvents: () => fetchApi<any[]>("/audit/events"),
  verifyAuditChain: () => fetchApi<any>("/audit/verify"),
  getGovernancePackage: () => fetchApi<any>("/reports/governance-package"),
};

