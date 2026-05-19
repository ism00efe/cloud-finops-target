# Autonomous Cloud FinOps Agent

 **Live Demo:** [FinOps Agent](https://cloud-finops-target-2qm5afamxndg5sj66egggc.streamlit.app/)

A human-in-the-loop (HITL) optimization engine that analyzes cloud infrastructure metrics and autonomously modifies Terraform configurations via GitLab APIs to reduce costs.

## Tech Stack
* **AI/LLM Engine:** Google Gemini 2.5 Flash
* **Interface:** Streamlit
* **Infrastructure Management:** Terraform (HCL)
* **Version Control & CI/CD:** GitLab API

## Architecture & Workflow

The system bridges the gap between autonomous AI decision-making and strict infrastructure security constraints.

1.  **State Ingestion:** Pulls current AWS resource utilization data and fetches the active `main.tf` state from the remote repository.
2.  **Constraint-Aware Analysis:** An LLM evaluates the state against strict FinOps rules (e.g., modifying underutilized Staging instances, tagging Development environments for scheduling, and strictly ignoring Production resources).
3.  **Human-in-the-Loop:** Halts execution and presents a financial impact analysis alongside proposed infrastructure changes on a Streamlit dashboard.
4.  **GitOps Execution:** Upon manual approval, creates a unique branch and opens a standardized Merge Request in GitLab containing the updated Terraform code.

## Future Roadmap

While the core MVP demonstrates the feasibility of LLM-driven infrastructure management, planned Phase 2 features include:

* **Granular Action Approval:** Transitioning from bulk Merge Requests to a modular system where engineers can selectively approve or reject individual AI-proposed changes before the final Terraform state is generated.
* **Secondary Audit Agent:** Implementing a Multi-Agent architecture where an independent auditor model reviews the primary agent's output for compliance violations before human review.

## Setup Instructions

**Prerequisites:** Python 3.9+

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables
# Create a .env file with the following keys:
GEMINI_API_KEY=your_gemini_api_key
GITLAB_TOKEN=your_gitlab_personal_access_token
GITLAB_PROJECT_ID=your_gitlab_project_id

# 4. Initialize the Dashboard
streamlit run app.py
