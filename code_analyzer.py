import re
import difflib

def analyze_cpp_code(code):
    """
    Analyze C++ code for common issues and improvement opportunities.
    
    Args:
        code (str): The C++ code to analyze
        
    Returns:
        dict: Analysis results with categories of issues and suggestions
    """
    analysis = {
        "performance_issues": [],
        "memory_management": [],
        "code_style": [],
        "modern_cpp": [],
        "game_specific": [],
        "potential_bugs": []
    }
    
    # Split code into lines for analysis
    lines = code.split('\n')
    
    # Check for raw pointers (could be replaced with smart pointers)
    raw_pointer_pattern = r'\b(\w+)\s*\*\s*(\w+)\s*='
    for i, line in enumerate(lines):
        if re.search(raw_pointer_pattern, line) and 'std::' not in line and 'shared_ptr' not in line and 'unique_ptr' not in line:
            analysis["memory_management"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Raw pointer usage",
                "suggestion": "Consider using smart pointers (std::unique_ptr or std::shared_ptr) for automatic memory management"
            })
    
    # Check for C-style arrays (could use std::array or std::vector)
    c_array_pattern = r'\b(\w+)\s+(\w+)\[(\d+)\]'
    for i, line in enumerate(lines):
        if re.search(c_array_pattern, line) and 'char' not in line:  # Exclude char arrays which might be for C strings
            analysis["modern_cpp"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "C-style array usage",
                "suggestion": "Consider using std::array for fixed-size arrays or std::vector for dynamic arrays"
            })
    
    # Check for manual loop iterations over containers (could use range-based for loops)
    for i, line in enumerate(lines):
        if 'for' in line and '; i < ' in line and '.size()' in line:
            analysis["modern_cpp"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Index-based loop over container",
                "suggestion": "Consider using range-based for loop: for (auto& element : container)"
            })
    
    # Check for potential performance issues in game code
    for i, line in enumerate(lines):
        # Check for sqrt in tight loops (expensive operation)
        if 'sqrt' in line and ('for' in lines[max(0, i-5):i] or 'while' in lines[max(0, i-5):i]):
            analysis["performance_issues"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Expensive sqrt operation in loop",
                "suggestion": "For magnitude comparisons, consider using squared magnitude (x*x + y*y) instead of sqrt(x*x + y*y)"
            })
        
        # Check for string operations in performance-critical sections
        if ('std::string' in line or '+=' in line and '"' in line) and ('update' in lines[max(0, i-10):i] or 'render' in lines[max(0, i-10):i]):
            analysis["performance_issues"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "String operations in performance-critical code",
                "suggestion": "String operations can be expensive. Consider moving string manipulations outside of update/render loops"
            })
    
    # Check for game-specific patterns
    for i, line in enumerate(lines):
        # Check for direct floating-point comparisons (problematic in games)
        if re.search(r'(==|!=)\s*\d*\.\d+f?', line):
            analysis["game_specific"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Direct floating-point comparison",
                "suggestion": "Use epsilon-based comparison for floating-point values to avoid precision issues"
            })
        
        # Check for magic numbers in game code
        if re.search(r'[^\.]\d+\.\d+f?', line) and not re.search(r'const\s+float', line) and not re.search(r'#define', line):
            analysis["code_style"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Magic number usage",
                "suggestion": "Define named constants for magic numbers to improve code readability and maintainability"
            })
    
    # Check for potential bugs
    for i, line in enumerate(lines):
        # Check for uninitialized variables
        if re.search(r'(\w+)\s+(\w+);', line) and not re.search(r'=', line) and not re.search(r'class|struct|enum', line):
            # Check if it's a primitive type
            primitive_types = ['int', 'float', 'double', 'bool', 'char']
            for type_name in primitive_types:
                if re.search(rf'{type_name}\s+\w+;', line):
                    analysis["potential_bugs"].append({
                        "line": i + 1,
                        "code": line.strip(),
                        "issue": "Uninitialized primitive variable",
                        "suggestion": "Initialize variables at declaration to avoid undefined behavior"
                    })
        
        # Check for potential null pointer dereference
        if '->' in line and 'if' not in lines[max(0, i-3):i] and 'nullptr' not in lines[max(0, i-3):i] and 'NULL' not in lines[max(0, i-3):i]:
            analysis["potential_bugs"].append({
                "line": i + 1,
                "code": line.strip(),
                "issue": "Potential null pointer dereference",
                "suggestion": "Add null check before dereferencing pointers"
            })
    
    return analysis

def generate_diff(original_code, improved_code):
    """
    Generate a diff between original and improved code.
    
    Args:
        original_code (str): The original code
        improved_code (str): The improved code
        
    Returns:
        str: HTML-formatted diff
    """
    diff = difflib.HtmlDiff().make_file(
        original_code.splitlines(),
        improved_code.splitlines(),
        "Original Code",
        "Improved Code",
        context=True
    )
    return diff

def suggest_improvements(analysis, code):
    """
    Generate improvement suggestions based on analysis results.
    
    Args:
        analysis (dict): Analysis results
        code (str): The original code
        
    Returns:
        dict: Suggested improvements with explanations
    """
    suggestions = {
        "code_changes": [],
        "explanations": []
    }
    
    # Process each category of issues
    for category, issues in analysis.items():
        if issues:
            category_name = category.replace('_', ' ').title()
            suggestions["explanations"].append(f"## {category_name}")
            
            for issue in issues:
                line_num = issue["line"]
                suggestion = issue["suggestion"]
                code_snippet = issue["code"]
                
                suggestions["explanations"].append(f"- Line {line_num}: {issue['issue']}")
                suggestions["explanations"].append(f"  - Current: `{code_snippet}`")
                suggestions["explanations"].append(f"  - Suggestion: {suggestion}")
                
                # Add to code changes if we have a specific replacement
                if "replacement" in issue:
                    suggestions["code_changes"].append({
                        "line": line_num,
                        "original": code_snippet,
                        "replacement": issue["replacement"]
                    })
    
    return suggestions
