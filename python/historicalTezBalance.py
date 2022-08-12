import os.path
from taxUtils import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "user_wallets.json"))

# Get the combined historical tez balance from all the user wallets
historical_balance = get_user_historical_balance(user_wallets)

# Save the data in a csv file
file_name = "historical_tez_balance_%s.csv" % list(user_wallets.keys())[0]
columns = ["timestamp", "level", "tez", "euros", "usd", "tez_to_euros",
           "tez_to_usd"]
format = ["%s", "%i", "%f", "%f", "%f", "%f", "%f"]

with open(os.path.join(data_directory, file_name), "w") as file:
    # Write the header
    file.write(",".join(columns) + "\n")

    # Loop over the historical tez balance
    for balance in historical_balance:
        # Write the balance data in the output file
        data = (
            balance["timestamp"],
            balance["level"],
            balance["balance"],
            balance["balance"] * balance["quote"]["eur"],
            balance["balance"] * balance["quote"]["usd"],
            balance["quote"]["eur"],
            balance["quote"]["usd"])
        text = ",".join(format) % data
        file.write(text + "\n")
