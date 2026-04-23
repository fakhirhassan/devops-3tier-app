# Kubernetes Cluster Setup & 3-Tier Application Deployment

**Name:** Fakhir Hassan
**Subject:** DevOps
**Date:** March 2026

---

## Introduction

This assignment demonstrates setting up a Kubernetes cluster with one **Master Node** and one **Worker Node** on AWS EC2 instances running Ubuntu 24.04. A **3-Tier Application** (Frontend → Backend → Database) is then deployed on the cluster.

### Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                Kubernetes Cluster                 │
│                                                   │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  Master Node     │    │  Worker Node          │ │
│  │  16.16.200.99    │    │  16.171.46.33         │ │
│  │  (Control Plane) │    │  (Runs Application)   │ │
│  │                  │    │                       │ │
│  │  - API Server    │    │  - Frontend (Nginx)   │ │
│  │  - Scheduler     │    │  - Backend (Flask)    │ │
│  │  - Controller    │    │  - Database (MySQL)   │ │
│  │  - etcd          │    │                       │ │
│  └─────────────────┘    └──────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### 3-Tier Application Stack

| Tier       | Technology | Purpose                    | Port  |
|------------|-----------|----------------------------|-------|
| Frontend   | Nginx     | Serves web UI              | 30080 |
| Backend    | Flask API | Business logic & REST API  | 5000  |
| Database   | MySQL     | Data storage               | 3306  |

---

## Section 1: Kubernetes Cluster Initialization

### Step 1: Find Private IP of Master Node

SSH into the master node and find the private IP address.

```bash
hostname -I
```

The private IP (172.31.7.232) is used to advertise the Kubernetes API server to other nodes in the cluster.

> **📸 Screenshot:** Add screenshot of `hostname -I` output here
> ![hostname output](screenshots/step1_hostname.png)

---

### Step 2: Initialize Kubernetes Cluster

Run `kubeadm init` on the master node to set up the control plane components (API Server, Scheduler, Controller Manager, etcd).

```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=172.31.7.232
```

- `--pod-network-cidr=10.244.0.0/16` sets the IP range for pods (required by Flannel).
- `--apiserver-advertise-address` tells the API server to listen on the master's private IP.

> **📸 Screenshot:** Add screenshot showing successful initialization output
> ![kubeadm init](screenshots/step2_kubeadm_init.png)

---

### Step 3: Configure kubectl

Configure kubectl so the current user can interact with the cluster without using sudo.

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

These commands copy the admin credentials to the user's home directory and set proper ownership.

> **📸 Screenshot:** Add screenshot of commands executed
> ![kubectl config](screenshots/step3_kubectl_config.png)

---

### Step 4: Install Flannel Pod Network Plugin

Deploy the Flannel CNI (Container Network Interface) plugin to enable pod-to-pod communication across nodes.

```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

Without a network plugin, pods on different nodes cannot communicate with each other.

> **📸 Screenshot:** Add screenshot showing Flannel resources created
> ![flannel install](screenshots/step4_flannel.png)

---

## Section 2: Joining Worker Node to the Cluster

### Step 5: Configure AWS Security Group

Before the worker can join, both EC2 instances must be able to communicate internally.

**Steps:**
1. Go to **AWS Console → EC2 → Security Groups**
2. Select the security group attached to the instances
3. Click **Edit Inbound Rules → Add Rule**
4. Set: **Type:** All Traffic | **Source:** 172.31.0.0/16
5. Click **Save Rules**

This allows all internal VPC traffic between the master and worker nodes.

> **📸 Screenshot:** Add screenshot of AWS Security Group inbound rules
> ![security group](screenshots/step5_security_group.png)

---

### Step 6: Generate Join Command on Master Node

On the master node, generate a fresh token and join command for the worker node.

```bash
kubeadm token create --print-join-command
```

This outputs a command containing a bootstrap token and certificate hash that the worker uses to securely join the cluster.

> **📸 Screenshot:** Add screenshot of join command output
> ![join command](screenshots/step6_join_command.png)

---

### Step 7: Join Worker Node to the Cluster

SSH into the worker node and run the join command (from Step 6) with sudo.

```bash
sudo kubeadm join 172.31.7.232:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
```

The worker node contacts the master's API server on port 6443, authenticates using the token, and registers itself as a cluster member.

> **📸 Screenshot:** Add screenshot showing "This node has joined the cluster" message
> ![node joined](screenshots/step7_node_joined.png)

---

### Step 8: Verify Both Nodes are Ready

Back on the master node, verify both nodes are registered and in Ready status.

```bash
kubectl get nodes
```

**Expected Output:**
```
NAME               STATUS   ROLES           AGE   VERSION
ip-172-31-7-232    Ready    control-plane   9m    v1.29.15
ip-172-31-10-210   Ready    <none>          1m    v1.29.15
```

Both nodes showing `Ready` confirms the cluster is fully operational.

> **📸 Screenshot:** Add screenshot of `kubectl get nodes` showing both nodes Ready
> ![get nodes](screenshots/step8_get_nodes.png)

---

## Section 3: Building & Pushing Docker Images

### Step 9: Transfer Application Files to Master Node

From the local machine, copy the application source code and Kubernetes manifests to the master node.

```bash
scp -i mypc.pem -r frontend/ backend/ k8s/ ubuntu@16.16.200.99:~/
```

This transfers three directories: `frontend/` (Nginx web app), `backend/` (Flask API), and `k8s/` (Kubernetes YAML manifests).

> **📸 Screenshot:** Add screenshot of scp file transfer
> ![scp transfer](screenshots/step9_scp.png)

---

### Step 10: Login to Docker Hub

On the master node, authenticate with Docker Hub to push container images.

```bash
sudo docker login
```

Enter your Docker Hub username and password when prompted.

> **📸 Screenshot:** Add screenshot of "Login Succeeded" message
> ![docker login](screenshots/step10_docker_login.png)

---

### Step 11: Build and Push Frontend Image

Build the Nginx-based frontend Docker image and push it to Docker Hub.

```bash
cd ~/frontend
sudo docker build -t fakhirhassan/three-tier-frontend:latest .
sudo docker push fakhirhassan/three-tier-frontend:latest
```

> **📸 Screenshot:** Add screenshot of successful build and push
> ![frontend build](screenshots/step11_frontend_build.png)

---

### Step 12: Build and Push Backend Image

Build the Flask API backend Docker image and push it to Docker Hub.

```bash
cd ~/backend
sudo docker build -t fakhirhassan/three-tier-backend:latest .
sudo docker push fakhirhassan/three-tier-backend:latest
```

> **📸 Screenshot:** Add screenshot of successful build and push
> ![backend build](screenshots/step12_backend_build.png)

---

## Section 4: Deploying the 3-Tier Application

### Step 13: Deploy Kubernetes Resources

Apply all Kubernetes manifests to deploy the complete 3-tier application.

```bash
cd ~/k8s
kubectl apply -f namespace.yaml
kubectl apply -f mysql-secret.yaml
kubectl apply -f mysql-init-configmap.yaml
kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
```

This creates:
- A dedicated namespace `three-tier-app`
- MySQL database with secrets, persistent storage, and initialization
- Flask backend API (2 replicas)
- Nginx frontend (2 replicas)

> **📸 Screenshot:** Add screenshot of all kubectl apply outputs
> ![deploy all](screenshots/step13_deploy.png)

---

### Step 14: Verify All Pods and Services

Check that all deployments, pods, and services are running in the cluster.

```bash
kubectl get all -n three-tier-app
```

**Expected Output:**
```
NAME                           READY   STATUS    RESTARTS   AGE
pod/backend-6659fd9bd9-gl2x2   1/1     Running   0          20h
pod/backend-6659fd9bd9-zdt74   1/1     Running   0          20h
pod/frontend-c58dbb777-5jgw2   1/1     Running   0          20h
pod/frontend-c58dbb777-qg9ht   1/1     Running   0          20h
pod/mysql-f8cb646c4-rgpd8      1/1     Running   0          20h

