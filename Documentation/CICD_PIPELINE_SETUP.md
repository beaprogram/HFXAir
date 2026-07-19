# CI/CD Pipeline Setup Documentation

> **Historical course pipeline:** This guide documents the original self-hosted
> GitLab runners and VM deployment. Do not reuse its hosts, users, tokens, or keys.
> GitHub pull requests now use `.github/workflows/ci.yml` for test feedback only.

## HFXAIR Flask Backend - Step-by-Step Implementation Guide

---

## Table of Contents

1. [Introduction](#introduction)
2. [Step 1: SSH Key Setup for GitLab CI/CD](#step-1-ssh-key-setup-for-gitlab-cicd)
3. [Step 2: Configure GitLab CI/CD Variables](#step-2-configure-gitlab-cicd-variables)
4. [Step 3: Register GitLab Runner on VM](#step-3-register-gitlab-runner-on-vm)
5. [Step 4: Configure Sudoers for Passwordless Deployment](#step-4-configure-sudoers-for-passwordless-deployment)
6. [Step 5: Prepare Project Structure](#step-5-prepare-project-structure)
7. [Step 6: Create the CI/CD Pipeline Configuration](#step-6-create-the-cicd-pipeline-configuration)
8. [Step 7: Create DCodeHub Upload Script](#step-7-create-dcodehub-upload-script)
9. [Step 8: Clean Up Git Repository](#step-8-clean-up-git-repository)
10. [Step 9: Push Pipeline to Main Branch](#step-9-push-pipeline-to-main-branch)
11. [Step 10: Verify Pipeline Execution](#step-10-verify-pipeline-execution)
12. [Pipeline Overview](#pipeline-overview)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

This document provides a complete step-by-step guide to setting up a CI/CD (Continuous Integration/Continuous Deployment) pipeline for the HFXAIR Flask backend application hosted on GitLab.

### Project Details

| Attribute | Value |
|-----------|-------|
| **Project Name** | HFXAIR (Halifax Airport Management System) |
| **Backend Framework** | Python/Flask |
| **GitLab Instance** | git.cs.dal.ca (Self-hosted by Dalhousie) |
| **Deployment VM** | csci5308-vm1.research.cs.dal.ca |
| **VM Username** | student |
| **Project Path on VM** | /home/student/HFXAIR/group01 |
| **Flask App Path** | /home/student/HFXAIR/group01/flask_app |
| **Virtual Environment** | /home/student/venv |
| **systemd Service** | hfxair.service |

### Pipeline Stages

| Stage | Purpose | Runner |
|-------|---------|--------|
| Build | Install dependencies and verify app loads | VM Runner (vm-runner) |
| Test | Run pytest test suite with coverage | VM Runner (vm-runner) |
| Deploy | Sync code using rsync and restart service | VM Runner (vm-runner) |
| Code Quality | Analyze code with DPy, submit to DCodeHub | Docker Runner (dalfcs_docker_kvm) |

---

## Step 1: SSH Key Setup for GitLab CI/CD

**Purpose**: Generate SSH keys to allow GitLab CI/CD to connect to the VM for automated deployments.

### 1.1 Connect to the VM

```bash
ssh student@csci5308-vm1.research.cs.dal.ca
```

Enter your password when prompted.

### 1.2 Generate SSH Key Pair

```bash
ssh-keygen -t ed25519 -f ~/.ssh/gitlab_ci_key -N ""
```

**Output**:
```
Generating public/private ed25519 key pair.
Your identification has been saved in /home/student/.ssh/gitlab_ci_key
Your public key has been saved in /home/student/.ssh/gitlab_ci_key.pub
```

### 1.3 Add Public Key to Authorized Keys

```bash
cat ~/.ssh/gitlab_ci_key.pub >> ~/.ssh/authorized_keys
```

### 1.4 View the Private Key

```bash
cat ~/.ssh/gitlab_ci_key
```

The output is sensitive key material. Do not paste it into documentation, issues,
chat, terminal recordings, or repository files. Store it only in the approved CI
secret/file-variable interface for a newly provisioned environment.

### 1.5 Base64 Encode the Private Key (Required for GitLab)

```bash
cat ~/.ssh/gitlab_ci_key | base64 -w 0 && echo
```

**Output**: A single line of encoded text (copy this for GitLab variable).

---

## Step 2: Configure GitLab CI/CD Variables

**Purpose**: Store sensitive information securely in GitLab that the pipeline can access.

### 2.1 Navigate to CI/CD Variables

1. Open your browser and go to: `https://git.cs.dal.ca`
2. Navigate to your project (e.g., `courses/2025-Fall/csci-5308/group01`)
3. Go to **Settings** → **CI/CD**
4. Expand the **Variables** section

### 2.2 Add SSH Private Key Variable

Click **Add variable** and enter:

| Field | Value |
|-------|-------|
| **Key** | `SSH_PRIVATE_KEY` |
| **Value** | (Paste the base64-encoded key from Step 1.5) |
| **Type** | Variable |
| **Protect variable** | Unchecked |
| **Mask variable** | Checked |
| **Expand variable reference** | Checked |

Click **Add variable**.

### 2.3 Add VM Host Variable

Click **Add variable** and enter:

| Field | Value |
|-------|-------|
| **Key** | `VM_HOST` |
| **Value** | `csci5308-vm1.research.cs.dal.ca` |
| **Type** | Variable |
| **Protect variable** | Unchecked |
| **Mask variable** | Unchecked |

Click **Add variable**.

### 2.4 Add VM User Variable

Click **Add variable** and enter:

| Field | Value |
|-------|-------|
| **Key** | `VM_USER` |
| **Value** | `student` |
| **Type** | Variable |
| **Protect variable** | Unchecked |
| **Mask variable** | Unchecked |

Click **Add variable**.

### 2.5 Add DCodeHub Variables

Click **Add variable** for each:

**Variable 1**:
| Field | Value |
|-------|-------|
| **Key** | `DCODE_API_KEY` |
| **Value** | (Your DCodeHub API key) |
| **Mask variable** | Checked |

**Variable 2**:
| Field | Value |
|-------|-------|
| **Key** | `DCODE_PROJECT_ID` |
| **Value** | (Your DCodeHub project ID) |
| **Mask variable** | Checked |

### 2.6 Verify Variables

You should now have these variables configured:

| Key | Masked |
|-----|--------|
| SSH_PRIVATE_KEY | Yes |
| VM_HOST | No |
| VM_USER | No |
| DCODE_API_KEY | Yes |
| DCODE_PROJECT_ID | Yes |

---

## Step 3: Register GitLab Runner on VM

**Purpose**: Set up a GitLab Runner on the VM that will execute pipeline jobs locally.

### 3.1 Connect to VM

```bash
ssh student@csci5308-vm1.research.cs.dal.ca
```

### 3.2 Check if GitLab Runner is Installed

```bash
sudo gitlab-runner --version
```

**Expected Output**:
```
Version:      18.6.1
Git revision: b5e9c6d0
Git branch:   18-6-stable
GO version:   go1.23.4
Built:        2025-01-16T12:37:41+0000
OS/Arch:      linux/amd64
```

### 3.3 Create Project Runner in GitLab

1. Go to your project on **git.cs.dal.ca**
2. Navigate to **Settings** → **CI/CD** → **Runners**
3. Click **"Create project runner"**
4. Select **Linux** as the operating system
5. In the **Tags** field, enter: `vm-runner`
6. Click **"Create runner"**
7. **Copy the registration token** (starts with `glrt-...`)

### 3.4 Clear Existing Runner Configuration (if any)

```bash
sudo rm /etc/gitlab-runner/config.toml
sudo touch /etc/gitlab-runner/config.toml
```

### 3.5 Register the Runner

Replace `YOUR_TOKEN_HERE` with the token from Step 3.3:

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://git.cs.dal.ca" \
  --token "YOUR_TOKEN_HERE" \
  --executor "shell" \
  --description "csci5308-vm1"
```

**Expected Output**:
```
Runtime platform                                    arch=amd64 os=linux pid=267648 revision=b5e9c6d0 version=18.6.1
Registering runner... succeeded                     runner=qGXImjiq
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!
```

### 3.6 Verify Runner Registration

```bash
sudo gitlab-runner list
```

**Expected Output**:
```
Runtime platform                                    arch=amd64 os=linux pid=267648 revision=b5e9c6d0 version=18.6.1
Listing configured runners                          ConfigFile=/etc/gitlab-runner/config.toml
csci5308-vm1                                        Executor=shell Token=glrt-xxxxx URL=https://git.cs.dal.ca
```

### 3.7 Check Runner Status

```bash
sudo gitlab-runner status
```

**Expected Output**:
```
Runtime platform                                    arch=amd64 os=linux pid=267561 revision=b5e9c6d0 version=18.6.1
gitlab-runner: Service is running
```

### 3.8 Fix Shell Profile Issue (Important!)

The GitLab Runner may fail due to shell profile issues. Fix by backing up `.bash_logout`:

```bash
mv ~/.bash_logout ~/.bash_logout.bak
```

---

## Step 4: Configure Sudoers for Passwordless Deployment

**Purpose**: Allow the GitLab Runner to restart the Flask service without requiring a password.

### 4.1 Open Sudoers File

```bash
sudo visudo
```

### 4.2 Add Passwordless Rule

Add the following line at the end of the file:

```
student ALL=(ALL) NOPASSWD: /bin/systemctl restart hfxair.service
```

### 4.3 Save and Exit

- If using nano: Press `Ctrl+X`, then `Y`, then `Enter`
- If using vi: Press `Esc`, type `:wq`, press `Enter`

### 4.4 Verify the Configuration

```bash
sudo systemctl restart hfxair.service
```

This command should now execute without asking for a password.

---

## Step 5: Prepare Project Structure

**Purpose**: Create necessary directories and verify project structure.

### 5.1 Connect to VM

```bash
ssh student@csci5308-vm1.research.cs.dal.ca
```

### 5.2 Navigate to Project Directory

```bash
cd /home/student/HFXAIR/group01
```

### 5.3 Verify Project Structure

```bash
ls -la
```

**Expected Output**:
```
drwxrwxr-x   8 student student    4096 Nov 26 14:44 .
drwxrwxr-x   3 student student    4096 Nov  7 01:56 ..
drwxrwxr-x   8 student student    4096 Nov 25 18:55 .git
-rw-rw-r--   1 student student     xxx Nov 26 xx:xx .gitlab-ci.yml
drwxrwxr-x   7 student student    4096 Nov 26 14:44 flask_app
...
```

### 5.4 Verify Flask App Structure

```bash
ls -la flask_app/
```

**Expected Output**:
```
drwxrwxr-x  7 student student  4096 Nov 26 14:44 .
drwxrwxr-x  8 student student  4096 Nov 26 14:44 ..
-rw-rw-r--  1 student student   225 Nov 26 14:30 .env
-rw-rw-r--  1 student student   422 Nov 20 00:27 .gitignore
-rw-rw-r--  1 student student   741 Nov 24 22:08 __init__.py
-rw-rw-r--  1 student student 11794 Nov 24 22:08 app.py
-rw-rw-r--  1 student student  1215 Nov 20 00:27 auth.py
drwxrwxr-x  3 student student    96 Nov 20 00:27 config
drwxrwxr-x  3 student student    96 Nov 20 00:27 helper
-rw-rw-r--  1 student student    96 Nov 20 00:27 requirements.txt
-rw-rw-r--  1 student student 29153 Nov 24 22:08 shop.py
drwxrwxr-x 11 student student   352 Nov 24 22:08 tests
```

### 5.5 Verify Tests Directory

```bash
ls -la flask_app/tests/
```

**Expected Output**:
```
drwxrwxr-x 2 student student  4096 Nov 25 19:04 .
drwxrwxr-x 7 student student  4096 Nov 26 14:44 ..
-rw-rw-r-- 1 student student   483 Nov 25 19:04 conftest.py
-rw-rw-r-- 1 student student  1087 Nov 25 19:04 test_arrivals_departures.py
-rw-rw-r-- 1 student student   578 Nov 25 19:04 test_flight_details.py
-rw-rw-r-- 1 student student   557 Nov 25 19:04 test_flights.py
-rw-rw-r-- 1 student student  3130 Nov 25 19:04 test_login.py
-rw-rw-r-- 1 student student 29347 Nov 25 19:04 test_shops.py
-rw-rw-r-- 1 student student   942 Nov 25 19:04 test_subscribe.py
```

### 5.6 Create Quality Scripts Directory

```bash
mkdir -p .quality
```

### 5.7 Verify systemd Service

```bash
sudo systemctl status hfxair.service
```

**Expected Output**:
```
● hfxair.service - HFXAIR Flask Application
     Loaded: loaded (/etc/systemd/system/hfxair.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-11-24 15:46:31 UTC; 1 day 1h ago
   Main PID: 255803 (gunicorn)
      Tasks: 5 (limit: 4722)
     Memory: 120.8M
     CGroup: /system.slice/hfxair.service
             ├─255803 /home/student/venv/bin/python3 /home/student/venv/bin/gunicorn...
```

### 5.8 Verify rsync is Installed

```bash
rsync --version
```

**Expected Output**:
```
rsync  version 3.2.7  protocol version 31
...
```

If rsync is not installed, install it:
```bash
sudo apt-get update
sudo apt-get install rsync
```

---

## Step 6: Create the CI/CD Pipeline Configuration

**Purpose**: Create the `.gitlab-ci.yml` file that defines the pipeline stages and jobs.

### 6.1 Navigate to Project Root

```bash
cd /home/student/HFXAIR/group01
```

### 6.2 Create the .gitlab-ci.yml File

```bash
nano .gitlab-ci.yml
```

### 6.3 Add Pipeline Configuration

Copy and paste the following content:

```yaml
stages:
  - build
  - test
  - deploy
  - code-quality

variables:
  PYTHONPATH: "${CI_PROJECT_DIR}"

# ==================== BUILD ====================
build:
  stage: build
  tags:
    - vm-runner
  script:
    - cd $CI_PROJECT_DIR/flask_app
    - source /home/student/venv/bin/activate
    - pip install -r requirements.txt
    - python -c "from flask_app.app import app; print('App loads successfully')"
  only:
    - main

# ==================== TEST ====================
test:
  stage: test
  tags:
    - vm-runner
  script:
    - cd $CI_PROJECT_DIR/flask_app
    - source /home/student/venv/bin/activate
    - pip install pytest pytest-cov
    - pytest tests/ -v --tb=short --cov=. --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  only:
    - main
  needs:
    - build

# ==================== DEPLOY ====================
deploy:
  stage: deploy
  tags:
    - vm-runner
  script:
    - echo "Syncing code to deployment directory..."
    - rsync -av --delete --exclude='.git' --exclude='venv' --exclude='__pycache__' $CI_PROJECT_DIR/ /home/student/HFXAIR/group01/
    - sudo systemctl restart hfxair.service
    - echo "Deployment complete!"
  only:
    - main
  needs:
    - test

# ==================== CODE QUALITY ====================
run-dpy:
  stage: code-quality
  image: python:3.10
  tags:
    - dalfcs_docker_kvm
  script:
    - echo "Downloading DPy..."
    - wget -q https://www.designite-tools.com/assets/DPy-linux.zip -O DPy.zip
    - python3 -m zipfile -e DPy.zip .
    - chmod +x DPy
    - echo "Running DPy on flask_app..."
    - mkdir -p smells/
    - ./DPy analyze -i $CI_PROJECT_DIR/flask_app -o $CI_PROJECT_DIR/smells/ -f csv
    - echo "DPy analysis complete!"
    - ls -la smells/
  artifacts:
    paths:
      - smells/
  only:
    - main
  needs:
    - deploy

submit-dcode:
  stage: code-quality
  image: python:3.10-alpine
  tags:
    - dalfcs_docker_kvm
  dependencies:
    - run-dpy
  script:
    - pip install requests --quiet
    - python3 $CI_PROJECT_DIR/.quality/push_to_dcode.py $DCODE_PROJECT_ID $DCODE_API_KEY $CI_PROJECT_DIR/smells/ $CI_COMMIT_SHA
  only:
    - main
  needs:
    - run-dpy
```

### 6.4 Save and Exit

Press `Ctrl+X`, then `Y`, then `Enter`

### 6.5 Verify File Creation

```bash
cat .gitlab-ci.yml
```

### 6.6 Understanding the Pipeline Configuration

#### Global Variables
```yaml
variables:
  PYTHONPATH: "${CI_PROJECT_DIR}"
```
- Sets the Python path to the project directory for proper module imports

#### Build Stage
```yaml
build:
  stage: build
  tags:
    - vm-runner
  script:
    - cd $CI_PROJECT_DIR/flask_app
    - source /home/student/venv/bin/activate
    - pip install -r requirements.txt
    - python -c "from flask_app.app import app; print('App loads successfully')"
  only:
    - main
```
- **Purpose**: Install dependencies and verify the Flask application loads correctly
- **Runner**: VM runner (shell executor)
- **Trigger**: Only on `main` branch

#### Test Stage
```yaml
test:
  stage: test
  tags:
    - vm-runner
  script:
    - cd $CI_PROJECT_DIR/flask_app
    - source /home/student/venv/bin/activate
    - pip install pytest pytest-cov
    - pytest tests/ -v --tb=short --cov=. --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  only:
    - main
  needs:
    - build
```
- **Purpose**: Run pytest with coverage reporting
- **Coverage Regex**: Extracts coverage percentage from pytest output
- **Dependencies**: Requires `build` stage to pass first

#### Deploy Stage
```yaml
deploy:
  stage: deploy
  tags:
    - vm-runner
  script:
    - echo "Syncing code to deployment directory..."
    - rsync -av --delete --exclude='.git' --exclude='venv' --exclude='__pycache__' $CI_PROJECT_DIR/ /home/student/HFXAIR/group01/
    - sudo systemctl restart hfxair.service
    - echo "Deployment complete!"
  only:
    - main
  needs:
    - test
```
- **Purpose**: Sync code using rsync and restart the service
- **rsync flags**:
  - `-a`: Archive mode (preserves permissions, timestamps)
  - `-v`: Verbose output
  - `--delete`: Remove files in destination not in source
  - `--exclude`: Skip specified directories
- **Dependencies**: Requires `test` stage to pass first

#### Code Quality Stage
- **run-dpy**: Downloads and runs DPy code smell analyzer
- **submit-dcode**: Uploads analysis results to DCodeHub
- Both jobs run on Docker runner (`dalfcs_docker_kvm`)

---

## Step 7: Create DCodeHub Upload Script

**Purpose**: Create a Python script to upload code quality reports to DCodeHub.

### 7.1 Navigate to Quality Directory

```bash
cd /home/student/HFXAIR/group01/.quality
```

### 7.2 Create the Upload Script

```bash
nano push_to_dcode.py
```

### 7.3 Add Script Content

Copy and paste the following content:

```python
#!/usr/bin/env python3
"""
Python script to upload project inputs to DCodeHub.
Replaces the bash script to avoid shell environment issues in CI.
"""
import sys
import os
import requests 

def main():
    # --- ARGUMENT VALIDATION ---
    if len(sys.argv) != 5:
        print("Error: Incorrect number of arguments.", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} <project-id> <api-key> <directory-to-upload> <commit-hash>", file=sys.stderr)
        sys.exit(1)

    project_id = sys.argv[1]
    api_key = sys.argv[2]
    file_dir = sys.argv[3]
    commit_sha = sys.argv[4]

    # Check if the provided directory exists
    if not os.path.isdir(file_dir):
        print(f"Error: Directory '{file_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # --- POPULATE FILE ARGUMENTS ---
    print(f"Collecting files from '{file_dir}'...")
    files_to_upload = {}
    open_files = []  # To store file handles for proper closing
    
    try:
        # Find all files in the directory
        file_paths = []
        for entry in os.listdir(file_dir):
            full_path = os.path.join(file_dir, entry)
            if os.path.isfile(full_path):
                file_paths.append(full_path)

        # Check if any files were actually found
        if not file_paths:
            print(f"No files found in '{file_dir}'. Nothing to upload.")
            sys.exit(0)

        # Prepare files for multipart upload
        for i, file_path in enumerate(file_paths, 1):
            field_name = f"file{i}"
            # Open file in binary read mode
            file_handle = open(file_path, 'rb')
            open_files.append(file_handle)
            # Add to the files dictionary
            files_to_upload[field_name] = (os.path.basename(file_path), file_handle)

        # --- PREPARE REQUEST ---
        url = f"https://dcodehub.com/api/projects/{project_id}/upload/"
        headers = {
            "X-API-Key": api_key,
            "X-Commit-ID": commit_sha,
            "X-Tool": "DPy"
        }

        print(f"Sending {len(files_to_upload)} file(s) to {url}...")

        # --- EXECUTE REQUEST ---
        response = requests.post(url, headers=headers, files=files_to_upload)

        # Check for HTTP errors (e.g., 404, 500)
        response.raise_for_status()

        # --- OUTPUT RESULTS ---
        print("Upload successful.")
        print(f"Server response: {response.text}")
        sys.exit(0)

    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP request failed with status code {e.response.status_code}.", file=sys.stderr)
        print(f"Server response (if any): {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed. Details: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure all file handles are closed
        for f in open_files:
            f.close()

if __name__ == "__main__":
    main()
```

### 7.4 Save and Exit

Press `Ctrl+X`, then `Y`, then `Enter`

### 7.5 Make Script Executable

```bash
chmod +x push_to_dcode.py
```

### 7.6 Verify Script Creation

```bash
ls -la
```

**Expected Output**:
```
drwxrwxr-x 2 student student 4096 Nov 26 xx:xx .
drwxrwxr-x 8 student student 4096 Nov 26 xx:xx ..
-rwxrwxr-x 1 student student 2456 Nov 26 xx:xx push_to_dcode.py
```

---

## Step 8: Clean Up Git Repository

**Purpose**: Remove unnecessary files from Git tracking and update `.gitignore`.

### 8.1 Navigate to Project Root

```bash
cd /home/student/HFXAIR/group01
```

### 8.2 Remove Python Cache Files from Tracking

```bash
git rm -r --cached flask_app/__pycache__
```

**Output**:
```
rm 'flask_app/__pycache__/__init__.cpython-310.pyc'
rm 'flask_app/__pycache__/app.cpython-310.pyc'
...
```

### 8.3 Update .gitignore

```bash
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
```

### 8.4 Verify .gitignore

```bash
cat .gitignore
```

**Expected Output**:
```
__pycache__/
*.pyc
.env
venv/
```

### 8.5 Configure Git User (if not already done)

```bash
git config --global user.email "your-email@dal.ca"
git config --global user.name "Your Name"
```

### 8.6 Commit the Cleanup

```bash
git add .gitignore
git commit -m "Remove pycache from tracking and add to gitignore"
```

### 8.7 Push to Main Branch

```bash
git push origin main
```

If you encounter a rejection error:
```bash
git pull origin main --rebase
git push origin main
```

---

## Step 9: Push Pipeline to Main Branch

**Purpose**: Add the CI/CD configuration files and push to main to trigger the pipeline.

### 9.1 Navigate to Project Root

```bash
cd /home/student/HFXAIR/group01
```

### 9.2 Ensure You're on Main and Updated

```bash
git checkout main
git pull origin main
```

### 9.3 Add All New Files

```bash
git add .gitlab-ci.yml
git add .quality/push_to_dcode.py
```

### 9.4 Verify Staged Files

```bash
git status
```

**Expected Output**:
```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   .gitlab-ci.yml
        new file:   .quality/push_to_dcode.py
```

### 9.5 Commit Changes

```bash
git commit -m "Add CI/CD pipeline with build, test, deploy, and code quality stages"
```

### 9.6 Push to Main Branch

```bash
git push origin main
```

**Output**:
```
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 2.15 KiB | 2.15 MiB/s, done.
Total 5 (delta 1), reused 0 (delta 0), pack-reused 0
To git.cs.dal.ca:courses/2025-Fall/csci-5308/group01.git
   xxxxxxx..xxxxxxx  main -> main
```

---

## Step 10: Verify Pipeline Execution

**Purpose**: Monitor and verify the pipeline runs successfully.

### 10.1 Open GitLab in Browser

Navigate to: `https://git.cs.dal.ca/courses/2025-Fall/csci-5308/group01`

### 10.2 Go to Pipelines

Click on **CI/CD** → **Pipelines**

### 10.3 View Pipeline Status

You should see a pipeline running with the following stages:
- **build** (running on vm-runner)
- **test** (waiting for build)
- **deploy** (waiting for test)
- **code-quality** (waiting for deploy)

### 10.4 Monitor Job Logs

Click on each job to view detailed logs:

**Build Stage Expected Output**:
```
Running on csci5308-vm1...
$ cd $CI_PROJECT_DIR/flask_app
$ source /home/student/venv/bin/activate
$ pip install -r requirements.txt
Requirement already satisfied: flask in /home/student/venv/lib/python3.10/site-packages
...
$ python -c "from flask_app.app import app; print('App loads successfully')"
App loads successfully
Job succeeded
```

**Test Stage Expected Output**:
```
Running on csci5308-vm1...
$ cd $CI_PROJECT_DIR/flask_app
$ source /home/student/venv/bin/activate
$ pip install pytest pytest-cov
$ pytest tests/ -v --tb=short --cov=. --cov-report=term
============================= test session starts =============================
collected X items
test_arrivals_departures.py::test_... PASSED
test_flight_details.py::test_... PASSED
...
---------- coverage: platform linux, python 3.10.x -----------
Name                      Stmts   Miss  Cover
---------------------------------------------
app.py                      XXX    XXX    XX%
...
---------------------------------------------
TOTAL                       XXX    XXX    XX%
============================= X passed in X.XXs =============================
Job succeeded
```

**Deploy Stage Expected Output**:
```
Running on csci5308-vm1...
$ echo "Syncing code to deployment directory..."
Syncing code to deployment directory...
$ rsync -av --delete --exclude='.git' --exclude='venv' --exclude='__pycache__' $CI_PROJECT_DIR/ /home/student/HFXAIR/group01/
sending incremental file list
./
flask_app/
flask_app/app.py
...
sent XXX bytes  received XXX bytes  XXX bytes/sec
total size is XXX  speedup is X.XX
$ sudo systemctl restart hfxair.service
$ echo "Deployment complete!"
Deployment complete!
Job succeeded
```

**Code Quality Stage Expected Output**:
```
Running on docker runner...
$ echo "Downloading DPy..."
Downloading DPy...
$ wget -q https://www.designite-tools.com/assets/DPy-linux.zip -O DPy.zip
$ python3 -m zipfile -e DPy.zip .
$ chmod +x DPy
$ echo "Running DPy on flask_app..."
Running DPy on flask_app...
$ mkdir -p smells/
$ ./DPy analyze -i $CI_PROJECT_DIR/flask_app -o $CI_PROJECT_DIR/smells/ -f csv
...
DPy analysis complete!
$ ls -la smells/
total XX
-rw-r--r-- 1 root root XXXX design_smells.csv
-rw-r--r-- 1 root root XXXX implementation_smells.csv
...
Job succeeded
```

### 10.5 Verify All Stages Passed

The pipeline should show green checkmarks for all stages:
- ✅ build
- ✅ test
- ✅ deploy
- ✅ run-dpy
- ✅ submit-dcode

### 10.6 View Test Coverage

In GitLab, you can view the test coverage percentage:
1. Go to **CI/CD** → **Pipelines**
2. Click on the pipeline
3. Look for the coverage badge or percentage displayed

---

## Pipeline Overview

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PIPELINE FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    Push to main branch                                                       │
│                          │                                                   │
│                          ▼                                                   │
│    ┌────────────────────────────────────────────────────────────────────┐   │
│    │                         STAGE 1: BUILD                              │   │
│    │  Runner: vm-runner (Shell on VM)                                    │   │
│    │  Commands:                                                          │   │
│    │    1. cd $CI_PROJECT_DIR/flask_app                                  │   │
│    │    2. source /home/student/venv/bin/activate                        │   │
│    │    3. pip install -r requirements.txt                               │   │
│    │    4. python -c "from flask_app.app import app; print('...')"       │   │
│    └────────────────────────────────────────────────────────────────────┘   │
│                          │                                                   │
│                    [Build Passes]                                            │
│                          │                                                   │
│                          ▼                                                   │
│    ┌────────────────────────────────────────────────────────────────────┐   │
│    │                         STAGE 2: TEST                               │   │
│    │  Runner: vm-runner (Shell on VM)                                    │   │
│    │  Commands:                                                          │   │
│    │    1. cd $CI_PROJECT_DIR/flask_app                                  │   │
│    │    2. source /home/student/venv/bin/activate                        │   │
│    │    3. pip install pytest pytest-cov                                 │   │
│    │    4. pytest tests/ -v --tb=short --cov=. --cov-report=term         │   │
│    │  Coverage: Extracts percentage using regex                          │   │
│    └────────────────────────────────────────────────────────────────────┘   │
│                          │                                                   │
│                    [Tests Pass]                                              │
│                          │                                                   │
│                          ▼                                                   │
│    ┌────────────────────────────────────────────────────────────────────┐   │
│    │                        STAGE 3: DEPLOY                              │   │
│    │  Runner: vm-runner (Shell on VM)                                    │   │
│    │  Commands:                                                          │   │
│    │    1. rsync -av --delete --exclude='.git' --exclude='venv'          │   │
│    │       --exclude='__pycache__' $CI_PROJECT_DIR/                      │   │
│    │       /home/student/HFXAIR/group01/                                 │   │
│    │    2. sudo systemctl restart hfxair.service                         │   │
│    └────────────────────────────────────────────────────────────────────┘   │
│                          │                                                   │
│                   [Deploy Success]                                           │
│                          │                                                   │
│                          ▼                                                   │
│    ┌────────────────────────────────────────────────────────────────────┐   │
│    │                    STAGE 4: CODE QUALITY                            │   │
│    │                                                                     │   │
│    │  Job 4a: run-dpy                                                    │   │
│    │  Runner: dalfcs_docker_kvm (Docker)                                 │   │
│    │  Image: python:3.10                                                 │   │
│    │  Commands:                                                          │   │
│    │    1. wget DPy-linux.zip                                            │   │
│    │    2. python3 -m zipfile -e DPy.zip .                               │   │
│    │    3. chmod +x DPy                                                  │   │
│    │    4. ./DPy analyze -i flask_app -o smells/ -f csv                  │   │
│    │  Artifacts: smells/ directory                                       │   │
│    │                          │                                          │   │
│    │                          ▼                                          │   │
│    │  Job 4b: submit-dcode                                               │   │
│    │  Runner: dalfcs_docker_kvm (Docker)                                 │   │
│    │  Image: python:3.10-alpine                                          │   │
│    │  Commands:                                                          │   │
│    │    1. pip install requests                                          │   │
│    │    2. python3 push_to_dcode.py (upload to DCodeHub)                 │   │
│    └────────────────────────────────────────────────────────────────────┘   │
│                          │                                                   │
│                          ▼                                                   │
│                   PIPELINE COMPLETE ✓                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages Summary

| Stage | Job | Runner | Purpose | Key Commands |
|-------|-----|--------|---------|--------------|
| Build | build | vm-runner | Install dependencies, verify app loads | `pip install`, `python -c "from flask_app.app import app"` |
| Test | test | vm-runner | Run pytest with coverage | `pytest tests/ --cov=.` |
| Deploy | deploy | vm-runner | Sync code, restart service | `rsync`, `systemctl restart` |
| Code Quality | run-dpy | dalfcs_docker_kvm | Analyze code smells | `./DPy analyze -f csv` |
| Code Quality | submit-dcode | dalfcs_docker_kvm | Upload to DCodeHub | `python3 push_to_dcode.py` |

---

## Troubleshooting

### Issue 1: Runner Not Picking Up Jobs

**Symptom**: Pipeline stuck with "This job is stuck because you don't have any active runners"

**Solution**:
```bash
# Check runner status
sudo gitlab-runner status

# Restart runner
sudo gitlab-runner restart

# Verify runner
sudo gitlab-runner verify
```

### Issue 2: Shell Profile Error

**Symptom**: `ERROR: Job failed: prepare environment: exit status 1`

**Solution**:
```bash
# Backup and remove .bash_logout
mv ~/.bash_logout ~/.bash_logout.bak
```

### Issue 3: Permission Denied for systemctl

**Symptom**: `sudo: a password is required`

**Solution**:
```bash
# Edit sudoers
sudo visudo

# Add this line at the end
student ALL=(ALL) NOPASSWD: /bin/systemctl restart hfxair.service
```

### Issue 4: rsync Command Not Found

**Symptom**: `bash: rsync: command not found`

**Solution**:
```bash
sudo apt-get update
sudo apt-get install rsync
```

### Issue 5: Build Stage - Module Import Error

**Symptom**: `ModuleNotFoundError: No module named 'flask_app'`

**Solution**: 
The `PYTHONPATH` variable in the pipeline should be set correctly:
```yaml
variables:
  PYTHONPATH: "${CI_PROJECT_DIR}"
```

If issues persist, check the import statement in the build job.

### Issue 6: DPy GLIBC Error

**Symptom**: `GLIBC_2.38 not found`

**Solution**: Use Docker runner (`dalfcs_docker_kvm`) instead of VM runner for code-quality jobs. This is already configured in the pipeline.

### Issue 7: DCodeHub Upload Failed

**Symptom**: `HTTP request failed with status code 403`

**Solution**:
1. Verify `DCODE_API_KEY` in GitLab CI/CD Variables
2. Verify `DCODE_PROJECT_ID` in GitLab CI/CD Variables
3. Check if API key has expired on DCodeHub

### Issue 8: Tests Failing

**Symptom**: pytest shows failed tests

**Solution**:
```bash
# Run tests locally to debug
cd /home/student/HFXAIR/group01/flask_app
source /home/student/venv/bin/activate
pytest tests/ -v
```

### Issue 9: Coverage Not Showing in GitLab

**Symptom**: No coverage percentage displayed in pipeline

**Solution**: Ensure the coverage regex matches your pytest output:
```yaml
coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `sudo gitlab-runner status` | Check if runner is running |
| `sudo gitlab-runner list` | List registered runners |
| `sudo gitlab-runner restart` | Restart the runner service |
| `sudo systemctl status hfxair.service` | Check Flask app status |
| `sudo systemctl restart hfxair.service` | Restart Flask app |
| `git status` | Check Git repository status |
| `git log --oneline -5` | View recent commits |
| `rsync --version` | Check rsync version |
| `pytest tests/ -v --cov=.` | Run tests with coverage locally |

---

## Summary

This CI/CD pipeline automates the following workflow:

1. **Build Stage**: Installs dependencies and verifies the Flask application loads correctly
2. **Test Stage**: Runs pytest test suite with coverage reporting
3. **Deploy Stage**: Syncs code to deployment directory using rsync and restarts the Flask service
4. **Code Quality Stage**: Analyzes code for design and implementation smells using DPy and uploads reports to DCodeHub

The pipeline triggers only on pushes to the `main` branch, ensuring continuous integration and deployment with code quality monitoring.

---
