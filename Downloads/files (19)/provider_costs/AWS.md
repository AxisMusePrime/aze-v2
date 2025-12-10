# AWS — Cost Estimates (Minimal / Production)

Minimal (small deployment, serverless preferred)
- AWS S3 (static assets): $0.50 - $5/month (very small)
- AWS Lambda (infrequent Python tasks): $0 - $5/month depending on invocations
- API Gateway (if used): $3 - $20/month
- Route53 (DNS): $1 - $1.50/month
- Backup (S3 IA or Glacier for archival): $1 - $10/month

Estimated monthly (minimal): $6 - $40

Production
- EC2 instances (t2.micro/t3.small or larger): $10 - $80 per instance
- RDS managed database: $15 - $200+ depending on size
- Elastic Load Balancer: $18+ per month
- CloudWatch (logs/metrics): $10 - $200
- S3 storage & data transfer: variable

Estimated monthly (prod): $200 - $2,000+

Notes:
- AWS offers granular pricing; serverless can be very cheap for low traffic.
- Consider AWS Lightsail for simplified pricing tiers.
