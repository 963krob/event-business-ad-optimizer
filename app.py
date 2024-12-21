import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Initialize all session state variables
defaults = {
    "scenarios": {},
    "fixed_costs": 0.0,
    "event_cost": 0.0,
    "ticket_price_pre": 0.0,
    "ticket_price_post": 0.0,
    "venue_capacity": 1,
    "events_per_month": 1,
    "attendance_percentage": 50,
    "sales_mix_pre": 50,
    "ad_spend": 0.0,
    "tickets_sold": 0,
    "historical_attendance": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def save_scenario(name: str, values: dict) -> bool:
    """
    Save current scenario to session state with a custom name.
    
    Args:
        name (str): User-provided name for the scenario
        values (dict): Current input values to save
    
    Returns:
        bool: True if save was successful, False if name already exists
    """
    # Check if name already exists
    if name in st.session_state.scenarios:
        return False
    
    # Add timestamp to values for reference
    values["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.scenarios[name] = values
    return True

def get_current_values():
    """Get current values of all input fields."""
    return {
        "fixed_costs": st.session_state.fixed_costs,
        "event_cost": st.session_state.event_cost,
        "ticket_price_pre": st.session_state.ticket_price_pre,
        "ticket_price_post": st.session_state.ticket_price_post,
        "venue_capacity": st.session_state.venue_capacity,
        "events_per_month": st.session_state.events_per_month,
        "attendance_percentage": st.session_state.attendance_percentage,
        "sales_mix_pre": st.session_state.sales_mix_pre,
        "ad_spend": st.session_state.ad_spend,
        "tickets_sold": st.session_state.tickets_sold,
        "historical_attendance": st.session_state.historical_attendance
    }

def calculate_avg_ticket_price(ticket_price_pre: float, ticket_price_post: float, 
                             sales_mix_pre: float) -> float:
    """
    Calculate weighted average ticket price based on pre-show and post-show prices and their sales mix.
    Formula: (ticket_price_pre * sales_mix_pre/100) + (ticket_price_post * sales_mix_post/100)
    where sales_mix_post = 100 - sales_mix_pre
    
    Args:
        ticket_price_pre (float): Early bird ticket price
        ticket_price_post (float): Regular ticket price
        sales_mix_pre (float): Percentage of tickets sold at pre-show price (0-100)
    
    Returns:
        float: Weighted average ticket price
        
    Raises:
        ValueError: If sales_mix_pre is not between 0 and 100
        ValueError: If ticket prices are negative
    """
    if not 0 <= sales_mix_pre <= 100:
        raise ValueError("Pre-show sales mix must be between 0 and 100")
    if ticket_price_pre < 0 or ticket_price_post < 0:
        raise ValueError("Ticket prices cannot be negative")
    
    # Calculate post-show sales mix
    sales_mix_post = 100 - sales_mix_pre
    
    # Calculate weighted average using the specified formula
    return (ticket_price_pre * sales_mix_pre/100) + (ticket_price_post * sales_mix_post/100)

def calculate_total_fixed_costs(fixed_costs: float, events_per_month: int) -> float:
    """
    Calculate total fixed costs for the month.
    Formula: fixed_costs * events_per_month
    
    Args:
        fixed_costs (float): Monthly overhead costs
        events_per_month (int): Number of events planned for the month
    
    Returns:
        float: Total fixed costs for the month
        
    Raises:
        ValueError: If fixed_costs or events_per_month is negative
    """
    if fixed_costs < 0:
        raise ValueError("Fixed costs cannot be negative")
    if events_per_month < 0:
        raise ValueError("Events per month cannot be negative")
        
    return fixed_costs * events_per_month

def calculate_projected_revenue(avg_ticket_price: float, venue_capacity: int, 
                              attendance_percentage: float, events_per_month: int) -> float:
    """
    Calculate projected revenue based on average ticket price, capacity, and attendance.
    Formula: avg_ticket_price * capacity * (attendance_percentage/100) * events_per_month
    
    Args:
        avg_ticket_price (float): Weighted average ticket price
        venue_capacity (int): Maximum venue capacity
        attendance_percentage (float): Expected attendance percentage (0-100)
        events_per_month (int): Number of events per month
    
    Returns:
        float: Projected monthly revenue
        
    Raises:
        ValueError: If attendance_percentage is not between 0 and 100
        ValueError: If venue_capacity is negative
        ValueError: If events_per_month is negative
    """
    if not 0 <= attendance_percentage <= 100:
        raise ValueError("Attendance percentage must be between 0 and 100")
    if venue_capacity < 0:
        raise ValueError("Venue capacity cannot be negative")
    if events_per_month < 0:
        raise ValueError("Events per month cannot be negative")
    
    # Calculate revenue per event first
    revenue_per_event = avg_ticket_price * venue_capacity * (attendance_percentage/100)
    
    # Multiply by number of events to get monthly revenue
    return revenue_per_event * events_per_month

def calculate_projected_profit(projected_revenue: float, total_fixed_costs: float,
                             event_cost: float, events_per_month: int, ad_spend: float) -> float:
    """
    Calculate projected profit by subtracting all costs from revenue.
    Formula: projected_revenue - total_fixed_costs - (event_cost * events_per_month) - ad_spend
    
    Args:
        projected_revenue (float): Total projected revenue
        total_fixed_costs (float): Total fixed costs
        event_cost (float): Cost per event
        events_per_month (int): Number of events planned for the month
        ad_spend (float): Current advertising spend
    
    Returns:
        float: Projected profit
        
    Raises:
        ValueError: If any cost values are negative
    """
    if any(cost < 0 for cost in [event_cost, events_per_month, ad_spend]):
        raise ValueError("Cost values cannot be negative")
    
    return projected_revenue - total_fixed_costs - (event_cost * events_per_month) - ad_spend

def calculate_breakeven_roas(total_fixed_costs: float, event_cost: float,
                           events_per_month: int, projected_revenue: float) -> float:
    """
    Calculate break-even Return on Ad Spend (ROAS).
    First calculates breakeven_ad_spend, then determines ROAS needed to break even.
    
    Args:
        total_fixed_costs (float): Total fixed costs
        event_cost (float): Cost per event
        events_per_month (int): Number of events per month
        projected_revenue (float): Projected revenue at current attendance
    
    Returns:
        float: Break-even ROAS value
    """
    # Calculate breakeven ad spend (total costs excluding ad spend)
    breakeven_ad_spend = total_fixed_costs + (event_cost * events_per_month)
    
    # Calculate break-even ROAS
    # ROAS = projected_revenue / breakeven_ad_spend
    return projected_revenue / breakeven_ad_spend if breakeven_ad_spend > 0 else float('inf')

def calculate_current_roas(projected_revenue: float, ad_spend: float) -> float:
    """
    Calculate current Return on Ad Spend (ROAS).
    Formula: total_revenue / ad_spend
    
    Args:
        projected_revenue (float): Total projected revenue
        ad_spend (float): Current advertising spend
    
    Returns:
        float: Current ROAS value, or None if ad_spend is 0
    """
    if ad_spend == 0:
        return None
    return projected_revenue / ad_spend

def calculate_current_cpp(ad_spend: float, tickets_sold: int) -> float:
    """
    Calculate current Cost Per Purchase (CPP).
    Formula: ad_spend / tickets_sold
    
    Args:
        ad_spend (float): Current advertising spend
        tickets_sold (int): Number of tickets sold
    
    Returns:
        float: Current CPP value, or None if no tickets sold
    """
    if tickets_sold == 0:
        return None
    return ad_spend / tickets_sold

def calculate_breakeven_cpp(total_fixed_costs: float, event_cost: float,
                          events_per_month: int, venue_capacity: int,
                          attendance_percentage: float) -> float:
    """
    Calculate break-even Cost Per Purchase (CPP).
    Formula: breakeven_ad_spend / projected_tickets_sold
    
    Args:
        total_fixed_costs (float): Total fixed costs
        event_cost (float): Cost per event
        events_per_month (int): Number of events per month
        venue_capacity (int): Venue capacity
        attendance_percentage (float): Expected attendance percentage
    
    Returns:
        float: Break-even CPP value
    """
    # Calculate breakeven ad spend (total costs excluding ad spend)
    breakeven_ad_spend = total_fixed_costs + (event_cost * events_per_month)
    
    # Calculate projected tickets sold
    projected_tickets_sold = venue_capacity * (attendance_percentage/100) * events_per_month
    
    # Calculate break-even CPP
    return breakeven_ad_spend / projected_tickets_sold if projected_tickets_sold > 0 else float('inf')

# Page configuration
st.set_page_config(
    page_title="Event Business Ad Optimizer",
    page_icon="icon.svg",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    
    /* Containers */
    .metric-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Text styles */
    .info-text {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Input fields */
    .stNumberInput input {
        border: 2px solid #dee2e6 !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem !important;
        transition: border-color 0.15s ease-in-out;
    }
    .stNumberInput input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31,119,180,0.25) !important;
    }
    
    /* Slider */
    .stSlider {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    .stSlider .stSlider-value {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        color: #1f77b4 !important;
    }
    
    /* Profit/Loss colors */
    .profit-positive {
        color: #28a745 !important;
    }
    .profit-negative {
        color: #dc3545 !important;
    }
    .profit-zero {
        color: #6c757d !important;
    }
    
    /* Table enhancements */
    .stDataFrame {
        border: 1px solid #dee2e6 !important;
        border-radius: 0.5rem !important;
    }
    .stDataFrame th {
        background-color: #f8f9fa !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize scenarios if not present
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = {}

# Main title and help section
st.markdown("<h1 class='main-header'>Event Business Ad Optimizer</h1>", unsafe_allow_html=True)

# Help button in top right
help_col1, help_col2 = st.columns([11, 1])
with help_col2:
    show_help = st.button("❔ Help", help="Click for help and documentation", type="secondary")

# Help modal
if show_help:
    with st.container():
        st.markdown("<div class='metric-container' style='padding: 2rem;'>", unsafe_allow_html=True)
        
        # Title with close button
        close_col1, close_col2 = st.columns([11, 1])
        with close_col1:
            st.markdown("<h2 style='margin-top: 0;'>Understanding the Ad Optimizer</h2>", unsafe_allow_html=True)
        with close_col2:
            if st.button("✕", help="Close help"):
                st.rerun()
        
        # Divider
        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        # Two-column layout for content
        help_left, help_right = st.columns(2)
        
        with help_left:
            st.markdown("""
            #### 📊 Key Metrics
            
            **Break-even ROAS**  
            The Return on Ad Spend needed to cover your costs. If your ROAS is lower, you're losing money. If it's higher, you're making money.
            
            **Break-even CPP**  
            The Cost Per Purchase you need to reach to cover your costs. If your CPP is higher, you're losing money. If it's lower, you're making money.
            
            **Projected Profit/Loss**  
            Your expected total profit or loss based on current inputs. Red indicates a loss, green indicates profit. Monitor this to track profitability.
            """)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            #### 🎯 Understanding Results
            
            **Color Coding**
            - 🟢 Green: Profitable
            - 🔴 Red: Loss
            - ⚪ Gray: Break-even
            
            **Thresholds Table**  
            Shows break-even metrics at different attendance levels to help optimize your strategy.
            """)
        
        with help_right:
            st.markdown("""
            #### 🛠️ Tool Features
            
            **Save Scenario** 💾  
            Save your current inputs to return to them later. Perfect for experimenting with multiple scenarios.
            
            **Load Scenario** 📂  
            Load a previously saved scenario to save time and effort when comparing options.
            
            **Reset Inputs** 🔄  
            Quickly clear all current input values to start fresh.
            """)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            #### 💡 Tips
            
            - All monetary values are in USD
            - Values update in real-time
            - Use the attendance slider to test different scenarios
            - Compare scenarios to optimize your strategy
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)

def reset_inputs():
    """Reset all input fields to their default values."""
    defaults = {
        "fixed_costs": 0.0,
        "event_cost": 0.0,
        "ticket_price_pre": 0.0,
        "ticket_price_post": 0.0,
        "venue_capacity": 1,
        "events_per_month": 1,
        "attendance_percentage": 50,
        "sales_mix_pre": 50,
        "ad_spend": 0.0,
        "tickets_sold": 0,
        "historical_attendance": 0
    }
    for key, value in defaults.items():
        st.session_state[key] = value

# Save/Load section with improved layout
st.markdown("<h2 class='section-header'>Scenario Management</h2>", unsafe_allow_html=True)
scenario_container = st.container()
with scenario_container:
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
    save_col, load_col, reset_col = st.columns([4, 4, 2])
    
    # Save controls
    with save_col:
        st.markdown("<p class='info-text'>Save Current Scenario</p>", unsafe_allow_html=True)
        scenario_name = st.text_input(
            "Scenario Name",
            key="scenario_name",
            help="Enter a unique name for this scenario"
        )
        
        if st.button("💾 Save", help="Save current input values as a new scenario"):
            if not scenario_name.strip():
                st.error("Please enter a name for the scenario.")
            else:
                try:
                    if save_scenario(scenario_name.strip(), get_current_values()):
                        st.success(f"Scenario saved successfully as: {scenario_name}")
                        # Clear the input field
                        st.session_state.scenario_name = ""
                    else:
                        st.error(f"A scenario with the name '{scenario_name}' already exists. Please use a different name.")
                except Exception as e:
                    st.error(f"Error saving scenario: {str(e)}")
    
    # Load controls
    with load_col:
        st.markdown("<p class='info-text'>Load Saved Scenario</p>", unsafe_allow_html=True)
        if st.session_state.scenarios:
            # Sort scenarios by save time if available
            scenarios = list(st.session_state.scenarios.items())
            scenarios.sort(key=lambda x: x[1].get("saved_at", ""), reverse=True)
            scenario_names = [name for name, _ in scenarios]
            
            selected_scenario = st.selectbox(
                "Select Scenario",
                options=scenario_names,
                help="Choose a saved scenario to load",
                format_func=lambda x: f"{x} (Saved: {st.session_state.scenarios[x].get('saved_at', 'Unknown date')})"
            )
            
            if st.button("📂 Load", help="Load the selected scenario"):
                try:
                    values = st.session_state.scenarios[selected_scenario]
                    # Don't copy saved_at to session state
                    values.pop("saved_at", None)
                    for key, value in values.items():
                        st.session_state[key] = value
                    st.success(f"Loaded scenario: {selected_scenario}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading scenario: {str(e)}")
        else:
            st.info("No saved scenarios available")
    # Reset controls
    with reset_col:
        st.markdown("<p class='info-text'>Reset All Inputs</p>", unsafe_allow_html=True)
        if st.button("🔄 Reset", 
                    help="Reset all input fields to their default values",
                    type="secondary"):
            reset_inputs()
            st.success("All inputs have been reset to defaults")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Create two columns for the main layout
left_col, right_col = st.columns([4, 6], gap="large")

# Input fields in the left column
with left_col:
    st.markdown("<h2 class='section-header'>Business Parameters</h2>", unsafe_allow_html=True)
    
    # Cost inputs
    st.subheader("Cost Parameters")
    
    fixed_costs = st.number_input(
        "Monthly Overhead Costs (USD)",
        key="fixed_costs",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Fixed monthly costs including rent, salaries, utilities, etc. Must be 0 or greater."
    )
    if fixed_costs < 0:
        st.error("Monthly overhead costs cannot be negative.")
    
    event_cost = st.number_input(
        "Event Production Cost (USD)",
        key="event_cost",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Cost to produce a single event including talent, equipment, staff, etc. Must be 0 or greater."
    )
    if event_cost < 0:
        st.error("Event production cost cannot be negative.")
    
    # Ticket pricing inputs
    st.subheader("Ticket Parameters")
    
    ticket_price_pre = st.number_input(
        "Pre-Show Ticket Price (USD)",
        key="ticket_price_pre",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Early bird ticket price before the event. Must be 0 or greater."
    )
    if ticket_price_pre < 0:
        st.error("Pre-show ticket price cannot be negative.")
    
    ticket_price_post = st.number_input(
        "Post-Show Ticket Price (USD)",
        key="ticket_price_post",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Regular ticket price closer to the event. Must be 0 or greater."
    )
    if ticket_price_post < 0:
        st.error("Post-show ticket price cannot be negative.")
    
    # Capacity and schedule inputs
    st.subheader("Venue Parameters")
    
    venue_capacity = st.number_input(
        "Venue Capacity",
        key="venue_capacity",
        min_value=1,
        value=1,
        step=10,
        help="Maximum number of tickets that can be sold per event. Must be at least 1."
    )
    if venue_capacity < 1:
        st.error("Venue capacity must be at least 1.")
    
    events_per_month = st.number_input(
        "Number of Events per Month",
        key="events_per_month",
        min_value=1,
        value=1,
        step=1,
        help="How many events you plan to run each month. Must be at least 1."
    )
    if events_per_month < 1:
        st.error("Number of events must be at least 1.")
    
    st.markdown("---")  # Visual separator
    
    # Attendance and sales mix inputs
    st.subheader("Performance Parameters")
    
    # Attendance percentage with enhanced display
    st.markdown("<p class='info-text'>Attendance Percentage</p>", unsafe_allow_html=True)
    attendance_percentage = st.slider(
        "##",  # Hidden label since we're using custom one above
        key="attendance_percentage",
        min_value=0,
        max_value=100,
        value=50,
        help="Expected percentage of venue capacity that will attend. Must be between 0 and 100."
    )
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #1f77b4;'><strong>{attendance_percentage}%</strong></p>", unsafe_allow_html=True)
    
    sales_mix_pre = st.number_input(
        "Sales Mix - Pre-Show Tickets (%)",
        key="sales_mix_pre",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="Percentage of tickets expected to be sold at pre-show price. Must be between 0 and 100."
    )
    if not 0 <= sales_mix_pre <= 100:
        st.error("Sales mix percentage must be between 0 and 100.")
    
    # Display the calculated post-show sales mix
    st.info(f"Sales Mix - Post-Show Tickets: {100 - sales_mix_pre}%")
    
    # Ad spend and current sales inputs
    st.subheader("Current Performance")
    
    ad_spend = st.number_input(
        "Current Ad Spend (USD)",
        key="ad_spend",
        min_value=0.0,
        value=0.0,
        step=50.0,
        help="Current advertising budget being spent. Must be 0 or greater."
    )
    if ad_spend < 0:
        st.error("Ad spend cannot be negative.")
    
    tickets_sold = st.number_input(
        "Current Number of Tickets Sold",
        key="tickets_sold",
        min_value=0,
        value=0,
        step=1,
        help="Number of tickets sold so far for the upcoming event. Must be 0 or greater."
    )
    if tickets_sold < 0:
        st.error("Number of tickets sold cannot be negative.")
    
    historical_attendance = st.number_input(
        "Historical Average Attendance (Optional)",
        key="historical_attendance",
        min_value=0,
        value=0,
        step=10,
        help="Optional: Input your historical average attendance if available. Must be 0 or greater if provided."
    )
    if historical_attendance < 0:
        st.error("Historical attendance cannot be negative.")

def calculate_threshold_metrics(attendance_level: float, avg_ticket_price: float,
                              venue_capacity: int, events_per_month: int,
                              total_fixed_costs: float, event_cost: float) -> tuple[float, float]:
    """
    Calculate Break-Even ROAS and CPP for a given attendance level.
    Uses existing calculation functions for consistency.
    
    Args:
        attendance_level (float): Attendance percentage to calculate for
        avg_ticket_price (float): Average ticket price
        venue_capacity (int): Venue capacity
        events_per_month (int): Number of events per month
        total_fixed_costs (float): Total fixed costs
        event_cost (float): Cost per event
    
    Returns:
        tuple[float, float]: (Break-even ROAS, Break-even CPP)
    """
    # Calculate projected revenue at this attendance level
    revenue = calculate_projected_revenue(
        avg_ticket_price=avg_ticket_price,
        venue_capacity=venue_capacity,
        attendance_percentage=attendance_level,
        events_per_month=events_per_month
    )
    
    # Calculate break-even ROAS
    roas = calculate_breakeven_roas(
        total_fixed_costs=total_fixed_costs,
        event_cost=event_cost,
        events_per_month=events_per_month,
        projected_revenue=revenue
    )
    
    # Calculate break-even CPP
    cpp = calculate_breakeven_cpp(
        total_fixed_costs=total_fixed_costs,
        event_cost=event_cost,
        events_per_month=events_per_month,
        venue_capacity=venue_capacity,
        attendance_percentage=attendance_level
    )
    
    return roas, cpp

# Calculate current values
try:
    # Average ticket price
    avg_ticket_price = calculate_avg_ticket_price(
        ticket_price_pre=ticket_price_pre,
        ticket_price_post=ticket_price_post,
        sales_mix_pre=sales_mix_pre
    )
    
    # Total fixed costs
    total_fixed_costs = calculate_total_fixed_costs(
        fixed_costs=fixed_costs,
        events_per_month=events_per_month
    )
    
    # Projected revenue
    projected_revenue = calculate_projected_revenue(
        avg_ticket_price=avg_ticket_price,
        venue_capacity=venue_capacity,
        attendance_percentage=attendance_percentage,
        events_per_month=events_per_month
    )
    
    # Projected profit (including ad spend)
    projected_profit = calculate_projected_profit(
        projected_revenue=projected_revenue,
        total_fixed_costs=total_fixed_costs,
        event_cost=event_cost,
        events_per_month=events_per_month,
        ad_spend=ad_spend
    )
    
    # Break-even ROAS
    breakeven_roas = calculate_breakeven_roas(
        total_fixed_costs=total_fixed_costs,
        event_cost=event_cost,
        events_per_month=events_per_month,
        projected_revenue=projected_revenue
    )
    
    # Break-even CPP
    breakeven_cpp = calculate_breakeven_cpp(
        total_fixed_costs=total_fixed_costs,
        event_cost=event_cost,
        events_per_month=events_per_month,
        venue_capacity=venue_capacity,
        attendance_percentage=attendance_percentage
    )
    
    # Display metrics in the right column
    with right_col:
        st.markdown("<h2 class='section-header'>Financial Projections</h2>", unsafe_allow_html=True)
        
        # Key financial metrics
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        
        # Profit display with color coding
        profit_class = (
            "profit-positive" if projected_profit > 0
            else "profit-negative" if projected_profit < 0
            else "profit-zero"
        )
        profit_value = f"${abs(projected_profit):,.2f}"
        if projected_profit < 0:
            profit_value = f"-{profit_value}"
        
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h3 style='margin-bottom: 0.5rem;'>Monthly Profit/Loss</h3>
                <p class='{profit_class}' style='font-size: 2rem; font-weight: bold; margin: 0;'>
                    {profit_value}
                </p>
                <p style='margin-top: 0.5rem; text-align: center;' class='{profit_class}'>
                    {
                        "Your current scenario is profitable." if projected_profit > 0
                        else "Your current scenario is at break-even." if projected_profit == 0
                        else "Your current scenario is not yet profitable."
                    }
                </p>
                <p style='margin-top: 0.5rem; text-align: center; font-style: italic;'>
                    {
                        "Your current ROAS is below break-even. Consider increasing ad spend or attendance to reach profitability."
                        if current_roas is not None and current_roas < breakeven_roas
                        else "Your current ROAS is at or above break-even."
                        if current_roas is not None
                        else ""
                    }
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Revenue and pricing metrics
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric(
                label="Monthly Revenue",
                value=f"${projected_revenue:,.2f}",
                help="Projected total revenue for the month"
            )
            st.metric(
                label="Average Ticket Price",
                value=f"${avg_ticket_price:,.2f}",
                help="Weighted average of pre-show and post-show ticket prices"
            )
        
        with metric_cols[1]:
            st.metric(
                label="Total Fixed Costs",
                value=f"${total_fixed_costs:,.2f}",
                help="Total monthly fixed costs"
            )
            st.metric(
                label="Total Event Costs",
                value=f"${event_cost * events_per_month:,.2f}",
                help="Total costs for all events this month"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Performance metrics
        st.markdown("<h3 class='section-header'>Performance Metrics</h3>", unsafe_allow_html=True)
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        perf_cols = st.columns(2)
        
        with perf_cols[0]:
            st.metric(
                label="Break-even ROAS",
                value=f"{breakeven_roas:.2f}x" if breakeven_roas != float('inf') else "∞",
                help="Revenue needed per dollar of ad spend to break even"
            )
            current_roas = calculate_current_roas(
                projected_revenue=projected_revenue,
                ad_spend=ad_spend
            )
            st.metric(
                label="Current ROAS",
                value=("N/A" if current_roas is None else 
                      f"{current_roas:.2f}x " + 
                      (f"<span style='color: #28a745;'>⬤ (Good)</span>" if current_roas is not None and current_roas >= breakeven_roas else 
                       f"<span style='color: #dc3545;'>⬤ (Needs Improvement)</span>" if current_roas is not None else "")),
                help="Current revenue per dollar of ad spend",
                delta=None if current_roas is None or breakeven_roas == float('inf')
                else f"{current_roas - breakeven_roas:.2f}x",
                delta_color="normal" if current_roas is None else "inverse"
            )
        
        with perf_cols[1]:
            st.metric(
                label="Break-even CPP",
                value=f"${breakeven_cpp:,.2f}" if breakeven_cpp != float('inf') else "∞",
                help="Cost per ticket needed to break even"
            )
            current_cpp = calculate_current_cpp(
                ad_spend=ad_spend,
                tickets_sold=tickets_sold
            )
            st.metric(
                label="Current CPP",
                value=("N/A" if current_cpp is None else 
                      f"${current_cpp:,.2f} " + 
                      (f"<span style='color: #28a745;'>⬤ (Good)</span>" if current_cpp is not None and current_cpp <= breakeven_cpp else 
                       f"<span style='color: #dc3545;'>⬤ (Needs Improvement)</span>" if current_cpp is not None else "")),
                help="Current ad spend per ticket sold",
                delta=None if current_cpp is None or breakeven_cpp == float('inf')
                else breakeven_cpp - current_cpp,
                delta_color="normal" if current_cpp is None else "inverse"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Profitability thresholds table
        st.markdown("<h3 class='section-header'>Profitability Thresholds</h3>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            # Calculate metrics for different attendance levels
            attendance_levels = [40, 50, 60, 70, 80, 90]
            threshold_data = []
            
            for level in attendance_levels:
                roas, cpp = calculate_threshold_metrics(
                    attendance_level=level,
                    avg_ticket_price=avg_ticket_price,
                    venue_capacity=venue_capacity,
                    events_per_month=events_per_month,
                    total_fixed_costs=total_fixed_costs,
                    event_cost=event_cost
                )
                
                threshold_data.append({
                    "Attendance Level": f"{level}%",
                    "Break-Even ROAS": f"{roas:.2f}x" if roas != float('inf') else "∞",
                    "Break-Even CPP": f"${cpp:.2f}" if cpp != float('inf') else "∞"
                })
            
            # Display the table with enhanced styling
            st.dataframe(
                threshold_data,
                column_config={
                    "Attendance Level": st.column_config.TextColumn(
                        "Attendance Level",
                        help="Percentage of venue capacity"
                    ),
                    "Break-Even ROAS": st.column_config.TextColumn(
                        "Break-Even ROAS",
                        help="Revenue needed per dollar of ad spend to break even"
                    ),
                    "Break-Even CPP": st.column_config.TextColumn(
                        "Break-Even CPP",
                        help="Cost per ticket needed to break even"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

except ValueError as e:
    st.error(f"Calculation Error: {str(e)}")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
