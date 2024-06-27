import os
import requests
import re
import argparse
import time
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent, create_openai_tools_agent
from langchain.agents import tool
from langchain.prompts import PromptTemplate
from langchain.globals import set_debug
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun

from wikibaseintegrator import wbi_helpers
from wikibaseintegrator.wbi_config import config as wbi_config


WB_LANGUAGE = 'en'
#WB_LANGUAGE = 'pt-br'
WB_LIMIT = 200
WB_USER_AGENT = 'MyWikibaseBot/1.0'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0'

def extract_error_message(response):
  pattern = re.compile(r'MalformedQueryException:(.*)\n')
  match = pattern.search(response.text)
  if match:
    return match.group(1).strip()
  else:
    return None

def performSparqlQuery(query: str) -> str:
  url = "https://query.wikidata.org/sparql"
  user_agent_header = WB_USER_AGENT

  query = str(query).lstrip('sparql').strip('\n').strip("'").strip('"').strip('`')

  headers = {"Accept": "application/json"}
  if user_agent_header is not None:
      headers["User-Agent"] = user_agent_header

  return requests.get(
      url, headers=headers, params={"query": query, "format": "json"}
  )

@tool
def WikidataRetrieval(item: str) -> str:
  """Returns all the information about the input Q item or property from my wikibase."""
  wikidata = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())

  return wikidata.run(item)

@tool
def checkSparql(query: str) -> str:
  """Given a SPARQL query check if is valid."""

  response = performSparqlQuery(query)

  if response.status_code != 200:
      error_message = extract_error_message(response)
      if error_message:
          return f'Query failed with this syntax error: {error_message}, try to fix it with another one.'
      else:
        return 'Query failed, try another one.'

#  print(f"Sparql results: {response.json()}")

  return 'Query is valid'

@tool
def runSparql(query: str) -> str:
  """Given a SPARQL query returns the results."""

  response = performSparqlQuery(str(query))

  if response.status_code != 200:
      error_message = extract_error_message(response)
      if error_message:
          return f'Query failed with this syntax error: {error_message}, try to fix it with another one.'
      else:
        return 'Query failed, try another one.'

  return response.json()

@tool
def getQItem(name: str) -> str:
  """Returns the Q item from my wikibase."""

  name = str(name).strip("'").strip('"')

  data = {
    'action': 'wbsearchentities',
    'search': name,
    'type': 'item',
    'language': WB_LANGUAGE,
    'limit': WB_LIMIT
  }
  result = wbi_helpers.mediawiki_api_call_helper(data=data, allow_anonymous=True)
  if result['search']:
      return result['search'][0]['id']
  else:
    return 'Item not found by this name, try another name.'

@tool
def getProperty(name: str) -> str:
  """Returns the property from my wikibase."""

  name = str(name).strip("'").strip('"')

  data = {
    'action': 'wbsearchentities',
    'search': name,
    'type': 'property',
    'language': WB_LANGUAGE,
    'limit': WB_LIMIT
  }
  result = wbi_helpers.mediawiki_api_call_helper(data=data, allow_anonymous=True)
  if result['search']:
    return result['search'][0]['id']
  else:
    return 'Property not found by this name, try another name.'

@tool
def runSparqlQuery(query: str) -> str:
  """Given a SPARQL query returns the results."""
  try:
    results = wbi_helpers.execute_sparql_query(query, max_retries=1)
    return results
  except Exception as e:
    return 'Query is not working, try another one.'

def load_prompt_file(full_path):
  with open(full_path, 'r') as f:
    txt_prompt = f.read()
  prompt = PromptTemplate.from_template(txt_prompt);
  return prompt


def answer_the_question(question):

  llm = ChatGoogleGenerativeAI(model="gemini-pro")

  tools = [getQItem, getProperty, checkSparql, runSparql, WikidataRetrieval]
  prompt = load_prompt_file('prompts/gemini.prompt')

  agent = create_react_agent(llm, tools, prompt)

  agent_executor = AgentExecutor(
          agent=agent,
          tools=tools, 
          verbose=True, 
          handle_parsing_errors=True,
          early_stop_method='generate',
          return_intermediate_steps=False,
          max_iteration=10
          )

  set_debug(False)

  result = agent_executor.invoke({"input": f"{question}"})
  return result

def parse_arguments():
    parser = argparse.ArgumentParser(description='Ask questions to Wikidata using the power of LLMs.')

    return parser.parse_args()

def main():
  args = parse_arguments()

  while True:
      query = input("\nEnter a query: ")
      if query == "exit":
          break
      if query.strip() == "":
          continue
      # Get the answer from the agent
      start = time.time()
      result = answer_the_question(query)
      end = time.time()
        
      start_readable = datetime.utcfromtimestamp(start)
      end_readable = datetime.utcfromtimestamp(end)


      # Print the result
      print("\n\n> Question:")
      print(query)
      print(result)
      print("start time:", start_readable)
      print("end time", end_readable)

if __name__ == '__main__':
  main()
