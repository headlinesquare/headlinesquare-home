from openai import OpenAI
import time, streamlit as st, os
from datetime import datetime

'''
Installation:
pip install openai streamlit

Example:
    C:\\Users\\YourName>streamlit run your_script.py
'''

st.write("Current working directory:", os.getcwd())

# Define a persistent flag file to track if the process has run.
FLAG_FILE = "process_ran.flag"

def has_process_run():
    return os.path.exists(FLAG_FILE)

def mark_process_as_run():
    with open(FLAG_FILE, "w") as f:
        f.write("done")

# Load the API key from environment variables.
# Ensure that your environment variable "OPENROUTER_API_KEY" is set.
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"  # New parameter for OpenRouter
)

st.title("Automated LLM Multi-Turn Conversation (Streaming)")

# OpenAI
# Feb 12, 2025
# Pricing: openai/o3-mini-high $1.1/M input tokens, $4.4/M output tokens
# Now Hybrid
REASONING_MODEL = "openai/o3-mini-high"
WRITING_MODEL = "anthropic/claude-3.7-sonnet:thinking"

# Anthropic
# Feb 24, 2025
# Pricing: $3/M input tokens, $15/M output tokens
# REASONING_MODEL = "anthropic/claude-3.7-sonnet:thinking"
# WRITING_MODEL = "anthropic/claude-3.7-sonnet:thinking"

# Gemini
# Mar 25, 2025
# Pricing: Free
# 03/28/2025 doesn't work
# REASONING_MODEL = "google/gemini-2.5-pro-exp-03-25:free"
# WRITING_MODEL = "google/gemini-2.5-pro-exp-03-25:free"

# DeepSeek
# Pricing: Free
# Jan 20, 2025 for R1, Mar 24, 2025 for V3-0324
# REASONING_MODEL = "deepseek/deepseek-r1:free"
# WRITING_MODEL = "deepseek/deepseek-r1:free"
# WRITING_MODEL = "deepseek/deepseek-chat-v3-0324:free"

st.write(f"\n\nREASONING_MODEL: {REASONING_MODEL}\n\nWRITING_MODEL: {WRITING_MODEL}\n\n")

