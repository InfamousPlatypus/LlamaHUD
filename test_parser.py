from CommandParser import CommandParser
import LLMs

# Mock LLMs for testing
def mock_change_provider(name):
    return f"Switched to provider: {name}"

LLMs.change_provider = mock_change_provider

parser = CommandParser()

test_commands = [
    "#changeBackend GPT4All",
    "#changeBackend OpenAI",
    "#shell dir",
    "Normal text",
    "#unknown command"
]

print("Testing CommandParser...")
for cmd in test_commands:
    print(f"\nInput: '{cmd}'")
    text, feedback = parser.parse(cmd, confirmation_callback=lambda x: True)
    print(f"Processed Text: '{text}'")
    print(f"Feedback: {feedback}")
