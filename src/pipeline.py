from src.utils.input_handler import InputHandler
from src.agents.prompt_agent import PromptAgent
from src.agents.report_generation_agent import ReportGenerationAgent
import os
from src.agents.citation_agent import get_citations
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

class ProcessingPipeline:
    """Pipeline that connects input handling to report generation."""

    # def __init__(self, api_key):
    #     self.api_key = api_key
    #     # Set default paths relative to project root
    #     self.research_papers_dir = os.path.join(os.path.dirname(__file__), "..", "Research_papers")
    #     self.format_dir = os.path.join(os.path.dirname(__file__), "..", "Format")
    def __init__(self, api_key):
        self.api_key = api_key
        base_path = os.path.dirname(os.path.dirname(__file__))  # Project root
        self.research_papers_dir = os.path.join(base_path, "Research_papers")
        self.format_dir = os.path.join(base_path, "Format")

    def _get_pdf_files(self, directory):
        """Get all PDF files from a directory."""
        pdf_files = []
        for file in os.listdir(directory):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(directory, file))
        return pdf_files

    def _get_output_format(self):
        """Prompt user to select output format."""
        while True:
            print("\nPlease select output format:")
            print("1. IEEE Report")
            print("2. Beamer Presentation")
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                return "IEEE report"
            elif choice == "2":
                return "Beamer presentation"
            else:
                print("Invalid choice. Please enter 1 or 2.")

    def run(self):
        """Runs the processing pipeline."""
        # Get output format from user
        output_format = self._get_output_format()
        
        # Step 1: Get research papers and format file
        try:
            research_papers = self._get_pdf_files(self.research_papers_dir)
            format_files = self._get_pdf_files(self.format_dir)
            
            if not research_papers:
                raise ValueError("No research papers found in Research_papers folder")
            if not format_files:
                raise ValueError("No format file found in Format folder")
            
            # Use first format file found
            format_pdf = format_files[0]
            
        except Exception as e:
            print(f"Error locating input files: {e}")
            return None

        # Step 2: Extract Text from PDFs
        input_handler = InputHandler(research_papers, format_pdf)
        processed_data = input_handler.process_inputs()

        # Step 3: Convert Extracted Text into LangChain Documents
        research_documents = processed_data["research_papers"]
        format_requirements = processed_data["format_requirements"]

        print("\nExtracted Research Content:")
        print("+" * 60)
        print("\n".join(doc.page_content[:200] + "..." for doc in research_documents))  # Show preview
        print("+" * 60)

        # Step 4: Extract Citations
        extracted_citations = get_citations(research_papers)
        print("\nExtracted Citations:")
        print("+" * 60)
        print(extracted_citations[:500] + "..." if len(extracted_citations) > 500 else extracted_citations)
        print("+" * 60)

        # Step 5: Generate Structured Prompt and Get LLM Response
        agent = PromptAgent(self.api_key)
        llm_output = agent.get_response(research_documents, format_requirements, extracted_citations, output_format)

        # Step 6: Generate Final LaTeX Document
        report_agent = ReportGenerationAgent()
        final_latex = report_agent.generate_latex_document(llm_output, extracted_citations, output_format)

        output_filename = "generated_report.tex" if "report" in output_format.lower() else "generated_presentation.tex"
        output_path = report_agent.save_latex_file(output_filename, final_latex)

        return output_path, output_format

# Example Usage
if __name__ == "__main__":
    api_key = os.getenv("GROQ")
    if not api_key:
        raise ValueError("Error: GROQ_API_KEY is missing.  Please set it in the .env file.")                                
    print("=== BibTeX AI Report Generator ===")
    pipeline = ProcessingPipeline(api_key)
    result, format_type = pipeline.run()
    
    if result:
        print(f"\nSuccessfully generated {format_type} at: {result}")
    else:
        print("\nFailed to generate output. Please check error messages.")