# ATL Entry — Apache Kafka on AWS MSK

**Synthetic demo document.**

| Field | Value |
| --- | --- |
| **Status** | APPROVED (with conditions) |
| **ATL ID** | ATL-2024-MSG-0006 |
| **Approved version range** | Kafka 3.5.x – 3.7.x on MSK |
| **Deployment model** | AWS MSK provisioned (not serverless) for production workloads |
| **Data classifications permitted** | Internal, Confidential. NOT approved for in-flight client funds messages. |
| **Owner** | Streaming Platform Team |

## Conditions

1. mTLS authentication required between producers/consumers and brokers.
2. ACL-based authorization; no anonymous access.
3. KMS encryption at rest. TLS in transit.
4. Multi-AZ broker deployment (minimum 3 brokers across 3 AZs).
5. Schema Registry usage required for all topics carrying structured data.
6. Topic-level retention max 30 days unless documented exception filed.

## Non-approved alternatives

- **MSK Serverless**: NOT on ATL. Capacity-management concerns for our workload patterns.
- **Self-managed Kafka on EC2**: NOT on ATL. Removed from ATL 2024-Q2; existing deployments grandfathered to 2026-12-31.
- **Confluent Cloud**: Pending vendor risk review. Do not adopt until ATL entry posted.
