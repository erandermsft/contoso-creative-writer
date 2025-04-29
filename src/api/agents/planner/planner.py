import json
import os 
from openai import AzureOpenAI
from dotenv import load_dotenv 
from pathlib import Path
from prompty.tracer import trace
from azure.ai.inference.prompts import PromptTemplate

folder = Path(__file__).parent.absolute().as_posix()


load_dotenv()

@trace
def plan(goal):
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("APIM_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("APIM_SUBSCRIPTION_KEY"),
    )
    
    prompt_template = PromptTemplate.from_prompty(file_path="planner.prompty")

    messages = prompt_template.create_messages(goal=goal)

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=messages,
        max_tokens=prompt_template.parameters["max_tokens"],
        temperature=prompt_template.parameters["temperature"],
        response_format=prompt_template.parameters["response_format"],
    )

    result = response.choices[0].message.content
    result = json.loads(result)
    
    print(f"Result: {result}")

    return result


if __name__ == "__main__":

    result = plan(
        "Write a comprehensive article titled 'A Complete Guide to Winter Camping' that incorporates both the research findings and product recommendations. The article should be informative, engaging, and between 800 to 1000 words long.",
    )
    # parse string to json
    result = json.loads(result)
    print(result)