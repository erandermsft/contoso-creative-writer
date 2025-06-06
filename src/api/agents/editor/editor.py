import json
import os 
from openai import AzureOpenAI
from dotenv import load_dotenv 
from prompty.tracer import trace
from azure.ai.inference.prompts import PromptTemplate
from pathlib import Path
folder = Path(__file__).parent.absolute().as_posix()

load_dotenv()

@trace
def editor_feedback(article, feedback):
    
    print('Starting editing feedback')

    client = AzureOpenAI(
        azure_endpoint=os.getenv("APIM_ENDPOINT"),
        api_version="2024-12-01-preview",
        api_key=os.getenv("APIM_SUBSCRIPTION_KEY"),
    )
    
    prompt_template = PromptTemplate.from_prompty(file_path="editor.prompty")

    messages = prompt_template.create_messages(article=article, feedback=feedback)

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_O3_MINI_DEPLOYMENT_NAME"),
        messages=messages,
        max_completion_tokens=prompt_template.parameters["max_tokens"],
        response_format=prompt_template.parameters["response_format"],
    )

    result = response.choices[0].message.content
    result = json.loads(result)
    
    print("Editing feedback completed")
    print(f"Result: {result}")

    return result


if __name__ == "__main__":

    result = editor_feedback(
        "Satya Nadella: A Symphony of Education and Innovation\n\nIn a world constantly reshaped by technology, Satya Nadella stands as a testament to the power of education as a launching pad for innovative leadership. Born on August 19, 1967, in Hyderabad, India, Nadella's journey from a middle-class family to the helm of Microsoft is a narrative of persistence, intellectual curiosity, and the transformative influence of education.\n\nThe formative phase of Nadella's education took root at the Hyderabad Public School, Begumpet, where he cultivated a passion for learning and a clear intellectual aptitude [Citation](https://www.educba.com/satya-nadella-biography/). This academic foundation soon spread its branches outward, reaching the Manipal Institute of Technology in Karnataka, India, where Nadella earned a bachelor's degree in electrical engineering in 1988 [Citation](https://en.wikipedia.org/wiki/Satya_Nadella).\n\nHowever, the essence of Nadella's educational prowess lies not merely in the degrees obtained but in his unwavering zeal for knowledge which propelled him across oceans. Post his undergraduate studies, Nadella pursued a Master's degree in Computer Science from the University of Wisconsin-Milwaukee and further, an MBA from the University of Chicago. This diverse educational landscape equipped him with a robust technical expertise, a strategic business acumen, and a global perspective—cornerstones of his leadership philosophy at Microsoft.\n\nNadella's educational journey emerges as a beacon of his career trajectory, exemplified in his ascension to becoming the executive vice president of Microsoft's cloud and enterprise group, and ultimately the CEO and Chairman of Microsoft [Citation](https://www.britannica.com/biography/Satya-Nadella). His leadership is a continual echo of his learnings, emphasizing the importance of continuous growth and the potential of technology to empower people and organizations across the globe.\n\nIn conclusion, the educational odyssey of Satya Nadella illuminates his career at Microsoft and beyond, underscoring the necessity of a strong educational foundation in molding the leaders who shape our digital futures.",
        "Research Feedback:\nAdditional specifics on how each phase of his education directly influenced particular career decisions or leadership styles at Microsoft would enhance the narrative. Information on key projects or initiatives that Nadella led, correlating to his expertise gained from his various degrees, would add depth to the discussion on the interplay between his education and career milestones.",
    )
    # parse string to json
    result = json.loads(result)
    print(result)