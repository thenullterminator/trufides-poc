import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

from report_generator_utils.sanctions import get_sanction_data
from report_generator_utils.website import get_important_pages
from report_generator_utils.document import extract_data_from_document
from report_generator_utils.report import generate_report


# Stream lit app layout
st.title("Due Diligence Report Generator")

name = st.text_input("Business Name")
jurisdiction = st.text_input("Jurisdiction")
website = st.text_input("Business Website")

incorporation_document = st.file_uploader("Incorporation Document", type=["pdf"])

transactions = st.file_uploader("Transactions alerted", type=["csv"])

open_source_search_options = ["NIA", "OFAC", "Social Media", "Google News", "Yahoo News"]
selected_open_source_options = st.multiselect("Conduct Open Source Searches", open_source_search_options)

private_search_options = ["Lexis Nexis", "World Check", "Onfido", "Signzy"]
selected_private_database = st.multiselect("Conduct Private database Searches", private_search_options)


if st.button("Generate Report"):

     if name and website and jurisdiction and incorporation_document and selected_open_source_options:

          report = None
          transactions_data = None

          with st.status("Generating Report ...", expanded=True) as status:
               
               st.write("Checking for Sanctions...")
               sanction_data = get_sanction_data(name, jurisdiction)

               st.write("Reading Incorporation document...")
               document_data = extract_data_from_document(incorporation_document)

               st.write("Going through Website...")
               website_data = get_important_pages(website)

               st.write("Conducting open source searches on " + ', '.join(selected_open_source_options) +"...")

               if(transactions):
                    st.write("Understanding transactions...")
                    transactions_data = pd.read_csv(transactions)

               st.write("Writing report...")
               report = generate_report(name, website, sanction_data, document_data, website_data,', '.join(selected_open_source_options), transactions_data)

               status.update(label="Report Generated!", state="complete", expanded=False)

          st.write(report)
     else:
          st.error("Please enter a valid input value.")
