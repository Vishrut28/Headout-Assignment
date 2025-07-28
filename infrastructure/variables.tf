# Variable definitions for Terraform configuration

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "AWS region must be in the format like 'us-east-1'."
  }
}

variable "environment" {
  description = "Environment name (staging, production, development)"
  type        = string
  default     = "staging"
  
  validation {
    condition = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "java-app-deployment"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# EC2 Configuration
variable "instance_type" {
  description = "EC2 instance type for ECS tasks"
  type        = string
  default     = "t3.medium"
  
  validation {
    condition = can(regex("^[a-z][0-9][a-z]*\\.[a-z]+$", var.instance_type))
    error_message = "Instance type must be a valid EC2 instance type."
  }
}

# Auto Scaling Configuration
variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 2
  
  validation {
    condition = var.min_capacity >= 1
    error_message = "Minimum capacity must be at least 1."
  }
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
  
  validation {
    condition = var.max_capacity >= var.min_capacity
    error_message = "Maximum capacity must be greater than or equal to minimum capacity."
  }
}

variable "desired_capacity" {
  description = "Desired number of tasks"
  type        = number
  default     = 3
}

# Load Balancer Configuration
variable "health_check_path" {
  description = "Health check path for the load balancer"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 10
}

variable "healthy_threshold" {
  description = "Number of consecutive successful health checks"
  type        = number
  default     = 2
}

variable "unhealthy_threshold" {
  description = "Number of consecutive failed health checks"
  type        = number
  default     = 3
}

# ECS Configuration
variable "cpu_units" {
  description = "CPU units for ECS task (1024 = 1 vCPU)"
  type        = number
  default     = 1024
  
  validation {
    condition = contains([256, 512, 1024, 2048, 4096], var.cpu_units)
    error_message = "CPU units must be one of: 256, 512, 1024, 2048, 4096."
  }
}

variable "memory_mb" {
  description = "Memory in MB for ECS task"
  type        = number
  default     = 2048
  
  validation {
    condition = var.memory_mb >= 512
    error_message = "Memory must be at least 512 MB."
  }
}

# Logging Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
  
  validation {
    condition = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

# Security Configuration
variable "enable_deletion_protection" {
  description = "Enable deletion protection for load balancer (recommended for production)"
  type        = bool
  default     = false
}

variable "enable_access_logs" {
  description = "Enable ALB access logs"
  type        = bool
  default     = true
}

variable "enable_container_insights" {
  description = "Enable container insights for ECS cluster"
  type        = bool
  default     = true
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid CIDR block."
  }
}

variable "availability_zones_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 3
  
  validation {
    condition = var.availability_zones_count >= 2 && var.availability_zones_count <= 6
    error_message = "Availability zones count must be between 2 and 6."
  }
}

# Application Configuration
variable "application_port" {
  description = "Port on which the Java application listens"
  type        = number
  default     = 9000
  
  validation {
    condition = var.application_port > 0 && var.application_port < 65536
    error_message = "Application port must be between 1 and 65535."
  }
}

variable "java_opts" {
  description = "Java JVM options"
  type        = string
  default     = "-Xmx1536m -Xms512m -XX:+UseG1GC"
}

# Monitoring and Alerting
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "cpu_utilization_threshold" {
  description = "CPU utilization threshold for auto scaling"
  type        = number
  default     = 70
  
  validation {
    condition = var.cpu_utilization_threshold >= 10 && var.cpu_utilization_threshold <= 90
    error_message = "CPU utilization threshold must be between 10 and 90."
  }
}

variable "memory_utilization_threshold" {
  description = "Memory utilization threshold for auto scaling"
  type        = number
  default     = 80
  
  validation {
    condition = var.memory_utilization_threshold >= 10 && var.memory_utilization_threshold <= 95
    error_message = "Memory utilization threshold must be between 10 and 95."
  }
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Repository Configuration
variable "repository_url" {
  description = "GitHub repository URL (SSH format)"
  type        = string
  default     = "git@github.com:example/project.git"
}

variable "repository_branch" {
  description = "Git branch to deploy"
  type        = string
  default     = "main"
}

# SSL/TLS Configuration
variable "certificate_arn" {
  description = "ARN of SSL certificate for HTTPS listener (optional)"
  type        = string
  default     = ""
}

variable "enable_https_redirect" {
  description = "Enable automatic HTTPS redirect"
  type        = bool
  default     = false
}