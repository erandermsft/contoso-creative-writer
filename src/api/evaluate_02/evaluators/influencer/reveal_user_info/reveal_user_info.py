import json
import os
import prompty
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer
from dotenv import load_dotenv
load_dotenv()
from typing import TypedDict

class RevealUserInfoEvalOutput(TypedDict):
  aligned: str
  reason: str

@trace
def reveal_user_info_eval(    
      instructions_influencer: str,
      article: str,
      mediaPost: str,
) -> RevealUserInfoEvalOutput:

  # execute the prompty file
  model_config = {
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
        #"api_version": os.environ["AZURE_OPENAI_API_VERSION"],
        "api_key": os.environ["AZURE_OPENAI_API_KEY"],

  }

  result = prompty.execute(
    "C:/Users/albinlnnflt/OneDrive - Microsoft/Customer/scale_ai_2/contoso-creative-writer/src/api/evaluate_02/evaluators/influencer/reveal_user_info/reveal_user_info.prompty", 
    inputs={
      "instructions": instructions_influencer,
      "article": article,
      "mediaPost": mediaPost
    },
    configuration=model_config
  )

  # Parse the result string into a dictionary if it's a string
  if isinstance(result, str):
      result_dict = json.loads(result)
  else:
      result_dict = result

  return result_dict


if __name__ == "__main__":

  result = reveal_user_info_eval(
    instructions_influencer="You are a social media influencer. You are given an article and a media post. You need to evaluate if the media post is aligned with the article. If it is aligned, return 'aligned'. If it is not aligned, return 'not aligned'.",
    article="This is an article about the benefits of exercise.",
    mediaPost="This is a media post about the benefits of exercise."
  )

  print("Result:", result)
