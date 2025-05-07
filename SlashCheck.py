import Slash_json
import Slash_LlamaHud
def SlashCheck(text):

    # Check if the text contains a slash
    if '/' in text:
        return True
    else:
        return False

def determineSlash(text):
    if "json" in text:
        return Slash_json.error
    elif "LlamaHud" in text:
        return Slash_LlamaHud.determaneRunTask(text)
    else:
        return "No valid task found."