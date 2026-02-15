
def calculate_tax_demo():
    income = 2500
    print(f"--- Calculating Tax for Income: ${income} ---")

    print("\nMethod 1: Step-by-Step (Progressive)")
    # Bracket 1: 0 - 1000 @ 0%
    tax_b1 = 0
    print(f" 1. First $1,000 @ 0%: $0")

    # Bracket 2: 1001 - 2000 @ 10%
    tax_b2 = 1000 * 0.10
    print(f" 2. Next $1,000 @ 10%: ${tax_b2}")

    # Bracket 3: 2001+ @ 20%
    remaining = income - 2000
    tax_b3 = remaining * 0.20
    print(f" 3. Remaining ${remaining} @ 20%: ${tax_b3}")

    total_step_tax = tax_b1 + tax_b2 + tax_b3
    print(f"TOTAL (Step-by-Step): ${total_step_tax}")

    print("\nMethod 2: The Shortcut (Sustraendo)")
    print("Formula: (Total Income * Top Rate) - Sustraendo")
    
    # Top Rate is 20%
    # Sustraendo calc: (2000 * 20%) - (Actual Tax at 2000 which is 100) = 400 - 100 = 300
    sustraendo = 300 
    
    shortcut_tax = (income * 0.20) - sustraendo
    print(f"Formula: ({income} * 0.20) - {sustraendo}")
    print(f"       : {income * 0.20} - {sustraendo}")
    print(f"TOTAL (Shortcut): ${shortcut_tax}")
    
    if total_step_tax == shortcut_tax:
        print("\n✅ MATCH: The shortcut works perfectly!")

if __name__ == "__main__":
    calculate_tax_demo()
