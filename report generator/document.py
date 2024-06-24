from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import fitz


def extract_text_from_pdf(file):
     document = fitz.open(stream=file.read(), filetype="pdf")
     text = ""
     for page in document:
          text += page.get_text()
     return text


def extract_data_from_document(file):

     prompt = ChatPromptTemplate.from_messages(
          [
               (
                    "system", 
                    """
                    You are an Expert Assistant in reading and understanding business documents. 
                    You will be given text content parsed from a Bussiness Incorporation PDF. 
                    You need to return a JSON containing the following fields:
                    1. name - string, business registered name
                    2. address - string, business registered address
                    3. pan - string, Permanent Account Number or PAN of the company
                    4. cin - string, Corporate Identity Number of the company

                    All fields are compulsory in the JSON output. If you are enable to find a field, make it null
                    """
               ),
               ("human", "PDF Text Content: {input}")
          ]
     )

     llm  = ChatOpenAI(model="gpt-4o", temperature=0)

     chain = prompt | llm

     text = extract_text_from_pdf(file)

     response = chain.invoke({
          "input": text
     })

     return response.content
