# Data Model Reference — Data Quality Assessment API

## 1. Why this document exists
- Gives supervisors and agents a shared glossary of the data we expect.
- Helps rule authors, API designers, and integrators stay consistent.
- Acts as the source of truth when onboarding new tenants or mapping files.

## 2. Scope and structure
- Covers the canonical business concepts (logical fields) used by validation rules.
- Describes how tenant-specific files map into those logical fields.
- Lists common dataset types and their required sheets/columns.
- Highlights data quality signals (formats, ranges) that rules will rely on.

Out of scope:
- Low-level database schema or ORM models (handled during implementation).
- Analytics/reporting warehouse structures (covered later in reporting spec).

## 3. Canonical datasets

### 3.1 Billing transactions
- **Purpose:** Records customer billing activity by period.
- **Required logical fields:** `BillingPeriod`, `CustomerId`, `InvoiceNumber`, `GrossAmount`, `TaxAmount`, `NetAmount`, `Currency`, `BillingStatus`.
- **Typical file structure:** Worksheet `Billing`, columns for invoice meta plus amounts.
- **Key rules rely on:** Presence of all monetary fields, currency format, net amount = gross - tax.

### 3.2 Payment receipts
- **Purpose:** Tracks payments received against invoices.
- **Required logical fields:** `PaymentDate`, `CustomerId`, `InvoiceNumber`, `PaymentMethod`, `PaymentAmount`, `Currency`.
- **Typical file structure:** Worksheet `Payments`, columns aligning with invoice references.
- **Key rules rely on:** Payment amount formats, invoice cross-reference, date ranges.

### 3.3 Customer master
- **Purpose:** Provides reference data for customers linked to billing and payments.
- **Required logical fields:** `CustomerId`, `CustomerName`, `Segment`, `Region`, `Status`, `ActivationDate`.
- **Typical file structure:** Worksheet `Customers` with unique IDs.
- **Key rules rely on:** Customer status validation, region codes, activation date presence.

## 4. Logical field dictionary
| Field name | Description | Data type | Allowed values / format | Notes |
| ---------- | ----------- | --------- | ----------------------- | ----- |
| `BillingPeriod` | Period the invoice covers | `string` | `YYYY-MM` or `YYYYMM` | Configurable per tenant; default monthly. |
| `CustomerId` | Unique customer identifier | `string` | Alphanumeric, length ≤ 20 | Required for joins across datasets. |
| `InvoiceNumber` | Invoice reference | `string` | Tenant-specific format | Must be unique per billing period. |
| `GrossAmount` | Invoice total before tax | `decimal` | >= 0, two decimal places | Cross-check with `TaxAmount`. |
| `TaxAmount` | Tax charged | `decimal` | >= 0, two decimal places | Optional if zero tax; still captured. |
| `NetAmount` | Gross - tax | `decimal` | >= 0, two decimal places | System rule verifies arithmetic. |
| `Currency` | Currency code | `string` | ISO 4217 (e.g., `USD`) | Tenant-specific whitelist allowed. |
| `BillingStatus` | Invoice state | `string` | `draft`, `issued`, `paid`, `void` | Localized labels can map to these states. |
| `PaymentDate` | Payment posting date | `date` | ISO 8601 (`YYYY-MM-DD`) | Time zone defaults to tenant locale. |
| `PaymentMethod` | How payment was made | `string` | `ACH`, `Wire`, `Card`, `Cash`, `Other` | Expandable via tenant mapping. |
| `PaymentAmount` | Amount received | `decimal` | >= 0, two decimal places | Must balance to invoices over time. |
| `Segment` | Customer grouping | `string` | `Retail`, `Wholesale`, `Enterprise`, etc. | Configurable list per tenant. |
| `Region` | Geographic area | `string` | ISO country or internal region codes | Normalized for reporting. |
| `Status` | Customer lifecycle state | `string` | `active`, `inactive`, `prospect`, etc. | Hard rules may require `active`. |
| `ActivationDate` | When customer became active | `date` | ISO 8601 | Used for recency checks. |

### 4.1 Derived or calculated fields
- `NetTransactionAmount = GrossAmount - TaxAmount - Discounts`
- `OutstandingBalance = NetAmount - AppliedPayments`
- `DaysPastDue = Today - DueDate`

Rules may compute these at runtime if tenants do not supply them. Configurations must define formula components and fallback values.

## 5. Data cleansing rule catalog

