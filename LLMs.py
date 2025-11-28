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
    
    # The initial settings loading logic is now handled by load_settings() on module import.
    # No need for the if default_app == "" block here anymore.
    
    context = "\n".join([f"User: {entry['user']}\nLLM: {entry['llm']}" for entry in chat_history])
    full_prompt = f"{context}\nUser: {prompt}" if context else f"User: {prompt}"
    
    if default_app == "Ollama":
        response = sendToLLM_Ollama(full_prompt)
        if response:
            chat_history.append({"user": prompt, "llm": response})
            return response
    else:
        # Try generic OpenAI-compatible provider
        response = sendToLLM_Generic(full_prompt)
        if response:
            chat_history.append({"user": prompt, "llm": response})
            return response
        return "Unsupported application or configuration error."

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

def sendToLLM_Generic(prompt):
    """Generic handler for OpenAI-compatible APIs (GPT4All, LM Studio, etc.)"""
    try:
        import openai
    except ImportError:
        return "Error: openai library not installed."
        
    try:
        # Get provider settings
        with open("settings.json", "r") as file:
            settings = json.load(file)
            
        provider_settings = settings.get("providers", {}).get(default_app, {})
        api_key = provider_settings.get("api_key", "not-needed")
        base_url = provider_settings.get("base_url", "http://localhost:4891/v1") # Default to GPT4All port
        
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model=default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling {default_app}: {str(e)}"

def get_chat_history():
    return chat_history

def change_provider(provider_name: str) -> str:
    """Change the active LLM provider"""
    global default_app
    
    # Load settings to check availability
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
            
        if "providers" not in settings:
            settings["providers"] = {}
            
        # Allow adding new providers dynamically
        if provider_name not in settings["providers"] and provider_name != "Ollama":
             # Add default config for new provider
             settings["providers"][provider_name] = {
                 "model": "default",
                 "base_url": "http://localhost:4891/v1" # Default assumption
             }
        
        settings["default_app"] = provider_name
        default_app = provider_name
        
        # Update default model if available
        if provider_name in settings["providers"]:
            model = settings["providers"][provider_name].get("model")
            if model:
                global default_model
                default_model = model
                settings["default_model"] = model
        
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
    # Ensure settings are loaded
    if default_app == "":
        load_settings()
    return {"provider": default_app, "model": default_model}

def load_settings():
    """Load settings from file"""
    global default_app, default_model
    try:
        with open("settings.json", "r") as file:
            settings = json.load(file)
            default_app = settings.get("default_app", "Ollama")
            default_model = settings.get("default_model", "llama3.1")
    except FileNotFoundError:
        default_app = "Ollama"
        default_model = "llama3.1"
        # If settings.json doesn't exist, create it with defaults
        with open("settings.json", "w") as file:
            json.dump({"default_app": default_app, "default_model": default_model, "providers": {}}, file, indent=4)


# Load settings on module import
load_settings()

if __name__ == "__main__":
    while True:
        prompt = input("Enter your prompt (or type 'exit' to quit): ")
        if prompt.lower() == "exit":
            break
        response = sendToLLM(prompt)
        print("Response from LLM:", response)