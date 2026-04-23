# Ansible Automation Assignment

**Name:** Fakhir Hassan Shaba
**Registration:** FA22-BSE-084
**Course:** DevOps
**University:** COMSATS University Islamabad, Wah Campus

---

## What is Ansible?

Ansible is an open-source automation tool used for configuration management, application deployment, and task automation. It allows you to manage multiple servers from a single machine by writing simple YAML files called **playbooks** — instead of manually SSHing into each server and running commands one by one.

### Key Benefits:
- **Agentless:** No software needs to be installed on managed servers — it uses SSH
- **Simple:** Uses human-readable YAML syntax
- **Scalable:** Run the same playbook on 1 server or 1000 servers
- **Idempotent:** Running a playbook multiple times produces the same result — it won't duplicate work

---

## Prerequisites

- A control machine (macOS/Linux) with Ansible installed
- A target Linux server (EC2 instance) accessible via SSH
- SSH key (.pem file) for authentication

## Environment Setup

- **Control Machine:** macOS (local machine)
- **Target Server:** Ubuntu EC2 Instance — `13.53.192.144`
- **SSH Key:** `mypc.pem`

---

## Step 1: Install Ansible

```bash
# Install Ansible on macOS using Homebrew
brew install ansible

# Verify installation
ansible --version
```

---

## Step 2: Project Structure

```
ansible/
├── inventory.ini          # Defines target servers
├── install-nginx.yml      # Playbook: Install Nginx + deploy CV
├── create-users.yml       # Playbook: Create 2 users
└── cv.html                # Custom CV page
```

---

## Step 3: Inventory File

The inventory file tells Ansible which servers to manage.

**File: `inventory.ini`**
```ini
[webservers]
13.53.192.144 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
```

### Test Connection:
```bash
ansible -i inventory.ini webservers -m ping
```

**Expected Output:**
```
13.53.192.144 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## Task 1: Install Nginx and Deploy Custom CV Page

### Playbook: `install-nginx.yml`

```yaml
---
- name: Install Nginx and deploy custom CV page
  hosts: webservers
  become: yes  # Run as root (sudo)

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install Nginx
      apt:
        name: nginx
        state: present

    - name: Start and enable Nginx
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Copy custom CV page to Nginx default site
      copy:
        src: cv.html
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Restart Nginx to apply changes
      service:
        name: nginx
        state: restarted
```

### Run Command:
```bash
cd ~/Desktop/DEVOPS/ansible
ansible-playbook -i inventory.ini install-nginx.yml
```

### What Each Task Does:
| Task | Purpose |
|------|---------|
| Update apt cache | Refreshes the package list (like `sudo apt update`) |
| Install Nginx | Installs the Nginx web server |
| Start and enable Nginx | Starts Nginx and ensures it auto-starts on boot |
| Copy custom CV page | Copies `cv.html` from local machine to server as the default page |
| Restart Nginx | Restarts Nginx so the new page is served |

### Manual Equivalent Commands (What Ansible Does Behind the Scenes):
```bash
# SSH into the server
ssh -i ~/Desktop/DEVOPS/mypc.pem ubuntu@13.53.192.144

# Update packages
sudo apt update

# Install Nginx
sudo apt install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Copy CV page (from local machine)
scp -i ~/Desktop/DEVOPS/mypc.pem cv.html ubuntu@13.53.192.144:/tmp/cv.html
ssh -i ~/Desktop/DEVOPS/mypc.pem ubuntu@13.53.192.144 "sudo cp /tmp/cv.html /var/www/html/index.html"

# Restart Nginx
sudo systemctl restart nginx
```

### Verification:
Open browser and navigate to: **http://13.53.192.144**

The custom CV page should be displayed.

### Screenshot:
> *(Add screenshot of the CV page running in the browser here)*

---

## Task 2: Create 2 Users on Linux Machine

### Playbook: `create-users.yml`

```yaml
---
- name: Create 2 users on Linux machine
  hosts: webservers
  become: yes  # Run as root (sudo)

  tasks:
    - name: Create user 'devuser1'
      user:
        name: devuser1
        comment: "Dev User 1"
        shell: /bin/bash
        create_home: yes
        state: present

    - name: Create user 'devuser2'
      user:
        name: devuser2
        comment: "Dev User 2"
        shell: /bin/bash
        create_home: yes
        state: present

    - name: Verify users were created
      command: id {{ item }}
      loop:
        - devuser1
        - devuser2
      register: user_info

    - name: Display user info
      debug:
        msg: "{{ item.stdout }}"
      loop: "{{ user_info.results }}"
