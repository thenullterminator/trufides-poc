import streamlit as st
import pandas as pd
import random
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from report_generator_utils.sanctions import get_sanction_data_for_person
import json

# Sample data
data = {
     "Name": ["Inderjeet Singh", "Robert W. Lewise", "Michelle Bouvard"],
     "Country": ["India", "United States", "France"],
     "DOB": ["2005", "1970", "1954"],
     "Risk Status": ["High", "High", "High"],
     "Reason": ["Politically Exposed (PEP)", "Adverse Media", "Politically Exposed (PEP)"],
     "Type": ["Onboarding", "Transaction", "Onboarding"]
}

open_source_info = {
     "Inderjeet Singh": {"google_news":None, "linkedin":{"description":"Computer Science Student at IIT KGP (2022-2026), India", "link":"https://www.linkedin.com/in/devang-singhi/"}},
     "Robert W. Lewise": {"google_news":{"description":"Big Shock:Branch Manager, 54 charged for committing 15 million USD fraud at Silicon Valley Bank", "link":"https://www.business-standard.com/world-news/year-after-silicon-valley-bank-crisis-a-struggle-over-what-needs-to-change-124031000694_1.html"}, "linkedin":{"description":"Branch Manager, Silicon Valley Bank, San Jose, United States", "link":"https://www.linkedin.com/in/devang-singhi/"}},
     "Michelle Bouvard": {"google_news":None, "linkedin":{"description":"Professor, International School of Nice, France", "link":"https://www.linkedin.com/in/devang-singhi/"}},
}


reason = {}

df = pd.DataFrame(data)

# Placeholder for the data
risk_status_options = ["Medium", "Medium", "Low"]

st.title("Alert raised for following Customers")



if 'df' not in st.session_state:
     st.session_state['df'] = df

if 'reasons' not in st.session_state:
     st.session_state['reasons'] = {}


def double_check_through_ai(
     name,
     dob,
     nationality
):

     sanctions_data = get_sanction_data_for_person(name,dob,nationality)

     prompt = ChatPromptTemplate.from_messages([
          ("system", 
          """
               You are an Expert Assistant in Know Your Business (KYB) or Business Due Diligence process.
               You will serve as a second check for the alerts raised by onboarding system or transaction monitoring system.

               You will be given a name of the customer, nationality, Year of birth and the closest match of the customer in the open sanctions database in json format because of which an alert was raised.

               You need to match both of them and return a JSON containing 2 fields: 
               1. risk - string, high or low
               2. reason - string, give a reasonable explaination not more than 200 words explaining why you feel the risk is given.

               For matching, you can use names (phonetic etc), if you cannot deduce from names, use nationality or dob or open source search results and so on. Please make sure you always give proper reasoning.

               If the match is high, the risk should be high. Since only high risk businesses are present in open sanctions database.

               Example output:
               {{"risk":"High", "reason": "[explain the reason]"}}

               The reason should be in MARKDOWN format with following sections:
               1. Reason of Alert.
               2. Customer Details. (Without Open Source results)
               3. Matching Entity Details.
               4. Open Source Search Results (Along with all available links)
               5. Conclusion. (Please include all details and links of how you did match, all the values, all assertions, every detail of all kind of match and mismatches in point format)
               6. Updated Risk Value.

               If there is not much information try to add realistic dummy data.

               RETURN IN JSON FORMAT, NO OTHER DATA SHOULD BE RETURNED.
          """),
          ("human", 
          """
               Make a due diligence report for the below customer with given details

               Name: {name}
               Year of Birth: {dob}
               Nationality: {nationality}
               Open Source Search Results: {open_source_search_results}

               Closest match in open sanctions: {sanction_data}
          """)
     ])

     llm  = ChatOpenAI(model="gpt-4o", temperature=0)

     chain = prompt | llm

     response = chain.invoke({
          "name": name,
          "dob": dob,
          "sanction_data": sanctions_data,
          "nationality": nationality,
          "open_source_search_results":open_source_info[name]
     })

     result_json = response.content[7:-4].strip() if response.content.startswith('```json') else response.content.strip()

     result_dict = json.loads(result_json)
     return result_dict

# Function to simulate risk assessment (for demo purposes)
def assess_risk(business_name):     return random.choice(risk_status_options)

# Function to fill the data row by row
def fill_data():
     
     for i in range(len(st.session_state['df'])):
          current_row = i
          name = st.session_state['df'].at[current_row, "Name"]
          dob = st.session_state['df'].at[current_row, "DOB"]
          nationality = st.session_state['df'].at[current_row, "Country"]


          print(f"fp checking: {name} {dob} {nationality}")


          response = double_check_through_ai(name, dob, nationality)

          print(f"response: {response}")
          print(f"response risk: {response['risk']}")

          new_risk = response['risk']
          st.session_state['df'].at[current_row, "Risk Status"] = new_risk
          
          st.session_state['reasons'][name]= response['reason']
     st.rerun()


# Function to get the color for the risk status
def get_color(risk_status):
     if risk_status == "High":
          return "red"
     elif risk_status == "Medium":
          return "orange"
     elif risk_status == "Low":
          return "green"
     return "black"

header_cols = st.columns((1, 1, 1, 1, 1, 1, 1))
header_cols[0].write("Name")
header_cols[1].write("Country")
header_cols[2].write("DOB")
header_cols[3].write("Risk Status")
header_cols[4].write("Reason")
header_cols[5].write("Type")
header_cols[6].write("Details")

# Display the table
for index, row in st.session_state['df'].iterrows():
     cols = st.columns((1, 1, 1, 1, 1, 1, 1))
     cols[0].write(row['Name'])
     cols[1].write(row['Country'])
     cols[2].write(row['DOB'])
     if row['Risk Status']:
          color = get_color(row['Risk Status'])
          cols[3].markdown(f"<span style='color:{color}'>{row['Risk Status']}</span>", unsafe_allow_html=True)
     else:
          cols[3].write("")
     
     cols[4].write(row['Reason'])
     cols[5].write(row['Type'])

     if cols[6].button("Show Details", key=f"details_{index}"):
          st.write(f"### Details for {row['Name']}")
          st.write(f"Risk Status: {row['Risk Status'] if row['Risk Status'] else 'Not assessed yet'}")
          st.write(f"{st.session_state['reasons'][row['Name']]}")

# Button to fill data row by row
if st.button("Check for False Positives"):
     fill_data()




# print(double_check_through_ai("Citi, India"))