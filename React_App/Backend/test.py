import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Raw data
data = [
    {"Timestamp": 1730738985, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 300, "Unit_Price": 50, "Units_Consumed": 6.0},
    {"Timestamp": 1731037038, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 380, "Unit_Price": 50, "Units_Consumed": 7.6},
    {"Timestamp": 1731678152, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 480, "Unit_Price": 50, "Units_Consumed": 9.6},
    {"Timestamp": 1731747129, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 400, "Unit_Price": 50, "Units_Consumed": 8.0},
    {"Timestamp": 1731811147, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 270, "Unit_Price": 50, "Units_Consumed": 5.4},
    {"Timestamp": 1732010073, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 50, "Unit_Price": 50, "Units_Consumed": 1.0},
    {"Timestamp": 1732186112, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 460, "Unit_Price": 50, "Units_Consumed": 9.2},
    {"Timestamp": 1732268989, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 300, "Unit_Price": 50, "Units_Consumed": 6.0},
    {"Timestamp": 1732430636, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 60, "Unit_Price": 50, "Units_Consumed": 1.2},
    {"Timestamp": 1732553394, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 500, "Unit_Price": 50, "Units_Consumed": 10.0},
    {"Timestamp": 1732704781, "Charger_ID": "EV-L001-1", "User_ID": "7178", "Transaction_Amount": 100, "Unit_Price": 50, "Units_Consumed": 2.0},
    {"Timestamp": 1732790734, "Charger_ID": "EV-L001-1", "User_ID": "7178", "Transaction_Amount": 250, "Unit_Price": 50, "Units_Consumed": 5.0},
    {"Timestamp": 1732948097, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 480, "Unit_Price": 50, "Units_Consumed": 9.6},
    {"Timestamp": 1733050317, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 60, "Unit_Price": 50, "Units_Consumed": 1.2},
    {"Timestamp": 1733105484, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 110, "Unit_Price": 50, "Units_Consumed": 2.2},
    {"Timestamp": 1733225455, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 490, "Unit_Price": 50, "Units_Consumed": 9.8},
    {"Timestamp": 1733316275, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 280, "Unit_Price": 50, "Units_Consumed": 5.6},
    {"Timestamp": 1733463474, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 270, "Unit_Price": 50, "Units_Consumed": 5.4},
    {"Timestamp": 1733565667, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 360, "Unit_Price": 50, "Units_Consumed": 7.2},
    {"Timestamp": 1733882718, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 240, "Unit_Price": 50, "Units_Consumed": 4.8},
    {"Timestamp": 1734094281, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 140, "Unit_Price": 50, "Units_Consumed": 2.8},
    {"Timestamp": 1734191919, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 280, "Unit_Price": 50, "Units_Consumed": 5.6},
    {"Timestamp": 1734594025, "Charger_ID": "EV-L001-1", "User_ID": "7178", "Transaction_Amount": 240, "Unit_Price": 50, "Units_Consumed": 4.8},
    {"Timestamp": 1734780591, "Charger_ID": "EV-L001-1", "User_ID": "7178", "Transaction_Amount": 320, "Unit_Price": 50, "Units_Consumed": 6.4},
    {"Timestamp": 1735030273, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 80, "Unit_Price": 50, "Units_Consumed": 1.6},
    {"Timestamp": 1735282149, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 90, "Unit_Price": 50, "Units_Consumed": 1.8},
    {"Timestamp": 1735522244, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 240, "Unit_Price": 50, "Units_Consumed": 4.8},
    {"Timestamp": 1735731709, "Charger_ID": "EV-L001-1", "User_ID": "7053", "Transaction_Amount": 230, "Unit_Price": 50, "Units_Consumed": 4.6},
    {"Timestamp": 1735787313, "Charger_ID": "EV-L001-1", "User_ID": "2925", "Transaction_Amount": 200, "Unit_Price": 50, "Units_Consumed": 4.0},
    {"Timestamp": 1736521830, "Charger_ID": "EV-L001-1", "User_ID": "8620", "Transaction_Amount": 300, "Unit_Price": 50, "Units_Consumed": 6.0},
]

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)

# Convert Timestamp to human-readable date
df['Date'] = pd.to_datetime(df['Timestamp'], unit='s')

# Sort by Date
df.sort_values(by='Date', inplace=True)

# Display the data in tabular format
print(df[['Date', 'Charger_ID', 'User_ID', 'Units_Consumed']])

# Plot the data
plt.figure(figsize=(12, 6))
plt.bar(df['Date'].dt.strftime('%b %d'), df['Units_Consumed'], color='skyblue')
plt.title('Units Consumed by Date', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Units Consumed (kWh)', fontsize=14)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

