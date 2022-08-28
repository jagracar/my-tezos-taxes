import os.path
import pandas as pd
from taxUtils import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "input", "user_wallets.json"))
user_first_wallet = list(user_wallets.keys())[0]

# Load the csv file containing all the user operations
file_name = "operations_%s.csv" % user_first_wallet
operations = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

# Load the csv file containing all the user token transfers
file_name = "token_transfers_%s.csv" % user_first_wallet
token_transfers = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

# Change the token editions column type to str
token_transfers["token_id"] = token_transfers["token_id"].astype(str)
token_transfers["token_editions"] = token_transfers["token_editions"].astype(str)

# Add a column to indicate which transfers have been used during the next steps
token_transfers["used"] = False

# Don't use internal token transfers
token_transfers.loc[token_transfers["internal"], "used"] = True

# Get the information about the minted, collected, dropped, sold and transferred tokens
minted_tokens = get_minted_tokens(operations, token_transfers)
collected_tokens = get_collected_tokens(operations, token_transfers)
dropped_tokens = get_dropped_tokens(operations, token_transfers, collected_tokens)
sold_tokens = get_sold_tokens(operations, token_transfers)
transferred_tokens = get_transferred_tokens(operations, token_transfers)

# Save the data frames as csv files
minted_tokens_file_name = "minted_tokens_%s.csv" % user_first_wallet
minted_tokens.to_csv(os.path.join(data_directory, "output", minted_tokens_file_name), index=False)
collected_tokens_file_name = "collected_tokens_%s.csv" % user_first_wallet
collected_tokens.to_csv(os.path.join(data_directory, "output", collected_tokens_file_name), index=False)
dropped_tokens_file_name = "dropped_tokens_%s.csv" % user_first_wallet
dropped_tokens.to_csv(os.path.join(data_directory, "output", dropped_tokens_file_name), index=False)
sold_tokens_file_name = "sold_tokens_%s.csv" % user_first_wallet
sold_tokens.to_csv(os.path.join(data_directory, "output", sold_tokens_file_name), index=False)
transferred_tokens_file_name = "transferred_tokens_%s.csv" % user_first_wallet
transferred_tokens.to_csv(os.path.join(data_directory, "output", transferred_tokens_file_name), index=False)

# Print some details
print("\n NFT operations associated to the user wallets:\n")

if minted_tokens.size > 0:
    print("  - Minted %i tokens." % (minted_tokens["token_id"] + minted_tokens["token_address"]).unique().size)
    print("    See %s for more details.\n" % os.path.join(data_directory, "output", minted_tokens_file_name))

if collected_tokens.size > 0:
    print("  - Collected %i tokens from other artists." % (collected_tokens["token_id"] + collected_tokens["token_address"]).unique().size)
    print("    See %s for more details.\n" % os.path.join(data_directory, "output", collected_tokens_file_name))

if dropped_tokens.size > 0:
    print("  - Received %i tokens as free drops." % (dropped_tokens["token_id"] + dropped_tokens["token_address"]).unique().size)
    print("    See %s for more details.\n" % os.path.join(data_directory, "output", dropped_tokens_file_name))

if sold_tokens.size > 0:
    print("  - Sold %i tokens collected from other artists." % (sold_tokens["token_id"] + sold_tokens["token_address"]).unique().size)
    print("    See %s for more details.\n" % os.path.join(data_directory, "output", sold_tokens_file_name))

if transferred_tokens.size > 0:
    print("  - Burned or transferred to other users %i tokens." % (transferred_tokens["token_id"] + transferred_tokens["token_address"]).unique().size)
    print("    See %s for more details.\n" % os.path.join(data_directory, "output", transferred_tokens_file_name))
