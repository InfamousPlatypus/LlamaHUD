import ollama
import json
from Notifs import easy_notification
default_app = ""  # Default application for LLMs
default_model = ""  # Default model for LLMs
chat_history = []  # List to store chat history

def sendToLLM(prompt):
    global default_app, default_model, chat_history  # Declare global variables

    # Check if default_app is set
    if default_app == "":
        # Attempt to read the settings from a JSON file
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                default_app = settings.get("default_app", "Ollama")
                default_model = settings.get("default_model", "llama3.1")
        except FileNotFoundError:
            default_app = "Ollama"
            default_model = "llama3.1"
            with open("settings.json", "w") as file:
                json.dump({"default_app": default_app, "default_model": default_model}, file)

# Include chat history in the prompt
    context = "\n".join([f"User: {entry['user']}\nLLM: {entry['llm']}" for entry in chat_history])
    full_prompt = f"{context}\nUser: {prompt}" if context else f"User: {prompt}"

    if default_app == "Ollama":
        response = sendToLLM_Ollama(full_prompt)
        if response:  # Ensure response is not None
            # Add the user prompt and LLM response to the chat history
            chat_history.append({"user": prompt, "llm": response})
            resp=response
    else: 
        resp = "Unsupported application. Please check your settings."

    #easy_notification(resp)  # Send notification with the response
    return resp  # Return the response for further processing

def sendToLLM_Ollama(prompt):
    # Call the default Ollama model with the provided prompt
    try:
        # Adjust the function call to match the correct API usage
        response = ollama.generate(model=default_model, prompt=prompt)
        return response.get("response", "No response received.")  # Extract the response text
    except Exception as e:
        return f"Error: {str(e)}"

def get_chat_history():
    """Return the chat history."""
    return chat_history

if __name__ == "__main__":
    while True:
        prompt = input("Enter your prompt (or type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        response = sendToLLM(prompt)
        print("Response from LLM:", response)
        