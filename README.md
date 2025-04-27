# BibTex AI 🎓📝

BibTex AI is an intelligent academic writing assistant that helps users generate structured LaTeX reports or Beamer presentations automatically from research papers.

It extracts key points, manages citations, formats according to a provided template, and generates professional LaTeX files — streamlining the research presentation workflow.

---

## ✨ Features

- 📄 Upload multiple **Research Papers (PDFs)**
- 🎨 Upload your desired **Format Template (PDF)** (e.g., IEEE Report or Beamer Presentation)
- 🧠 **Summarizes** research content using Groq LLM (DeepSeek Model)
- 📚 **Extracts citations** automatically using Google Gemini API
- 📂 Outputs a ready-to-use **LaTeX .tex file** (report or presentation)
- ⚡ Built with Python, LangChain, Streamlit

---

## 🚀 How to Set Up

1. Clone the repository

```bash
git clone https://github.com/abhishek2452002/BibTex_AI.git
cd BibTex_AI

2. Install requirements

pip install -r requirements.txt

3. Create a .env file in the project root

touch .env

Add your API keys inside .env:

GROQ=your_groq_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

4. Run the application

python -m streamlit run app.py

.

📂 Project Structure

BibTex_AI/
│
├── app.py                      # Streamlit web interface
├── .env                         # Your API keys (not pushed to GitHub)
├── .gitignore                   # Ignores .env, __pycache__, etc.
├── requirements.txt             # Python dependencies
│
├── src/
│   ├── agents/
│   │   ├── citation_agent.py    # Citation extraction (Gemini API)
│   │   ├── prompt_agent.py      # Prompt generation for LLM
│   │   └── report_generation_agent.py # LaTeX code generation
│   │
│   ├── llm/
│   │   └── llm_interface.py     # LLM (Groq/DeepSeek) interface
│   │
│   ├── utils/
│   │   ├── input_handler.py     # PDF processing
│   │   └── pdf_extractor.py     # (Helper for text extraction)
│   │
│   └── pipeline.py              # Main processing pipeline
│
└── Research_papers/             # Folder to put your research papers
└── Format/                      # Folder to put your format PDF (template)



🛡️ Security
.env is protected via .gitignore.

API keys are loaded securely at runtime.

No sensitive information is committed.


🧑‍💻 Author:
Abhishek
GitHub: abhishek2452002


⭐ Future Improvements
Add support for multiple output styles (ACM, Springer, etc.)

Add more customizable Beamer presentation layouts

Add option to edit extracted content before final generation

📢 Disclaimer
This tool is designed for academic assistance and learning purposes.
Please verify the final content and citations manually before official use.