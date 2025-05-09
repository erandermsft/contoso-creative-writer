from typing import List, Literal, Union
from prompty.tracer import trace
from pydantic import BaseModel, Field
import logging
import json
import asyncio

# agents
from agents.researcher import researcher
from agents.product import product
from agents.writer import writer
from agents.publisher import publisher
# from agents.designer import designer
from agents.editor import editor
from agents.influencer import influencer
from agents.planner import planner
from evaluate.evaluators import evaluate_article_in_background
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer

types = Literal["message", "researcher", "marketing", "designer","writer", "editor", "error", "partial", "publishing", "influencer"]

class Message(BaseModel):
    type: types
    message: str | dict | None
    data: List | dict = Field(default={})

    def to_json_line(self):
        return self.model_dump_json().replace("\n", "") + "\n"

class Goal(BaseModel):
    goal: str

class Task(BaseModel):
    research: str 
    products: str 
    assignment: str
    influence: str 

DEFAULT_LOG_LEVEL = 25

def log_output(*args):
    logging.log(DEFAULT_LOG_LEVEL, *args)


def start_message(type: types):
    return Message(
        type="message", message=f"Starting {type} agent task..."
    ).to_json_line()

def complete_message(type: types, result):
    return Message(
        type=type, message=f"Completed {type} task", data=result
    ).to_json_line()


def error_message(error: Exception):
    return Message(
        type="error", message="An error occurred.", data={"error": str(error)}
    ).to_json_line()

def send_research(research_result):
    return json.dumps(("researcher", research_result))

def send_products(product_result):
    return json.dumps(("products", product_result))

def send_writer(full_result):
    return json.dumps(("writer", full_result))

def building_agents_message():
    return Message(
        type="message", message=f"Initializing Agent Service, please wait a few seconds..."
    ).to_json_line()

@trace
def plan(goal):
    # yield start_message("planner")
    plan_result = planner.plan(goal)
    return plan_result
    # yield complete_message("researcher", plan_result)

@trace
def create(research_context, product_context, assignment_context, influencer_context=None, evaluate=False, output_path=None):
    
    feedback = "No Feedback"

    yield building_agents_message()

    yield start_message("researcher")
    research_result = researcher.research(research_context, feedback)
    yield complete_message("researcher", research_result)

    yield start_message("marketing")
    product_result = product.find_products(product_context)
    yield complete_message("marketing", product_result)

    yield start_message("writer")
    yield complete_message("writer", {"start": True})
    writer_result = writer.write(
        research_context,
        research_result,
        product_context,
        product_result,
        assignment_context,
        feedback,
    )

    full_result = " "
    for item in writer_result:
        full_result = full_result + f'{item}'
        yield complete_message("partial", {"text": item})

    processed_writer_result = writer.process(full_result)

    # send article to the designer, to generate an image for the blog
    # yield start_message("designer")
    # designer_response = designer.design(processed_writer_result['article'])
    # yield complete_message("designer", [f"Image stored in {designer_response}"])

    # Then send it to the editor, to decide if it's good or not
    yield start_message("editor")
    editor_response = editor.editor_feedback(processed_writer_result['article'], processed_writer_result["feedback"])

    yield complete_message("editor", editor_response)
    yield complete_message("writer", {"complete": True})

    retry_count = 0
    while(str(editor_response["decision"]).lower().startswith("accept")):
        yield ("message", f"Sending editor feedback ({retry_count + 1})...")

        # Regenerate with feedback loop
        researchFeedback = editor_response.get("researchFeedback", "No Feedback")
        editorFeedback = editor_response.get("editorFeedback", "No Feedback")

        research_result = researcher.research(research_context, researchFeedback)
        yield complete_message("researcher", research_result)

        yield start_message("writer")
        yield complete_message("writer", {"start": True})
        writer_result = writer.write(research_context, research_result, product_context, product_result, assignment_context, editorFeedback)

        full_result = " "
        for item in writer_result:
            full_result = full_result + f'{item}'
            yield complete_message("partial", {"text": item})

        processed_writer_result = writer.process(full_result)

        # Then send it to the editor, to decide if it's good or not
        yield start_message("editor")
        editor_response = editor.editor_feedback(processed_writer_result['article'], processed_writer_result["feedback"])

        retry_count += 1
        if retry_count >= 2:
            break

        yield complete_message("editor", editor_response)
        yield complete_message("writer", {"complete": True})


    if evaluate:
        #these need to be yielded for calling evals from evaluate.evaluate
        yield send_research(research_result)
        yield send_products(product_result)
        yield send_writer(full_result) 
        print("Evaluating article...")
        evaluate_article_in_background(
            research_context=research_context,
            product_context=product_context,
            assignment_context=assignment_context,
            research=research_result,
            products=product_result,
            article=full_result,
        )
    
    # Send the article to the influencer
    if influencer_context:
        yield start_message("influencer")
        influencer_response = asyncio.run(influencer.influence_sk(article=processed_writer_result['article'], customers=None, instructions=influencer_context))
        #influencer_response = influencer.influence(article=processed_writer_result['article'], customers=None, instructions=influencer_context)
        influencer_response = json.loads(influencer_response)
        if influencer_response is not None and "posts" in influencer_response:
            influencer_response = influencer_response["posts"]
        else:
            influencer_response = "No influencer response"
        yield complete_message("influencer", influencer_response)


    # Store agent input and output if path is provided


    # yield start_message("publishing")
    # publisher_result = asyncio.run(publisher.publish(full_result))
    # yield complete_message("publishing", publisher_result)


@trace  
def test_create_article(research_context, product_context, assignment_context):
    for result in create(research_context, product_context, assignment_context):
        parsed_result = json.loads(result)
        if type(parsed_result) is dict:
            if parsed_result['type'] == 'researcher':
                print(parsed_result['data'])
            if parsed_result['type'] == 'marketing':
                print(parsed_result['data'])
            if parsed_result['type'] == 'editor':
                print(parsed_result['data'])
        if type(parsed_result) is list:
            if parsed_result[0] == "writer":
                article = parsed_result[1]
                print(f'Article: {article}')
    
if __name__ == "__main__":

    local_trace = PromptyTracer()
    Tracer.add("PromptyTracer", local_trace.tracer)
    research_context = "Can you find the latest camping trends and what folks are doing in the winter?"
    product_context = "Can you use a selection of tents and sleeping bags as context?"
    assignment_context = '''Write a fun and engaging article that includes the research and product information. 
    The article should be between 800 and 1000 words.
    Make sure to cite sources in the article as you mention the research not at the end.'''

    test_create_article(research_context=research_context, product_context=product_context, assignment_context=assignment_context)


def append_to_file(output_path: str, content: dict):
    """
    Append a dictionary as a JSON line to a JSONL file.
    
    Args:
        output_path: Path to the JSONL file
        content: Dictionary to append as a JSON line
    """
    # Convert the dictionary to a JSON string with newlines removed to maintain JSONL format
    json_line = json.dumps(content).replace("\n", "") + "\n"
    
    # Open the file in append mode, creating it if it doesn't exist
    with open(output_path, "a") as f:
        f.write(json_line)
