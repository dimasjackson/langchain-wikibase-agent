import gradio as gr
import wikibase_agent
from wikibase_agent import answer_the_question
import os

LANGCHAIN_TRACING_V2=os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_API_KEY=os.getenv('LANGCHAIN_API_KEY')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

def result(question, history):
    answer = answer_the_question(question)
    return answer['output']

chat = gr.ChatInterface(
    result, 
    chatbot=gr.Chatbot(height=300),
    title="Wikidata Chat ✨",
    description="Ask a question to Wikidata!",
    theme="soft",
    examples=['What is the USA GDP?', 'What is the population of São Paulo', "Who is Albert Einstein?"],
    cache_examples=False,
    undo_btn="⬅️ Undo",
    clear_btn="🗑️ Clean",
    )

if __name__ == "__main__":
    chat.launch(server_name="10.0.2.88",server_port=7861)
