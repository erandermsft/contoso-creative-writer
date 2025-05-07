from azure.ai.evaluation import evaluate
import os
import sys
import pandas as pd
import ast
import argparse
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from reveal_user_info.reveal_user_info import reveal_user_info_eval
from mention_competitor.mention_competitor_eval import mention_competitor_eval

from azure.ai.evaluation import FluencyEvaluator, CoherenceEvaluator, ProtectedMaterialEvaluator
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration



# If you want to use Azure AI Foundry
"""
azure_ai_project = {
    "subscription_id": "a9e36d3f-2f31-4258-b33f-d805e08511bd",
    "resource_group_name": "rg-demo-01",
    "project_name": "contoso_ecommer",
}
"""


model_config = AzureOpenAIModelConfiguration(
    type="azure_openai",
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)



def evaluate_influencer(input, output_path, id):
    result_eval = evaluate(
        data=input,
        evaluators={
            "reveal_user_info_eval": reveal_user_info_eval,
            "mention_competitor_eval": mention_competitor_eval,
            "fluency": FluencyEvaluator(model_config),
        },
        evaluator_config={
            "fluency": {
                "column_mapping": {
                    "response": "${data.mediaPost}",
                },
            },
            "reveal_user_info_eval": {
                "instructions_influencer": "${data.instructions_influencer}",
                "article": "${data.article}",
                "mediaPost": "${data.mediaPost}",
            },
            "mention_competitor_eval": {
                "mediaPost": "${data.mediaPost}",
            },

        },
        #azure_ai_project=azure_ai_project
    )

    eval_result = pd.DataFrame(result_eval["rows"])

    save_eval_result(eval_result, output_path, id)

    return eval_result


def save_eval_result(eval_result, output_path, id):
    """
    Save evaluation results as a CSV file in a dedicated directory.
    
    Args:
        eval_result (pd.DataFrame): Evaluation results to save
        output_path (str): Base path for output files
        id (str): Unique identifier for this evaluation run
    """
    # Create a dedicated directory for this evaluation run
    eval_dir = os.path.join(output_path, id)
    os.makedirs(eval_dir, exist_ok=True)
    
    # Save the evaluation result to a CSV file inside the created directory
    csv_filename = f"eval_result_{id}.csv"
    csv_path = os.path.join(eval_dir, csv_filename)
    eval_result.to_csv(csv_path, index=False)
    
    print(f"Evaluation results saved to: {csv_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Evaluate influencer')
    parser.add_argument('--input_path', type=str, default="src/api/evaluate_02/data/agents_results/agent_result.jsonl")
    parser.add_argument('--output_path', type=str, default="src/api/evaluate_02/data/eval_result")

    args = parser.parse_args()

    evaluate_influencer(args.input_path, args.output_path, "test_id")


