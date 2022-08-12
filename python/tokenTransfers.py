import os.path
from taxUtils import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "user_wallets.json"))

# Get the raw token transfers associated with the user
raw_token_transfers = get_user_token_transfers(user_wallets)

# Get the list of FA2 contracts associated to the objkt.com collections
objktcom_collections = get_objktcom_collections()

# Get the main tezos tokens and smart contract aliases
token_aliases = {address: name for name, address in TOKENS.items()}
smart_contract_aliases = {address: alias for alias, address in SMART_CONTRACTS.items()}

# Process the raw token transfers
token_transfers = []

for tt in raw_token_transfers:
    # Save the most relevant information
    token_transfer = {
        "timestamp": tt["timestamp"],
        "level": tt["level"],
        "from": tt["from"]["address"] if "from" in tt else None,
        "to": tt["to"]["address"],
        "internal": False,
        "mint": False,
        "send": False,
        "receive": False,
        "burn": False,
        "token_id": tt["token"]["tokenId"],
        "token_editions": int(tt["amount"]),
        "token_address": tt["token"]["contract"]["address"]}

    # Check if it's an internal transaction between the user wallets
    token_transfer["internal"] = (token_transfer["from"] in user_wallets) and (token_transfer["to"] in user_wallets)

    # Check if it's associated with a token mint
    token_transfer["mint"] = token_transfer["from"] is None

    # Check if the token was sent, received or burned
    token_transfer["send"] = (not token_transfer["internal"]) and (token_transfer["from"] in user_wallets)
    token_transfer["receive"] = (not token_transfer["internal"]) and (token_transfer["to"] in user_wallets)
    token_transfer["burn"] = token_transfer["to"] == "tz1burnburnburnburnburnburnburjAYjjX"

    # Add the processed token transfer
    token_transfers.append(token_transfer)

# Get all address aliases
aliases = {}
aliases.update(user_wallets)
aliases.update(token_aliases)
aliases.update(smart_contract_aliases)
aliases.update({"tz1burnburnburnburnburnburnburjAYjjX": "Burn address"})

# Save the processed data in a csv file
file_name = "token_transfers_%s.csv" % list(user_wallets.keys())[0]
columns = [
    "timestamp", "level", "from", "to", "internal", "mint", "send", "receive",
    "burn", "token_name", "token_id", "token_editions", "token_address"]
format = [
    "%s", "%i", "%s", "%s", "%r", "%r", "%r", "%r", "%r", "%s", "%s", "%s",
    "%s"]

with open(os.path.join(data_directory, file_name), "w") as file:
    # Write the header
    file.write(",".join(columns) + "\n")

    # Loop over the token transfers
    for tt in token_transfers:
        # Write the token transfer data in the output file
        data = (
            tt["timestamp"],
            tt["level"],
            aliases.get(tt["from"], tt["from"]) if tt["from"] is not None else "",
            aliases.get(tt["to"], tt["to"]),
            tt["internal"],
            tt["mint"],
            tt["send"],
            tt["receive"],
            tt["burn"],
            token_aliases[tt["token_address"]] if tt["token_address"] in token_aliases else ("objkt.com collection" if tt["token_address"] in objktcom_collections else ""),
            tt["token_id"] if tt["token_id"] is not None else "",
            tt["token_editions"] if tt["token_editions"] is not None else "",
            tt["token_address"] if tt["token_address"] is not None else "")
        text = ",".join(format) % data
        file.write(text + "\n")
