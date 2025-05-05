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

model_config = {
      "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
      #"api_version": os.environ["AZURE_OPENAI_API_VERSION"],
      "api_key": os.getenv("AZURE_OPENAI_API_KEY"),

}

class CompetitorEvalOutput(TypedDict):
  aligned: str
  reason: str

@trace
def mention_competitor_eval(
      mediaPost: str,
) -> CompetitorEvalOutput:

  result = prompty.execute(
    "mention_competitor.prompty", 
    inputs={
      "mediaPost": mediaPost
    },
    configuration=model_config
  )

  if isinstance(result, str):
      result_dict = json.loads(result)
  else:
      result_dict = result

  return result_dict

if __name__ == "__main__":

  result = mention_competitor_eval(
    mediaPost="This is a media post about the benefits of exercise."
  )

  print("Result:", result)

