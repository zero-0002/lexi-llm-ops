variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "legal-chatbot-cluster"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

# VPC Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_private_subnets" {
  description = "Private subnets CIDR"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "vpc_public_subnets" {
  description = "Public subnets CIDR"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# Node Group Variables
variable "general_instance_types" {
  description = "Instance types for general node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "general_min_size" {
  description = "Minimum number of nodes in general group"
  type        = number
  default     = 1
}

variable "general_max_size" {
  description = "Maximum number of nodes in general group"
  type        = number
  default     = 3
}

variable "general_desired_size" {
  description = "Desired number of nodes in general group"
  type        = number
  default     = 1
}

variable "embedding_instance_types" {
  description = "Instance types for embedding node group"
  type        = list(string)
  default     = ["c5.large"]
}

variable "embedding_min_size" {
  description = "Minimum number of nodes in embedding group"
  type        = number
  default     = 1
}

variable "embedding_max_size" {
  description = "Maximum number of nodes in embedding group"
  type        = number
  default     = 2
}

variable "embedding_desired_size" {
  description = "Desired number of nodes in embedding group"
  type        = number
  default     = 1
}