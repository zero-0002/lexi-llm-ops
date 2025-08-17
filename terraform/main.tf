terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Cập nhật phiên bản mới
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"  # Cập nhật phiên bản mới

  name = "${var.cluster_name}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = var.vpc_private_subnets
  public_subnets  = var.vpc_public_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = true
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # Tags for EKS
  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    Project = "legal-chatbot"
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
}

# EKS Module
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"  # Phiên bản mới nhất

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  # OIDC Identity provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }

  # Cluster access entry
  enable_cluster_creator_admin_permissions = true

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    general = {
      name           = "general"
      use_name_prefix = false

      subnet_ids = module.vpc.private_subnets

      min_size     = var.general_min_size
      max_size     = var.general_max_size
      desired_size = var.general_desired_size

      ami_type       = "AL2_x86_64"
      instance_types = var.general_instance_types

      k8s_labels = {
        Environment = "production"
        NodeType    = "general"
      }

      update_config = {
        max_unavailable_percentage = 33
      }

      tags = {
        Name = "${var.cluster_name}-general"
        NodeType = "general"
      }
    }

    embedding = {
      name           = "embedding"
      use_name_prefix = false

      subnet_ids = module.vpc.private_subnets

      min_size     = var.embedding_min_size
      max_size     = var.embedding_max_size
      desired_size = var.embedding_desired_size

      ami_type       = "AL2_x86_64"
      instance_types = var.embedding_instance_types

      k8s_labels = {
        Environment = "production"
        NodeType    = "embedding"
      }

      taints = [
        {
          key    = "workload"
          value  = "embedding"
          effect = "NO_SCHEDULE"
        }
      ]

      update_config = {
        max_unavailable_percentage = 50
      }

      tags = {
        Name = "${var.cluster_name}-embedding"
        NodeType = "embedding"
      }
    }
  }

  tags = {
    Environment = "production"
    Project     = "legal-chatbot"
  }

}