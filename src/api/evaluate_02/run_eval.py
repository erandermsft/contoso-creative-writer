from orchestrator import plan, create
from evaluate_02.evaluators.influencer.evaluators_influencer import evaluate as influencer_evaluate 
import json
import uuid


def evaluate(input):
    
    # Generate a random GUID
    id = str(uuid.uuid4())

    influencer_evaluate(input, id)

