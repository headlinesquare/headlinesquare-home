# Detailed Documentation for LLM_controller_03292025.py

This document provides a comprehensive explanation of the structure, functionality, and usage of the "LLM_controller_03292025.py" file. It serves as both a README and inline documentation for future developers.

---

## 1. Overview

This script implements an automated multi-turn conversation system powered by large language models (LLMs). It leverages the OpenRouter API (compatible with OpenAI’s API style) for streaming chat responses. The application is built on top of Streamlit, which is used to render the user interface and manage persistent session state. Key features include:

- **Dynamic prompt loading** from a designated folder.
- **Streaming responses** from selected LLM providers.
- **Saving conversation history** as both text files and HTML snapshots.
- **One-time execution control** using a persistent flag file.
- **Robust Retry Mechanism:** If an API error occurs during a conversation turn (e.g., "Internal Error 500" or other errors), the system deletes the erroneous reply, waits 60 seconds, and retries that turn. This retry loop repeats up to 60 times (over 3600 seconds). If no valid reply is received after 60 retries, the loop is exited and the final conversation (so far) is saved.

---

## 2. Prerequisites and Installation

### Requirements

- Python 3.7+
- External packages: `openai`, `streamlit`

### Installation

Install the required packages via pip:

```bash
pip install openai streamlit
```

### Execution

Run the script using Streamlit from your command line:

```bash
streamlit run LLM_controller_03292025.py
```

> **Note:** Ensure that your environment variable `OPENROUTER_API_KEY` is set with your API key. You may also adjust the folder names and model selections as needed.

---

## 3. File Structure and Key Components

### A. Imports and Global Variables

- **Libraries Imported:**
  - `openai`
  - `time`
  - `os`
  - `datetime`
  - `streamlit as st`
- **Global Constants & Settings:**
  - `FLAG_FILE`: A file used to indicate whether the process has been executed.
  - The API key is loaded from the environment variable `OPENROUTER_API_KEY`.
  - **Model Configuration:** Several model configurations are provided via commented sections:
    - Active models:
      - `REASONING_MODEL = "openai/o3-mini-high"`
      - `WRITING_MODEL = "anthropic/claude-3.7-sonnet:thinking"`

### B. UI Initialization

- The current working directory is displayed using `st.write()`.
- The application title and model configuration details are rendered using `st.title()` and `st.write()`.

### C. Persistent Session State

- Conversation history is maintained using Streamlit’s `session_state` for the duration of the session.

---

## 4. Detailed Function Documentation

### A. Process Control Functions

#### `has_process_run()`

- **Purpose:** Checks if the LLM process has already been executed by looking for the existence of a persistent flag file.
- **Implementation:** Uses `os.path.exists()` to check for the `FLAG_FILE` (named "process_ran.flag").

#### `mark_process_as_run()`

- **Purpose:** Marks that the process has been executed by creating (or overwriting) the flag file.
- **Implementation:** Writes a simple string (e.g., `"done"`) into the `FLAG_FILE`.

---

### B. Prompt Loading Function

#### `load_prompts(prompt_folder="Prompt")`

- **Purpose:** Loads and sorts prompt files from a specified folder (default `"Prompt"`) that start with the prefix `"Prompt_"`.
- **Process:**
  - Checks if the prompt folder exists; if not, an error is displayed.
  - Retrieves filenames starting with `"Prompt_"` and sorts them alphabetically.
  - For each file:
    - Reads and normalizes the content (converting Windows line endings to Unix style).
    - Determines which model to use:
      - If the filename contains `"reasoning"` (case-insensitive), selects `REASONING_MODEL`.
      - Otherwise, selects `WRITING_MODEL`.
    - Appends a tuple in the form `(prompt_text, model)` to a list.
- **Returns:** A list of tuples where each tuple comprises the prompt text and its corresponding model.

---

### C. Chat Response Streaming Function

#### `stream_chat_response(client, model, conversation_history, response_container)`

- **Purpose:** Streams a chat response from the LLM service via the OpenRouter API.
- **Parameters:**
  - `client`: Configured OpenAI API client.
  - `model`: The selected LLM model (e.g., `REASONING_MODEL` or `WRITING_MODEL`).
  - `conversation_history`: A list of dictionaries containing previous conversation messages (with keys `"role"` and `"content"`).
  - `response_container`: A Streamlit placeholder (created with `st.empty()`) used for real-time display.
- **Process:**
  - Constructs an API request with:
    - The chosen model.
    - The conversation history as `messages`.
    - Streaming mode enabled (`"stream": True`).
  - Iterates over streaming response chunks:
    - Retrieves new content fragments (`delta`) and appends them to a cumulative response string.
    - Continuously updates the Streamlit container using Markdown formatting.
  - If an exception occurs during streaming, an error is reported via `st.error` and the function returns `None`. **(CHANGE: Return `None` on error to trigger the retry mechanism.)**
  - Checks and warns if the response is truncated due to maximum token limits.
- **Returns:** The fully concatenated response as a string, or `None` if an error occurred.

---

### D. Saving Conversation History to a Text File

#### `save_conversation(conversation_history, folder="conversations")`

- **Purpose:** Saves the conversation history to a text file.
- **Parameters:**
  - `conversation_history`: List of conversation messages.
  - `folder`: Directory where the conversation file should be saved (default is `"conversations"`).
