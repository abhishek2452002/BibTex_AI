#llm_interface.py
from langchain.schema import HumanMessage
import os
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMInterface:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        api_key=os.getenv("GROQ")
    
    # other params...
)

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
    def generate_text(self, prompt):
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return response.content


    def generate_text(self, prompt):
        """
        Generates text using the LLM based on the given prompt.

        :param prompt: Input prompt string.
        :return: AI-generated response.
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])

        return response.content

# Example Usage:
if __name__ == "__main__":
    llm_interface = LLMInterface("test_api_key")
    response = llm_interface.generate_text("Write a summary of AI applications in healthcare.")