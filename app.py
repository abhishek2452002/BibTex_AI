import streamlit as st
import os
import tempfile
import base64
import time
import sys
from PIL import Image
from io import BytesIO

# Add project root to path to enable imports
sys.path.append(os.path.abspath('.'))

# Import project components
try:
    from src.utils.input_handler import InputHandler
    from src.agents.prompt_agent import PromptAgent
    from src.agents.report_generation_agent import ReportGenerationAgent
    from src.agents.citation_agent import get_citations
except ImportError as e:
    st.error(f"Error loading project modules: {e}. Make sure the application is run from the project root directory.")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="BibTeX AI - Research Document Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the UI more appealing
st.markdown("""
<style>
    /* General Styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        animation: fadeIn 1.2s ease-in-out;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .card {
        border-radius: 10px;
        padding: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced intro card with better readability */
    .intro-card {
        background-color: #1E3A8A;
        color: white;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 1s ease-in-out;
    }
    .intro-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.2);
    }
    .intro-card h3 {
        color: #ffffff;
        font-size: 1.6rem;
        margin-bottom: 15px;
        font-weight: 600;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        padding-bottom: 10px;
    }
    .intro-card p {
        color: #f0f0f0;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .intro-card strong {
        color: #ffeb3b;
        font-weight: 600;
    }
    
    .success-box {
        background-color: #d1e7dd;
        border-left: 5px solid #198754;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        animation: slideIn 0.5s ease-out;
    }
    .info-text {
        color: #555;
        font-size: 0.9rem;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: 500;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0D2B76;
        transform: scale(1.05);
    }
    .stButton>button:active {
        transform: scale(0.98);
    }
    
    /* Format Selection Cards */
    .format-card {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        transition: all 0.3s ease;
        height: 100%;
        background-color: white;
    }
    .format-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .format-card.selected {
        border-color: #1E3A8A;
        background-color: #E6F0FF;
        box-shadow: 0 5px 15px rgba(30, 58, 138, 0.2);
    }
    .format-card.selected h4,
    .format-card.selected p {
        color: #000 !important;
    }
    .format-card h4 {
        margin-top: 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1E3A8A;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(30, 58, 138, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(30, 58, 138, 0); }
        100% { box-shadow: 0 0 0 0 rgba(30, 58, 138, 0); }
    }
    
    /* Progress animation */
    .progress-animation {
        animation: pulse 2s infinite;
    }
    
    /* Tab content padding */
    .tab-content {
        padding: 20px 0;
    }
    
    /* Upload indicators */
    .upload-success {
        color: #198754;
        display: inline-flex;
        align-items: center;
        animation: fadeIn 0.5s ease-out;
    }
    .upload-icon {
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)


def load_lottie_animation():
    """Generate a lottie animation for the sidebar"""
    return """
    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <lottie-player src="https://assets2.lottiefiles.com/packages/lf20_bdlckx53.json" background="transparent" speed="1" style="width: 100%; height: 200px;" loop autoplay></lottie-player>
    """


def create_download_link(file_path, link_text):
    """Create a download link for a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    
    b64_content = base64.b64encode(file_content.encode()).decode()
    filename = os.path.basename(file_path)
    return f"""
    <a href="data:application/x-tex;base64,{b64_content}" download="{filename}" 
       style="text-decoration:none;padding:10px 15px;background-color:#1E3A8A;color:white;border-radius:5px;
       display:inline-block;transition:all 0.3s ease;text-align:center;">
       <span style="display:inline-flex;align-items:center;justify-content:center;">
       <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
       style="margin-right:8px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
       <polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
       {link_text}</span>
    </a>
    """


def save_uploaded_file(uploaded_file, directory):
    """Save uploaded file to a temporary directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    temp_path = os.path.join(directory, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_path


def display_latex_content(latex_content, tab_title="Generated LaTeX"):
    """Display LaTeX content in a formatted way."""
    with st.expander(f"View {tab_title}", expanded=True):
        st.code(latex_content, language="latex")


def check_api_key():
    """Check if API key is provided in secrets or needs to be entered by user."""
    if 'GROQ' in os.environ:
        return os.environ['GROQ']
    else:
        return st.sidebar.text_input("Enter GROQ API Key", type="password")


def main():
    # Sidebar content
    with st.sidebar:
        st.markdown('<div style="padding:15px 0;">', unsafe_allow_html=True)
        
        # Logo with animation
        st.markdown("""
        <div style="text-align:center; animation: fadeIn 1s ease-in-out;">
            <h1 style="color:#1E3A8A;font-size: 48px;">BibTeX AI</h1>
            <p style="font-style:italic;">Intelligent Document Generation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Animated illustration
        st.markdown(load_lottie_animation(), unsafe_allow_html=True)
        
        # API Key input
        st.subheader("Configuration")
        api_key = check_api_key()
        
        # Project info
        st.markdown("### About")
        st.markdown("""
        BibTeX AI transforms research papers into formatted academic documents using AI technology.
        
        **Features:**
        - IEEE Reports
        - Beamer Presentations
        - Citation Extraction
        - AI-Powered Content Organization
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area
    st.markdown('<h1 class="main-header">📚 BibTeX AI Document Generator</h1>', unsafe_allow_html=True)
    
    # Hero section with illustration
    col1, col2 = st.columns([1, 2])
    with col1:
        # Display an illustration related to document generation
        st.image("https://img.freepik.com/free-vector/scientific-research-concept-illustration_114360-7378.jpg?w=900&t=st=1713383800~exp=1713384400~hmac=9f7d6ac6b6b3c3e7a8f1aa0d3d5651ca8e01be4ebcf1e9e87a7c4afb99a1edfc", 
                 use_column_width=True)
    
    with col2:
        # Enhanced intro card with better readability and contrast
        st.markdown("""
        <div class="intro-card">
            <h3>Transform Research Papers into Professional Documents</h3>
            <p>BibTeX AI uses advanced AI to analyze your research papers and generate perfectly formatted LaTeX documents 
            in either IEEE report format or Beamer presentation style, complete with proper citations.</p>
            <p><strong>How it works:</strong> Upload your research papers and a format template, select your desired 
            output format, and let BibTeX AI do the rest!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs with custom styling
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📄 Upload Papers", "🔍 Generated Output"])
    
    with tab1:
        # Paper upload section with appealing boxes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="sub-header">Research Papers</h3>', unsafe_allow_html=True)
            st.markdown('<div class="info-text">Upload one or more research papers in PDF format</div>', unsafe_allow_html=True)
            uploaded_research_papers = st.file_uploader(
                "Choose research paper PDFs",
                type="pdf",
                accept_multiple_files=True,
                key="research_papers"
            )
            
            if uploaded_research_papers:
                st.markdown(f"""
                <div class='upload-success'>
                    <span class='upload-icon'>✅</span> {len(uploaded_research_papers)} paper(s) uploaded
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h3 class="sub-header">Format Template</h3>', unsafe_allow_html=True)
            st.markdown('<div class="info-text">Upload a template for the output format</div>', unsafe_allow_html=True)
            uploaded_format = st.file_uploader(
                "Choose format PDF",
                type="pdf",
                key="format_pdf"
            )
            
            if uploaded_format:
                st.markdown("""
                <div class='upload-success'>
                    <span class='upload-icon'>✅</span> Template uploaded
                </div>
                """, unsafe_allow_html=True)
        
        # Output format selection with visual indicators
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h3 class="sub-header">Output Format</h3>', unsafe_allow_html=True)
        
        format_col1, format_col2 = st.columns(2)
        
        with format_col1:
            ieee_selected = st.radio(
                "Select output format",
                ["IEEE report", "Beamer presentation"],
                horizontal=False,
                key="output_format",
                label_visibility="collapsed"
            ) == "IEEE report"
            
            st.markdown(f"""
            <div class="format-card {'selected' if ieee_selected else ''}">
                <h4>IEEE Report Format</h4>
                <p>Formal academic paper format following IEEE standards.</p>
                <p><small>Perfect for journal submissions and conference papers.</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        with format_col2:
            beamer_selected = not ieee_selected
            
            st.markdown(f"""
            <div class="format-card {'selected' if beamer_selected else ''}">
                <h4>Beamer Presentation</h4>
                <p>Professional slide presentation format.</p>
                <p><small>Ideal for conferences and academic presentations.</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        output_format = "IEEE report" if ieee_selected else "Beamer presentation"
        
        # Process button section
        st.markdown("<br>", unsafe_allow_html=True)
        process_button_disabled = (
            not uploaded_research_papers or 
            not uploaded_format or 
            not api_key
        )
        
        # Center align the generate button
        st.markdown('<div style="display:flex;justify-content:center;">', unsafe_allow_html=True)
        generate_col = st.columns(3)[1]
        
        # Progress tracking
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        
        if 'output_file_path' not in st.session_state:
            st.session_state.output_file_path = None
            
        if 'latex_content' not in st.session_state:
            st.session_state.latex_content = None
            
        if 'output_format_used' not in st.session_state:
            st.session_state.output_format_used = None
        
        # Process button
        with generate_col:
            if st.button("🚀 Generate Document", disabled=process_button_disabled, use_container_width=True):
                if process_button_disabled:
                    st.warning("Please upload research papers, format template, and provide API key.")
                else:
                    # Create temporary directories
                    temp_dir = tempfile.mkdtemp()
                    research_dir = os.path.join(temp_dir, "Research_papers")
                    format_dir = os.path.join(temp_dir, "Format")
                    os.makedirs(research_dir, exist_ok=True)
                    os.makedirs(format_dir, exist_ok=True)
                    
                    try:
                        # Save uploaded files
                        research_paths = []
                        for paper in uploaded_research_papers:
                            paper_path = save_uploaded_file(paper, research_dir)
                            research_paths.append(paper_path)
                        
                        format_path = save_uploaded_file(uploaded_format, format_dir)
                        
                        # Show progress with custom styling
                        st.markdown('<div class="card progress-animation">', unsafe_allow_html=True)
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: Process inputs
                        status_text.markdown("🔍 **Processing input files...**")
                        progress_bar.progress(10)
                        time.sleep(0.5)  # Small delay for animation effect
                        
                        input_handler = InputHandler(research_paths, format_path)
                        processed_data = input_handler.process_inputs()
                        progress_bar.progress(30)
                        time.sleep(0.5)
                        
                        # Step 2: Extract citations
                        status_text.markdown("📚 **Extracting citations...**")
                        extracted_citations = get_citations(research_paths)
                        progress_bar.progress(50)
                        time.sleep(0.5)
                        
                        # Step 3: Generate content with LLM
                        status_text.markdown("🧠 **Generating document content with AI...**")
                        agent = PromptAgent(api_key)
                        llm_output = agent.get_response(
                            processed_data["research_papers"],
                            processed_data["format_requirements"],
                            extracted_citations,
                            output_format
                        )
                        progress_bar.progress(80)
                        time.sleep(0.5)
                        
                        # Step 4: Generate LaTeX document
                        status_text.markdown("📄 **Creating final LaTeX document...**")
                        report_agent = ReportGenerationAgent(temp_dir)
                        final_latex = report_agent.generate_latex_document(
                            llm_output, 
                            extracted_citations, 
                            output_format
                        )
                        
                        # Save LaTeX file
                        output_filename = "generated_report.tex" if "report" in output_format.lower() else "generated_presentation.tex"
                        output_path = os.path.join(temp_dir, output_filename)
                        
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(final_latex)
                        
                        # Store results in session state
                        st.session_state.output_file_path = output_path
                        st.session_state.latex_content = final_latex
                        st.session_state.processing_complete = True
                        st.session_state.output_format_used = output_format
                        
                        progress_bar.progress(100)
                        status_text.markdown("✅ **Document generation complete!**")
                        time.sleep(1)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Switch to results tab automatically
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"An error occurred during processing: {str(e)}")
                        st.session_state.processing_complete = False
                        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add input requirements if not all conditions are met
        if process_button_disabled:
            requirements = []
            if not uploaded_research_papers:
                requirements.append("❌ Research papers need to be uploaded")
            if not uploaded_format:
                requirements.append("❌ Format template needs to be uploaded")
            if not api_key:
                requirements.append("❌ API key needs to be provided")
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#fff3cd;border-left:5px solid #ffc107;padding:15px;border-radius:5px; color:#000000; /* or color: black */">
                    <h4 style="margin-top:0">Required to proceed:</h4>
                    <ul>{"".join([f"<li>{req}</li>" for req in requirements])}</ul>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.processing_complete and st.session_state.latex_content:
            output_format = st.session_state.output_format_used
            document_type = "IEEE Report" if "report" in output_format.lower() else "Beamer Presentation"
            
            st.markdown(f"""
            <div class="success-box">
                <h3 style="margin-top:0">✅ {document_type} Generated Successfully!</h3>
                <p>Your LaTeX document has been created and is ready for download.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Preview section - No unnecessary card, direct expander
            st.markdown(f"### 📄 {document_type} Preview", unsafe_allow_html=False)
            display_latex_content(st.session_state.latex_content, document_type)
            
            # Download section - No unnecessary card
            if st.session_state.output_file_path:
                st.markdown("### 💾 Download Your Document", unsafe_allow_html=False)
                
                filename = os.path.basename(st.session_state.output_file_path)
                download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
                with download_col2:
                    st.markdown(f"""
                    <div style="text-align:center;margin:20px 0;animation:pulse 2s infinite;">
                        {create_download_link(st.session_state.output_file_path, f"📥 Download {filename}")}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tips for using the generated file - No unnecessary card
                st.markdown("### 📝 How to Use Your LaTeX File", unsafe_allow_html=False)
                
                with st.expander("View Instructions", expanded=True):
                    st.markdown("""
                    ### Instructions for Using Your LaTeX Document
                    
                    1. **Download the generated LaTeX file** using the download button above
                    2. **Upload to an Online LaTeX Editor** like [Overleaf](https://www.overleaf.com) or open with your local LaTeX editor
                    3. **Compile the document**:
                       - For IEEE reports: Use `pdflatex` compiler 
                       - For Beamer presentations: Use `pdflatex` with Beamer support
                    4. **Review and edit** the content as needed before final use
                    5. **Check all citations** to ensure they're correctly formatted
                    
                    > **Note**: The document is ready to compile without additional packages!
                    """)
        else:
            st.markdown("""
            <div style="text-align:center;padding:50px 20px;background-color:#f8f9fa;border-radius:10px;margin-top:30px;
                      animation: fadeIn 1s ease-in-out;">
                <img src="https://img.freepik.com/free-vector/no-data-concept-illustration_114360-536.jpg?w=740&t=st=1713384380~exp=1713384980~hmac=e3d03339f2e3e7a2dac2e8c43be61cd8f1a831c6f4f5c32e45cb4e68e50361e0" style="max-width:250px;">
                <h3>No Document Generated Yet</h3>
                <p>Go to the "Upload Papers" tab to create a new document.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align:center;margin-top:30px;padding-top:20px;border-top:1px solid #ddd;font-size:0.8rem;color:#666;">
        <p>BibTeX AI | Research Document Generator | &copy; 2025</p>
        <p>Powered by GROQ and Gemini</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()