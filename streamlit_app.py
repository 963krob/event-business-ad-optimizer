import streamlit as st
import pandas as pd

# Initialize session state with default values if not already set
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.fixed_costs = 5000
    st.session_state.event_cost = 1000
    st.session_state.ticket_price_pre = 50
    st.session_state.ticket_price_post = 75
    st.session_state.capacity = 500
    st.session_state.attendance_percentage = 60
    st.session_state.sales_mix_pre = 40
    st.session_state.sales_mix_post = 60
    st.session_state.ad_spend = 1000
    st.session_state.events_per_month = 4
    st.session_state.tickets_sold = 100

# Format functions
def format_currency(x): return f"${x:,.2f}"
def format_percent(x): return f"{x}%"

# Input fields
st.sidebar.header("Input Parameters")

# Currency inputs with thousand separators
fixed_costs = st.sidebar.number_input(
    "Monthly Overhead Costs ($)",
    min_value=0, value=st.session_state.fixed_costs, step=100,
    help="Fixed monthly costs")

event_cost = st.sidebar.number_input(
    "Event Production Cost (per event) ($)",
    min_value=0, value=st.session_state.event_cost, step=100,
    help="Cost per event")

ticket_price_pre = st.sidebar.number_input(
    "Pre-Show Ticket Price ($)",
    min_value=0, value=st.session_state.ticket_price_pre, step=5,
    help="Price for pre-show tickets")

ticket_price_post = st.sidebar.number_input(
    "Post-Show Ticket Price ($)",
    min_value=0, value=st.session_state.ticket_price_post, step=5,
    help="Price for post-show tickets")

# Numeric inputs
capacity = st.sidebar.number_input(
    "Venue Capacity",
    min_value=0, value=st.session_state.capacity, step=50,
    help="Maximum number of attendees")

attendance_percentage = st.sidebar.slider(
    "Projected/Target Attendance Percentage",
    min_value=0, max_value=100, value=st.session_state.attendance_percentage,
    format="%d%%",
    help="Expected attendance as percentage of capacity")

# Percentage inputs
sales_mix_pre = st.sidebar.number_input(
    "Expected Sales Mix - Pre-Show Tickets (%)",
    min_value=0, max_value=100, value=st.session_state.sales_mix_pre, step=5,
    help="Percentage of pre-show ticket sales")

sales_mix_post = st.sidebar.number_input(
    "Expected Sales Mix - Post-Show Tickets (%)",
    min_value=0, max_value=100, value=st.session_state.sales_mix_post, step=5,
    help="Percentage of post-show ticket sales")

# Additional inputs
ad_spend = st.sidebar.number_input(
    "Current Ad Spend ($)",
    min_value=0, value=st.session_state.ad_spend, step=100,
    help="Current advertising spend")

events_per_month = st.sidebar.number_input(
    "Number of Events in Current Month",
    min_value=1, value=st.session_state.events_per_month, step=1,
    help="Number of events scheduled this month")

tickets_sold = st.sidebar.number_input(
    "Current Number of Tickets Sold",
    min_value=0, value=st.session_state.tickets_sold, step=10,
    help="Total tickets sold so far")

# Update session state with current values
st.session_state.fixed_costs = fixed_costs
st.session_state.event_cost = event_cost
st.session_state.ticket_price_pre = ticket_price_pre
st.session_state.ticket_price_post = ticket_price_post
st.session_state.capacity = capacity
st.session_state.attendance_percentage = attendance_percentage
st.session_state.sales_mix_pre = sales_mix_pre
st.session_state.sales_mix_post = sales_mix_post
st.session_state.ad_spend = ad_spend
st.session_state.events_per_month = events_per_month
st.session_state.tickets_sold = tickets_sold

# Calculations

def calculate_average_ticket_price(ticket_price_pre, ticket_price_post, sales_mix_pre, sales_mix_post):
    if (sales_mix_pre + sales_mix_post) == 0:
        return 0
    return (ticket_price_pre * (sales_mix_pre / 100)) + (ticket_price_post * (sales_mix_post / 100))

