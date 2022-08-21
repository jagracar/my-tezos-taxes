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

# Get the information about the minted, collected and sold tokens
minted_tokens = get_minted_tokens(operations, token_transfers)
collected_tokens = get_collected_tokens(operations, token_transfers)
sold_tokens = get_sold_tokens(operations, token_transfers)

# Get the token trades information
token_trades = get_token_trades(sold_tokens, collected_tokens, token_transfers)

# Save the data frames as csv files
minted_tokens_file_name = "minted_tokens_%s.csv" % user_first_wallet
minted_tokens.to_csv(os.path.join(data_directory, "output", minted_tokens_file_name), index=False)
collected_tokens_file_name = "collected_tokens_%s.csv" % user_first_wallet
collected_tokens.to_csv(os.path.join(data_directory, "output", collected_tokens_file_name), index=False)
sold_tokens_file_name = "sold_tokens_%s.csv" % user_first_wallet
sold_tokens.to_csv(os.path.join(data_directory, "output", sold_tokens_file_name), index=False)
token_trades_file_name = "token_trades_%s.csv" % user_first_wallet
token_trades.to_csv(os.path.join(data_directory, "output", token_trades_file_name), index=False)

# Print some details
print("\n NFT operations associated to the user wallets:\n")
print("  - Minted %i tokens." % (minted_tokens["token_id"] + minted_tokens["token_address"]).unique().size)
print("    See %s for more details.\n" % os.path.join(data_directory, "output", minted_tokens_file_name))
print("  - Collected %i tokens from other artists." % (collected_tokens["token_id"] + collected_tokens["token_address"]).unique().size)
print("    See %s for more details.\n" % os.path.join(data_directory, "output", collected_tokens_file_name))
print("  - Sold %i tokens collected from other artists." % (sold_tokens["token_id"] + sold_tokens["token_address"]).unique().size)
print("    See %s for more details." % os.path.join(data_directory, "output", sold_tokens_file_name))
print("    The token trade information is stored in %s\n" % os.path.join(data_directory, "output", token_trades_file_name))