```

### Run Command:
```bash
cd ~/Desktop/DEVOPS/ansible
ansible-playbook -i inventory.ini create-users.yml
```

### What Each Task Does:
| Task | Purpose |
|------|---------|
| Create user 'devuser1' | Creates a new Linux user with home directory and bash shell |
| Create user 'devuser2' | Creates a second Linux user with the same configuration |
| Verify users were created | Runs `id` command for each user to confirm they exist |
| Display user info | Prints the user details (UID, GID, groups) in the terminal |

### Manual Equivalent Commands:
```bash
# SSH into the server
ssh -i ~/Desktop/DEVOPS/mypc.pem ubuntu@13.53.192.144

# Create users
sudo useradd -m -s /bin/bash -c "Dev User 1" devuser1
sudo useradd -m -s /bin/bash -c "Dev User 2" devuser2

# Verify users
id devuser1
id devuser2
```

### Verification Commands:
```bash
# Check if users exist
ansible -i inventory.ini webservers -m command -a "id devuser1" --become
ansible -i inventory.ini webservers -m command -a "id devuser2" --become

# Or SSH in and check
ssh -i ~/Desktop/DEVOPS/mypc.pem ubuntu@13.53.192.144
cat /etc/passwd | grep devuser
```

**Expected Output:**
```
devuser1:x:1001:1001:Dev User 1:/home/devuser1:/bin/bash
devuser2:x:1002:1002:Dev User 2:/home/devuser2:/bin/bash
```

### Screenshot:
> *(Add screenshot of the playbook output showing users created successfully)*

---

## Important AWS Security Group Configuration

Before accessing the CV page in the browser, ensure **port 80 (HTTP)** is open in the EC2 Security Group:

1. Go to **AWS Console → EC2 → Security Groups**
2. Select the security group attached to your instance
3. Click **Edit Inbound Rules**
4. Add rule: **Type:** HTTP | **Port:** 80 | **Source:** 0.0.0.0/0
5. Save

---

## Summary

| Task | Tool Used | Result |
|------|-----------|--------|
| Install Nginx | `apt` module | Nginx web server installed and running |
| Deploy CV Page | `copy` module | Custom `cv.html` served as default page |
| Create Users | `user` module | `devuser1` and `devuser2` created on the server |

---

## Running on Multiple EC2 Machines

This is where Ansible truly shines. The **playbooks remain exactly the same** — you only change the **inventory file** to add more servers.

### Step 1: Update Inventory File

**File: `inventory.ini`**
```ini
[webservers]
13.53.192.144 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
54.12.88.201 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
18.200.45.67 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
```

> Replace the IPs above with your actual EC2 instance IPs. If different servers use different keys or usernames, specify them per line.

**Example with different keys/users:**
```ini
[webservers]
13.53.192.144 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
54.12.88.201 ansible_user=ec2-user ansible_ssh_private_key_file=~/Desktop/DEVOPS/devops.pem
18.200.45.67 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
```

### Step 2: Test Connection to All Servers

```bash
ansible -i inventory.ini webservers -m ping
```

**Expected Output:**
```
13.53.192.144 | SUCCESS => { "ping": "pong" }
54.12.88.201  | SUCCESS => { "ping": "pong" }
18.200.45.67  | SUCCESS => { "ping": "pong" }
```

### Step 3: Run Playbooks (Same Commands — No Change!)

```bash
# Install Nginx + deploy CV on ALL servers at once
ansible-playbook -i inventory.ini install-nginx.yml

# Create users on ALL servers at once
ansible-playbook -i inventory.ini create-users.yml
```

Ansible will automatically run the tasks on **all 3 servers in parallel**.

### The Real Power of Ansible

| Approach | 1 Server | 3 Servers | 50 Servers |
|----------|----------|-----------|------------|
| **Manual (SSH)** | Run 6 commands | Run 6 commands × 3 = 18 commands | Run 6 commands × 50 = 300 commands |
| **Ansible** | 1 command | 1 command (same) | 1 command (same) |

You just add more IPs to the inventory file. The playbook and the run command stay **exactly the same**. This is why Ansible is used in production — managing hundreds of servers becomes as simple as managing one.

### Optional: Group Servers by Role

You can also organize servers into different groups:

```ini
[webservers]
13.53.192.144 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem
54.12.88.201 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem

[dbservers]
18.200.45.67 ansible_user=ubuntu ansible_ssh_private_key_file=~/Desktop/DEVOPS/mypc.pem

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

Then target specific groups in your playbooks:
```yaml
hosts: webservers    # Only runs on web servers
hosts: dbservers     # Only runs on database servers
hosts: all           # Runs on every server in the inventory
```

---

### Key Ansible Concepts Used:
- **Inventory:** Defines which servers to manage
- **Playbook:** YAML file containing ordered list of tasks
- **Modules:** Pre-built tools (`apt`, `service`, `copy`, `user`, `command`, `debug`)
- **Become:** Privilege escalation to run tasks as root (sudo)
- **Idempotency:** Running playbooks multiple times produces the same result without duplication
