# Wikidata Chat
## Usage
* Create a python virtual env and install the requirements.txt packages.
* Export your GOOGLE_APY_KEY as env variable.
* Run the ui.py file
* The Wikidata Chat must be running on http://localhost:7861

  
![Captura de tela 2024-06-27 094505](https://github.com/dimasjackson/langchain-wikibase-agent/assets/114688989/c6ba6f47-cd42-492e-b8af-e39fcbb7ace3)

![image](https://github.com/dimasjackson/langchain-wikibase-agent/assets/114688989/9191536b-83f9-4a1b-a75e-0cdd047d53e2)

This repository contains work on a langchain agent for question answering against a Wikidata or any local instance of Wikibase/Mediawiki.

We've added agents that can connect to locally running LLMs via Ollama, like Mixtral 70b and remote running via API like Google Gemini pro. Also, a simple chatbot user interface built with Gradio was added.

At present, this work is very preliminary, contributions are welcome! 

# Use in local Wikibase instance

To use in your local Wikibase instance change the base url in ``wikibase_agent.py`` and customize the WikidataAPIWrapper settings in ``langchain_com/utilities`` directory.
