from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


def generate_report(
     business_name,
     business_website,
     sanction_data,
     document_data,
     website_data,
     open_source_search_options,
     transactions_data
):

     prompt = ChatPromptTemplate.from_messages([
          ("system", 
          """
               You are an Expert Assistant in Know Your Business (KYB) or Business Due Diligence process.
               You will be given some data, along with their sources and you need to generate a due diligence report
               which will help a compliance / KYC analyst make a judgment whether they should do business with a business or not. 
               Make sure all headings and subheadings are proper and the analyst can read it easily.
               The report should be in MARKDOWN format. 
               NOTE:
               1. Do not write JSON in the report, make it clear, bulleted points.
               2. The report should be in MARKDOWN format. 
               3. OpenSanctions API returns the closest match of the company which has been on the sanctions list. If you feel the company is exactly the same, mention that it is on the sanction list with relevant details; do not directly dump the OpenSanctions API response.
               4. The report should contain the following sections:
                    a. Business Overview
                    b. Sanctions
                    c. Business Incorporation Documents
                    d. Open Source Information
                    e. Website Information
                    f. Transaction Analysis
                    g. Anomalies and Concerns
                    h. Potential Next Steps.
               5. Include relevant subsections in the above sections if needed.
          """),
          ("human", 
          """
               Make a due diligence report for the below business with given details
               
               Business Name: {business_name}
               Business Website: {business_website}

               Data from OpenSanctions API regarding the business: {sanction_data}
               
               Data extracted from business incorporation document: {document_data}
               
               Important scrapped web pages from their website: {website_data}
               
               Conducted open source searches: {open_source_search_options}

               Transaction data flagged for anomalies: {transactions_data}

               Note: You do not need to do actual open source search just include some relevant realistic data, for proof of concept purposes, for each of the sources that are mentioned.

               If information is not consistent, make sure you raise it as an anomaly. For example, if the business name and the name extracted from the document do not match, etc
          """)
     ])

     llm  = ChatOpenAI(model="gpt-4o", temperature=0)

     chain = prompt | llm

     response = chain.invoke({
          "business_name": business_name,
          "business_website": business_website,
          "sanction_data": sanction_data,
          "document_data": document_data,
          "website_data": website_data,
          "open_source_search_options": open_source_search_options,
          "transactions_data": transactions_data
     })

     return response.content