NAME                       TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/backend-service    ClusterIP   10.109.174.3   <none>        5000/TCP       20h
service/frontend-service   NodePort    10.105.8.142   <none>        80:30080/TCP   20h
service/mysql-service      ClusterIP   10.107.210.6   <none>        3306/TCP       20h
```

All 5 pods (2 frontend, 2 backend, 1 MySQL) should be in `Running` status.

> **📸 Screenshot:** Add screenshot of `kubectl get all` output
> ![get all](screenshots/step14_get_all.png)

---

### Step 15: Check Pod Distribution Across Nodes

Verify which pods are running on which node.

```bash
kubectl get pods -n three-tier-app -o wide
```

**Expected Output:**
```
NAME                       READY   STATUS    NODE
backend-6659fd9bd9-gl2x2   1/1     Running   ip-172-31-10-210 (Worker)
backend-6659fd9bd9-zdt74   1/1     Running   ip-172-31-10-210 (Worker)
frontend-c58dbb777-5jgw2   1/1     Running   ip-172-31-10-210 (Worker)
frontend-c58dbb777-qg9ht   1/1     Running   ip-172-31-10-210 (Worker)
mysql-f8cb646c4-rgpd8      1/1     Running   ip-172-31-10-210 (Worker)
```

Pods run on the worker node since the master has a control-plane taint that prevents scheduling application workloads.

> **📸 Screenshot:** Add screenshot of pods with node info
> ![pods wide](screenshots/step15_pods_wide.png)

---

## Section 5: Accessing the Application

### Step 16: Open NodePort in AWS Security Group

Add an inbound rule to allow external browser access on port 30080.

**Steps:**
1. Go to **AWS Console → EC2 → Security Groups**
2. Click **Edit Inbound Rules → Add Rule**
3. Set: **Type:** Custom TCP | **Port:** 30080 | **Source:** 0.0.0.0/0
4. Click **Save Rules**

> **📸 Screenshot:** Add screenshot of security group with port 30080 rule
> ![nodeport sg](screenshots/step16_nodeport_sg.png)

---

### Step 17: Access the Application in Browser

Open the application using the worker node's public IP.

```
http://16.171.46.33:30080
```

The frontend page loads via Nginx, communicates with the Flask backend API, which in turn connects to the MySQL database — completing the 3-tier architecture.

> **📸 Screenshot:** Add screenshot of the application running in browser
> ![app running](screenshots/step17_app_browser.png)

---

## Summary

| Component          | Details                          |
|--------------------|----------------------------------|
| Master Node        | 16.16.200.99 (ip-172-31-7-232)  |
| Worker Node        | 16.171.46.33 (ip-172-31-10-210) |
| Kubernetes Version | v1.29.15                         |
| Pod Network        | Flannel (10.244.0.0/16)         |
| Total Pods         | 5 (2 Frontend + 2 Backend + 1 MySQL) |
| App Access URL     | http://16.171.46.33:30080       |
| Frontend           | Nginx (NodePort 30080)          |
| Backend            | Flask API (ClusterIP 5000)      |
| Database           | MySQL (ClusterIP 3306)          |
