import csv
import os.path
from taxUtils import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "input", "user_wallets.json"))
user_first_wallet = list(user_wallets.keys())[0]

# Get the combined tez balance from all the user wallets
tez_balance = get_user_tez_balance(user_wallets)

# Save the data in a csv file
file_name = "tez_balance_%s.csv" % user_first_wallet
columns = [
    "timestamp", "level", "tez", "euros", "usd", "tez_to_euros", "tez_to_usd"]
format = ["%s", "%i", "%f", "%f", "%f", "%f", "%f"]

with open(os.path.join(data_directory, "output", file_name), "w", newline="\n") as output_file:
    writer = csv.writer(output_file)

    # Write the header
    writer.writerow(columns)

    # Loop over the tez balance
    for balance in tez_balance:
        # Write the balance data in the output file
        data = [
            balance["timestamp"],
            balance["level"],
            balance["balance"],
            balance["balance"] * balance["quote"]["eur"],
            balance["balance"] * balance["quote"]["usd"],
            balance["quote"]["eur"],
            balance["quote"]["usd"]]
        writer.writerow(data)

# Print some details
print("\n We discovered %i changes in the tez balance associated to the user wallets." % len(tez_balance))
print(" You can find the processed information in %s\n" % os.path.join(data_directory, "output", file_name))
