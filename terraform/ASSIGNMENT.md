# Terraform Assignment: AWS Infrastructure with Remote State

**Name:** Fakhir Hassan
**Date:** March 30, 2026
**Topic:** Terraform — EC2, S3, Workspaces & Remote State with S3 + DynamoDB Locking

---

## Table of Contents

1. [Prerequisites & Installation](#1-prerequisites--installation)
2. [AWS CLI Configuration](#2-aws-cli-configuration)
3. [Step 1: Creating a Simple EC2 Instance](#3-step-1-creating-a-simple-ec2-instance)
4. [Step 2: Using Variables (Best Practices)](#4-step-2-using-variables-best-practices)
5. [Step 3: Adding S3 Bucket, Workspaces & Resource Dependencies](#5-step-3-adding-s3-bucket-workspaces--resource-dependencies)
6. [Step 4: Remote State with S3 & DynamoDB Locking](#6-step-4-remote-state-with-s3--dynamodb-locking)
7. [IAM Permissions Required](#7-iam-permissions-required)
8. [Final Folder Structure](#8-final-folder-structure)

---

## 1. Prerequisites & Installation

### Install Terraform

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Verify installation:**

```bash
terraform -version
```

**Output:**

```
Terraform v1.x.x
on darwin_arm64
```

### Install AWS CLI

```bash
brew install awscli
```

**Verify installation:**

```bash
aws --version
```

**Output:**

```
aws-cli/2.x.x Python/3.x.x Darwin/25.2.0 source/arm64
```

---

## 2. AWS CLI Configuration

### Create IAM Access Keys

Since the AWS Console UI was giving errors while creating access keys, we used **AWS CloudShell** as an alternative:

```bash
# First, find your username
aws sts get-caller-identity

# Then create access keys
aws iam create-access-key --user-name "fakhir@"
```

**Output:**

```json
{
    "AccessKey": {
        "UserName": "fakhir@",
        "AccessKeyId": "AKIA...",
        "Status": "Active",
        "SecretAccessKey": "xxxxxxxxxxxxxxxxxxxxxxxx",
        "CreateDate": "2026-03-29T..."
    }
}
```

### Configure AWS CLI

```bash
aws configure
```

**Prompts:**

```
AWS Access Key ID [None]: <your-access-key-id>
AWS Secret Access Key [None]: <your-secret-access-key>
Default region name [None]: eu-north-1
Default output format [None]: (press Enter)
```

---

## 3. Step 1: Creating a Simple EC2 Instance

In this step, we created a basic EC2 instance with hardcoded values.

### Directory Setup

```bash
mkdir -p ~/Desktop/DEVOPS/terraform
cd ~/Desktop/DEVOPS/terraform
```

### provider.tf

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}
```

### main.tf

```hcl
resource "aws_instance" "my_ec2" {
  ami           = "ami-080254318c2d8932f"
  instance_type = "t3.small"

  tags = {
    Name = "my-ec2-instance"
  }
}
```

### Running Terraform

```bash
terraform init
```

**Output:**

```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.100.0...
- Installed hashicorp/aws v5.100.0 (signed by HashiCorp)

Terraform has been successfully initialized!
```

```bash
terraform plan
```

**Output:**

```
Terraform will perform the following actions:

  # aws_instance.my_ec2 will be created
  + resource "aws_instance" "my_ec2" {
      + ami                          = "ami-080254318c2d8932f"
      + instance_type                = "t3.small"
      + tags                         = {
          + "Name" = "my-ec2-instance"
        }
      ...
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

```bash
terraform apply
```

**Output:**

```
aws_instance.my_ec2: Creating...
aws_instance.my_ec2: Still creating... [10s elapsed]
aws_instance.my_ec2: Creation complete after 15s [id=i-xxxxxxxxxxxxxxxxx]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

### Error Encountered: IAM Permissions

On first run, we got a `403 UnauthorizedOperation` error because the IAM user didn't have EC2 permissions. This was resolved by attaching the EC2 policy (see [IAM Permissions section](#7-iam-permissions-required)).

---

## 4. Step 2: Using Variables (Best Practices)

Instead of hardcoding values, we moved everything into variables — this is the **industry standard** approach.

### variables.tf

```hcl
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
}
```

### terraform.tfvars

```hcl
aws_region    = "eu-north-1"
ami_id        = "ami-080254318c2d8932f"
instance_type = "t3.small"
instance_name = "my-ec2-instance"
```

### Updated provider.tf

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Updated main.tf

```hcl
resource "aws_instance" "my_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name = var.instance_name
  }
}
```

### outputs.tf

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.my_ec2.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.my_ec2.public_ip
}
```

**Key Takeaway:** All actual values live in `terraform.tfvars`. To change any configuration, you only edit that one file. No hardcoded values in resource definitions.

---

## 5. Step 3: Adding S3 Bucket, Workspaces & Resource Dependencies

### What Are Terraform Workspaces?

Workspaces allow you to manage **multiple environments** (dev, staging, prod) using the **same Terraform code** but with **separate state files**. Each workspace is isolated.

### What is `depends_on`?

`depends_on` forces Terraform to create resources in a specific order. In our case, the S3 bucket is created **before** the EC2 instance.

### Updated variables.tf

```hcl
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "s3_bucket_name" {
  description = "Base name for the S3 bucket"
  type        = string
}
```

### Updated terraform.tfvars

```hcl
aws_region     = "eu-north-1"
ami_id         = "ami-080254318c2d8932f"
instance_type  = "t3.small"
project_name   = "myproject"
s3_bucket_name = "fakhir-terraform-bucket"
```

### Updated main.tf

```hcl
# S3 bucket - created first
resource "aws_s3_bucket" "my_bucket" {
  bucket = "${var.s3_bucket_name}-${terraform.workspace}"

  tags = {
    Name        = "${var.s3_bucket_name}-${terraform.workspace}"
    Environment = terraform.workspace
  }
}

# EC2 instance - created after S3 bucket
resource "aws_instance" "my_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type

  depends_on = [aws_s3_bucket.my_bucket]

  tags = {
    Name        = "${var.project_name}-ec2-${terraform.workspace}"
    Environment = terraform.workspace
  }
}
```

### Updated outputs.tf

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.my_ec2.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.my_ec2.public_ip
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.my_bucket.bucket
}

output "environment" {
  description = "Current workspace/environment"
  value       = terraform.workspace
}
```

### Workspace Commands

```bash
# Destroy the old instance first
terraform destroy
```

**Output:**

```
aws_instance.my_ec2: Destroying... [id=i-xxxxxxxxxxxxxxxxx]
aws_instance.my_ec2: Destruction complete after 30s

Destroy complete! Resources: 1 destroyed.
```

```bash
# Create a dev workspace
terraform workspace new dev
```

**Output:**

```
Created and switched to workspace "dev"!
```

```bash
# Apply in dev workspace
terraform apply
```

**Output:**

```
aws_s3_bucket.my_bucket: Creating...
aws_s3_bucket.my_bucket: Creation complete after 3s [id=fakhir-terraform-bucket-dev]
aws_instance.my_ec2: Creating...
aws_instance.my_ec2: Creation complete after 15s [id=i-xxxxxxxxxxxxxxxxx]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:

instance_id    = "i-xxxxxxxxxxxxxxxxx"
public_ip      = "x.x.x.x"
s3_bucket_name = "fakhir-terraform-bucket-dev"
environment    = "dev"
```

**Note:** S3 bucket was created first, then EC2 — this is because of `depends_on`.

### Managing Multiple Environments

```bash
# Create staging workspace
terraform workspace new staging
terraform apply
# Creates: fakhir-terraform-bucket-staging + myproject-ec2-staging

# Create prod workspace
terraform workspace new prod
terraform apply
# Creates: fakhir-terraform-bucket-prod + myproject-ec2-prod

# List all workspaces
terraform workspace list

# Switch between workspaces
terraform workspace select dev
```

---

## 6. Step 4: Remote State with S3 & DynamoDB Locking

### The Problem with Local State

By default, Terraform stores state in a local `terraform.tfstate` file. This has major issues:

| Problem | Description |
|---------|-------------|
| **No collaboration** | Team members don't have access to your local state file |
| **No backup** | If your machine crashes, the state is lost |
| **No locking** | Two people running `terraform apply` simultaneously can corrupt the state |

### The Solution

| Component | Purpose |
|-----------|---------|
| **S3 Bucket** | Stores the `.tfstate` file remotely — shared, versioned, encrypted |
| **DynamoDB Table** | Acts as a lock — when someone runs `apply`, it creates a lock entry so no one else can run it at the same time |

### Backend Folder Structure

```
terraform/
├── backend/          ← Creates S3 + DynamoDB (run this FIRST)
│   ├── provider.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   ├── main.tf
│   └── outputs.tf
├── provider.tf       ← Uses S3 backend
├── main.tf
├── variables.tf
├── terraform.tfvars
└── outputs.tf
```

### backend/provider.tf

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

### backend/variables.tf

```hcl
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "state_bucket_name" {
  description = "Name of the S3 bucket to store Terraform state"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
}
```

### backend/terraform.tfvars

```hcl
aws_region          = "eu-north-1"
state_bucket_name   = "fakhir-terraform-state-bucket"
dynamodb_table_name = "terraform-state-lock"
```

### backend/main.tf

```hcl
# S3 bucket to store Terraform state files
resource "aws_s3_bucket" "terraform_state" {
  bucket = var.state_bucket_name

  # Prevent accidental deletion of this bucket
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name    = "Terraform State Bucket"
    Purpose = "Stores Terraform remote state"
  }
}

# Enable versioning so we can see the history of state files
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access to the state bucket
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_lock" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name    = "Terraform State Lock Table"
    Purpose = "Locks Terraform state to prevent concurrent modifications"
  }
}
```

### backend/outputs.tf

```hcl
output "s3_bucket_name" {
  description = "Name of the S3 bucket storing Terraform state"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_lock.name
}
```

### Updated Main provider.tf (with remote backend)

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "fakhir-terraform-state-bucket"
    key            = "terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
```

### Running the Backend Setup

```bash
# Step 1: Create backend infrastructure
cd ~/Desktop/DEVOPS/terraform/backend
terraform init
terraform plan
terraform apply
```

**Output:**

```
aws_s3_bucket.terraform_state: Creating...
aws_s3_bucket.terraform_state: Creation complete after 3s
aws_s3_bucket_versioning.terraform_state: Creating...
aws_s3_bucket_server_side_encryption_configuration.terraform_state: Creating...
aws_s3_bucket_public_access_block.terraform_state: Creating...
aws_dynamodb_table.terraform_lock: Creating...
aws_dynamodb_table.terraform_lock: Creation complete after 8s

Apply complete! Resources: 5 added, 0 changed, 0 destroyed.

Outputs:

s3_bucket_name      = "fakhir-terraform-state-bucket"
dynamodb_table_name = "terraform-state-lock"
```

```bash
# Step 2: Migrate main config to remote backend
cd ~/Desktop/DEVOPS/terraform
terraform init
```

**Output:**

```
Initializing the backend...
Do you want to copy existing state to the new backend?
  Enter a value: yes

Successfully configured the backend "s3"!
```

Now the state is stored remotely in S3 and locked with DynamoDB.

---

## 7. IAM Permissions Required

The IAM user needed the following policies attached. These were added via **AWS CloudShell** since the Console UI was not working:

```bash
# EC2 permissions
aws iam attach-user-policy \
  --user-name "fakhir@" \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

# S3 permissions
aws iam attach-user-policy \
  --user-name "fakhir@" \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# DynamoDB permissions (for state locking)
aws iam attach-user-policy \
  --user-name "fakhir@" \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

---

## 8. Final Folder Structure

```
terraform/
├── backend/
│   ├── provider.tf          # AWS provider config
│   ├── variables.tf         # Variable declarations
│   ├── terraform.tfvars     # Variable values
│   ├── main.tf              # S3 bucket + DynamoDB table
│   └── outputs.tf           # Outputs bucket & table names
│
├── provider.tf              # AWS provider + S3 backend config
├── variables.tf             # Variable declarations
├── terraform.tfvars         # Variable values
├── main.tf                  # S3 bucket + EC2 instance
└── outputs.tf               # Outputs instance ID, IP, bucket, env
```

---

## Key Concepts Summary

| Concept | Description |
|---------|-------------|
| **Provider** | Plugin that lets Terraform interact with AWS |
| **Resource** | Infrastructure component (EC2, S3, etc.) |
| **Variables** | Parameterize configs — no hardcoding |
| **tfvars** | File containing actual variable values |
| **Outputs** | Display useful info after apply |
| **Workspaces** | Manage multiple environments (dev/staging/prod) with same code |
| **depends_on** | Force creation order between resources |
| **Remote State** | Store state in S3 instead of locally |
| **State Locking** | DynamoDB prevents concurrent state modifications |
| **Versioning** | S3 versioning keeps history of state changes |
| **Encryption** | State file is encrypted at rest in S3 |

---

## Useful Terraform Commands

```bash
terraform init          # Initialize & download providers
terraform plan          # Preview changes
terraform apply         # Apply changes
terraform destroy       # Destroy all resources
terraform workspace list       # List workspaces
terraform workspace new dev    # Create new workspace
terraform workspace select dev # Switch workspace
terraform state list           # List resources in state
terraform output               # Show outputs
```
