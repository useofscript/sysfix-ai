import subprocess


import subprocess

def query_lfm25_thinking(prompt: str) -> str:
    """
    Query the lfm2.5-thinking Ollama model locally via CLI.
    Args:
        prompt (str): The prompt to send to the AI model.
    Returns:
        str: The AI model's response.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", "lfm2.5-thinking", prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # seconds
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "AI query timed out. Ollama may be busy or unresponsive."
    except Exception as e:
        return f"AI query failed: {e}"

def ask_ai_for_fix(issue: str) -> str:
    """
    Given an issue description, ask the lfm2.5-thinking model for a recommended fix.
    Args:
        issue (str): Description of the problem.
    Returns:
        str: The AI’s recommended fix or advice.
    """
    prompt = (
        f"You are a Linux systems expert AI. The following issue was detected:\n\n{issue}\n\n"
        "Provide a concise and practical recommendation on how to fix this issue, or what steps to take next. "
        "Do NOT recommend closing browsers or actively used programs unless you first ask the user for confirmation, or unless the program is clearly idle or unresponsive. "
        "If recommending to close a browser or other program, always warn the user and suggest saving work first."
    )
    response = query_lfm25_thinking(prompt)
    return response

def ask_ai_deep_dive(prompt: str) -> str:
    """
    Given a detailed issue description, ask the lfm2.5-thinking model for an in-depth analysis.
    Args:
        prompt (str): Detailed description of the problem and context.
    Returns:
        str: The AI’s detailed analysis and troubleshooting guide.
    """
    detailed_prompt = (
        f"You are a Linux systems expert AI. The user has provided the following detailed issue:\n\n{prompt}\n\n"
        "Provide a comprehensive analysis, including:"
        "1. Potential root causes."
        "2. Step-by-step troubleshooting guide."
        "3. Commands or tools to use for diagnosis."
        "4. Safety warnings or precautions."
        "5. Recommendations for prevention."
    )
    response = query_lfm25_thinking(detailed_prompt)
    return response