# -------------------------------
# Function to load prompts from text files in the "prompt" folder.
def load_prompts(prompt_folder="Prompt"):
    """
    Reads all files starting with 'prompt_' from the specified folder,
    sorts them alphabetically, and returns a list of tuples:
    (prompt_text, model)

    If the filename contains "reasoning" (case-insensitive), we use:
        a reasoning model
    Otherwise, we use:
        a non-reasoning model that is better at writing
    """
    if not os.path.exists(prompt_folder):
        st.error(f"The folder '{prompt_folder}' does not exist.")
        return []
    
    prompt_files = sorted(f for f in os.listdir(prompt_folder) if f.startswith("Prompt_"))
    prompts_info = []

    for filename in prompt_files:
        file_path = os.path.join(prompt_folder, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().replace("\r\n", "\n").strip()
            
            # Choose model based on file name label.
            if "reasoning" in filename.lower():
                model = REASONING_MODEL
            else:
                model = WRITING_MODEL

            prompts_info.append((content, model))

        except Exception as e:
            st.error(f"Error reading {file_path}: {e}")

    return prompts_info

# Load prompts from files.
prompts = load_prompts()

# -------------------------------
# Use Streamlit's session_state for persistent conversation history.
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# -------------------------------
# Modularized function to stream chat response.
def stream_chat_response(client, model, conversation_history, response_container):
    """
    Streams a chat response from OpenAI.
    Handles errors and checks if the response was truncated.
    Returns the full streamed response.
    """
    streamed_response = ""
    finish_reason = None
    
    create_kwargs = {
        "model": model,
        "messages": conversation_history,
        "max_tokens": 20000,  # Adjust this if you suspect token limits
        "stream": True
    }
    
    try:
        stream = client.chat.completions.create(**create_kwargs)
        for chunk in stream:
            finish_reason = chunk.choices[0].finish_reason
            delta = chunk.choices[0].delta
            if delta and delta.content:
                streamed_response += delta.content
                # Considering output Markdown format, add one extra line
                response_container.markdown(f"**Assistant:** {streamed_response.replace('\n', '\n\n')}")
    except Exception as e:
        st.error(f"An error occurred while streaming: {e}")
        # Return None on error to signal failure
        return None

    if finish_reason == "length":
        st.warning("Response was truncated due to the max token limit.")

    return streamed_response

# -------------------------------
# Function to save the conversation to a file.
def save_conversation(conversation_history, folder="conversations"):
    """
    Saves the conversation history to a text file using the current date and time
    as the file name. Files are saved in the specified folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # Create a filename using the current date and time.
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(folder, f"conversation_{now}.txt")
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"\n============================================================\n    REASONING_MODEL: {REASONING_MODEL}\n    WRITING_MODEL: {WRITING_MODEL}\n============================================================\n\n\n\n")
            count_cycle = 0
            for message in conversation_history:
                role = message["role"].capitalize()
                content = message["content"]
                if role == "User":
                    count_cycle += 1
                f.write(f"\n====================\n    Round {count_cycle}\n    {role}: \n====================\n\n{content}\n\n")
        st.success(f"Conversation saved to {filename}")
    except Exception as e:
        st.error(f"Failed to save conversation: {e}")

# -------------------------------
# Function to save the entire webpage as HTML.
def save_conversation_HTML():
    """
    Saves the rendered Streamlit webpage as an HTML file using the current date and time
    as the file name. The file will be automatically downloaded by the user's browser.
    """
    import streamlit.components.v1 as components  # Ensure components is imported

    # Create a filename using the current date and time.
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"conversation_{now}.html"  # Filename mimics that of save_conversation()

    components.html(
        f"""
        <script>
        // Wait a moment to ensure the full page is rendered, then trigger download.
        setTimeout(function(){{
            // Use the parent document's HTML instead of the iframe's.
            var htmlContent = window.parent.document.documentElement.outerHTML;
            var blob = new Blob([htmlContent], {{type: "text/html"}});
            var a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "{filename}";  // File name is set dynamically here.
            a.click();
        }}, 2000);  // Increased delay to 2000ms for better reliability.
        </script>
        """,
        height=0
    )

# -------------------------------
# Run the LLM process only if it hasn't been run before.
if not has_process_run():
    if not prompts:
        st.error("No prompts loaded. Please check your 'prompt' folder.")
    else:
        for i, (prompt_text, model) in enumerate(prompts, 1):
            st.session_state.conversation_history.append({"role": "user", "content": prompt_text})
            st.markdown(f"**User (Round {i}):** {prompt_text.replace('\n', '\n\n')}")
            
            response_container = st.empty()
            
            # Implement Retry Mechanism for each conversation turn
            retry_count = 0
            good_response = None
            while retry_count < 60:
                full_history = st.session_state.conversation_history
                if len(full_history) <= 5:
                    trimmed_history = full_history
                else:
                    trimmed_history = full_history[:2] + (full_history[-5:] if len(full_history) % 2 == 1 else full_history[-4:])
                streamed_response = stream_chat_response(
                    client=client,
                    model=model,
                    conversation_history=trimmed_history,
                    response_container=response_container
                )
                if streamed_response is not None:
                    good_response = streamed_response
                    break
                else:
                    retry_count += 1
                    time.sleep(60)
            if good_response is None:
                st.error("Failed to get a valid response after 60 retries. Exiting conversation loop.")
                break  # Exit the for loop if we exceed retries
            # Implement Retry Mechanism

            st.session_state.conversation_history.append(
                {"role": "assistant", "content": good_response}
            )
            
            st.write("---")
            time.sleep(2)
            save_conversation(st.session_state.conversation_history)
        
        save_conversation_HTML()
        save_conversation(st.session_state.conversation_history, "final_conversation")
    
    # Mark that the process has now run by creating the flag file.
    mark_process_as_run()
else:
    st.info("The LLM process has already been executed in a previous session.")
