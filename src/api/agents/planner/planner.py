from promptflow.core import Prompty, AzureOpenAIModelConfiguration
import json
import os 
from dotenv import load_dotenv 
from pathlib import Path
from prompty.tracer import trace
folder = Path(__file__).parent.absolute().as_posix()


load_dotenv()
@trace
def plan(goal):
    
    # Load prompty with AzureOpenAIModelConfiguration override
    configuration = AzureOpenAIModelConfiguration(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_NAME')}.cognitiveservices.azure.com/"
    )
 
    override_model = {
        "configuration": configuration,
        # "parameters": {"max_tokens": 512}
    }
    path_to_prompty = folder + "/planner.prompty"
    agent_definitions = json.loads(open(folder + "/agent_definitions.json").read())

    prompty_obj = Prompty.load(path_to_prompty, model=override_model)
    result = prompty_obj(goal=goal, agent_definitions=agent_definitions)
    
    return result


if __name__ == "__main__":

    result = plan(
        "Write a comprehensive article titled 'A Complete Guide to Winter Camping' that incorporates both the research findings and product recommendations. The article should be informative, engaging, and between 800 to 1000 words long.",
    )
    # parse string to json
    result = json.loads(result)
    print(result)