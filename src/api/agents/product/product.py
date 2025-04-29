import os
import json
from typing import Dict, List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from prompty.tracer import trace
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.ai.inference.prompts import PromptTemplate
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType,
)

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = "text-embedding-ada-002"
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_INDEX = "contoso-products"
APIM_ENDPOINT = os.getenv("APIM_ENDPOINT")
APIM_SUBSCRIPTION_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")

@trace
def generate_embeddings(queries: List[str]) -> str:

    client = AzureOpenAI(
        azure_endpoint=APIM_ENDPOINT,
        api_version=AZURE_OPENAI_VERSION,
        api_key=APIM_SUBSCRIPTION_KEY
    )

    embeddings = client.embeddings.create(input=queries, model="text-embedding-ada-002")
    embs = [emb.embedding for emb in embeddings.data]
    items = [{"item": queries[i], "embedding": embs[i]} for i in range(len(queries))]

    return items


@trace
def retrieve_products(items: List[Dict[str, any]], index_name: str) -> str:
    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=index_name,
        credential=DefaultAzureCredential(),
    )

    products = []
    for item in items:
        vector_query = VectorizedQuery(
            vector=item["embedding"], k_nearest_neighbors=3, fields="contentVector"
        )
        results = search_client.search(
            search_text=item["item"],
            vector_queries=[vector_query],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="default",
            query_caption=QueryCaptionType.EXTRACTIVE,
            query_answer=QueryAnswerType.EXTRACTIVE,
            top=2,
        )

        docs = [
            {
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "url": doc["url"],
            }
            for doc in results
        ]

        # Remove duplicates
        products.extend([i for i in docs if i["id"] not in [x["id"] for x in products]])

    return products


@trace
def find_products(context: str) -> Dict[str, any]:

    print("Finding products...")
    
    client = AzureOpenAI(
        azure_endpoint=APIM_ENDPOINT,
        api_version=AZURE_OPENAI_VERSION,
        api_key=APIM_SUBSCRIPTION_KEY
    )
    
    prompt_template = PromptTemplate.from_prompty(file_path="product.prompty")

    messages = prompt_template.create_messages(context=context)

    # Get product queries
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=messages,
        max_tokens=prompt_template.parameters["max_tokens"],
        response_format=prompt_template.parameters["response_format"],
    )
    queries = response.choices[0].message.content

    qs = json.loads(queries)
    print(f"Queries: {qs}")
    # Generate embeddings
    items = generate_embeddings(qs['queries'])
    # Retrieve products
    products = retrieve_products(items, "contoso-products")

    print("Products found:")
    for product in products:
        print(f"Product ID: {product['id']}")
        print(f"Title: {product['title']}")
        print(f"Content: {product['content']}")
        print(f"URL: {product['url']}")
        print()
    return products


if __name__ == "__main__":
    context = "Can you use a selection of tents and backpacks as context?"
    answer = find_products(context)
    print(json.dumps(answer, indent=2))
