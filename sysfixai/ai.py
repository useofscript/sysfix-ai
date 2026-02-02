import subprocess
import json

def query_granite4(prompt: str) -> str:
    """
    Sends the prompt to the Granite4 Ollama model via CLI and returns the AI response as text.
    """
    try:
        # Run the ollama query command with granite4 model and prompt
        result = subprocess.run(
            ["ollama", "query", "granite4", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse the JSON output from ollama
        output = json.loads(result.stdout)
        # Extract the AI's response text
        return output.get("response", "").strip()
    except Exception as e:
        return f"AI query failed: {e}"
