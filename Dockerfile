# Multi-stage Dockerfile for Java Application Deployment
# Optimized for EC2 deployment with minimal footprint

# Build stage - Use Amazon Corretto as base image (AWS recommended)
FROM amazoncorretto:17-alpine AS builder

# Set working directory
WORKDIR /app

# Install required packages for build
RUN apk add --no-cache \
    git \
    openssh-client \
    python3 \
    py3-pip \
    bash \
    curl \
    && rm -rf /var/cache/apk/*

# Install Python dependencies for deployment script
RUN pip3 install --no-cache-dir \
    psutil \
    requests

# Copy deployment script and make it executable
COPY deploy.py /app/deploy.py
RUN chmod +x /app/deploy.py

# Create SSH directory and set permissions
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Add GitHub to known hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Production stage - Minimal runtime image
FROM amazoncorretto:17-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    bash \
    curl \
    python3 \
    py3-pip \
    git \
    openssh-client \
    procps \
    && rm -rf /var/cache/apk/*

# Install Python runtime dependencies
RUN pip3 install --no-cache-dir \
    psutil \
    requests

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -h /app -s /sbin/nologin -G appuser appuser

# Set working directory
WORKDIR /app

# Copy deployment script from builder stage
COPY --from=builder /app/deploy.py /app/deploy.py
RUN chmod +x /app/deploy.py

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Copy SSH configuration setup script
COPY <<EOF /app/setup-ssh.sh
#!/bin/bash
set -e

# Create SSH directory
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Copy SSH key from environment or mounted volume
if [ -f "/secrets/ssh_key" ]; then
    cp /secrets/ssh_key /root/.ssh/id_rsa
    chmod 600 /root/.ssh/id_rsa
elif [ ! -z "\$SSH_PRIVATE_KEY" ]; then
    echo "\$SSH_PRIVATE_KEY" > /root/.ssh/id_rsa
    chmod 600 /root/.ssh/id_rsa
else
    echo "Warning: No SSH key found. Please mount SSH key at /secrets/ssh_key or set SSH_PRIVATE_KEY environment variable"
fi

# Add GitHub to known hosts
ssh-keyscan github.com >> /root/.ssh/known_hosts

echo "SSH setup completed"
EOF

RUN chmod +x /app/setup-ssh.sh

# Create health check script
COPY <<EOF /app/health-check.sh
#!/bin/bash
set -e

# Check if application is running on port 9000
if curl -f http://localhost:9000/health > /dev/null 2>&1; then
    echo "Application is healthy"
    exit 0
else
    # Alternative check - test if port is listening
    if nc -z localhost 9000; then
        echo "Application is running (port check)"
        exit 0
    else
        echo "Application is not healthy"
        exit 1
    fi
fi
EOF

RUN chmod +x /app/health-check.sh

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

echo "Starting application deployment..."

# Setup SSH
/app/setup-ssh.sh

# Set default values
REPO_URL=\${REPO_URL:-"git@github.com:example/project.git"}
REPO_NAME=\${REPO_NAME:-"project"}
BRANCH=\${BRANCH:-"main"}
MONITOR_DURATION=\${MONITOR_DURATION:-300}

# Run deployment
python3 /app/deploy.py \
    --repo-url "\$REPO_URL" \
    --repo-name "\$REPO_NAME" \
    --branch "\$BRANCH" \
    --monitor "\$MONITOR_DURATION"
EOF

RUN chmod +x /app/start.sh

# Expose port 9000
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh

# Set environment variables
ENV REPO_URL=""
ENV REPO_NAME=""
ENV BRANCH="main"
ENV MONITOR_DURATION=300
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Create volume for SSH keys
VOLUME ["/secrets"]

# Switch to non-root user for security (commented out for SSH access)
# USER appuser

# Set entrypoint
ENTRYPOINT ["/app/start.sh"]

# Metadata
LABEL maintainer="DevOps Engineer" \
      description="Java Application Deployment Container" \
      version="1.0" \
      java.version="17" \
      org.opencontainers.image.source="https://github.com/example/project"