def calculate_total_fixed_costs(fixed_costs, events_per_month):
    return fixed_costs * events_per_month

def calculate_projected_revenue(avg_ticket_price, capacity, attendance_percentage):
    return (avg_ticket_price * capacity) * (attendance_percentage / 100)

def calculate_projected_profit(projected_revenue, total_fixed_costs, event_cost, events_per_month):
     return projected_revenue - total_fixed_costs - (event_cost * events_per_month)

def calculate_breakeven_roas(fixed_costs, event_cost, events_per_month):
    total_fixed_costs = fixed_costs * events_per_month
    if total_fixed_costs == 0:
        return 0 # Avoid division by zero
    total_costs = total_fixed_costs + (event_cost * events_per_month)
    return round((total_costs / total_fixed_costs), 2)

def calculate_breakeven_cpp(total_fixed_costs, event_cost, events_per_month, attendance_percentage, capacity):
     if (attendance_percentage == 0) or (capacity == 0):
         return 0
     total_costs = total_fixed_costs + (event_cost * events_per_month)
     return round((total_costs / (capacity * attendance_percentage / 100)), 2)

def calculate_current_roas(ad_spend, projected_revenue):
    if ad_spend == 0:
        return 0 # Avoid division by zero
    return round((projected_revenue / ad_spend), 2)

def calculate_current_cpp(ad_spend, tickets_sold):
    if tickets_sold == 0:
        return 0
    return round((ad_spend / tickets_sold), 2)

# Calculations
avg_ticket_price = calculate_average_ticket_price(ticket_price_pre, ticket_price_post, sales_mix_pre, sales_mix_post)
total_fixed_costs = calculate_total_fixed_costs(fixed_costs, events_per_month)
projected_revenue = calculate_projected_revenue(avg_ticket_price, capacity, attendance_percentage)
projected_profit = calculate_projected_profit(projected_revenue, total_fixed_costs, event_cost, events_per_month)
breakeven_roas = calculate_breakeven_roas(fixed_costs, event_cost, events_per_month)
breakeven_cpp = calculate_breakeven_cpp(total_fixed_costs, event_cost, events_per_month, attendance_percentage, capacity)
current_roas = calculate_current_roas(ad_spend, projected_revenue)
current_cpp = calculate_current_cpp(ad_spend, tickets_sold)

# Output Fields
st.title("Event Business Ad Optimizer")
st.subheader("Results:")
col1, col2 = st.columns(2)

with col1:
    st.metric("Average Ticket Price", f"${avg_ticket_price:.2f}")
    st.metric("Total Fixed Costs", f"${total_fixed_costs:.2f}")
    st.metric("Break-Even ROAS", f"{breakeven_roas:.2f}")
    st.metric("Break-Even Cost Per Purchase", f"${breakeven_cpp:.2f}")

with col2:
    st.metric("Projected Revenue", f"${projected_revenue:.2f}")
    st.metric("Projected Profit/Loss", f"${projected_profit:.2f}")
    st.metric("Current ROAS", f"{current_roas:.2f}")
    st.metric("Current Cost Per Purchase", f"${current_cpp:.2f}")

st.subheader("Profitability Thresholds")

# Calculate thresholds
attendance_levels = [40, 50, 60, 70, 80, 90]
data = {
    'Attendance Percentage': [f"{p}%" for p in attendance_levels],
    'Break-Even ROAS': [calculate_breakeven_roas(fixed_costs, event_cost, events_per_month) for _ in attendance_levels],
    'Break-Even CPP': [calculate_breakeven_cpp(total_fixed_costs, event_cost, events_per_month, p, capacity) for p in attendance_levels]
}

# Format the DataFrame
df = pd.DataFrame(data)
df['Break-Even ROAS'] = df['Break-Even ROAS'].apply(lambda x: f"{x:.2f}")
df['Break-Even CPP'] = df['Break-Even CPP'].apply(lambda x: f"${x:.2f}")

st.table(df)
