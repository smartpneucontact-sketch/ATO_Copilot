# ATL Entry — PostgreSQL on AWS RDS (managed)

**Synthetic demo document. Not an actual State Street ATL record.**

| Field | Value |
| --- | --- |
| **Status** | APPROVED |
| **ATL ID** | ATL-2024-DB-0017 |
| **Approved version range** | 14.x, 15.x, 16.x (major-version uplift inherits approval per ATL-POL-04) |
| **Deployment model** | AWS RDS managed, single-region with cross-region read replica required for Tier 1 apps |
| **Data classifications permitted** | Internal, Confidential. PII / PCI / client funds data require additional InfoSec sign-off. |
| **Last reviewed** | 2026-01-15 |
| **Next review** | 2027-01-15 |
| **Owner** | Cloud Data Platform Team |

## Conditions of use

1. **Encryption at rest**: AWS KMS Customer-Managed Key (CMK) required; rotation per crypto standard (≤ 365 days).
2. **Encryption in transit**: TLS 1.2 minimum. Certificate via AWS Private CA.
3. **IAM**: RDS IAM authentication for application accounts; password-based access prohibited for non-break-glass identities.
4. **Backup**: Automated backups, 35-day retention. Point-in-time recovery enabled.
5. **Multi-AZ**: Required for Tier 1 / Tier 2 applications.
6. **Monitoring**: Enhanced Monitoring + Performance Insights enabled. Logs to CloudWatch + Splunk forwarder.
7. **Network**: Deployed in approved VPC + subnet group. No public endpoints.

## Notes

- Major-version uplifts within the approved range (e.g., 14 → 16) do not require a fresh ATO.
- Extension installations beyond the AWS-approved list require InfoSec review.
- For Aurora-PostgreSQL, see separate ATL entry ATL-2024-DB-0019.
