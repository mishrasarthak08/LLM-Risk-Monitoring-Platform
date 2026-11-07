/**
 * VERITAS AI — Official Node.js / TypeScript SDK
 */

export interface VeritasConfig {
  apiKey: string;
  baseUrl?: string;
  timeoutMs?: number;
  maxRetries?: number;
}

export interface SpanData {
  name: string;
  span_type: string;
  latency_ms: number;
  tokens?: number;
  input_data?: any;
  output_data?: any;
  error_message?: string;
}

export interface TracePayload {
  feature_name: string;
  model_name?: string;
  input_payload?: any;
  output_text?: string;
  input_tokens?: number;
  output_tokens?: number;
  latency_ms: number;
  status: "SUCCESS" | "ERROR" | "REFUSAL";
  error_message?: string;
  metadata_json?: any;
  spans?: SpanData[];
}

const SSN_REGEX = /\b\d{3}-\d{2}-\d{4}\b/g;
const CARD_REGEX = /\b(?:\d{4}[- ]?){3}\d{4}\b/g;

export function redactSensitiveData(obj: any): any {
  if (typeof obj === "string") {
    return obj.replace(SSN_REGEX, "[REDACTED_SSN]").replace(CARD_REGEX, "[REDACTED_CARD]");
  }
  if (Array.isArray(obj)) {
    return obj.map(redactSensitiveData);
  }
  if (typeof obj === "object" && obj !== null) {
    const res: any = {};
    for (const key of Object.keys(obj)) {
      res[key] = redactSensitiveData(obj[key]);
    }
    return res;
  }
  return obj;
}

export class Veritas {
  private apiKey: string;
  private baseUrl: string;
  private timeoutMs: number;

  constructor(config: VeritasConfig) {
    if (!config.apiKey) {
      throw new Error("VERITAS API key is required.");
    }
    this.apiKey = config.apiKey.trim();
    this.baseUrl = (config.baseUrl || "http://localhost:8000/api/v1").replace(/\/$/, "");
    this.timeoutMs = config.timeoutMs || 5000;
  }

  async sendTrace(payload: TracePayload): Promise<boolean> {
    const sanitized = redactSensitiveData(payload);
    try {
      const response = await fetch(`${this.baseUrl}/traces/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": this.apiKey,
          "User-Agent": "veritas-node-sdk/2.0.0",
        },
        body: JSON.stringify(sanitized),
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      return response.ok;
    } catch (err) {
      console.warn("VERITAS background telemetry delivery failed:", err);
      return false;
    }
  }

  async trace<T>(
    name: string,
    fn: (logger: {
      logInput: (data: any) => void;
      logOutput: (data: any) => void;
      logTokens: (input: number, output: number) => void;
    }) => Promise<T>
  ): Promise<T> {
    const start = performance.now();
    let inputPayload: any = undefined;
    let outputText: string = "";
    let inTok = 0;
    let outTok = 0;
    let status: "SUCCESS" | "ERROR" = "SUCCESS";
    let errMsg: string | undefined = undefined;

    try {
      const result = await fn({
        logInput: (data) => { inputPayload = data; },
        logOutput: (data) => { outputText = typeof data === "string" ? data : JSON.stringify(data); },
        logTokens: (inp, outp) => { inTok = inp; outTok = outp; },
      });
      if (!outputText && result !== undefined) {
        outputText = typeof result === "string" ? result : JSON.stringify(result);
      }
      return result;
    } catch (error: any) {
      status = "ERROR";
      errMsg = error?.message || String(error);
      throw error;
    } finally {
      const duration = Math.max(1, Math.round(performance.now() - start));
      // Fire-and-forget background transmission
      this.sendTrace({
        feature_name: name,
        input_payload: inputPayload,
        output_text: outputText,
        input_tokens: inTok,
        output_tokens: outTok,
        latency_ms: duration,
        status,
        error_message: errMsg,
      }).catch(() => {});
    }
  }
}

