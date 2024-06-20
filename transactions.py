import pandas as pd
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Generate enhanced dummy transaction data
def generate_dummy_transactions():
    company_name = "Porter"
    start_date = datetime(2024, 1, 1)
    transactions = []
    
    sources = ["Client A", "Client B", "Client C"]
    destinations = ["Supplier X", "Supplier Y", "Supplier Z"]
    
    for i in range(150):  # From Jan 1 to May 30, 2024
        date = start_date + timedelta(days=i)
        timestamp = date.strftime('%Y-%m-%d %H:%M:%S')
        invoice_id = f"INV-{i+1:04d}"
        account_number = f"{random.randint(1000000000, 9999999999)}"
        amount = round(random.uniform(100, 10000), 2)
        type = random.choice(['Credit', 'Debit'])
        
        if type == 'Credit':
            description = f"{random.choice(sources)}"
        else:
            description = f"{random.choice(destinations)}"
        
        # Introduce anomalies
        anomaly_type = None
        if i % 30 == 0:  # Large amounts on the same day each month
            amount = round(random.uniform(50000, 100000), 2)
            anomaly_type = "Large Transaction"
        if i % 45 == 0 and type == 'Debit':  # Large debit amounts every 45 days
            amount = round(random.uniform(10000, 50000), 2)
            anomaly_type = "Large Debit"

        transactions.append([
            timestamp, invoice_id, account_number, f"${amount}", type, description, anomaly_type
        ])
    
    df = pd.DataFrame(transactions, columns=[
        'Timestamp', 'Invoice ID', 'Account Number', 'Amount', 'Type', 'Description', 'Anomaly Type'
    ])
    return df

# Create PDF from transaction data with enhanced metadata
def create_pdf(transactions_df, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 10)
    c.drawString(30, height - 30, "Transaction Monitoring Alert Report")
    c.drawString(30, height - 45, "Company: Porter")
    c.drawString(30, height - 60, "Date Range: January - May 2024")
    
    # Table header
    headers = ['Timestamp', 'Invoice ID', 'Account Number', 'Amount', 'Type', 'Description', 'Anomaly Type']
    x_positions = [30, 130, 230, 330, 380, 430, 530]

    for x, header in zip(x_positions, headers):
        c.drawString(x, height - 90, header)
    
    y = height - 105
    for index, row in transactions_df.iterrows():
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40
            for x, header in zip(x_positions, headers):
                c.drawString(x, y, header)
            y -= 15

        for x, value in zip(x_positions, row):
            c.drawString(x, y, str(value))
        y -= 15

    c.save()
    
    with open(filename, 'wb') as f:
        f.write(buffer.getvalue())

# Generate and save the CSV file
def create_csv(transactions_df, filename):
    transactions_df.to_csv(filename, index=False)

# Generate the data
transactions_df = generate_dummy_transactions()

# Create and save the PDF
create_pdf(transactions_df, 'transaction_monitoring_alert_report.pdf')

# Create and save the CSV
create_csv(transactions_df, 'transaction_monitoring_alert_report.csv')

print("PDF and CSV files generated successfully!")
