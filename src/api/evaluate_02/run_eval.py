from orchestrator import plan, create
import json

def run_agent_system(input):
    # Rename the variable to avoid naming conflict with the function
    plan_result = plan(input)

    result_generator = create(
        research_context=plan_result["research_context"],
        product_context=plan_result["product_context"],
        assignment_context=plan_result["assignment_context"],
        influencer_context=plan_result["influencer_context"],
    )
    
    # Initialize dictionary to store results from each agent
    agent_results = {
        "researcher": None,
        "marketing": None,  # This is the product/find_products agent
        "writer": {
            "content": "",
            "complete": False
        },
        "editor": None,
        "influencer": None,
        "publisher": None
    }
    
    # Process each yielded message from the generator
    for result in result_generator:
        parsed_result = json.loads(result)
        
        # Handle dictionary results (most agents)
        if isinstance(parsed_result, dict):
            result_type = parsed_result.get('type')
            
            # Store researcher results
            if result_type == "researcher":
                agent_results["researcher"] = parsed_result.get('data')
            
            # Store marketing/product results
            elif result_type == "marketing":
                agent_results["marketing"] = parsed_result.get('data')
            
            # Handle writer status updates
            elif result_type == "writer":
                if parsed_result.get('data', {}).get('complete'):
                    agent_results["writer"]["complete"] = True
            
            # Store partial content from writer
            elif result_type == "partial":
                text_chunk = parsed_result.get('data', {}).get('text', '')
                agent_results["writer"]["content"] += text_chunk
            
            # Store editor results
            elif result_type == "editor":
                agent_results["editor"] = parsed_result.get('data')
            
            # Store influencer results
            elif result_type == "influencer":
                agent_results["influencer"] = parsed_result.get('data')
                
            # Store publishing results
            elif result_type == "publishing":
                agent_results["publisher"] = parsed_result.get('data')
        
        # Handle list format results
        elif isinstance(parsed_result, list) and len(parsed_result) >= 2:
            if parsed_result[0] == "writer":
                agent_results["writer"]["content"] = parsed_result[1]
    
    return agent_results


def evaluate