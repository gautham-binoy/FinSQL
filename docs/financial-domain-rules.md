# Financial Domain Intelligence & Accounting Rules

FinSQL Agent is built with explicit rules to handle common corporate accounting traps that trip up generic Text-to-SQL models.

---

## 1. Fiscal Year vs. Calendar Year

Public corporations often do not follow a calendar year ending on December 31:
- **Apple Inc. (AAPL)**: Fiscal year ends on the last Saturday of September (e.g. FY2023 ended September 30, 2023).
- **Microsoft Corporation (MSFT)**: Fiscal year ends June 30 (e.g. FY2023 ended June 30, 2023).
- **Nvidia Corporation (NVDA)**: Fiscal year ends late January (e.g. FY2024 ended January 28, 2024).

**System Rule**: Queries explicitly filter by `fiscal_year` and `fiscal_period = 'FY'` while stating accounting assumptions in the answer metadata.

---

## 2. Restatements (`is_restated`)

Financial statements can contain original filings and amended/restated figures due to accounting adjustments:
- If a query fails to filter `is_restated`, it will return duplicate rows for the same company, concept, and fiscal year.

**System Rule**: Default queries enforce `is_restated = FALSE`. When queries specifically ask for restatements, `is_restated = TRUE` is applied.

---

## 3. Consolidated vs. Standalone Reporting

- **Consolidated (`reporting_type = 'consolidated'`)**: Represents the entire parent company and all operating subsidiaries (standard for SEC Form 10-K).
- **Standalone (`reporting_type = 'standalone'`)**: Represents only the parent legal entity.

**System Rule**: Always filter for `reporting_type = 'consolidated'` unless the user query specifically asks for standalone parent accounting.

---

## 4. Incompatible Units

- Currency: `USD`
- Share counts: `shares`
- Earnings per share: `per-share`
- Ratios / Margins: `percentage`

**System Rule**: Arithmetic is never performed across incompatible units. Ratios (such as Net Income Margin) require dividing currency values (`NetIncome * 100.0 / Revenue`).
