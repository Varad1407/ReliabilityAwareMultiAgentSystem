from llm_client import generate_response

prompt = "Explain what SQL is in exactly two sentences."

print("Sending prompt to Qwen...")

response = generate_response(prompt)

print("\nQwen response:")
print(response)