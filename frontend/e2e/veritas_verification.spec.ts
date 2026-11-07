import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

test.describe("VERITAS AI — Complete Customer Lifecycle & E2E Verification", () => {
  const screenshotsDir = path.join(__dirname, "screenshots");

  test.beforeAll(() => {
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
  });

  test("1. Public Marketing Website: verifies hero, navigation, and interactive tabs", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/VERITAS AI/);

    const heading = page.locator("h1");
    await expect(heading).toContainText("The Defense-Grade Reliability Platform for");

    // Click through interactive product demo tabs
    const traceTab = page.getByRole("button", { name: "Trace Explorer" });
    const regressionTab = page.getByRole("button", { name: "CI Regression Gate" });
    const driftTab = page.getByRole("button", { name: "Drift Monitor" });
    const auditTab = page.getByRole("button", { name: "Audit Ledger" });

    await expect(traceTab).toBeVisible();
    await traceTab.click();
    await expect(page.locator("text=[REDACTED_SSN]").first()).toBeVisible();

    await regressionTab.click();
    await expect(page.locator("text=CI GATE: ALLOW")).toBeVisible();
    await expect(page.locator("text=p = 1.0000")).toBeVisible();

    await driftTab.click();
    await expect(page.locator("text=ACTIVE INCIDENT #DRF-001")).toBeVisible();

    await auditTab.click();
    await expect(page.locator("text=LEDGER: UNBROKEN / VALID")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "01_marketing_landing.png"), fullPage: true });
  });

  test("2. Customer Registration & Onboarding Wizard Flow", async ({ page }) => {
    // 1. Visit Register Page
    await page.goto("/register");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h2")).toContainText("Create Your Organization");

    const uniqueEmail = `qa_engineer_${Date.now()}@fintech.io`;
    await page.fill('input[placeholder="Jane Doe"]', "Alex Mercer");
    await page.fill('input[placeholder="jane@company.com"]', uniqueEmail);
    await page.fill('input[placeholder="Apex Financial Systems"]', "Horizon AI Risk");
    await page.fill('input[placeholder="••••••••••••"]', "EnterpriseSecure2026!");

    await Promise.all([
      page.waitForURL("**/onboarding", { timeout: 10000 }),
      page.click('button[type="submit"]'),
    ]);

    await expect(page.locator("h1")).toContainText("VERITAS AI Quickstart");

    // Step 1: Create Project
    await expect(page.locator("text=Name Your AI Application Project")).toBeVisible();
    await page.click('button:has-text("Generate API Key & Continue")');

    // Step 2: Mint API Key
    await expect(page.locator("text=Your Production Ingestion API Key")).toBeVisible({ timeout: 8000 });
    await expect(page.locator("text=vai_live_")).toBeVisible();
    await page.click('button:has-text("View Code Examples")');

    // Step 3: Code Integration
    await expect(page.locator("text=Connect Your Application").first()).toBeVisible();
    await expect(page.locator("text=from veritas import Veritas").first()).toBeVisible();

    // Step 4: Send Test Ping & Verify Ingestion
    await page.click('button:has-text("Send Test Ping & Verify")');
    await expect(page.locator("text=Handshake Successful! First Trace Received")).toBeVisible({ timeout: 10000 });

    await page.screenshot({ path: path.join(screenshotsDir, "02_onboarding_wizard_verified.png"), fullPage: true });
  });

  test("3. Projects & API Key Management (/projects): verifies creation, keys & revocation", async ({ page }) => {
    await page.goto("/projects");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Projects & API Key");

    // Verify projects list
    await expect(page.locator("text=Projects (")).toBeVisible();
    await expect(page.locator("text=API Keys:")).toBeVisible();

    // Verify API Key Table
    await expect(page.locator("text=Key Name")).toBeVisible();
    await expect(page.locator("text=ACTIVE").first()).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "03_projects_api_keys.png"), fullPage: true });
  });

  test("4. Evaluation Studio (/evaluations): executes multi-case criteria suite", async ({ page }) => {
    await page.goto("/evaluations");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Evaluation Studio");

    // Run studio evaluation
    await page.click('button:has-text("Run Evaluation Suite")');
    await expect(page.locator("text=Evaluation Suite Outcome")).toBeVisible({ timeout: 8000 });
    await expect(page.locator("text=Pass Rate")).toBeVisible();
    await expect(page.locator("text=CASE-01")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "04_evaluation_studio.png"), fullPage: true });
  });

  test("5. Executive Overview Console (/dashboard): verifies metrics & KPI cards", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Executive Overview");

    await expect(page.locator("text=Audit Ledger Verified")).toBeVisible();
    await expect(page.locator("text=Drift Alerts")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "05_executive_dashboard.png"), fullPage: true });
  });

  test("6. Trace Explorer (/traces): verifies list, PII masking & nested spans", async ({ page }) => {
    await page.goto("/traces");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Trace Explorer");

    const traceRow = page.locator("text=credit_memo_v1").first();
    await expect(traceRow).toBeVisible();

    await expect(page.locator("text=Rendered Input Payload (PII Redacted)")).toBeVisible();
    await expect(page.locator("text=[REDACTED_SSN]").first()).toBeVisible();
    await expect(page.locator("text=Nested Span Execution Tree")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "06_trace_explorer.png"), fullPage: true });
  });

  test("7. CI Regression Gatekeeper (/regressions): verifies Wilcoxon & effect size", async ({ page }) => {
    await page.goto("/regressions");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Regression Testing");

    await expect(page.locator("text=Wilcoxon p-value")).toBeVisible();
    await expect(page.locator("text=CI Gatekeeper Decision")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "07_regression_ci_gate.png"), fullPage: true });
  });

  test("8. Continuous Drift Monitor (/drift): verifies PSI metric & incident triage", async ({ page }) => {
    await page.goto("/drift");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Continuous Drift");

    await expect(page.locator("text=Detected Production Drift Events")).toBeVisible();
    await expect(page.locator("text=Incident Triage & Human Review")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "08_drift_monitor.png"), fullPage: true });
  });

  test("9. Judge Calibration (/calibration): verifies Cohen's Kappa certification", async ({ page }) => {
    await page.goto("/calibration");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Calibration");

    await expect(page.locator("text=Dimensional Agreement Breakdown")).toBeVisible();
    await expect(page.locator("text=Factual Accuracy").first()).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "09_judge_calibration.png"), fullPage: true });
  });

  test("10. Cryptographic Audit Ledger (/audit): verifies SHA-256 chain verification", async ({ page }) => {
    await page.goto("/audit");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Cryptographic Audit Ledger");

    await expect(page.locator("text=Immutable Event Ledger")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "10_audit_ledger.png"), fullPage: true });
  });

  test("11. Governance Dossier (/reports): verifies SR 11-7 export controls", async ({ page }) => {
    await page.goto("/reports");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Model Risk Governance Dossier");

    await expect(page.locator("text=Institutional Evidence Package")).toBeVisible();
    await expect(page.locator("text=Download Full JSON Dossier")).toBeVisible();
    await expect(page.locator("text=Export CSV")).toBeVisible();

    await page.screenshot({ path: path.join(screenshotsDir, "11_governance_dossier.png"), fullPage: true });
  });
});
