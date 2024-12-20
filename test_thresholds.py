def calculate_profitability_thresholds(
    fixed_costs: float,
    event_cost: float,
    capacity: int,
    ticket_price_pre: float,
    ticket_price_post: float,
    sales_mix_pre: float
) -> dict:
    """
    Calculate break-even metrics for different attendance levels.
    
    Args:
        fixed_costs (float): Monthly overhead costs
        event_cost (float): Cost per event
        capacity (int): Venue capacity
        ticket_price_pre (float): Early bird ticket price
        ticket_price_post (float): Regular ticket price
        sales_mix_pre (float): Percentage of pre-show sales (0-100)
    
    Returns:
        dict: Keys are attendance percentages, values are (break_even_roas, break_even_cpp) tuples
    """
    # Input validation
    if capacity <= 0:
        raise ValueError("Capacity must be positive")
    if any(price < 0 for price in [ticket_price_pre, ticket_price_post]):
        raise ValueError("Ticket prices cannot be negative")
    if not 0 <= sales_mix_pre <= 100:
        raise ValueError("Sales mix must be between 0 and 100")
    
    attendance_levels = [40, 50, 60, 70, 80, 90]
    thresholds = {}
    
    for attendance in attendance_levels:
        # Calculate total revenue at this attendance level using the specified formula
        total_revenue = (capacity * attendance/100) * (
            (ticket_price_pre * (sales_mix_pre/100)) + 
            (ticket_price_post * (1 - sales_mix_pre/100))
        )
        
        # Calculate total costs
        total_costs = fixed_costs + event_cost
        
        # Calculate break-even metrics
        if total_revenue > 0:
            breakeven_roas = total_costs / total_revenue
        else:
            breakeven_roas = float('inf')
            
        # Calculate break-even CPP
        attendance_count = capacity * attendance / 100
        if attendance_count > 0:
            breakeven_cpp = total_costs / attendance_count
        else:
            breakeven_cpp = float('inf')
            
        thresholds[f"{attendance}%"] = (breakeven_roas, breakeven_cpp)
    
    return thresholds

def test_thresholds():
    # Test inputs
    fixed_costs = 5000
    event_cost = 1000
    capacity = 200
    ticket_price_pre = 25
    ticket_price_post = 50
    sales_mix_pre = 75
    
    print("\nProfitability Thresholds Test", flush=True)
    print("-" * 60, flush=True)
    print(f"Fixed Costs: ${fixed_costs}", flush=True)
    print(f"Event Cost: ${event_cost}", flush=True)
    print(f"Capacity: {capacity}", flush=True)
    print(f"Pre-Show Price: ${ticket_price_pre}", flush=True)
    print(f"Post-Show Price: ${ticket_price_post}", flush=True)
    print(f"Pre-Show Sales Mix: {sales_mix_pre}%", flush=True)
    print("-" * 60, flush=True)
    print(f"{'Attendance':<12} {'Break-Even ROAS':<20} {'Break-Even CPP':<15}", flush=True)
    print("-" * 60, flush=True)
    
    # Debug calculation for 40% attendance
    attendance = 40
    total_revenue = (capacity * attendance/100) * (
        (ticket_price_pre * (sales_mix_pre/100)) + 
        (ticket_price_post * (1 - sales_mix_pre/100))
    )
    total_costs = fixed_costs + event_cost
    print(f"\nDebug 40% attendance:", flush=True)
    print(f"Total Revenue: ${total_revenue:,.2f}", flush=True)
    print(f"Total Costs: ${total_costs:,.2f}", flush=True)
    
    thresholds = calculate_profitability_thresholds(
        fixed_costs=fixed_costs,
        event_cost=event_cost,
        capacity=capacity,
        ticket_price_pre=ticket_price_pre,
        ticket_price_post=ticket_price_post,
        sales_mix_pre=sales_mix_pre
    )
    
    for attendance, (roas, cpp) in thresholds.items():
        print(f"{attendance:<12} {roas:,.2f}x{' ' * 13} ${cpp:,.2f}", flush=True)

if __name__ == "__main__":
    test_thresholds()