- **Process:**
  - Ensures the specified folder exists; if not, it is created.
  - Generates a filename using the current date and time.
  - Writes a header detailing the active models and then iterates over the conversation:
    - Each round is demarcated (with rounds counted based on user 
      messages) and messages are labeled as from the "User" or "Assistant".
- **Notifications:**
  - On success, displays a success message via `st.success`.
  - On failure, an error message is shown via `st.error`.

---

### E. Saving the Webpage as HTML

#### `save_conversation_HTML()`

- **Purpose:** Saves the rendered Streamlit webpage as an HTML file and triggers an automatic download.
- **Process:**
  - Uses Streamlit components to embed an HTML/JavaScript snippet.
  - The snippet waits (2000ms) to ensure the page is fully rendered, 
    captures the entire HTML content, and initiates a download with a 
    filename based on the current date and time.

---

### F. Robust Retry Mechanism *(NEW CHANGE)*

- **Purpose:** Enhances the reliability of the LLM streaming responses. If an error 
  (e.g., "Internal Error 500") occurs during a conversation turn:
  - Any erroneous (or partially received) reply is discarded.
  - The system waits for 60 seconds before retrying.
  - The retry loop is executed up to 60 times (a total of 3600 seconds of waiting).
    If a valid response is received within these attempts, processing 
    continues as normal. Otherwise, the conversation loop is exited, and the
     final conversation history is saved.
- **Implementation:**
  - The `stream_chat_response` function is modified to return `None` when an error occurs.
  - In the main conversation loop, a `while` loop encapsulates the streaming call. This loop retries the API call until a good response (non-`None`) is obtained or until 60 retries have been attempted.
  - These changes are clearly marked in the code with "BEGIN CHANGE" and "END CHANGE" comments.

---

## 5. Main Application Flow

1. **UI Initialization:**
   
   - The current working directory is printed.
   - The application title and model configuration details are displayed.

2. **Flag Check:**
   
   - The function `has_process_run()` verifies if the process has already been executed.
   - If the flag file exists, a message is displayed via Streamlit and the process is skipped.

3. **Prompt Loading and Conversation Setup:**
   
   - `load_prompts()` is called to retrieve all prompt files from the `"Prompt"` folder.
   - The conversation history is initialized in `st.session_state` if not already present.

4. **Interaction Loop:**
   
   - **For each loaded prompt:**
     - The prompt is added as a "User" message into the conversation history.
     - The prompt is displayed with a round counter.
     - A placeholder (`st.empty()`) is created for streaming the LLM response.
     - The conversation history is trimmed to avoid exceeding token limits.
     - **Robust Retry Mechanism:** *(CHANGE: The call to `stream_chat_response()` is now 
       wrapped in a while loop that retries up to 60 times if an error occurs. 
       Between retries, the system waits for 60 seconds. If successful, a valid
       reply is added to the conversation history; if not, the loop exits and 
       the conversation is terminated.)*
     - The assistant's response is then appended to the conversation history.
     - A visual divider is displayed, followed by a short pause using `time.sleep(2)`.
     - The updated conversation history is saved to a text file via `save_conversation()`.

5. **Final Steps:**
   
   - After processing all prompts (or exiting early due to repeated errors):
     - The entire conversation is saved as an HTML file.
     - A final save is performed in the `"final_conversation"` folder.
   - The process is marked as executed by creating the flag file using `mark_process_as_run()`, ensuring the process will not be repeated in a future session.

---

## 6. Model Selection and Comments

- **Multiple Model Options:** The code includes various commented configurations for different LLM providers (OpenAI, Anthropic, Gemini, DeepSeek).
- **Active Configuration:** The active models are:
  - `REASONING_MODEL`: `"openai/o3-mini-high"`
  - `WRITING_MODEL`: `"anthropic/claude-3.7-sonnet:thinking"`
- **Usage:** Modify or uncomment other configurations as needed based on pricing, performance, or API compatibility.

---

## 7. Running the Application

1. **Install Required Packages:**
- ```bash
  pip install openai streamlit
  ```

- **Set the API Key:** Ensure your environment variable `OPENROUTER_API_KEY` is correctly set.

- **Prepare the Prompts:** Place your prompt files in a folder named `Prompt` (file names should start with `Prompt_`).

- **Run the Application:**
1. ```bash
   streamlit run LLM_controller_03292025.py
   ```

2. **Follow On-Screen Instructions:** The application will display streamed responses and save conversation files as specified.

---

## 8. Summary

This script orchestrates an end-to-end interactive conversation with a large language model using Streamlit. Its key features include:

- **Dynamic Prompt Loading:** Prompts are read from files and dynamically processed.
- **Streaming LLM Responses:** Responses are streamed in real-time and rendered in the UI.
- **Persistent Conversation History:** Conversation messages are saved throughout the session and stored as text and HTML files.
- **One-Time Execution Control:** A persistent flag file ensures the process runs only once per session.
- **Robust Retry Mechanism:** Enhanced error handling ensures that transient API errors (e.g., 
  "Internal Error 500") are managed by retrying the conversation turn up 
  to 60 times, waiting 60 seconds between attempts.

Feel free to modify the prompt folder, file naming, model configurations, or conversation management logic to suit your specific use case.
