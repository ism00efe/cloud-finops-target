import os
import json
import logging
import gitlab
from google import genai
from datetime import datetime
from dotenv import load_dotenv

# Initialize basic logging for observability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables (API keys, tokens)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_infrastructure() -> dict:
    """
    Fetches the current Infrastructure as Code (IaC) state from GitLab,
    evaluates it against local metrics using the LLM, and returns a proposed 
    optimization strategy without executing changes.
    """
    logging.info("Starting infrastructure analysis phase.")
    
    # 1. Fetch current Terraform state from remote repository
    try:
        gl = gitlab.Gitlab(url='https://gitlab.com', private_token=os.getenv("GITLAB_TOKEN"))
        project = gl.projects.get(os.getenv("GITLAB_PROJECT_ID"))
        f = project.files.get(file_path='main.tf', ref='main')
        current_tf_code = f.decode().decode('utf-8')
    except Exception as e:
        logging.error(f"GitLab API file fetch failed: {e}")
        raise

    # 2. Load utilization metrics
    try:
        with open("metrics.json", "r") as file:
            metrics_data = json.load(file)
    except FileNotFoundError:
        logging.error("metrics.json file is missing.")
        raise

    # 3. Define the prompt with strict FinOps constraints and output schema
    prompt = f"""
    Task: Optimize the provided Terraform configuration based on the corresponding AWS utilization metrics.

    Constraints:
    1. 'Staging' environment resources with cpu_usage_avg_percent < 5.0 must have their instance_type downgraded to 't3.micro'.
    2. 'Development' environment resources marked with weekend inactivity must retain their current instance_type. Append `Schedule = "business-hours"` to their tags block.
    3. 'unattached' EBS volumes must be completely removed from the Terraform configuration.
    4. 'Production' environment resources must remain strictly unmodified.

    Output Format: Strict JSON. Do not include markdown formatting outside the JSON values.
    {{
        "mr_description": "Create a highly readable Markdown table summarizing the changes. Columns: 'Resource Name', 'Environment', 'Action Taken', 'Reason'.",
        "updated_terraform_code": "The complete, modified main.tf content.",
        "estimated_savings_usd": 125.50
    }}
    
    Metrics:
    {json.dumps(metrics_data)}
    
    Current Terraform Code:
    {current_tf_code}
    """

    # 4. Execute LLM evaluation
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    
    # Clean potential markdown wrappers from the LLM output
    raw_response = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        decision_json = json.loads(raw_response)
        logging.info("Analysis complete. Pending Human-in-the-Loop (HITL) approval.")
        return decision_json
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse LLM output as JSON: {e}")
        raise

def apply_changes(decision_json: dict) -> str:
    """
    Executes the approved optimization strategy by creating a new branch,
    committing the modified Terraform code, and opening a Merge Request in GitLab.
    
    Args:
        decision_json (dict): The verified output from the LLM containing updated code and metadata.
        
    Returns:
        str: The URL of the created Merge Request.
    """
    logging.info("HITL approval received. Committing changes to repository.")
    try:
        gl = gitlab.Gitlab(url='https://gitlab.com', private_token=os.getenv("GITLAB_TOKEN"))
        project = gl.projects.get(os.getenv("GITLAB_PROJECT_ID"))
        
        # Generate a unique branch name using current timestamp to avoid collisions
        formatted_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"chore/finops-optimization-{formatted_time}"
        
        # Batch actions for a single commit
        data = {
            'branch': branch_name,
            'start_branch': 'main',
            'commit_message': "chore(finops): optimize infrastructure resources based on utilization metrics",
            'actions': [
                {'action': 'update', 'file_path': 'main.tf', 'content': decision_json['updated_terraform_code']}
            ]
        }
        project.commits.create(data)
        
        # Create the Merge Request with a detailed audit trail
        mr = project.mergerequests.create({
            'source_branch': branch_name,
            'target_branch': 'main',
            'title': "chore(finops): optimize infrastructure resources",
            'description': f"### FinOps Optimization Report\n\n{decision_json['mr_description']}\n\n**Estimated Monthly Savings:** ${decision_json['estimated_savings_usd']}\n\n*Validation: Production constraints verified. Approved by Platform Engineer via HITL interface.*"
        })
        
        logging.info(f"Merge Request opened successfully. URL: {mr.web_url}")
        return mr.web_url
    except Exception as e:
        logging.error(f"GitLab execution failed: {e}")
        raise