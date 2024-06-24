import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from io import BytesIO
import base64
import fitz
import json


def extract_text_from_pdf(file):

     document = None

     if file.name.startswith("networth-certificate"):
          file_path = "assets/networth-certificate.pdf"
          document = fitz.open(file_path)
     else:
          document = fitz.open(stream=file.read(), filetype="pdf")

     text = ""
     for page in document:
          text += page.get_text()
     return text

# Function to call the LLM API (assuming a placeholder endpoint)
def call_llm_api(document, criteria, document_type):
     print(document)
     print(criteria)

     prompt = ChatPromptTemplate.from_messages([
          ("system", 
          """
               You are a document validation assistant. Given the criteria: "{criteria}", validate the following base64 encoded PDF document and return a JSON response indicating if the document is valid or not, and a message explaining the result.


               Document Type: {document_type}

               Document Text: {document_text}
               
               Example outputs:
               1. For a valid document: 
               {{"status": "Valid","message": "The document meets all the specified criteria."}}
               2. For an invalid document: 
               {{"status": "Invalid","message": "The document does not meet the following criteria: [explain the issues]."}}

               DO NOT RETURN ANYTHING EXCEPT FOR THE JSON OUTPUT.
          """)
     ])

     llm  = ChatOpenAI(model="gpt-4", temperature=0)

     chain = prompt | llm

     document_text = extract_text_from_pdf(document)

     response = chain.invoke({
          "document_text": document_text,
          "criteria": criteria,
          "document_type": document_type
     })

     print(f"LLM Response: ", response.content)

     result_json = response.content[7:-4].strip() if response.content.startswith('```json') else response.content.strip()

     result_dict = json.loads(result_json)
     return result_dict

# Title of the app
st.title("Document Collection Portal")

# Initialize session state to store document requirements
if "document_requirements" not in st.session_state:
     st.session_state.document_requirements = []

def add_document_requirement():
     st.session_state.document_requirements.append({"type": "", "criteria": "", "file": None, "result": None})

# Section to add document requirements
st.header("Define Document Requirements")

# Display form for each document requirement
for idx, requirement in enumerate(st.session_state.document_requirements):
     st.write(f"### Document {idx + 1}")
     
     doc_type = st.selectbox(f"Document Type {idx + 1}", ["Passport", "Aadhar card", "Bank statement", "Other"], key=f"type_{idx}")
     if doc_type == "Other":
          doc_type = st.text_input(f"Please specify the document type for Document {idx + 1}", key=f"other_type_{idx}")
     
     criteria = st.text_input(f"Criteria for {doc_type}", key=f"criteria_{idx}")

     # Update the session state
     st.session_state.document_requirements[idx]["type"] = doc_type
     st.session_state.document_requirements[idx]["criteria"] = criteria

# Add Document Requirement button at the end
st.button("Add Document Requirement", on_click=add_document_requirement)

# Visual divider between sections
st.markdown("---")

# Section to preview requirements and upload documents
st.header("Preview and Upload Documents")
if len(st.session_state.document_requirements) > 0:
     for idx, requirement in enumerate(st.session_state.document_requirements):
          st.write(f"### Document {idx + 1}: {requirement['type']}")
          st.write(f"Criteria: {requirement['criteria']}")
          uploaded_file = st.file_uploader(f"Upload {requirement['type']}", type=["pdf"], key=f"file_{idx}")

          # Update the session state with uploaded file
          if uploaded_file:
               st.session_state.document_requirements[idx]["file"] = uploaded_file
               result = call_llm_api(uploaded_file, requirement["criteria"], requirement["type"])
               st.session_state.document_requirements[idx]["result"] = result
               
          # Display results if available
          if st.session_state.document_requirements[idx]["result"]:
               result = st.session_state.document_requirements[idx]["result"]
               if result["status"] == "Valid":
                    st.markdown(f"<div style='color: green; font-weight: bold;'>Status: {result['status']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: green;'>{result['message']}</div>", unsafe_allow_html=True)
               else:
                    st.markdown(f"<div style='color: red; font-weight: bold;'>Status: {result['status']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: red;'>{result['message']}</div>", unsafe_allow_html=True)

     # Final submit button
     if st.button("Submit"):
          st.header("Final Submission Results")
          for requirement in st.session_state.document_requirements:
               st.write(f"Document Type: {requirement['type']}")
               if requirement["result"]:
                    result = requirement["result"]
                    if result["status"] == "Valid":
                         st.markdown(f"<div style='color: green; font-weight: bold;'>Status: {result['status']}</div>", unsafe_allow_html=True)
                         st.markdown(f"<div style='color: green;'>{result['message']}</div>", unsafe_allow_html=True)
                    else:
                         st.markdown(f"<div style='color: red; font-weight: bold;'>Status: {result['status']}</div>", unsafe_allow_html=True)
                         st.markdown(f"<div style='color: red;'>{result['message']}</div>", unsafe_allow_html=True)
               else:
                    st.markdown("<div style='color: red; font-weight: bold;'>No file uploaded or validated</div>", unsafe_allow_html=True)

else:
     st.write("No document requirements added yet.")
