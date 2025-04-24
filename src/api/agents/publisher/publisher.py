import json
import os
import asyncio
import logging
from dotenv import load_dotenv 
from pathlib import Path


from openai import AzureOpenAI, AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.mcp import MCPSsePlugin, MCPWebsocketPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.utils.logging import setup_logging

from opentelemetry import trace as oteltrace
from prompty.tracer import trace
import mcp
from mcp import types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
folder = Path(__file__).parent.absolute().as_posix()

load_dotenv()

systemMessage = """
# Publisher Agent
You are an publisher at a publishing company. You will have tools available to send the article to print. 
You output everything in JSON format. Here is an example:

Given an article you can respond as follows.

If the article is good enough to be published, you should call the tool for publish.

The following is examples of the JSON you should return:

{
  "decision": "publish",
  "publisherFeedback": "The article is well-written and informative. It meets our publication standards."
}

or if the article needs work or contains information that is not good to publish you reject the publish:
{
  "decision": "reject",
  "publisherFeedback": "The article contains some inaccuracies that need to be addressed before publication."
}

You should only **publish** or **reject** the article if you are sure about your decision.
It is **important** to **always** call the tool to publish the article if you decide to **publish** it.
You should also provide a response to the article if you publish it and suggest a response if you reject it in the
**publisherFeedback** field. **always** include the tool call in the **publisherFeedback** field if you decide to publish the article.
"""

input = """
This is the article to publish.
# Article
{article}
"""
@trace
async def publish(article):

    print('starting publishing article')

    result = await publish_article_sk(article)

    print('publishing article successfully completed')

    return result

@trace
async def publish_article_sdk(article):
    try:
        _streams_context = sse_client(url=os.getenv("MCP_SERVER_URL") + "/sse")

        streams = await _streams_context.__aenter__()

        _session_context = ClientSession(*streams)
        session = await _session_context.__aenter__()

        # Initialize
        await session.initialize()
        
        # List available tools
        response = await session.list_tools()
        tools = response.tools

        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in tools
        ]

        print(f"Connected to SSE MCP Server at {os.getenv("MCP_SERVER_URL")}/sse. Available tools: {[tool.name for tool in tools]}")

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        client = AsyncAzureOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_ad_token_provider=token_provider,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    
        formatedInput = input.format(article=article);

        messages = [
            {
                "role": "system",
                "content": systemMessage,
            },
            {
                "role": "user",
                "content": formatedInput,
            }
        ]

        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            max_tokens=4000,
            temperature=1,
            response_format={ "type": "json_object" }
        )
        response_message = response.choices[0].message
        messages.append(response_message)

        if response_message.tool_calls:
            print("Tool calls made by the model:")
            for tool_call in response_message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                print(f"Tool call ID: {tool_call.id}")
                print(f"Tool call function: {tool_call.function.name}")
                print(f"Tool call arguments: {function_args}")
                result = await session.call_tool(tool_call.function.name, function_args)
                print(f"Tool call result: {result}")
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": result.content,
                })
        else:
            json_r = json.loads(response_message.content)
            return json_r
        
        final_response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            max_tokens=1000,
            temperature=1,
            response_format={ "type": "json_object" }
        )

        final_response_message = final_response.choices[0].message
        messages.append(final_response_message)

        json_r = json.loads(final_response_message.content)
        print(f"Final response: {json_r}")
        return json_r
    except Exception as e:
        print(f"Error: {e}")
        result = {
            f"An exception occured: {str(e)}"
        }
        return result

@trace
async def publish_article_sk(article):
    setup_logging()

    logging.getLogger("kernel").setLevel(logging.DEBUG)
    logging.getLogger("semantic_kernel.connectors.mcp").setLevel(logging.DEBUG)

    kernel = Kernel()

    # token_provider = get_bearer_token_provider(
    #     DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    # )

    ctx = oteltrace.get_current_span().get_span_context()

    traceparent = f"00-{'{trace:032x}'.format(trace=ctx.trace_id)}-{'{span:016x}'.format(span=ctx.span_id)}-01"

    chat_completion = AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        #ad_token_provider=token_provider,
        api_version="2024-12-01-preview",
        api_key=os.getenv("APIM_SUBSCRIPTION_KEY"),
        endpoint=os.getenv("APIM_GATEWAY_URL"),
        default_headers={
            "traceparent": traceparent
        }
    )

    kernel.add_service(chat_completion)
    
    request_settings = AzureChatPromptExecutionSettings(
        temperature=1,
        max_tokens=4000,
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        response_format={ "type": "json_object" },
        #tool_choice="auto"
    )

    mcpPlugin = MCPSsePlugin(
            name="PublisherTools",
            url=os.getenv("MCP_SERVER_URL") + "/sse",
            headers={
                "traceparent": traceparent
            },
        )
    
    await mcpPlugin.connect()

    kernel.add_plugin(mcpPlugin)
    
    formatedInput = input.format(article=article);

    chatHistory = ChatHistory(system_message=systemMessage)
    chatHistory.add_user_message(formatedInput)
    
    result = await chat_completion.get_chat_message_contents(
        chat_history=chatHistory,
        settings=request_settings,
        kernel=kernel,
    )

    await mcpPlugin.close()

    jsonContent = str(result[0].content)
    json_r = json.loads(jsonContent)

    print(f"Final response: {json_r}")
    return json_r



if __name__ == "__main__":

    result = asyncio.run(publish(
        "Satya Nadella: A Symphony of Education and Innovation\n\nIn a world constantly reshaped by technology, Satya Nadella stands as a testament to the power of education as a launching pad for innovative leadership. Born on August 19, 1967, in Hyderabad, India, Nadella's journey from a middle-class family to the helm of Microsoft is a narrative of persistence, intellectual curiosity, and the transformative influence of education.\n\nThe formative phase of Nadella's education took root at the Hyderabad Public School, Begumpet, where he cultivated a passion for learning and a clear intellectual aptitude [Citation](https://www.educba.com/satya-nadella-biography/). This academic foundation soon spread its branches outward, reaching the Manipal Institute of Technology in Karnataka, India, where Nadella earned a bachelor's degree in electrical engineering in 1988 [Citation](https://en.wikipedia.org/wiki/Satya_Nadella).\n\nHowever, the essence of Nadella's educational prowess lies not merely in the degrees obtained but in his unwavering zeal for knowledge which propelled him across oceans. Post his undergraduate studies, Nadella pursued a Master's degree in Computer Science from the University of Wisconsin-Milwaukee and further, an MBA from the University of Chicago. This diverse educational landscape equipped him with a robust technical expertise, a strategic business acumen, and a global perspective—cornerstones of his leadership philosophy at Microsoft.\n\nNadella's educational journey emerges as a beacon of his career trajectory, exemplified in his ascension to becoming the executive vice president of Microsoft's cloud and enterprise group, and ultimately the CEO and Chairman of Microsoft [Citation](https://www.britannica.com/biography/Satya-Nadella). His leadership is a continual echo of his learnings, emphasizing the importance of continuous growth and the potential of technology to empower people and organizations across the globe.\n\nIn conclusion, the educational odyssey of Satya Nadella illuminates his career at Microsoft and beyond, underscoring the necessity of a strong educational foundation in molding the leaders who shape our digital futures.",
    ))
    # parse string to json
    result = json.loads(result)
    print(result)
