from azure.ai.evaluation import evaluate
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from reveal_user_info.reveal_user_info import reveal_user_info_eval
from mention_competitor.mention_competitor_eval import mention_competitor_eval


# If you want to use Azure AI Foundry
"""
azure_ai_project = {
    "subscription_id": "",
    "resource_group_name": "rg-demo-01",
    "project_name": "ai-project",
}
"""

def evaluate_influencer(input, id):
    result_eval = evaluate(
        data=input,
        evaluators={
            "reveal_user_info_eval": reveal_user_info_eval,
            "mention_competitor_eval": mention_competitor_eval,
        },
        evaluator_config={
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

    print("Evaluation result:", result_eval)


if __name__ == "__main__":
    input = "C:/Users/albinlnnflt/OneDrive - Microsoft/Customer/scale_ai_2/contoso-creative-writer/src/api/evaluate_02/data/agents_results/agent_result.jsonl"
    evaluate_influencer(input, "test_id")