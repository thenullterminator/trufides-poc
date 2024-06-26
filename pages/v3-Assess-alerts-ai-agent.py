import streamlit as st
import pandas as pd
import random
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from report_generator_utils.sanctions import get_sanction_data
import json

# Sample data
data = {
     "Business": ["Porter, India", "Wework, US", "Rim Group, US", "Citi, India"],
     "Risk Status": ["High", "High", "High", "High"],
     "Reason": ["Present in sanction list", "Present in sanction list", "Present in sanction list", "High Risk Country"],
     "Type": ["Onboarding", "Transaction", "Onboarding", "Onboarding"]
}

business_info = {
     "Porter": {"business":"offers last mile logistics solutions", "industry":"logistics", "Address":"Bengaluru, India"},
     "Wework": {"business": "coworking spaces","industry":"real estate", "Address":"USA"},
     "Rim Group": {"business": "investments","industry":"Finance", "Address":"Miami, Florida, USA"},
     "Citi": {"business": "investments","industry":"banking", "Address":"Bandra, Mumbai, India"}
}


reason = {}

df = pd.DataFrame(data)

# Placeholder for the data
risk_status_options = ["Medium", "Medium", "Low"]

st.title("Alert raised for following business")



if 'df' not in st.session_state:
     st.session_state['df'] = df

if 'reasons' not in st.session_state:
     st.session_state['reasons'] = {}


def double_check_through_ai(
     business
):
     business_name, country = business.split(", ")

     sanctions_data = get_sanction_data(business_name, country)

     prompt = ChatPromptTemplate.from_messages([
          ("system", 
          """
               You are an Expert Assistant in Know Your Business (KYB) or Business Due Diligence process.
               You will serve as a second check for the alerts raised by onboarding system or transaction monitoring system.

               You will be given a business name, country of jurisdiction and the closest match of the business in the open sanctions database in json format.

               You need to match both of them and return a JSON containing 2 fields: 
               1. risk - string, high or low
               2. reason - string, give a reasonable explaination not more than 200 words explaining why you feel the risk is given.

               For matching, you can use names, if you cannot deduce from names, use countries and so on. Please make sure you always give proper reasoning.

               If the match is high, the risk should be high. Since only high risk businesses are present in open sanctions database.

               Example output:
               {{"risk":"High", "reason": "[explain the reason]"}}

               The reason should be in MARKDOWN format with following sections:
               1. Reason of Alert.
               2. Company Details.
               3. Matching Company Details.
               4. Conclusion. (Please include all details of how you did match, all the values, all assertions, every detail of all kind of match and mismatches in point format)
               5. Updated Risk Value.

               If there is not much information try to add realistic dummy data.

               RETURN IN JSON FORMAT, NO OTHER DATA SHOULD BE RETURNED.
          """),
          ("human", 
          """
               Make a due diligence report for the below business with given details
               
               Business Name: {business_name}
               Country: {country}
               business: {business}
               industry: {industry}
               address: {address}

               Closest match in open sanctions: {sanction_data}
          """)
     ])

     llm  = ChatOpenAI(model="gpt-4o", temperature=0)

     chain = prompt | llm

     response = chain.invoke({
          "business_name": business_name,
          "country": country,
          "sanction_data": sanctions_data,
          "business":business_info[business_name]['business'],
          "industry":business_info[business_name]['industry'],
          "address": business_info[business_name]['Address']
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
          business = st.session_state['df'].at[current_row, "Business"]
          response = double_check_through_ai(business)

          print(f"response: {response}")
          print(f"response risk: {response['risk']}")

          new_risk = response['risk']
          st.session_state['df'].at[current_row, "Risk Status"] = new_risk
          
          st.session_state['reasons'][business]= response['reason']
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

header_cols = st.columns((1, 1, 1, 1, 1))
header_cols[0].write("Business Name")
header_cols[1].write("Risk Status")
header_cols[2].write("Reason")
header_cols[3].write("Type")
header_cols[4].write("Details")

# Display the table
for index, row in st.session_state['df'].iterrows():
     cols = st.columns((1, 1, 1, 1, 1))
     cols[0].write(row['Business'])
     if row['Risk Status']:
          color = get_color(row['Risk Status'])
          cols[1].markdown(f"<span style='color:{color}'>{row['Risk Status']}</span>", unsafe_allow_html=True)
     else:
          cols[1].write("")
     
     cols[2].write(row['Reason'])
     cols[3].write(row['Type'])

     if cols[4].button("Show Details", key=f"details_{index}"):
          st.write(f"### Details for {row['Business']}")
          st.write(f"Risk Status: {row['Risk Status'] if row['Risk Status'] else 'Not assessed yet'}")
          st.write(f"{st.session_state['reasons'][row['Business']]}")

# Button to fill data row by row
if st.button("Check for False Positives"):
     fill_data()




# print(double_check_through_ai("Citi, India"))