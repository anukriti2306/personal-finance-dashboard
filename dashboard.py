import streamlit as st
import pandas as pd
import numpy as np
import gspread
import hvplot.pandas
import holoviews as hv
from bokeh.models import Panel as BokehPanel

hv.extension('bokeh')

# Load data from Google Sheets
gc = gspread.service_account(filename="service_account.json")
sh = gc.open('bank_statement_april')
ws = sh.worksheet('Sheet1')
df = pd.DataFrame(ws.get_all_records())

# Data cleaning
df = df[['Date', 'Narration', 'Amount']]
df['Narration'] = df['Narration'].str.lower()
df.rename(columns={'Narration': 'Description'}, inplace=True)
df['Category'] = 'unassigned'

# Category assignment
df['Category'] = np.where(df['Description'].str.contains('utilities payment'), 'Utilities', df['Category'])
df['Category'] = np.where(df['Description'].str.contains('salary deposit'), 'Salary', df['Category'])
df['Category'] = np.where(df['Description'].str.contains('atm withdrawal'), 'ATM', df['Category'])
df['Category'] = np.where(df['Description'].str.contains('online shopping'), 'Shopping', df['Category'])
df['Category'] = np.where(df['Description'].str.contains('grocery store'), 'Grocery', df['Category'])

# Format Date
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['Month-Year'] = df['Date'].dt.to_period('M').astype(str)

# Filter latest expenses
latest_month = df['Month'].max()
latest_year = df['Year'].max()
latest_expense = df[((df['Month'] == latest_month) | (df['Month'] == latest_month - 1)) & (df['Year'] == latest_year)]

# Summarize
last_month_expenses = latest_expense.groupby('Category')['Amount'].sum().reset_index()
last_month_expenses = last_month_expenses[~last_month_expenses['Category'].str.contains('unassigned')]
last_month_expenses['Amount'] = last_month_expenses['Amount'].astype(float).abs().round().astype(int)
last_month_expenses = last_month_expenses.sort_values(by='Amount', ascending=False)
total_expense = last_month_expenses['Amount'].sum()

# Sidebar Inputs
st.sidebar.image("image.png", width=250)
st.sidebar.markdown("### Income & Expenses")
income = st.sidebar.number_input("Monthly Income", min_value=0, value=0)
recurring = st.sidebar.number_input("Recurring Expenses", min_value=0, value=0)
non_recurring = st.sidebar.number_input("Non-Recurring Expenses", value=int(total_expense))
savings = income - recurring - non_recurring
st.sidebar.metric("Estimated Savings", f"₹ {savings}")

# Expense Category Bar Chart
st.header("💸 Last Month's Expenses by Category")
bar_chart = last_month_expenses.hvplot.bar(
    x='Category', y='Amount', height=300, width=700, title='Expenses', ylim=(0, 500)
)
st.bokeh_chart(hv.render(bar_chart, backend='bokeh'), use_container_width=True)

# Trend by Month
monthly_expenses = df.groupby(['Month-Year', 'Category'])['Amount'].sum().reset_index()
monthly_expenses = monthly_expenses[~monthly_expenses['Category'].str.contains('unassigned')]
monthly_expenses['Amount'] = monthly_expenses['Amount'].astype(float).abs().round().astype(int)

st.header("📈 Monthly Expenses Trend")
categories = ['All'] + sorted(monthly_expenses['Category'].unique())
selected_category = st.selectbox("Choose a category", categories)

if selected_category == 'All':
    trend_df = monthly_expenses.groupby('Month-Year')['Amount'].sum().reset_index()
else:
    trend_df = monthly_expenses[monthly_expenses['Category'] == selected_category]

line_chart = trend_df.hvplot.bar(x='Month-Year', y='Amount', title=f"Trend - {selected_category}")
st.bokeh_chart(hv.render(line_chart, backend='bokeh'), use_container_width=True)

# Summary Table
st.header("📊 Transaction Summary")
if selected_category == 'All':
    summary_df = df[df['Category'] != 'unassigned']
else:
    summary_df = df[df['Category'] == selected_category]

summary_df = summary_df[['Date', 'Category', 'Description', 'Amount']]
summary_df['Amount'] = summary_df['Amount'].astype(float).abs().round().astype(int)
st.dataframe(summary_df.reset_index(drop=True), height=400)
