import fitz
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
# Load environment variables
load_dotenv()

# Configure Gemini API
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("Error: GOOGLE_API_KEY is missing. Please set it correctly.")

genai.configure(api_key=google_api_key)


def get_citations(research_papers: list):
    references = []
    text = ""
    for file_path in research_papers:   
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
            
    llm = genai.GenerativeModel('gemini-1.5-flash')
        
    prompt = f'''Extract 15 references from the following research paper:
    Research Paper:
    {text}

    Generate LaTeX code for the citations using the following format:
    \\bibitem{{key}} Author(s), "Title," Journal/Conference, vol., no., pp., year.

    Instructions:
    - Only include the \\bibitem entries
    - Return exactly 15 references
    - Each reference should be on its own line
    - Do not include any \\begin or \\end commands
    '''         
    response = llm.generate_content([prompt])
    response.resolve()
    citations = response.text
    
    # Clean and split into individual references
    citations = citations.replace('```latex', '').replace('```', '')
    citations = citations.replace('\\begin{thebibliography}{99}', '')
    citations = citations.replace('\\end{thebibliography}', '')
    references = [ref.strip() for ref in citations.split('\\bibitem') if ref.strip()]
    references = [f'\\bibitem{ref}' for ref in references][:15]  # Ensure exactly 15
    
    return references







