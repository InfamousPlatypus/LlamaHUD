try:
    import ollama
except ImportError:
    ollama = None
import json

default_app = ""
default_model = ""
chat_history = []

def sendToLLM(prompt):
    global default_app, default_model, chat_history
    
    if default_app == "":
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
    
    context = "\n".join([f"User: {entry['user']}\nLLM: {entry['llm']}" for entry in chat_history])
    full_prompt = f"{context}\nUser: {prompt}" if context else f"User: {prompt}"
    
    if default_app == "Ollama":
        response = sendToLLM_Ollama(full_prompt)
        if response:
            chat_history.append({"user": prompt, "llm": response})
            return response
    else:
        return "Unsupported application. Please check your settings."

def sendToLLM_Ollama(prompt):
    if not ollama:
        return "Error: Ollama library not installed or failed to load."
        
    try:
        # Initialize Ollama client with explicit host
        client = ollama.Client(host='http://localhost:11434')
        response = client.generate(model=default_model, prompt=prompt)
        return response.get("response", "No response received.")
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"

def get_chat_history():
    return chat_history

def change_provider(provider_name: str) -> str:
    """Change the active LLM provider"""
    global default_app
    
    # Load settings to check availability
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
            providers = settings.get("providers", {})
            
            if provider_name not in providers and provider_name != "Ollama":
                 # Fallback check if it's a valid provider class even if not in settings yet
                 # For now, just check settings
                 return f"Error: Provider '{provider_name}' not found in settings."
            
            settings["default_app"] = provider_name
            default_app = provider_name
            
            with open("settings.json", "w") as outfile:
                json.dump(settings, outfile, indent=4)
                
            return f"Switched to provider: {provider_name}"
    except Exception as e:
        return f"Error changing provider: {e}"

def change_model(model_name: str) -> str:
    """Change the model for the current provider"""
    global default_model, default_app
    
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
            
        settings["default_model"] = model_name
        default_model = model_name
        
        # Also update the specific provider's model if it exists in the complex structure
        if "providers" in settings and default_app in settings["providers"]:
            settings["providers"][default_app]["model"] = model_name
            
        with open("settings.json", "w") as outfile:
            json.dump(settings, outfile, indent=4)
            
        return f"Switched model to: {model_name}"
    except Exception as e:
        return f"Error changing model: {e}"

def get_current_settings() -> dict:
    """Get current provider and model"""
    return {"provider": default_app, "model": default_model}

if __name__ == "__main__":
    while True:
        prompt = input("Enter your prompt (or type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        response = sendToLLM(prompt)
        print("Response from LLM:", response)