import groq
import re
import os
from code_analyzer import analyze_cpp_code, generate_diff

def generate_code_suggestions(code, prompt):
    """
    Generate code improvement suggestions using Groq API and local analysis.
    
    Args:
        code (str): The original C++ code
        prompt (str): User's improvement request
        
    Returns:
        tuple: (improved_code, explanation, diff)
    """
    # First perform local analysis to identify issues
    analysis = analyze_cpp_code(code)
    
    # Prepare a system message with the analysis results
    analysis_text = format_analysis_for_prompt(analysis)
    
    # Create a prompt for Groq that includes the analysis
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        # Initialize Groq client with minimal configuration
        client = groq.Groq(api_key=api_key)
        
        # Create the chat completion request
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": f"""You are a C++ expert specializing in game development. 
Your task is to improve the provided code based on the user's request and the static analysis results.
Focus on performance, readability, and best practices for game development.

Here's the static analysis of the code:
{analysis_text}

Provide your response in the following format:
1. The complete improved code in a ```cpp code block
2. A detailed explanation of all changes made, organized by category (performance, memory management, etc.)
3. Highlight the most important improvements first

Make sure your improvements address both the user's specific request and the issues identified in the analysis.
For game development, prioritize performance optimizations and memory management improvements."""},
                {"role": "user", "content": f"Here is my C++ game development code:\n\n```cpp\n{code}\n```\n\nI want to improve it by: {prompt}"}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content
        
        # Split the response into code and explanation
        improved_code, explanation = extract_code_and_explanation(response_text)
        
        # Generate a diff between original and improved code
        diff = generate_diff(code, improved_code)
        
        return improved_code, explanation, diff
    
    except Exception as e:
        return code, f"Error generating suggestions: {str(e)}", ""

def format_analysis_for_prompt(analysis):
    """
    Format the analysis results for inclusion in the OpenAI prompt.
    
    Args:
        analysis (dict): Analysis results from analyze_cpp_code
        
    Returns:
        str: Formatted analysis text
    """
    result = []
    
    for category, issues in analysis.items():
        if issues:
            category_name = category.replace('_', ' ').title()
            result.append(f"## {category_name}")
            
            for issue in issues:
                result.append(f"- Line {issue['line']}: {issue['issue']}")
                result.append(f"  Code: {issue['code']}")
                result.append(f"  Suggestion: {issue['suggestion']}")
            
            result.append("")  # Empty line between categories
    
    return "\n".join(result)

def extract_code_and_explanation(response_text):
    """
    Extract the improved code and explanation from the OpenAI response.
    
    Args:
        response_text (str): The raw response from OpenAI
        
    Returns:
        tuple: (improved_code, explanation)
    """
    # Extract code block
    code_pattern = r"```cpp\n(.*?)```"
    code_match = re.search(code_pattern, response_text, re.DOTALL)
    
    if code_match:
        improved_code = code_match.group(1).strip()
        # Remove the code block from the response to get the explanation
        explanation = re.sub(code_pattern, "", response_text, flags=re.DOTALL).strip()
    else:
        # If no code block is found, assume the model didn't provide code
        improved_code = ""
        explanation = response_text
    
    return improved_code, explanation

def highlight_changes(original_code, improved_code):
    """
    Create HTML with highlighted changes between original and improved code.
    
    Args:
        original_code (str): The original code
        improved_code (str): The improved code
        
    Returns:
        str: HTML with highlighted changes
    """
    original_lines = original_code.splitlines()
    improved_lines = improved_code.splitlines()
    
    # Use difflib to find differences
    diff = generate_diff(original_code, improved_code)
    
    return diff
