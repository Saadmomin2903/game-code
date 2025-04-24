# C++ Code Iterator for Game Developers

## Overview
This tool helps game developers improve their C++ code by suggesting optimizations, best practices, and fixes. It uses a combination of static code analysis and AI-powered suggestions to provide comprehensive code improvements.

## Features
- **Code Input**: Paste your C++ code or load from examples
- **Improvement Prompts**: Specify what aspects you want to improve
- **AI-Powered Suggestions**: Get intelligent code improvements
- **Static Analysis**: Identify common issues in your code
- **Diff View**: See exactly what changed between versions
- **Code Integration**: Apply changes with one click
- **Version History**: Track your code improvements over time

## How to Use
1. **Input Code**: Paste your C++ code in the left panel or select an example
2. **Specify Improvements**: Describe what you want to improve
3. **Generate Improvements**: Click the button to analyze and improve your code
4. **Review Changes**: Check the improved code, diff view, and analysis
5. **Integrate Code**: Apply the changes to continue iterating

## Technical Details
- Built with Streamlit and OpenAI
- Performs static analysis on C++ code
- Generates improvements using AI
- Tracks version history for iterative development

## Running Locally
```bash
cd code_iterator
python3 -m streamlit run app.py
```

## Public Access
The application is currently running and accessible at:
http://8501-ixwjw1bvssk652shtnxp4-38657343.manus.computer

## Example Use Cases
- Optimizing game physics code for performance
- Modernizing legacy C++ code with C++11/14/17/20 features
- Improving memory management in resource-intensive game systems
- Fixing potential bugs and edge cases
- Enhancing code readability and maintainability

## Limitations
- The tool works best with well-formed C++ code
- Very large codebases may need to be analyzed in smaller chunks
- Some game-specific optimizations may require domain knowledge

## Future Improvements
- Support for more game engines and frameworks
- Integration with version control systems
- More detailed performance analysis
- Support for additional programming languages