### 5.1 Canonical cleansing rule object
- `rule_id`: Unique identifier (UUID string).
- `name`: Human-readable label.
- `dataset_type`: Applies to a specific canonical dataset (e.g., `billing`, `payments`).
- `version`: Semantic version string managed independently from validation rules.
- `transformations`: Ordered list of transformation steps. Each step includes:
  - `type`: Transformation keyword (`standardize`, `deduplicate`, `normalize_field`, `enrich_lookup`, `drop_records`).
  - `target_fields`: Logical field names affected by the step.
  - `parameters`: Key/value map configuring the behaviour (e.g., `format`, `lookup_table`, `dedupe_keys`).
  - `condition`: Optional expression describing when to apply the step.
  - `severity`: `hard` removes or rejects records, `soft` logs warnings while retaining data.
- `audit_tags`: Metadata emitted with each run (e.g., `{"source": "system", "purpose": "pre-validation"}`).

### 5.2 Example cleansing rule snippet
```json
{
  "rule_id": "cln-billing-standardisation",
  "name": "Billing dataset standardisation",
  "dataset_type": "billing",
  "version": "2024.06.01",
  "transformations": [
    {
      "type": "standardize",
      "target_fields": ["Currency"],
      "parameters": {
        "format": "ISO-4217",
        "default_currency": "tenant_default"
      }
    },
    {
      "type": "deduplicate",
      "target_fields": ["InvoiceNumber"],
      "parameters": {
        "keys": ["InvoiceNumber", "BillingPeriod"],
        "retain": "latest"
      },
      "severity": "hard"
    },
    {
      "type": "fill_missing",
      "target_fields": ["CustomerId"],
      "parameters": {
        "lookup": "customer_master",
        "on_failure": "reject"
      }
    }
  ]
}
```

### 5.3 Typical cleansing transformations
- **Standardise formats:** Normalise date, currency, and code values to canonical formats before validation.
- **Deduplicate:** Remove duplicate records based on configurable keys; supports retaining earliest or latest record.
- **Fill or enrich:** Populate missing values using reference datasets or default expressions.
- **Split and merge:** Reshape columns (e.g., split concatenated fields) to match logical field expectations.
- **Reject with reason:** Flag and quarantine records that cannot be transformed safely; metadata layer records reason codes.

## 6. Mapping templates

### 6.1 Required columns for Billing dataset
| Logical field | File column example | Transform |
| ------------- | ------------------- | --------- |
| `BillingPeriod` | `Month` | Parse `MM/YYYY` to `YYYY-MM`. |
| `CustomerId` | `Customer Number` | Strip whitespace. |
| `InvoiceNumber` | `Invoice` | Direct copy. |
| `GrossAmount` | `Amount` | Convert to decimal, 2 places. |
| `TaxAmount` | `VAT` | Convert to decimal; default 0 if blank. |
| `NetAmount` | (derived) | `GrossAmount - TaxAmount`. |
| `Currency` | `Currency` | Uppercase 3-letter code. |
| `BillingStatus` | `Status` | Map local labels to canonical values. |

### 6.2 Mapping guidance
- Each tenant supplies a mapping file or uses the admin UI to align their column names to logical fields.
- Mappings must specify data type conversion rules and default values if the source column is missing.
- Configurations log the author, date, and version comment for traceability.
- System should validate mapped columns exist in uploaded files and raise warnings when optional fields are missing.

## 7. Data validation signals
- **Formats:** Currency fields must use decimal separators consistent with locale; dates must be ISO or convertible via mapping rules.
- **Ranges:** Monetary values should fall within tenant-defined ranges (e.g., -1,000 to 1,000,000). Negative values require explicit approval rules.
- **Uniqueness:** `InvoiceNumber` must be unique per tenant and billing period; duplicates flagged as hard failures.
- **Referential integrity:** Payments must reference existing invoices and customers.
- **Completeness:** Mandatory fields per dataset cannot be blank; soft rules may allow single blanks with warnings.
- **Derived accuracy:** Derived fields must match recomputed values; mismatches flagged for review.

## 8. Tenant onboarding checklist
- Gather sample billing, payment, and customer files.
- Identify column names, formats, and quirks (e.g., multiple sheets, locale differences).
- Complete mapping template with logical field links and transformation rules.
- Define tenant-specific value whitelists (currencies, segments).
- Confirm retention and privacy constraints for the tenant’s data.

## 9. Acceptance checkpoints
- Mapping templates validated against sample files without errors.
- Rule engine can execute a smoke test using the canonical datasets.
- Documentation updated when new logical fields or datasets are introduced.

## 10. Open questions
- Additional domain-specific datasets (e.g., adjustments, credits) needed for MVP?
- Minimum data sample size required before onboarding a tenant.
- Whether tenants can define custom derived fields beyond the baseline set.
- Localization handling for multi-language column headers.
