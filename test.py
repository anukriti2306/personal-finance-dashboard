import csv
import random
from datetime import datetime, timedelta

# Generate random transactions with additional fields
def generate_transactions(start_date, num_transactions, initial_balance=5000):
    transactions = []
    current_date = start_date
    closing_balance = initial_balance

    for _ in range(num_transactions):
        narration = random.choice(['ATM Withdrawal', 'Grocery Store', 'Salary Deposit', 'Utilities Payment', 'Online Shopping'])
        chq_ref_no = random.randint(100000, 999999)  # Random cheque or reference number
        value_dt = current_date + timedelta(days=random.randint(1, 3))  # Random value date within 1-3 days from transaction date
        amount = round(random.uniform(10, 1000), 2) if narration != 'Salary Deposit' else round(random.uniform(1000, 5000), 2)
        
        # Adjust balance based on transaction type
        if 'Deposit' in narration:
            closing_balance += amount
        else:
            closing_balance -= amount
        
        transactions.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Narration': narration,
            'Chq./Ref.No.': chq_ref_no,
            'Value Dt': value_dt.strftime('%Y-%m-%d'),
            'Amount': amount,
            'Closing Balance': round(closing_balance, 2)
        })
        
        # Move to the next day
        current_date += timedelta(days=random.randint(1, 3))  # Random interval between transactions
    
    return transactions

# Write the transactions to a CSV file
def write_csv(filename, transactions):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Amount', 'Closing Balance'])
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

# Main function to generate a sample bank statement CSV
def generate_bank_statement_csv():
    # Set the start date (e.g., first day of the month)
    start_date = datetime(2025, 4, 1)  # April 1st, 2025
    num_transactions = 100  # Number of transactions

    # Generate transactions
    transactions = generate_transactions(start_date, num_transactions)

    # Write to CSV file
    filename = 'bank_statement_april.csv'
    write_csv(filename, transactions)
    print(f"CSV file '{filename}' generated successfully!")

# Run the function
generate_bank_statement_csv()
