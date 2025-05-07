from promptflow.core import Prompty, AzureOpenAIModelConfiguration
import json
import os 
import logging
from prompty.tracer import trace
from openai import AzureOpenAI
from dotenv import load_dotenv 
from pathlib import Path
from prompty.tracer import trace
from pydantic import BaseModel

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.mcp import MCPSsePlugin, MCPWebsocketPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.utils.logging import setup_logging

import prompty
folder = Path(__file__).parent.absolute().as_posix()

class SocialMediaPost(BaseModel):
    customer: str
    socialMediaPost: str
class SocialMediaPosts(BaseModel):
    posts: list[SocialMediaPost]

system_prompt = """
system:
You are a social media influencer. Your job is to design a social media post tailored to a specific customer. 
You will have functions available to post the finished social media post, please do that if the post is good enough.
The social media post should be based on the contents of a blog article that has been created by our senior copywriter. Use emojis and other appropriate social media elements to make the post engaging and fun.
Respond in JSON format with an array of objects where each object contains the name of the customer and the social media post. Explicitly mention the customer's income level and how many products they can buy with their income.

## Customers
{customers}

# Article
Use the following article as context
{article}
# Additional instructions
{instructions}

# Output format
Only output the full array of social media posts. Its important that the output is a single JSON object with one key "posts".
Each post should should only contain two keys, customer and socialMediaPost, nothing else.
"""

customer = """
{name}

age: {demographic_age}

location: {demographic_location}

gender: {demographic_gender}

income: {incomeLevel}

interests:
{interests}
"""

load_dotenv()

@trace
def influence_old(article, customers, instructions):
    
    print("Influencing...")

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

    # create path to prompty file
    path_to_prompty = folder + "/influencer.prompty"

    # prompty_obj = Prompty.load(path_to_prompty, model=override_model)
    if customers == None:
       customers = json.loads(open(folder + "/customers.json").read())

# parameters={"response_format": SocialMediaPosts}
    result = prompty.execute("influencer.prompty",
                             inputs={"article":article, "customers": customers, "instructions": instructions})
    
    return result

@trace
def influence(article, customers, instructions):

    print("Influencing...")

    client = AzureOpenAI(
        azure_endpoint=os.getenv("APIM_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("APIM_SUBSCRIPTION_KEY"),
    )

    if customers == None:
       customers = json.loads(open(folder + "/customers.json").read())

    formatted_customers = []
    for customer_data in customers:
        interests = ""
        for interest in customer_data['interests']:
            interests += f"{interest} \n"

        formatted_customers.append(
           customer.format(name=customer_data['name'], 
                           demographic_age=customer_data['demographic']['age'],
                           demographic_location=customer_data['demographic']['location'], 
                           demographic_gender=customer_data['demographic']['gender'], 
                           incomeLevel=customer_data['incomeLevel'],
                           interests=interests))
        
    customers = "\n".join(formatted_customers)

    formattedSystemPrompt = system_prompt.format(customers=customers, article=article, instructions=instructions)

    messages = [
        {
            "role": "system",
            "content": formattedSystemPrompt,
        },
        {
            "role": "user",
            "content": "Please create the social media posts",
        }
    ]

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=messages,
        max_tokens=1200,
        temperature=0.2,
        response_format={ "type": "json_object" }
    )
    response_message = response.choices[0].message

    print('finished influencing...')

    return response_message.content

