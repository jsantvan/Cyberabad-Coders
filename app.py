import streamlit as st
import pandas as pd
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# --- Configuration ---
REQUIRED_SHEETS = ['Info', 'TimeSheet', 'LeaveRecords', 'Rules']


# --- Component Loading ---
@st.cache_resource
def load_and_prepare_data(excel_path, model_name):
    """
    Loads data from Excel, prepares a single context string, and initializes the LLM.
    """
    if not os.path.exists(excel_path):
        st.error(f"File not found at path: {excel_path}")
        return None, None

    try:
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        return None, None

    for sheet in REQUIRED_SHEETS:
        if sheet not in all_sheets:
            st.error(f"A required sheet was not found: '{sheet}'.")
            return None, None

    # --- 1. Convert ALL data to a single text block ---
    full_context_str = ""

    # Add company rules
    full_context_str += "--- COMPANY RULES ---\n"
    full_context_str += all_sheets['Rules'].iloc[:, 0].dropna().astype(str).str.cat(sep='\n')
    full_context_str += "\n\n"

    # Add employee info
    full_context_str += "--- EMPLOYEE INFO ---\n"
    full_context_str += all_sheets['Info'].to_string()
    full_context_str += "\n\n"

    # Add timesheet data
    full_context_str += "--- TIMESHEET RECORDS ---\n"
    full_context_str += all_sheets['TimeSheet'].to_string()
    full_context_str += "\n\n"

    # Add leave data
    full_context_str += "--- LEAVE RECORDS ---\n"
    full_context_str += all_sheets['LeaveRecords'].to_string()
    full_context_str += "\n\n"

    # --- 2. LLM Initialization ---
    try:
        llm = ChatOllama(model=model_name)
    except Exception as e:
        st.error(f"Failed to connect to Ollama with model '{model_name}'. Is Ollama running? Error: {e}")
        return None, None

    return llm, full_context_str


# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="HR Information Assistant", layout="centered")
    st.title("HR Information Assistant 🤖")

    with st.sidebar:
        st.header("Configuration")
        st.info("Please provide the details below to start the assistant.")
        model_name = st.text_input("1. Enter your Ollama Model Name:", value="llama3.2:3b")
        excel_file_path = st.text_input("2. Enter the full path to your Excel file:")
        st.caption("Example: C:\\Users\\YourUser\\Documents\\HR_Data.xlsx")

    if excel_file_path and model_name:
        llm, full_context = load_and_prepare_data(excel_file_path, model_name)

        if llm and full_context:
            st.success("Assistant is ready! You can now ask questions.")

            prompt_template = ChatPromptTemplate.from_template("""
            Answer the following question based ONLY on the provided context.

            --- CONTEXT START ---
            {context}
            --- CONTEXT END ---

            Question: {input}
            Answer:
            """)

            user_query = st.text_input(
                "Ask a question about policies or employee records...",
                placeholder="e.g., 'What is the sick leave policy?'"
            )

            if st.button("Get Answer"):
                if user_query:
                    with st.spinner("Thinking..."):
                        chain = prompt_template | llm
                        response = chain.invoke({"context": full_context, "input": user_query})
                        st.write(response.content)
                else:
                    st.warning("Please enter a question.")
    else:
        st.info("Please provide the path to your Excel file and a model name in the sidebar to begin.")


if __name__ == "__main__":
    main()