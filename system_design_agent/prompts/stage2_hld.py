"""
Prompts for Stage 2: High-Level Design (HLD).
"""

STAGE2_PROMPT_TEMPLATE = """You are acting in Stage 2 of the Technical Specification pipeline.
Given the Project Pitch and Section 1 Requirements, generate Section 2: High-Level Design (HLD).

Project Pitch:
\"\"\"{pitch}\"\"\"

Section 1 Context:
\"\"\"{stage1_context}\"\"\"

Required Output Structure:
### 2. High-Level Design (HLD)

#### Architectural Paradigm
- Chosen pattern (e.g., Modular Monolith with Asynchronous Broker, Event-Driven Architecture, Microservices).
- Concrete rationale detailing why this exact architecture fits this stage and scale (~{target_dau:,} DAU).

#### Component Topology Diagram
A valid, renderable Mermaid `graph TD` diagram illustrating:
- Client (Web/Mobile)
- API Gateway / Reverse Proxy
- Core Application Services
- In-Memory Cache (e.g., Redis)
- Message Broker / Task Queue (e.g., Redis Streams / RabbitMQ / Kafka)
- Persistent Storage (e.g., PostgreSQL Primary + Read Replica)
- Object Storage / External Services (if applicable)

Important Mermaid Rules:
- Only use `graph TD` or `flowchart TD`.
- Enclose node labels in double quotes if they contain parentheses, slashes, or special symbols (e.g., `App["Core API (FastAPI)"]`).
- No trailing semicolons or malformed arrows.

#### Technology Stack Matrix
A concise markdown table covering:
- Runtime / Language
- Web / API Framework
- Primary Database
- Cache / Message Broker
- Infrastructure / Hosting (e.g., AWS ECS/EKS, RDS Multi-AZ, S3, CloudFront)
Include a concise, 1-sentence trade-off rationale for each choice.

#### Cloud Infrastructure & Network Topology
- Cloud Provider Mapping (AWS, GCP, or Azure):
  - Network Boundary: VPC CIDR block, Public Subnets (ALB, NAT Gateways), Private Application Subnets (Containers/Compute), and Isolated Data Subnets (RDS, Redis).
  - Compute & Orchestration: Managed container platform (e.g., AWS ECS Fargate, GCP Cloud Run, or Kubernetes EKS/GKE) with target CPU/Memory allocations.
  - Security & IAM: IAM roles with least-privilege, AWS Secrets Manager / GCP Secret Manager for credentials, KMS encryption keys.
  - High Availability & Multi-AZ: Multi-AZ database replication, auto-scaling thresholds (target 70% CPU or queue backlog).

Output format: Return ONLY the GitHub-flavored markdown for Section 2.
"""