@trace
async def influence_sk(article, customers, instructions):
    setup_logging()
    
    logging.getLogger("kernel").setLevel(logging.DEBUG)
    logging.getLogger("semantic_kernel.connectors.mcp").setLevel(logging.DEBUG)

    print("Influencing...")

    kernel = Kernel()

    chat_completion = AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version="2024-12-01-preview",
        api_key=os.getenv("APIM_SUBSCRIPTION_KEY"),
        endpoint=os.getenv("APIM_ENDPOINT"),
    )

    kernel.add_service(chat_completion)
    
    request_settings = AzureChatPromptExecutionSettings(
        max_tokens=3000,
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        response_format={ "type": "json_object" }
    )

    mcpPlugin = MCPSsePlugin(
            name="PublisherTools",
            url=os.getenv("MCP_SERVER_URL") + "/sse",
        )
    
    await mcpPlugin.connect()

    kernel.add_plugin(mcpPlugin)

    if customers == None:
       customers = json.loads(open(folder + "/customers.json").read())

    formatted_customers = []
    for customer_data in customers:
        interests = ""
        for interest in customer_data['interests']:
            interests += f"{interest} \n"

        formatted_customers.append(
           customer.format(name=customer_data['name'], 
                           demographic_age=customer_data['demographic']['age'],
                           demographic_location=customer_data['demographic']['location'], 
                           demographic_gender=customer_data['demographic']['gender'], 
                           incomeLevel=customer_data['incomeLevel'],
                           interests=interests))
        
    customers = "\n".join(formatted_customers)

    formattedSystemPrompt = system_prompt.format(customers=customers, article=article, instructions=instructions)

    chatHistory = ChatHistory(system_message=formattedSystemPrompt)
    chatHistory.add_user_message("Please create the social media posts, if its good enough please use the PublisherTools to post it to social media")
    
    result = await chat_completion.get_chat_message_contents(
        chat_history=chatHistory,
        settings=request_settings,
        kernel=kernel,
    )

    await mcpPlugin.close()

    jsonContent = str(result[0].content)

    print('finished influencing...')

    return jsonContent


if __name__ == "__main__":

    result = influence(
        "Satya Nadella: A Symphony of Education and Innovation\n\nIn a world constantly reshaped by technology, Satya Nadella stands as a testament to the power of education as a launching pad for innovative leadership. Born on August 19, 1967, in Hyderabad, India, Nadella's journey from a middle-class family to the helm of Microsoft is a narrative of persistence, intellectual curiosity, and the transformative influence of education.\n\nThe formative phase of Nadella's education took root at the Hyderabad Public School, Begumpet, where he cultivated a passion for learning and a clear intellectual aptitude [Citation](https://www.educba.com/satya-nadella-biography/). This academic foundation soon spread its branches outward, reaching the Manipal Institute of Technology in Karnataka, India, where Nadella earned a bachelor's degree in electrical engineering in 1988 [Citation](https://en.wikipedia.org/wiki/Satya_Nadella).\n\nHowever, the essence of Nadella's educational prowess lies not merely in the degrees obtained but in his unwavering zeal for knowledge which propelled him across oceans. Post his undergraduate studies, Nadella pursued a Master's degree in Computer Science from the University of Wisconsin-Milwaukee and further, an MBA from the University of Chicago. This diverse educational landscape equipped him with a robust technical expertise, a strategic business acumen, and a global perspective—cornerstones of his leadership philosophy at Microsoft.\n\nNadella's educational journey emerges as a beacon of his career trajectory, exemplified in his ascension to becoming the executive vice president of Microsoft's cloud and enterprise group, and ultimately the CEO and Chairman of Microsoft [Citation](https://www.britannica.com/biography/Satya-Nadella). His leadership is a continual echo of his learnings, emphasizing the importance of continuous growth and the potential of technology to empower people and organizations across the globe.\n\nIn conclusion, the educational odyssey of Satya Nadella illuminates his career at Microsoft and beyond, underscoring the necessity of a strong educational foundation in molding the leaders who shape our digital futures.",
        "Research Feedback:\nAdditional specifics on how each phase of his education directly influenced particular career decisions or leadership styles at Microsoft would enhance the narrative. Information on key projects or initiatives that Nadella led, correlating to his expertise gained from his various degrees, would add depth to the discussion on the interplay between his education and career milestones.",
    )
    # parse string to json
    result = json.loads(result)
    print(result)