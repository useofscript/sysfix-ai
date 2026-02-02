import subprocess

def query_granite4(prompt: str) -> str:
    """
    Query the Granite4 Ollama model via the CLI.

    Args:
        prompt (str): The prompt to send to the AI model.

    Returns:
        str: The AI model's response.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", "granite4", "--prompt", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"AI query failed: {e}"

def ask_ai_for_fix(issue: str) -> str:
    """
    Given an issue description, ask the Granite4 model for a recommended fix.

    Args:
        issue (str): Description of the problem.

    Returns:
        str: The AI’s recommended fix or advice.
    """
    prompt = (
        f"You are a Linux systems expert AI. The following issue was detected:\n\n{issue}\n\n"
        "Provide a concise and practical recommendation on how to fix this issue, "
        "or what steps to take next."
    )
    response = query_granite4(prompt)
    return response
