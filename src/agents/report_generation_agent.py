#report_generation_agent.py

import os

class ReportGenerationAgent:
    """Agent to generate structured LaTeX reports or Beamer presentations."""

    def __init__(self, output_dir="output"):
        """
        Initializes the ReportGenerationAgent.

        :param output_dir: Directory where generated LaTeX files will be saved.
        """
        self.output_dir = os.path.abspath(output_dir)  # Use absolute path
        os.makedirs(self.output_dir, exist_ok=True)  # Create the output directory if it does not exist

    def generate_latex_document(self, research_content, citations, output_format="IEEE"):
        """
        Generates and saves a LaTeX document in IEEE or Beamer format.

        :param research_content: Structured research content (can be a string or dictionary).
        :param citations: Formatted BibTeX citations.
        :param output_format: "IEEE" for IEEE paper, "Beamer presentation" for Beamer slides.
        :return: Path to the saved LaTeX file.
        """

        if output_format.lower() == "beamer presentation":
            latex_content = self._generate_beamer_presentation(research_content, citations)
        else:
            latex_content = self._generate_ieee_report(research_content, citations)

        if not latex_content.strip():
            print("WARNING: LaTeX content is empty! The file will not be saved.")

        return latex_content

 

    def _generate_ieee_report(self, research_content, citations):
        """Constructs an optimized IEEE-style LaTeX report."""

        # Process citations first
        if isinstance(citations, str) and citations.startswith('['):
            try:
                # Safely evaluate the string as a list
                import ast
                citations = ast.literal_eval(citations)
            except:
                citations = []
        
        # Convert citations to proper LaTeX format
        if isinstance(citations, list):
            formatted_citations = []
            for cite in citations:
                if cite.strip().startswith(r'\bibitem'):
                    formatted_citations.append(cite)
                else:
                    # Handle improperly formatted citations
                    try:
                        key = cite.split('{')[1].split('}')[0]
                        content = cite.split('}', 1)[1].strip()
                        formatted_citations.append(f"\\bibitem{{{key}}} {content}")
                    except:
                        continue
            citations = "\n".join(formatted_citations)
        else:
            citations = ""  # Fallback if citations are not in expected format

        # Rest of your report generation code remains the same
        if isinstance(research_content, str):
            title = "Generated Report"
            author = "AI-generated"
            abstract = research_content
            sections = [
                {"heading": "Introduction", "content": self._generate_introduction()},
                {"heading": "Background", "content": self._generate_background()},
                {"heading": "Methodology", "content": self._generate_methodology()},
                {"heading": "Results", "content": self._generate_results()},
                {"heading": "Discussion", "content": self._generate_discussion()},
                {"heading": "Conclusion", "content": self._generate_conclusion()},
            ]
        else:
            title = research_content.get("title", "Generated Report")
            author = research_content.get("author", "AI-generated")
            abstract = research_content.get("abstract", "No abstract provided.")
            sections = research_content.get("sections", [
                {"heading": "Introduction", "content": self._generate_introduction()},
                {"heading": "Background", "content": self._generate_background()},
                {"heading": "Methodology", "content": self._generate_methodology()},
                {"heading": "Results", "content": self._generate_results()},
                {"heading": "Discussion", "content": self._generate_discussion()},
                {"heading": "Conclusion", "content": self._generate_conclusion()},
            ])

        latex_sections = "\n".join(
            f"\\section{{{section['heading']}}}\n{section['content']}" for section in sections
        )

        return f"""
    \\documentclass[conference]{{IEEEtran}}
    \\IEEEoverridecommandlockouts
    \\usepackage{{cite, amsmath, amssymb, graphicx, xcolor}}
    \\begin{{document}}

    \\title{{{title}}}
    \\author{{{author}}}
    \\maketitle

    \\begin{{abstract}}
    {abstract}
    \\end{{abstract}}

    {latex_sections}

    \\bibliographystyle{{IEEEtran}}
    \\begin{{thebibliography}}{{99}}
    {citations}
    \\end{{thebibliography}}

    \\end{{document}}
    """.strip()


    def _generate_introduction(self):
        """Concise Introduction section."""
        return """Multi-agent systems (MAS) and large language models (LLMs) play key roles in automation and decision-making. 
        Their integration enhances task coordination and adaptability. This report explores their applications and efficiency improvements."""

    def _generate_background(self):
        """Concise Background section."""
        return """LLMs have been used to improve multi-agent collaboration in robotics, healthcare, and finance. Centralized approaches offer control, 
        but decentralized models scale better. Prior research highlights these trade-offs in real-world applications."""

    def _generate_methodology(self):
        """Concise Methodology section."""
        return """We compare centralized vs. decentralized LLM-based MAS using structured experiments. Evaluation metrics include accuracy, scalability, and communication efficiency.
        Simulated environments test performance across different agent configurations."""

    def _generate_results(self):
        """Concise Results section."""
        return """Results indicate that centralized LLMs excel in planning accuracy but struggle with scalability. Decentralized approaches handle large-scale collaboration better but introduce coordination challenges."""

    def _generate_discussion(self):
        """Concise Discussion section."""
        return """Findings suggest hybrid models could balance accuracy and scalability. Future improvements should focus on real-time decision-making and reducing computation overhead."""

    def _generate_conclusion(self):
        """Concise Conclusion section."""
        return """This study highlights the strengths and weaknesses of MAS-LLM integration. Future research should refine hybrid approaches for adaptive, scalable automation solutions."""





    def _generate_beamer_presentation(self, research_content, references):
        """Constructs a properly formatted Beamer presentation with bullet points."""
        title = research_content.get("title", "Generated Presentation")
        author = research_content.get("author", "AI-generated")
        sections = research_content.get("sections", [])
        
        def format_content_as_bullets(content):
            """Ensures content is formatted as bullet points."""
            if isinstance(content, str):  # Fallback for unexpected string content
                points = content.split(". ")
            elif isinstance(content, list):  # Expected bullet point format
                points = content
            else:
                points = []

            return "".join(f"\\item {point.strip()}\n" for point in points if point.strip())

        latex_sections = "".join(rf"""
        \section{{{s['heading']}}}
        \begin{{frame}}{{{s['heading']}}}
        \frametitle{{{s['heading']}}}
        \begin{{itemize}}
        {format_content_as_bullets(s['content'])}
        \end{{itemize}}
        \end{{frame}}
        """ for s in sections)
        
        if not sections:
            print("WARNING: No sections found in research content!")
            return ""  # Prevent writing an empty file

        # Split references into groups of 3 per slide
        ref_slides = []
        refs_per_slide = 3
        for i in range(0, len(references), refs_per_slide):
            slide_refs = references[i:i+refs_per_slide]
            ref_slides.append("\n".join(slide_refs))
        
        # Generate reference slides
        reference_slides = ""
        for i, slide_refs in enumerate(ref_slides, 1):
            reference_slides += rf"""
            \begin{{frame}}{{References (Part {i})}}
            \begin{{thebibliography}}{{99}}
            {slide_refs}
            \end{{thebibliography}}
            \end{{frame}}
            """
        
        return rf"""
        \documentclass{{beamer}}
        \usepackage[british]{{babel}}
        \usepackage{{graphicx, hyperref, algorithm, algpseudocode, subcaption}}
        \definecolor{{blueone}}{{RGB}}{{26,123,242}}
        \setbeamercolor{{titlelike}}{{bg=blueone}}
        \setbeamertemplate{{footline}}[frame number]
        
        \title{{{title}}}
        \author{{{author}}}
        
        \begin{{document}}
        \begin{{frame}}
        \titlepage
        \end{{frame}}
        
        \begin{{frame}}{{Table of Contents}}
        \tableofcontents
        \end{{frame}}
        
        {latex_sections}
        
        {reference_slides}
        
        \end{{document}}
        """.strip()    
    def save_latex_file(self, filename, latex_content):
        """Saves the generated LaTeX document to a file."""
        if not latex_content.strip():  # Check if content is empty
            print("WARNING: LaTeX content is empty. File will not be written.")
            return None  # Prevent saving an empty file
        
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(latex_content)
            print(f"File saved successfully: {file_path}")
            return file_path
        except Exception as e:
            print(f"ERROR: Failed to save file - {e}")
            return None

