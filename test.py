# Task: Get Active Day from an over 31-element list
days = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'] # Start from January 1 which is Wednesday
monthly_messages = [4, 9, 5, 9, 7, 5, 1, 1, 1, 6, 3, 4, 0, 7, 9, 3, 3, 1, 8, 9, 4, 10, 0, 9, 0, 7, 10, 10, 8, 1, 5]

added_weekly_messages = [sum(monthly_messages[i::7]) for i in range(7)]
active_day = max(added_weekly_messages)
day_indexes = ", ".join(days[i] for i,v in enumerate(added_weekly_messages) if v == active_day)

if day_indexes.count(",") == 6:
    day_indexes = " "
print(f"Answer: {day_indexes}")

# Output: returns days[i] with the most accumulated messages