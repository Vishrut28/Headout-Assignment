# Java Application Deployment Automation

## Overview

This project provides a comprehensive DevOps solution for automating the deployment of Java applications from GitHub repositories to AWS infrastructure. The solution includes deployment scripts, containerization, CI/CD pipelines, and infrastructure as code.

## 🏗️ Architecture

The solution implements a modern, scalable architecture:

- **Application Load Balancer (ALB)** for traffic distribution
- **Amazon ECS Fargate** for container orchestration
- **Auto Scaling** for dynamic capacity management
- **Amazon ECR** for container registry
- **CloudWatch** for monitoring and logging
- **GitHub Actions** for CI/CD automation
- **Terraform** for infrastructure as code

## 📁 Project Structure

```
├── deploy.py                    # Main deployment script
├── Dockerfile                   # Container configuration
├── .github/workflows/deploy.yml # CI/CD pipeline
├── infrastructure/              # Terraform infrastructure code
│   ├── main.tf                 # Main infrastructure configuration
│   ├── variables.tf            # Variable definitions
│   └── outputs.tf              # Output values
├── tests/                      # Test files
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker
- AWS CLI configured
- Terraform 1.6+
- Git with SSH access to GitHub

### Local Deployment

1. **Clone and start application locally:**
   ```bash
   python3 deploy.py \
     --repo-url "git@github.com:your-org/your-repo.git" \
     --repo-name "your-repo" \
     --branch "main"
   ```

2. **Using Docker:**
   ```bash
   docker build -t java-app-deployment .
   docker run -d \
     -e REPO_URL="git@github.com:your-org/your-repo.git" \
     -e REPO_NAME="your-repo" \
     -v ~/.ssh:/secrets:ro \
     -p 9000:9000 \
     java-app-deployment
   ```

### AWS Deployment

1. **Deploy infrastructure:**
   ```bash
   cd infrastructure/
   terraform init
   terraform plan -var="environment=staging"
   terraform apply
   ```

2. **Deploy via GitHub Actions:**
   - Push code to `main` branch for production
   - Push to `develop` branch for staging
   - Use workflow dispatch for manual deployments

## 🛠️ Components

### 1. Deployment Script (`deploy.py`)

**Purpose:** Automates the process of cloning a GitHub repository and starting a Java application.

**Features:**
- SSH-based Git cloning with authentication
- Comprehensive error handling and logging
- Java process management with health checks
- Port availability verification
- Graceful shutdown handling
- Process monitoring and alerting

**Error Handling:**
- **SSH Connection Failures:** Validates SSH keys and GitHub connectivity
- **Repository Access:** Handles authentication and network issues
- **JAR File Issues:** Searches for alternative JAR locations
- **Port Conflicts:** Automatically terminates conflicting processes
- **Process Crashes:** Monitors application health and restarts if needed

**Logging:**
- **INFO:** Successful operations and progress updates
- **WARNING:** Non-critical issues that don't stop deployment
- **ERROR:** Critical failures that require attention
- **DEBUG:** Detailed information for troubleshooting

### 2. Dockerfile

**Base Image:** Amazon Corretto 17 Alpine (AWS optimized)

**Key Features:**
- Multi-stage build for minimal production image
- Security best practices (non-root user)
- Health checks and monitoring
- SSH key management for GitHub access
- Optimized for EC2 deployment

**Security Considerations:**
- Minimal attack surface using Alpine Linux
- SSH keys mounted as secrets (not baked into image)
- Non-root execution (when SSH access isn't required)
- Regular vulnerability scanning

### 3. CI/CD Pipeline (`.github/workflows/deploy.yml`)

**Stages:**
1. **Security Scan:** Trivy vulnerability scanning
2. **Build & Test:** Code quality checks and testing
3. **Docker Build:** Multi-platform container builds
4. **Deploy Staging:** Automated staging deployment
5. **Deploy Production:** Manual approval with blue-green deployment
6. **Rollback:** Automated rollback capability

**Features:**
- Branch-based deployment strategy
- Manual approval for production
- Comprehensive health checks
- Slack notifications
- Artifact management

### 4. Infrastructure (Terraform)

**AWS Resources Created:**

#### Application Load Balancer Configuration

**Parameters Set:**
- **Load Balancer Type:** Application (Layer 7) for HTTP/HTTPS routing
- **Internet-facing:** Public accessibility
- **Cross-zone Load Balancing:** Enabled for even distribution
- **HTTP/2:** Enabled for performance
- **Access Logs:** Enabled for monitoring and debugging
- **Security Groups:** Restrictive ingress (80/443) with full egress

**Parameters Not Set (and why):**
- **SSL Certificate:** Not configured by default (requires domain setup)
- **WAF Integration:** Not included (adds complexity and cost for basic deployment)
- **Custom Domain:** Uses AWS-generated DNS name for simplicity

#### Target Group Configuration

**Health Check Parameters:**
- **Path:** `/health` (assumes Spring Boot Actuator or similar)
- **Interval:** 30 seconds (balance between responsiveness and resource usage)
- **Timeout:** 10 seconds (sufficient for most applications)
- **Healthy Threshold:** 2 checks (quick recovery)
- **Unhealthy Threshold:** 3 checks (avoid false positives)
- **Protocol:** HTTP (suitable for most Java web applications)

**Why These Settings:**
- **30s interval:** Standard AWS recommendation, good balance
- **10s timeout:** Generous for network latency
- **2/3 thresholds:** Quick recovery while avoiding flapping

#### Auto Scaling Configuration

**CPU Scaling:**
- **Target:** 70% utilization
- **Metric:** ECS Service Average CPU
- **Policy Type:** Target Tracking

**Memory Scaling:**
- **Target:** 80% utilization  
- **Metric:** ECS Service Average Memory
- **Policy Type:** Target Tracking

**Why These Thresholds:**
- **CPU 70%:** Allows headroom for traffic spikes
- **Memory 80%:** Higher threshold as memory is more predictable
- **Target Tracking:** Automatically adjusts capacity smoothly

#### ECS Configuration

**Fargate Settings:**
- **CPU:** 1024 units (1 vCPU)
- **Memory:** 2048 MB (2 GB)
- **Network Mode:** awsvpc (required for Fargate)

**Service Configuration:**
- **Desired Count:** 3 (multi-AZ deployment)
- **Deployment:** Rolling update with circuit breaker
- **Service Discovery:** Enabled for internal communication

## 🔒 Security Considerations

### Network Security
- Private subnets for application containers
- Security groups with minimal required access
- VPC isolation with NAT gateways for outbound access

### Container Security
- Non-root user execution where possible
- SSH keys managed as secrets (not in container images)
- Regular vulnerability scanning with Trivy
- Minimal base images (Alpine Linux)

### Access Management
- IAM roles with least privilege principles
- Secrets Manager for sensitive data
- No hardcoded credentials in code or containers

## 📊 Monitoring and Logging

### CloudWatch Integration
- **Container Insights:** Enabled for detailed metrics
- **Log Aggregation:** Centralized logging for all containers
- **Custom Metrics:** Application-specific monitoring
- **Alarms:** Automated alerting for critical issues

### Health Checks
- **Load Balancer:** HTTP health checks on `/health`
- **Container:** Docker health check script
- **Application:** Spring Boot Actuator integration (if available)

## 🚨 Failure Scenarios and Handling

### Common Failure Points

1. **SSH Authentication Failures**
   - **Detection:** SSH connection test during deployment
   - **Handling:** Clear error messages with setup instructions
   - **Recovery:** Manual SSH key configuration required

2. **Repository Access Issues**
   - **Detection:** Git clone failures with specific error codes
   - **Handling:** Retry logic with exponential backoff
   - **Recovery:** Check repository permissions and SSH keys

3. **JAR File Not Found**
   - **Detection:** File existence checks after clone
   - **Handling:** Search for alternative JAR files in repository
   - **Recovery:** Use found JAR files or fail with clear message

4. **Port Already in Use**
   - **Detection:** Port availability check before starting application
   - **Handling:** Attempt to terminate existing processes
   - **Recovery:** Force kill if graceful termination fails

5. **Application Startup Failures**
   - **Detection:** Process monitoring and health checks
   - **Handling:** Capture stdout/stderr for debugging
   - **Recovery:** Automatic restart with backoff strategy

6. **Infrastructure Failures**
   - **Detection:** Terraform state monitoring and AWS API responses
   - **Handling:** Automatic rollback for failed deployments
   - **Recovery:** Circuit breaker pattern for repeated failures

### Logging Strategy

**Log Levels:**
- **ERROR:** Critical failures requiring immediate attention
- **WARN:** Issues that don't stop operation but need monitoring
- **INFO:** Normal operation status and milestones
- **DEBUG:** Detailed troubleshooting information (disabled in production)

**Log Destinations:**
- **Local Files:** `deployment.log` for script execution
- **CloudWatch:** Centralized logging for container applications
- **ALB Logs:** Access patterns and performance metrics

## 🎯 Assumptions and Decisions

### Technical Assumptions

1. **Java Application Structure**
   - JAR file located at `build/libs/project.jar`
   - Application listens on port 9000
   - Health endpoint available at `/health`
   - Standard Spring Boot application structure

2. **GitHub Repository**
   - SSH access configured and functional
   - Repository contains buildable Java project
   - Main/develop branch strategy for deployments
   - Secrets and configuration externalized

3. **AWS Environment**
   - AWS CLI configured with appropriate permissions
   - ECR repository access for image storage
   - VPC and networking resources can be created
   - S3 bucket for Terraform state management exists

### Design Decisions

1. **Container Orchestration: ECS Fargate**
   - **Why:** Serverless container management, no EC2 management overhead
   - **Alternative Considered:** EKS (too complex for this use case)
   - **Trade-off:** Less control over underlying infrastructure

2. **Load Balancer: Application Load Balancer**
   - **Why:** Layer 7 routing, better health checks, AWS integration
   - **Alternative Considered:** Network Load Balancer (Layer 4)
   - **Trade-off:** Higher cost but better features for web applications

3. **Infrastructure as Code: Terraform**
   - **Why:** Cloud-agnostic, mature, good state management
   - **Alternative Considered:** CloudFormation (AWS-specific)
   - **Trade-off:** Additional tool complexity vs. vendor lock-in

4. **Base Image: Amazon Corretto Alpine**
   - **Why:** AWS optimized, lightweight, security updates
   - **Alternative Considered:** OpenJDK (less optimized for AWS)
   - **Trade-off:** AWS ecosystem lock-in vs. optimization

5. **Auto Scaling Thresholds**
   - **CPU: 70%** - Conservative to handle traffic spikes
   - **Memory: 80%** - More aggressive as memory usage is predictable
   - **Alternative:** Custom metrics (requires application instrumentation)

## 🧪 Testing

### Automated Testing
- Unit tests for deployment script functions
- Dockerfile linting with Hadolint
- Terraform validation and planning
- Security scanning with Trivy

### Manual Testing Steps
1. Deploy to staging environment
2. Verify application health endpoints
3. Test auto-scaling behavior under load
4. Validate logging and monitoring
5. Test rollback procedures

## 🚀 Production Readiness Checklist

- [ ] SSH keys configured in Secrets Manager
- [ ] Custom domain and SSL certificate
- [ ] Production database connections
- [ ] Monitoring alerts configured
- [ ] Backup and disaster recovery procedures
- [ ] Security audit completed
- [ ] Performance testing under load
- [ ] Documentation updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create GitHub issues for bugs
- Use discussions for questions
- Check CloudWatch logs for debugging
- Review Terraform state for infrastructure issues

---

**Note:** This solution is designed as a production-ready template but may require customization for specific use cases and security requirements.