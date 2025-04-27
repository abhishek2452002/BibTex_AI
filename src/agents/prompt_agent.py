import sys
import os
import json
import logging
from langchain.schema import Document
import re

# Ensure the src directory is added to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.llm.llm_interface import LLMInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptAgent:
    """Agent to generate structured prompts for academic LaTeX output."""

    def __init__(self, api_key=None):
        self.llm = LLMInterface(api_key)

    def generate_prompt(self, research_papers: list[Document], format_requirements: str, citations: str, output_format: str) -> str:
        """
        Generates a structured prompt based on output format (IEEE or Beamer).
        """
        papers_text = "\n\n".join([
            f"Title: {doc.metadata.get('title', 'Unknown')}\n"
            f"Author: {doc.metadata.get('author', 'Unknown')}\n"
            f"Sections: {list(doc.metadata.get('sections', {}).keys())}\n"
            # f"Content:\n{doc.page_content[:500]}..."
            f"Content:\n{doc.page_content[:2000] + '...' if output_format.lower() == 'beamer' else doc.page_content[:8000] + '...'}"
            for doc in research_papers
        ])
        
        if output_format.lower() == "beamer":
            prompt = f"""
            You are an AI assistant that generates structured LaTeX content for Beamer presentations.
            Use the following research papers as references and format the output as per Format pdf submitted.
            Analyse the research papers to generate concise and informative content for the presentation.
            ONLY use the Format PDF to understand the layout and formatting structure. DO NOT copy or extract any content from the Format PDF.
            ALL CONTENT must be derived solely from the research papers. If the research papers do not provide specific details, generate meaningful content based on their insights, but NEVER use the Format PDF content.

            ******* Do not contents from the template *******
            === Research Papers ===
            {papers_text}

            === Template Format ===
            {format_requirements}

            Important additional instructions:
        - When mentioning concepts/findings from the research papers, include citations like: \\cite{{key}}
        - Only cite references that appear in the final bibliography
        - Each citation should correspond to a \\bibitem in the references
        - Example: "LLMs have improved task coordination\\cite{{Smith2020}}"
        - Ensure that the citations are relevant to the content and are not just placeholders.
        - Donot include any other irrelevant data in the output. such as the thinking of llm or any other data.

        Guidlines for  beamer content  generation:
        - Each section should contain a list of bullet points.
        - If a section has more points than can fit on a slide, split it into multiple slides.
        - Each slide must only contain maximum four bullet points.
        - The slides should not look like crowded with text.
        - Ensure the content is concise and informative.
        - Use the research papers as references to provide meaningful insights. 
        - Generate an appropriate title and the content after analysing the Research papers.
        - UNDER NO CIRCUMSTANCES should any content from the Format PDF be included in the output. The Format PDF is for layout reference only.
        - All generated content must be sourced from the Research Papers ONLY. If necessary, summarize or infer details based on the research papers.
        - If the research papers do not contain enough content, generate meaningful insights based on AI reasoning, but DO NOT take anything from the Format PDF.
        - Each page should only contain a few bullet points to maintain audience engagement.
        - Use the citations provided to reference the research papers.
        - each page must contain only a fixed number of citations. The reference section content should not go outside the slide.

        Generate structured LaTeX content in JSON format with the following keys:
        - "title": The title of the presentation.
        - "author": The author of the presentation.
        - "sections": A list of sections, where each section is a dictionary with "heading" and "content".
            The "content" must be a list of bullet points (not a single paragraph).No content in any section should go outside the slide each slide should only contain a fixed number of points so all the content remains inside the slide.
        - "citation": A list of citations where each citation is a dictionary wth key "citation" and value as the citation.
        Example:
        {{
            "title": "AI in Healthcare",
            "author": "AI Researcher",
            "sections": [
                {{"heading": "Introduction", "content": ["AI is transforming healthcare.", "Machine learning improves diagnostics."]}},
                {{"heading": "Challenges", "content": ["Data privacy concerns.", "High computational costs."]}}
            ],
            "citation": [ {"citation": ""}]

        }}

        Ensure the content is structured as a list of bullet points for each section.
        """.strip()
        else:
            prompt = f"""
            You are an AI assistant that generates structured LaTeX content for a research report.
            Use the following research papers as references and format the output as per the given requirements.

            === Research Papers ===
            {papers_text}

            === Required Format ===
            {format_requirements}

            Generate structured LaTeX content in JSON format with the following keys:
            - "title": The title of the report.
            - "author": The author of the report.
            - "abstract": A detailed abstract summarizing the report.
            - "sections": A list of sections, where each section is a dictionary with "heading" and "content".
            - Each section should be detailed and well-structured.
            - The final report must be at least **three full pages of LaTeX content**.
            - Ensure each section has enough content to meet this requirement.
            - If needed, add relevant analysis or discussions based on the research papers.
            - Do NOT generate less content than required.
            - Also mention each of the research papers based on there author or title and provide the insights mentioned in the input research papers in our final output and provide citation to it.**Its import to provide reference at places whereever the author is mentioned.**
            - Add relavent citaions  in the citations section in the following format.
                - Each citation should be in the format: "Author et al., Conference, Year"

            Example:
            {{
                "title": "AI in Healthcare",
                "author": "AI Researcher",
                "abstract": "This report explores the applications of AI in healthcare...",
                "sections": [
                    {{"heading": "Introduction", "content": "This is the introduction. It provides an overview of the topic..."}},
                    {{"heading": "Methodology", "content": "This section describes the methodology used in the study..."}},
                    {{"heading": "Results", "content": "This section presents the results of the experiments..."}},
                    {{"heading": "Conclusion", "content": "This section concludes the report and suggests future work..."}}
                ],
                
            }}

            Ensure the content is well-organized, detailed, and follows academic writing standards. i only want to see the output in JSON format. The thinking should not be in the output.
            """.strip()
        
        return prompt

    def clean_llm_json_response(self, llm_output, format_requirements):

        # Remove <think>...</think>
        llm_output = re.sub(r"<think>.*?</think>", "", llm_output, flags=re.DOTALL)

        # Check if LLM output contains any text from the Format PDF
        if format_requirements.strip() in llm_output:
            logger.warning("LLM output contains text from the Format PDF. Removing it...")
            llm_output = llm_output.replace(format_requirements.strip(), "")

        # Remove Markdown formatting
        return llm_output.replace("```json", "").replace("```", "")


    def get_response(self, research_papers, format_requirements, citations, output_format):
        """Gets AI-generated LaTeX output using the structured prompt."""
        logger.info("Generating prompt for LLM...")
        
        # Reset LLM memory (if applicable)
        self.llm = LLMInterface(self.llm.api_key)  # Reset LLM instance


        # Ensure format_requirements is set to a neutral instruction
        format_requirements = "This document provides layout guidelines. DO NOT use its content. Only follow its structure."

        prompt = self.generate_prompt(research_papers, format_requirements, citations, output_format)
        logger.info(f"Prompt: {prompt}")

        logger.info("Sending prompt to LLM...")
        llm_output = self.llm.generate_text(prompt)
        logger.info(f"Raw LLM output: {llm_output}")

        # Clean the JSON response
        llm_output = self.clean_llm_json_response(llm_output, format_requirements)

        # Parse the LLM output into a structured dictionary
        try:
            structured_output = json.loads(llm_output)  # Assuming the LLM returns JSON
            if not isinstance(structured_output, dict):
                raise json.JSONDecodeError("LLM output is not a dictionary.")
            logger.info("LLM output successfully parsed as JSON.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output as JSON: {e}")
            structured_output = {
                "title": "Generated Report" if output_format.lower() == "ieee" else "Generated Presentation",
                "author": "AI-generated",
                "sections": [{"heading": "Generated Content", "content": [llm_output]}],
                "citations": [{"citation": citations}]
            }

        return structured_output

