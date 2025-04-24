import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
import time
import difflib
import html
import groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from code_analyzer import analyze_cpp_code, generate_diff
from code_suggester import generate_code_suggestions

# Set page configuration
st.set_page_config(
    page_title="C++ Code Iterator for Game Developers",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stTextInput, .stTextArea {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .code-container {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 10px;
        font-family: 'Courier New', monospace;
    }
    .explanation-container {
        background-color: #3D3D3D;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
    }
    .diff-add {
        background-color: rgba(0, 255, 0, 0.2);
    }
    .diff-remove {
        background-color: rgba(255, 0, 0, 0.2);
    }
    .highlight-change {
        background-color: rgba(255, 255, 0, 0.2);
        padding: 2px;
        border-radius: 3px;
    }
    .tabs-container {
        margin-top: 20px;
    }
    .integration-success {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        animation: fadeIn 1s;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("C++ Code Iterator for Game Developers")
st.markdown("""
This tool helps game developers improve their C++ code by suggesting optimizations, 
best practices, and fixes. Simply paste your code, describe what you want to improve, 
and get AI-powered suggestions.
""")

# Initialize session state variables if they don't exist
if 'original_code' not in st.session_state:
    st.session_state.original_code = ""
if 'improved_code' not in st.session_state:
    st.session_state.improved_code = ""
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'diff_html' not in st.session_state:
    st.session_state.diff_html = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'integrated' not in st.session_state:
    st.session_state.integrated = False
if 'integration_history' not in st.session_state:
    st.session_state.integration_history = []

# Function to integrate the improved code
def integrate_code():
    """Add the improved code to integration history and mark as integrated"""
    if st.session_state.improved_code:
        # Add to integration history with timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.integration_history.append({
            "timestamp": timestamp,
            "original": st.session_state.original_code,
            "improved": st.session_state.improved_code,
            "explanation": st.session_state.explanation
        })
        
        # Update the original code with the improved version
        st.session_state.original_code = st.session_state.improved_code
        st.session_state.integrated = True

# Function to display diff with highlighted changes
def display_diff():
    """Display the diff between original and improved code"""
    if st.session_state.diff_html:
        # Clean up the diff HTML for display
        cleaned_diff = st.session_state.diff_html.replace(
            '<table class="diff"', 
            '<table class="diff" style="width:100%; font-family:monospace; border-collapse:collapse;"'
        )
        
        # Create a custom component to properly render the HTML
        components.html(
            cleaned_diff,
            height=600,
            scrolling=True
        )
    else:
        st.info("No differences to display.")

# Sidebar with example code and history
with st.sidebar:
    st.header("Example Code")
    example_files = {
        "None": "",
        "Game Physics System": Path("examples/entity_component.cpp").read_text(),
        "Entity Component System": Path("examples/game_physics.cpp").read_text()
    }
    
    selected_example = st.selectbox("Select an example:", list(example_files.keys()))
    
    if selected_example != "None" and example_files[selected_example]:
        if st.button("Load Example"):
            st.session_state.original_code = example_files[selected_example]
            st.session_state.improved_code = ""
            st.session_state.explanation = ""
            st.session_state.diff_html = ""
            st.session_state.integrated = False
    
    # Integration history
    st.header("Integration History")
    if st.session_state.integration_history:
        st.markdown("""
        <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <p>📝 <strong>Previous versions of your code are saved here.</strong> Click to expand and view.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, entry in enumerate(reversed(st.session_state.integration_history)):
            with st.expander(f"Integration #{len(st.session_state.integration_history) - i}: {entry['timestamp']}"):
                st.code(entry['improved'], language="cpp")
                if st.button(f"Restore this version", key=f"restore_{i}"):
                    st.session_state.original_code = entry['improved']
                    st.session_state.improved_code = ""
                    st.session_state.explanation = ""
                    st.session_state.diff_html = ""
                    st.session_state.integrated = False
                    st.rerun()
    else:
        st.info("No integration history yet. When you click 'Integrate Code', versions will be saved here.")

# Main content area with two columns
col1, col2 = st.columns(2)

# Left column for original code input
with col1:
    st.header("Original Code")
    original_code = st.text_area("Paste your C++ code here:", value=st.session_state.original_code, height=400, key="original_code_input")
    
    # Update session state when input changes
    if original_code != st.session_state.original_code:
        st.session_state.original_code = original_code
        st.session_state.improved_code = ""
        st.session_state.explanation = ""
        st.session_state.diff_html = ""
        st.session_state.integrated = False
    
    prompt = st.text_area("What would you like to improve?", 
                         placeholder="E.g., 'Optimize for performance', 'Improve memory management', 'Fix potential bugs', 'Apply modern C++ practices'",
                         height=100)
    
    if st.button("Generate Improvements", type="primary"):
        if st.session_state.original_code and prompt:
            with st.spinner("Analyzing code and generating improvements..."):
                # First perform local analysis
                analysis_results = analyze_cpp_code(st.session_state.original_code)
                st.session_state.analysis_results = analysis_results
                
                # Then generate suggestions using both local analysis and OpenAI
                improved_code, explanation, diff_html = generate_code_suggestions(
                    st.session_state.original_code, prompt
                )
                
                st.session_state.improved_code = improved_code
                st.session_state.explanation = explanation
                st.session_state.diff_html = diff_html
                st.session_state.integrated = False
                
                # Force a rerun to update the UI
                st.rerun()
        else:
            st.error("Please provide both code and improvement prompt.")

# Right column for improved code and explanation
with col2:
    st.header("Improved Code")
    
    if st.session_state.improved_code:
        # Create tabs for different views
        code_tab, diff_tab, analysis_tab = st.tabs(["Improved Code", "Diff View", "Analysis"])
        
        with code_tab:
            st.markdown('<div class="code-container">', unsafe_allow_html=True)
            st.code(st.session_state.improved_code, language="cpp")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Integrate Code", type="primary"):
                integrate_code()
                st.rerun()
        
        with diff_tab:
            st.markdown('<div class="diff-container">', unsafe_allow_html=True)
            display_diff()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with analysis_tab:
            st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
            for category, issues in st.session_state.analysis_results.items():
                if issues:
                    category_name = category.replace('_', ' ').title()
                    st.subheader(category_name)
                    for issue in issues:
                        st.markdown(f"**Line {issue['line']}**: {issue['issue']}")
                        st.code(issue['code'], language="cpp")
                        st.markdown(f"*Suggestion:* {issue['suggestion']}")
                        st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.header("Explanation of Changes")
        st.markdown(f'<div class="explanation-container">{st.session_state.explanation}</div>', unsafe_allow_html=True)
    else:
        st.info("Improved code will appear here after generation.")

# Final output section
if st.session_state.integrated:
    st.header("Integration Complete")
    st.markdown('<div class="integration-success">✅ Code successfully integrated! The improved code is now your new original code.</div>', unsafe_allow_html=True)
    
    # Add a visual indicator to show the flow of integration
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="text-align: center; padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-right: 20px;">
            <h4>Previous Original Code</h4>
        </div>
        <div style="font-size: 24px; margin-top: 10px;">➡️</div>
        <div style="text-align: center; padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; margin-left: 20px;">
            <h4>New Original Code</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show a message about the integration history
    st.info("This integration has been saved to the history panel in the sidebar. You can view and restore previous versions from there.")
    
    # Reset the integration flag after displaying the success message
    st.session_state.integrated = False
