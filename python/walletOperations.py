import csv
import os.path
from taxUtils import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "input", "user_wallets.json"))
user_first_wallet = list(user_wallets.keys())[0]

# Load the user baker wallets
baker_wallets = read_json_file(os.path.join(data_directory, "input", "baker_wallets.json"))

# Load the exchange wallets
exchange_wallets = read_json_file(os.path.join(data_directory, "input", "exchange_wallets.json"))

# Load the general wallets
general_wallets = read_json_file(os.path.join(data_directory, "input", "general_wallets.json"))

# Load the burn wallets
burn_wallets = read_json_file(os.path.join(data_directory, "input", "burn_wallets.json"))

# Load the csv file containing all the user token transfers
file_name = "token_transfers_%s.csv" % user_first_wallet
token_transfers = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

# Get the user raw information
raw_transactions = get_user_transactions(user_wallets)
raw_originations = get_user_originations(user_wallets)
raw_reveals = get_user_reveals(user_wallets)
raw_delegations = get_user_delegations(user_wallets)
raw_bakings = get_user_bakings(user_wallets)
raw_endorsing_rewards = get_user_endorsing_rewards(user_wallets)
raw_staking_rewards = get_user_staking_rewards(os.path.join(data_directory, "input", "staking_rewards.csv"))

# Get the user mints, swaps, collects, auction bids, art sales and collection sales
user_mints = get_user_mints(user_wallets)
user_swaps = get_user_swaps(user_wallets)
user_collects = get_user_collects(user_wallets)
user_auction_bids = get_user_auction_bids(user_wallets)
user_art_sales = get_user_art_sales(user_wallets)
user_collection_sales = get_user_collection_sales(user_wallets)

# Get the list of FA2 contracts associated to the objkt.com collections
objktcom_collections = get_objktcom_collections()

# Get the list of FA2 contracts associated to the objkt.com open editions
objktcom_open_editions = get_objktcom_open_editions()

# Get the list of FA2 contracts associated to the editart.xyz collections
editart_collections = get_editart_collections()

# Get the list of FA1.2 and FA2 tokens
fa12_tokens = get_fa12_tokens()
fa2_tokens = get_fa2_tokens()

# Get the 3Route tokens
three_route_tokens = {
    SMART_CONTRACTS["3Route v1"] : get_three_route_tokens(1),
    SMART_CONTRACTS["3Route v2"] : get_three_route_tokens(2),
    SMART_CONTRACTS["3Route v3"] : get_three_route_tokens(3),
    SMART_CONTRACTS["3Route v4"] : get_three_route_tokens(4)
}

# Get the main tezos tokens and smart contract aliases
token_aliases = {address: name for name, address in TOKENS.items()}
smart_contract_aliases = {address: alias for alias, address in SMART_CONTRACTS.items()}

# Process the raw transactions
transactions = []
unprocessed_transactions = []
three_route_operations = {}

for t in raw_transactions:
    # Save the most relevant information
    transaction = {
        "timestamp": t["timestamp"],
        "level": t["level"],
        "kind": None,
        "entrypoint": t["parameter"]["entrypoint"] if "parameter" in t else None,
        "parameters": t["parameter"]["value"] if "parameter" in t else None,
        "initiator": t["initiator"]["address"] if "initiator" in t else None,
        "sender": t["sender"]["address"],
        "target": t["target"]["address"],
        "applied": t["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": False,
        "baking": False,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": t["sender"]["address"] in exchange_wallets,
        "sell_tez": t["target"]["address"] in exchange_wallets,
        "amount": t["amount"] / 1e6,
        "fees": ((t["bakerFee"] + t["storageFee"] + t["allocationFee"]) / 1e6) if (t["status"] == "applied") else (t["bakerFee"] / 1e6),
        "tez_to_euros": t["quote"]["eur"],
        "tez_to_usd": t["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": t["hash"],
        "comment": ""}

    # Check if it's an internal transaction between the user wallets
    transaction["internal"] = (transaction["sender"] in user_wallets) and (transaction["target"] in user_wallets)

    # Ignore internal transactions for the tax calculations
    transaction["ignore"] = transaction["internal"]

    # Add the information from the known user transactions
    hash = t["hash"]

    if hash in user_mints:
        mint = user_mints[hash]
        transaction["mint"] = True
        transaction["token_id"] = mint["token_id"]
        transaction["token_editions"] = mint["editions"]
        transaction["token_address"] = mint["fa2_address"]

    if hash in user_swaps:
        swap = user_swaps[hash]

        if swap["amount"] is not None:
            token_editions = swap["amount"]
        elif swap["editions"] is not None:
            token_editions = swap["editions"]
        elif swap["type"] == "FX_LISTING":
            token_editions = 1
        else:
            token_editions = None

        transaction["token_id"] = swap["token_id"]
        transaction["token_editions"] = token_editions
        transaction["token_address"] = swap["fa2_address"]

    if hash in user_collects:
        collect = user_collects[hash]

        if collect["amount"] is not None:
            token_editions = collect["amount"]
        elif collect["editions"] is not None:
            token_editions = collect["editions"]
        else:
            token_editions = 1

        transaction["collect"] = (collect["implements"] == "SALE") or (collect["fulfilled_offer"] == True)
        transaction["active_offer"] = collect["active_offer"] == True
        transaction["token_id"] = collect["token_id"]
        transaction["token_editions"] = token_editions
        transaction["token_address"] = collect["fa2_address"]

        # Ignore transactions associated to offers that were not fulfilled and
        # are not active
        if collect["offer_id"] is not None or collect["bid_id"] is not None:
            if (not transaction["collect"]) and (not transaction["active_offer"]):
                transaction["ignore"] = True

    if hash in user_auction_bids:
        bid = user_auction_bids[hash]
        transaction["collect"] = bid["won_auction"]
        transaction["token_id"] = bid["token_id"]
        transaction["token_editions"] = 1
        transaction["token_address"] = bid["fa2_address"]

        # Ignore transactions associated to auction bids that were not won
        transaction["ignore"] = not transaction["collect"]

    if hash in user_art_sales:
        sale = user_art_sales[hash]
        transaction["art_sale"] = True
        transaction["primary_art_sale"] = sale["seller_address"] in user_wallets
        transaction["secondary_art_sale"] = sale["seller_address"] not in user_wallets
        transaction["token_id"] = sale["token_id"]
        transaction["token_editions"] = sale["amount"] if sale["amount"] is not None else 1
        transaction["token_address"] = sale["fa2_address"]

    if hash in user_collection_sales:
        sale = user_collection_sales[hash]
        transaction["collection_sale"] = True
        transaction["token_id"] = sale["token_id"]
        transaction["token_editions"] = sale["amount"] if sale["amount"] is not None else 1
        transaction["token_address"] = sale["fa2_address"]

    # Check if it is a simple tez transaction
    if transaction["entrypoint"] is None and transaction["amount"] > 0:
        if transaction["internal"]:
            transaction["kind"] = "internal tez transfer"
        elif transaction["sender"] in user_wallets:
            transaction["kind"] = "send tez"
        elif transaction["target"] in user_wallets:
            if transaction["sender"] in baker_wallets:
                transaction["kind"] = "receive tez from staking"
                transaction["staking"] = True
            else:
                transaction["kind"] = "receive tez"
        else:
            transaction["kind"] = "secondary tez transfer"

    # Check if the transaction is connected with a mint
    if transaction["entrypoint"] == "mint_OBJKT":
        if transaction["target"] == SMART_CONTRACTS["h=n marketplace v1"]:
            transaction["kind"] = "h=n mint"
            transaction["token_address"] = TOKENS["OBJKT"]
    elif transaction["entrypoint"] == "create_artist_collection":
        if transaction["target"] == SMART_CONTRACTS["objkt.com Minting Factory"]:
            transaction["kind"] = "create objkt.com collection"
    elif transaction["entrypoint"] == "mint_artist":
        if transaction["target"] == SMART_CONTRACTS["objkt.com Minting Factory"]:
            transaction["kind"] = "objkt.com collection mint"
    elif transaction["entrypoint"] == "mint_TYPED":
        if transaction["target"] == SMART_CONTRACTS["typed minter"]:
            transaction["kind"] = "typed mint"
    elif transaction["entrypoint"] == "mint_haiku":
        if transaction["target"] == TOKENS["8scribo token"]:
            transaction["kind"] = "8scribo mint"
    elif transaction["entrypoint"] == "mint_token":
        if transaction["target"] == SMART_CONTRACTS["contter marketplace II"]:
            transaction["kind"] = "contter mint"
            transaction["mint"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = TOKENS["contter token"]
    elif transaction["entrypoint"] == "default":
        if transaction["target"] == SMART_CONTRACTS["25FPS minter"]:
            transaction["kind"] = "25FPS mint"
            transaction["collect"] = True
            transaction["token_address"] = TOKENS["25FPS token"]
    elif transaction["entrypoint"] == "mint":
        if transaction["target"] == TOKENS["OBJKT"]:
            transaction["kind"] = "h=n mint"
            transaction["token_address"] = TOKENS["OBJKT"]
        elif transaction["target"] in objktcom_collections:
            transaction["kind"] = "objkt.com collection mint"
        elif transaction["target"] in objktcom_open_editions:
            transaction["kind"] = "objkt.com open edition mint"
        elif transaction["target"] == TOKENS["ITEM"]:
            transaction["kind"] = "versum mint"
        elif transaction["target"] in [TOKENS["8bidou 8x8 token"], TOKENS["8bidou 24x24 token"]]:
            transaction["kind"] = "8bidou mint"
        elif transaction["target"] == TOKENS["typed token"]:
            transaction["kind"] = "typed mint"
        elif transaction["target"] == TOKENS["Rarible token"]:
            transaction["kind"] = "rarible mint"
            transaction["mint"] = True
            transaction["token_id"] = transaction["parameters"]["itokenid"]
            transaction["token_editions"] = int(transaction["parameters"]["iamount"])
            transaction["token_address"] = TOKENS["Rarible token"]
        elif transaction["target"] == TOKENS["contter token"]:
            transaction["kind"] = "contter mint"
            transaction["mint"] = True
            transaction["token_address"] = TOKENS["contter token"]
        elif transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "FXHASH mint"
            transaction["mint"] = False
            transaction["collect"] = True
        elif transaction["target"] == SMART_CONTRACTS["FXHASH fx(text) minter v1"]:
            transaction["kind"] = "create FXHASH fx(text) article"
            transaction["mint"] = True
            transaction["collect"] = False
        elif transaction["target"] in [TOKENS["GENTK v1"], TOKENS["GENTK v2"], TOKENS["GENTK v3"]]:
            transaction["kind"] = "FXHASH mint"
            transaction["mint"] = False
            transaction["collect"] = True
        elif transaction["target"] == TOKENS["FXHASH ticket"]:
            transaction["kind"] = "FXHASH ticket mint"
            transaction["mint"] = False
            transaction["collect"] = True
            transaction["token_address"] = TOKENS["FXHASH ticket"]
        elif transaction["target"] == SMART_CONTRACTS["Tezzardz minter"]:
            transaction["kind"] = "Tezzardz mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["Tezzardz"]
        elif transaction["target"] == TOKENS["Tezzardz"]:
            transaction["kind"] = "Tezzardz mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["Tezzardz"]
        elif transaction["target"] == SMART_CONTRACTS["GOGOs minter"]:
            transaction["kind"] = "GOGOs mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["GOGOs"]
        elif transaction["target"] == TOKENS["GOGOs"]:
            transaction["kind"] = "GOGOs mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["GOGOs"]
        elif transaction["target"] == SMART_CONTRACTS["NEONZ minter"]:
            transaction["kind"] = "NEONZ mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["NEONZ"]
        elif transaction["target"] == TOKENS["NEONZ"]:
            transaction["kind"] = "NEONZ mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["NEONZ"]
        elif transaction["target"] == SMART_CONTRACTS["Ziggurats minter"]:
            transaction["kind"] = "Ziggurats mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["Ziggurats"]
        elif transaction["target"] == TOKENS["Ziggurats"]:
            transaction["kind"] = "Ziggurats mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["Ziggurats"]
        elif transaction["target"] == TOKENS["Hash Three Points token"]:
            transaction["kind"] = "Hash Three Points mint"
            transaction["collect"] = True
            transaction["token_editions"] = 1
            transaction["token_address"] = TOKENS["Hash Three Points token"]
        elif transaction["target"] == SMART_CONTRACTS["VesselsGen0 minter"]:
            transaction["kind"] = "VesselsGen0 mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["VesselsGen0"]
        elif transaction["target"] == TOKENS["VesselsGen0"]:
            transaction["kind"] = "VesselsGen0 mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["VesselsGen0"]
    elif transaction["entrypoint"] == "mint_issuer":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "create FXHASH collection"
    elif transaction["entrypoint"] == "burn":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "burn FXHASH collection"
    elif transaction["entrypoint"] == "mint_with_ticket":
        transaction["kind"] = "FXHASH mint with ticket"
        transaction["mint"] = False
        transaction["collect"] = True
    elif transaction["entrypoint"] == "hDAO_batch":
        transaction["kind"] = "hDAO mint"
        transaction["collect"] = True
        transaction["token_id"] = "0"
        transaction["token_address"] = TOKENS["hDAO"]

        for receiver in transaction["parameters"]:
            if receiver["to_"] in user_wallets:
                transaction["token_editions"] = int(receiver["amount"])
    elif transaction["entrypoint"] == "claim_materia":
        transaction["kind"] = "Materia mint"
        transaction["collect"] = True
        transaction["token_id"] = "0"
        transaction["token_address"] = TOKENS["Materia"]
    elif transaction["entrypoint"] == "buy":
        if transaction["target"] == SMART_CONTRACTS["Skeles minter"]:
            transaction["kind"] = "Skeles mint"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"])
            transaction["token_address"] = TOKENS["Skeles"]
        elif transaction["target"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar Buy"]:
            transaction["kind"] = "tezos domain mint"
            transaction["collect"] = True
            transaction["token_editions"] = "1"
            transaction["token_address"] = TOKENS["Tezos domain token"]
    elif transaction["entrypoint"] == "execute":
        if transaction["sender"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar"]:
            # if transaction["parameters"]["action_name"] == "SetChildRecord":
            transaction["kind"] = "tezos domain mint"
            transaction["collect"] = True
            transaction["token_editions"] = "1"
            transaction["token_address"] = TOKENS["Tezos domain token"]

    # Check if the transaction is connected with a token transfer
    if transaction["entrypoint"] == "transfer":
        if transaction["target"] in token_aliases:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                from_key = "from_" if "from_" in tt else "address"
                txs_key = "txs" if "txs" in tt else "list"
                to_key = "to_" if "to_" in tt[txs_key][0] else "to"

                if tt[from_key] in user_wallets:
                    transaction["kind"] = "send " + token_aliases[transaction["target"]]
                    transaction["token_id"] = tt[txs_key][0]["token_id"]
                    transaction["token_editions"] = int(tt[txs_key][0]["amount"])

                    for ttt in tt[txs_key]:
                        if ttt[to_key] in burn_wallets:
                            transaction["kind"] = "burn " + token_aliases[transaction["target"]]
                else:
                    for ttt in tt[txs_key]:
                        if ttt[to_key] in user_wallets:
                            transaction["kind"] = "receive " + token_aliases[transaction["target"]]
                            transaction["token_id"] = ttt["token_id"]
                            transaction["token_editions"] = int(ttt["amount"])

            if (transaction["kind"] is None) and (transaction["initiator"] in user_wallets):
                transaction["kind"] = "send " + token_aliases[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0][txs_key][0]["token_id"]
                transaction["token_editions"] = int(transaction["parameters"][0][txs_key][0]["amount"])
        elif transaction["target"] in objktcom_collections:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                if tt["from_"] in user_wallets:
                    transaction["kind"] = "send objkt.com collection token"
                    transaction["token_id"] = tt["txs"][0]["token_id"]
                    transaction["token_editions"] = int(tt["txs"][0]["amount"])

                    for ttt in tt["txs"]:
                        if ttt["to_"] in burn_wallets:
                            transaction["kind"] = "burn objkt.com collection token"
                else:
                    for ttt in tt["txs"]:
                        if ttt["to_"] in user_wallets:
                            transaction["kind"] = "receive objkt.com collection token"
                            transaction["token_id"] = ttt["token_id"]
                            transaction["token_editions"] = int(ttt["amount"])

            if (transaction["kind"] is None) and (transaction["initiator"] in user_wallets):
                transaction["kind"] = "send objkt.com collection token"
                transaction["token_id"] = transaction["parameters"][0]["txs"][0]["token_id"]
                transaction["token_editions"] = int(transaction["parameters"][0]["txs"][0]["amount"])
        elif transaction["target"] in objktcom_open_editions:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                if tt["from_"] in user_wallets:
                    transaction["kind"] = "send objkt.com open edition token"
                    transaction["token_id"] = tt["txs"][0]["token_id"]
                    transaction["token_editions"] = int(tt["txs"][0]["amount"])

                    for ttt in tt["txs"]:
                        if ttt["to_"] in burn_wallets:
                            transaction["kind"] = "burn objkt.com open edition token"
                else:
                    for ttt in tt["txs"]:
                        if ttt["to_"] in user_wallets:
                            transaction["kind"] = "receive objkt.com open edition token"
                            transaction["token_id"] = ttt["token_id"]
                            transaction["token_editions"] = int(ttt["amount"])

            if (transaction["kind"] is None) and (transaction["initiator"] in user_wallets):
                transaction["kind"] = "send objkt.com open edition token"
                transaction["token_id"] = transaction["parameters"][0]["txs"][0]["token_id"]
                transaction["token_editions"] = int(transaction["parameters"][0]["txs"][0]["amount"])
        elif transaction["target"] in editart_collections:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                if tt["from_"] in user_wallets:
                    transaction["kind"] = "send editart.xyz collection token"
                    transaction["token_id"] = tt["txs"][0]["token_id"]
                    transaction["token_editions"] = int(tt["txs"][0]["amount"])

                    for ttt in tt["txs"]:
                        if ttt["to_"] in burn_wallets:
                            transaction["kind"] = "burn editart.xyz collection token"
                else:
                    for ttt in tt["txs"]:
                        if ttt["to_"] in user_wallets:
                            transaction["kind"] = "receive editart.xyz collection token"
                            transaction["token_id"] = ttt["token_id"]
                            transaction["token_editions"] = int(ttt["amount"])

            if (transaction["kind"] is None) and (transaction["initiator"] in user_wallets):
                transaction["kind"] = "send editart.xyz collection token"
                transaction["token_id"] = transaction["parameters"][0]["txs"][0]["token_id"]
                transaction["token_editions"] = int(transaction["parameters"][0]["txs"][0]["amount"])
        elif transaction["target"] in fa2_tokens:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                if tt["from_"] in user_wallets:
                    transaction["kind"] = "send " + fa2_tokens[transaction["target"]]
                    transaction["token_id"] = tt["txs"][0]["token_id"]
                    transaction["token_editions"] = int(tt["txs"][0]["amount"])

                    for ttt in tt["txs"]:
                        if ttt["to_"] in burn_wallets:
                            transaction["kind"] = "burn " + fa2_tokens[transaction["target"]]
                else:
                    for ttt in tt["txs"]:
                        if ttt["to_"] in user_wallets:
                            transaction["kind"] = "receive " + fa2_tokens[transaction["target"]]
                            transaction["token_id"] = ttt["token_id"]
                            transaction["token_editions"] = int(ttt["amount"])

            if (transaction["kind"] is None) and (transaction["initiator"] in user_wallets):
                transaction["kind"] = "send " + fa2_tokens[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0][txs_key][0]["token_id"]
                transaction["token_editions"] = int(transaction["parameters"][0][txs_key][0]["amount"])
        elif transaction["target"] in fa12_tokens:
            transaction["token_id"] = "0"
            transaction["token_editions"] = int(transaction["parameters"]["value"])
            transaction["token_address"] = transaction["target"]

            if transaction["parameters"]["from"] in user_wallets:
                transaction["kind"] = "send " + fa12_tokens[transaction["target"]]

                if transaction["parameters"]["to"] in burn_wallets:
                    transaction["kind"] = "burn " + fa12_tokens[transaction["target"]]
            else:
                transaction["kind"] = "receive " + fa12_tokens[transaction["target"]]
    elif transaction["entrypoint"] == "burn":
        if transaction["target"] == TOKENS["typed token"]:
            transaction["kind"] = "burn " + token_aliases[transaction["target"]]
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = transaction["target"]
        elif transaction["target"] == TOKENS["Rarible token"]:
            transaction["kind"] = "burn " + token_aliases[transaction["target"]]
            transaction["token_id"] = transaction["parameters"]["itokenid"]
            transaction["token_editions"] = int(transaction["parameters"]["iamount"])
            transaction["token_address"] = transaction["target"]

    # Check if the transaction is connected with a token update operator
    if transaction["entrypoint"] == "update_operators":
        if transaction["target"] in token_aliases:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add %s operators" % token_aliases[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove %s operators" % token_aliases[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
        elif transaction["target"] in objktcom_collections:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add objkt.com collection operators"
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove objkt.com collection operators"
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
        elif transaction["target"] in objktcom_open_editions:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add objkt.com open edition operators"
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove objkt.com open edition operators"
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
        elif transaction["target"] in editart_collections:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add editart.xyz collection operators"
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove editart.xyz collection operators"
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
        elif transaction["target"] in fa2_tokens:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add %s operators" % fa2_tokens[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove %s operators" % fa2_tokens[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
    elif transaction["entrypoint"] == "approve":
        if transaction["target"] in fa12_tokens:
            transaction["token_id"] = "0"
            transaction["token_editions"] = int(transaction["parameters"]["value"])
            transaction["token_address"] = transaction["target"]

            if transaction["token_editions"] > 0:
                transaction["kind"] = "add %s operators" % fa12_tokens[transaction["target"]]
            else:
                transaction["kind"] = "remove %s operators" % fa12_tokens[transaction["target"]]
    elif transaction["entrypoint"] == "update_operators_for_all":
        if transaction["target"] in TOKENS["Rarible token"]:
            transaction["kind"] = "update %s operators" % token_aliases[transaction["target"]]
    elif transaction["entrypoint"] == "add_adhoc_operators":
        if transaction["target"] in token_aliases:
            transaction["kind"] = "update %s adhoc operators" % token_aliases[transaction["target"]]
            transaction["token_id"] = transaction["parameters"][0]["token_id"]
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

    # Check if the transaction is connected with a token balance of operation
    if transaction["entrypoint"] in ["balance_of", "getBalance"]:
        if transaction["target"] in token_aliases:
            transaction["kind"] = "check %s balance" % token_aliases[transaction["target"]]

    # Check if the transaction is connected with hDAO curation in h=n
    if transaction["entrypoint"] == "curate":
        if transaction["target"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n OBJKT-hDAO curation"]]:
            transaction["kind"] = "curate OBJKT using hDAO"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_editions"] = None
            transaction["token_address"] = TOKENS["OBJKT"]
    elif transaction["entrypoint"] == "claim_hDAO":
        if transaction["target"] == SMART_CONTRACTS["h=n OBJKT-hDAO curation"]:
            transaction["kind"] = "claim hDAO from curation"
            transaction["token_id"] = "0"
            transaction["token_editions"] = int(transaction["parameters"]["hDAO_amount"])
            transaction["token_address"] = TOKENS["hDAO"]

    # Check if the transaction is connected with swaps
    if transaction["entrypoint"] == "swap":
        if transaction["target"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n swap"
            transaction["token_address"] = TOKENS["OBJKT"]
        elif transaction["target"] == SMART_CONTRACTS["teia marketplace"]:
            transaction["kind"] = "teia swap"
        elif transaction["target"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_editions"] = int(transaction["parameters"]["objkt_amount"])
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] in [SMART_CONTRACTS["8bidou marketplace I"], SMART_CONTRACTS["8bidou marketplace II"]]:
            transaction["kind"] = "8bidou swap"
        elif transaction["target"] == SMART_CONTRACTS["typed marketplace"]:
            transaction["kind"] = "typed swap"
        elif transaction["target"] == SMART_CONTRACTS["8scribo marketplace"]:
            transaction["kind"] = "8scribo swap"
        elif transaction["target"] == SMART_CONTRACTS["akaMetaverse marketplace v1"]:
            transaction["kind"] = "akaSwap swap"
            transaction["token_id"] = transaction["parameters"]["akaOBJ_id"]
            transaction["token_editions"] = int(transaction["parameters"]["akaOBJ_amount"])
            transaction["token_address"] = TOKENS["akaSwap token"]
        elif transaction["target"] in [SMART_CONTRACTS["akaMetaverse marketplace v2"], SMART_CONTRACTS["akaMetaverse marketplace v2.1"]]:
            transaction["kind"] = "akaSwap swap"
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["token_amount"])
            transaction["token_address"] = transaction["parameters"]["token_fa2"]
    elif transaction["entrypoint"] == "cancel_swap":
        if transaction["target"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n cancel swap"
            transaction["token_address"] = TOKENS["OBJKT"]
        elif transaction["target"] == SMART_CONTRACTS["teia marketplace"]:
            transaction["kind"] = "teia cancel swap"
        elif transaction["target"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype cancel swap"
        elif transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum cancel swap"
        elif transaction["target"] == SMART_CONTRACTS["typed marketplace"]:
            transaction["kind"] = "typed cancel swap"
        elif transaction["target"] == SMART_CONTRACTS["8scribo marketplace"]:
            transaction["kind"] = "8scribo cancel swap"
        elif transaction["target"] in [SMART_CONTRACTS["akaMetaverse marketplace v1"], SMART_CONTRACTS["akaMetaverse marketplace v2"], SMART_CONTRACTS["akaMetaverse marketplace v2.1"]]:
            transaction["kind"] = "akaSwap cancel swap"
    elif transaction["entrypoint"] == "cancelswap":
        if transaction["target"] in [SMART_CONTRACTS["8bidou marketplace I"], SMART_CONTRACTS["8bidou marketplace II"]]:
            transaction["kind"] = "8bidou cancel swap"
    elif transaction["entrypoint"] == "ask":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com swap"
    elif transaction["entrypoint"] == "retract_ask":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com cancel swap"
    elif transaction["entrypoint"] == "listing":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH swap"
    elif transaction["entrypoint"] == "offer":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH swap"
    elif transaction["entrypoint"] == "listing_cancel":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH cancel swap"
    elif transaction["entrypoint"] == "cancel_offer":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH cancel swap"
    elif transaction["entrypoint"] == "create_swap":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum swap"
    elif transaction["entrypoint"] == "place_offer":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains marketplace offers"]:
            transaction["kind"] = "tezos domains swap"
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["parameters"]["token_contract"]
    elif transaction["entrypoint"] == "remove_offer":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains marketplace offers"]:
            transaction["kind"] = "tezos domains cancel swap"
    elif transaction["entrypoint"] == "list_token":
        if transaction["target"] == SMART_CONTRACTS["EmProps marketplace"]:
            transaction["kind"] = "EmProps swap"
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
    elif transaction["entrypoint"] == "unlist_token":
        if transaction["target"] == SMART_CONTRACTS["EmProps marketplace"]:
            transaction["kind"] = "EmProps cancel swap"
            transaction["token_editions"] = 1

    # Check if the transaction is connected with bids or offers
    if transaction["entrypoint"] == "bid":
        if transaction["target"] in [SMART_CONTRACTS["objkt.bid Legacy"], SMART_CONTRACTS["objkt.com marketplace v1"]]:
            transaction["kind"] = "objkt.com offer"
        elif transaction["target"] in [SMART_CONTRACTS["objkt.com English Auctions Old"], SMART_CONTRACTS["objkt.com English Auctions v1"], SMART_CONTRACTS["objkt.com English Auctions v2"]]:
            transaction["kind"] = "objkt.com bid in English auction"
        elif transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum bid in auction"
        elif transaction["target"] == SMART_CONTRACTS["Tezos Domains marketplace bids"]:
            transaction["kind"] = "tezos domains offer"
    elif transaction["entrypoint"] == "retract_bid":
        if transaction["target"] in [SMART_CONTRACTS["objkt.bid Legacy"], SMART_CONTRACTS["objkt.com marketplace v1"]]:
            transaction["kind"] = "objkt.com cancel offer"
    elif transaction["entrypoint"] == "swap":
        if transaction["target"] == SMART_CONTRACTS["objkt.bid Legacy"]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] == "fulfill_bid":
        if transaction["target"] == SMART_CONTRACTS["objkt.com marketplace v1"]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] == "offer":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com offer"
        elif transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH offer"
    elif transaction["entrypoint"] == "collection_offer":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH offer"
    elif transaction["entrypoint"] == "retract_offer":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com cancel offer"
    elif transaction["entrypoint"] == "offer_cancel":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH cancel offer"
    elif transaction["entrypoint"] == "collection_offer_cancel":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH cancel offer"
    elif transaction["entrypoint"] == "fulfill_offer":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] in ["offer_accept", "collection_offer_accept"]:
        if transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH accept offer"
    elif transaction["entrypoint"] == "make_offer":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum offer"
    elif transaction["entrypoint"] == "cancel_offer":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum cancel offer"
    elif transaction["entrypoint"] == "accept_offer":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum accept offer"
    elif transaction["entrypoint"] == "create_auction":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com English Auctions Old"], SMART_CONTRACTS["objkt.com English Auctions v1"]]:
            transaction["kind"] = "objkt.com create English auction"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] == SMART_CONTRACTS["objkt.com English Auctions v2"]:
            transaction["kind"] = "objkt.com create English auction"
            transaction["token_id"] = transaction["parameters"]["token"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["parameters"]["token"]["address"]
        elif transaction["target"] in [SMART_CONTRACTS["objkt.com Dutch Auctions Old"], SMART_CONTRACTS["objkt.com Dutch Auctions v1"]]:
            transaction["kind"] = "objkt.com create Dutch auction"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] == SMART_CONTRACTS["objkt.com Dutch Auctions v2"]:
            transaction["kind"] = "objkt.com create Dutch auction"
            transaction["token_id"] = transaction["parameters"]["token"]["token_id"]
            transaction["token_editions"] = int(transaction["parameters"]["editions"])
            transaction["token_address"] = transaction["parameters"]["token"]["address"]
        elif transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum create English auction"
            transaction["token_id"] = transaction["parameters"]["token"]["nat"]
            transaction["token_editions"] = int(transaction["parameters"]["token_amount"])
            transaction["token_address"] = transaction["parameters"]["token"]["address"]
    elif transaction["entrypoint"] == "cancel_auction":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com English Auctions Old"], SMART_CONTRACTS["objkt.com English Auctions v1"], SMART_CONTRACTS["objkt.com English Auctions v2"]]:
            transaction["kind"] = "objkt.com cancel English auction"
        elif transaction["target"] in [SMART_CONTRACTS["objkt.com Dutch Auctions Old"], SMART_CONTRACTS["objkt.com Dutch Auctions v1"], SMART_CONTRACTS["objkt.com Dutch Auctions v2"]]:
            transaction["kind"] = "objkt.com cancel Dutch auction"
    elif transaction["entrypoint"] == "conclude_auction":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com English Auctions Old"], SMART_CONTRACTS["objkt.com English Auctions v1"]]:
            transaction["kind"] = "objkt.com settle English auction"            
    elif transaction["entrypoint"] == "settle_auction":
        if transaction["target"] == SMART_CONTRACTS["objkt.com English Auctions v2"]:
            transaction["kind"] = "objkt.com settle English auction"            
    elif transaction["entrypoint"] == "withdraw":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum accept offer"
        elif transaction["target"] == SMART_CONTRACTS["Tezos Domains marketplace cancel bids"]:
            transaction["kind"] = "tezos domains cancel offer"

    # Check if the transaction is connected with collects
    if transaction["entrypoint"] == "collect":
        if transaction["target"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n collect"
            transaction["token_address"] = TOKENS["OBJKT"]
        elif transaction["target"] == SMART_CONTRACTS["teia marketplace"]:
            transaction["kind"] = "teia collect"
        elif transaction["target"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype collect prototype"
        elif transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH collect"
        elif transaction["target"] == SMART_CONTRACTS["typed marketplace"]:
            transaction["kind"] = "typed collect"
        elif transaction["target"] == SMART_CONTRACTS["8scribo marketplace"]:
            transaction["kind"] = "8scribo collect"
        elif transaction["target"] == SMART_CONTRACTS["akaMetaverse marketplace v1"]:
            transaction["kind"] = "akaSwap collect"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"]["akaOBJ_amount"])
            transaction["token_address"] = TOKENS["akaSwap token"]
        elif transaction["target"] in [SMART_CONTRACTS["akaMetaverse marketplace v2"], SMART_CONTRACTS["akaMetaverse marketplace v2.1"]]:
            transaction["kind"] = "akaSwap collect"
            transaction["collect"] = True
            transaction["token_editions"] = int(transaction["parameters"]["token_amount"])
        elif transaction["target"] == SMART_CONTRACTS["contter marketplace I"]:
            transaction["kind"] = "contter collect"
            transaction["collect"] = True
            transaction["token_address"] = TOKENS["contter token"]
        elif transaction["target"] == SMART_CONTRACTS["contter marketplace II"]:
            transaction["kind"] = "contter collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = TOKENS["contter token"]
    elif transaction["entrypoint"] == "fulfill_ask":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com collect"
    elif transaction["entrypoint"] == "claim":
        if transaction["target"] in objktcom_open_editions:
            transaction["kind"] = "objkt.com collect"
    elif transaction["entrypoint"] == "listing_accept":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"]]:
            transaction["kind"] = "FXHASH collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "claim":
        if transaction["target"] == TOKENS["FXHASH ticket"]:
            transaction["kind"] = "FXHASH ticket collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = TOKENS["FXHASH ticket"]
    elif transaction["entrypoint"] == "collect_swap":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum collect"
    elif transaction["entrypoint"] == "match_orders":
        if transaction["target"] == SMART_CONTRACTS["rarible marketplace v2"]:
            transaction["kind"] = "rarible collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "get_item":
        if transaction["target"] == SMART_CONTRACTS["tz1and world"]:
            transaction["kind"] = "tz1and collect"
            transaction["collect"] = True
            transaction["token_address"] = TOKENS["tz1and Item"]
    elif transaction["entrypoint"] == "bid":
        if transaction["target"] == SMART_CONTRACTS["tz1and auctions"]:
            transaction["kind"] = "tz1and collect"
            transaction["collect"] = True
            transaction["token_address"] = TOKENS["tz1and Place"]
    elif transaction["entrypoint"] == "buy":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com Dutch Auctions Old"], SMART_CONTRACTS["objkt.com Dutch Auctions v1"], SMART_CONTRACTS["objkt.com Dutch Auctions v2"]]:
            transaction["kind"] = "objkt.com collect in Dutch auction"
        elif transaction["target"] in [SMART_CONTRACTS["8bidou marketplace I"], SMART_CONTRACTS["8bidou marketplace II"]]:
            transaction["kind"] = "8bidou collect"
    elif transaction["entrypoint"] == "execute_offer":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains marketplace offers"]:
            transaction["kind"] = "tezos domains collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["parameters"]["token_contract"]
    elif transaction["entrypoint"] == "create_sale":
        if transaction["target"] == SMART_CONTRACTS["EmProps marketplace"]:
            transaction["kind"] = "EmProps collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
        if transaction["target"] == TOKENS["The Oracles token"]:
            transaction["kind"] = "EmProps collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["target"]
    elif transaction["entrypoint"] == "mint":
        if transaction["target"] in editart_collections:
            transaction["kind"] = "editart.xyz mint"
            transaction["mint"] = False
            transaction["collect"] = True
            transaction["token_editions"] = 1
            transaction["token_address"] = transaction["target"]
    elif transaction["entrypoint"] == "collect_from_machine":
        if transaction["target"] == SMART_CONTRACTS["NFT vending machine"]:
            transaction["kind"] = "NFT vending machine collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "createNFTCardForMember":
        if transaction["target"] == TOKENS["Tezos Community token"]:
            transaction["kind"] = "claim Tezos Community token"
            transaction["collect"] = True
            transaction["token_editions"] = 1
            transaction["token_address"] = TOKENS["Tezos Community token"]

    # Check if the transaction is connected with sells
    if (transaction["entrypoint"] is None) and (not transaction["internal"]) and (transaction["target"] in user_wallets):
        if transaction["sender"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n sell"
            transaction["token_address"] = TOKENS["OBJKT"]
        elif transaction["sender"] == SMART_CONTRACTS["teia marketplace"]:
            transaction["kind"] = "teia sell"
        elif transaction["sender"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype sell"
        elif transaction["sender"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"], SMART_CONTRACTS["objkt.com marketplace v3"]]:
            transaction["kind"] = "objkt.com sell"
        elif transaction["sender"] in [SMART_CONTRACTS["FXHASH marketplace v1"], SMART_CONTRACTS["FXHASH marketplace v2"], SMART_CONTRACTS["FXHASH marketplace v3"], SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "FXHASH sell"
        elif transaction["sender"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum sell"
        elif transaction["sender"] in [SMART_CONTRACTS["8bidou marketplace I"], SMART_CONTRACTS["8bidou marketplace II"]]:
            transaction["kind"] = "8bidou sell"
        elif transaction["sender"] == SMART_CONTRACTS["typed marketplace"]:
            transaction["kind"] = "typed sell"
        elif transaction["sender"] == SMART_CONTRACTS["8scribo marketplace"]:
            transaction["kind"] = "8scribo sell"
        elif transaction["sender"] == SMART_CONTRACTS["contter marketplace II"]:
            transaction["kind"] = "contter sell"
        elif transaction["sender"] in [SMART_CONTRACTS["Breadfond 1"], SMART_CONTRACTS["Breadfond 2"], SMART_CONTRACTS["Breadfond 3"], SMART_CONTRACTS["Breadfond 4"]]:
            transaction["kind"] = "Breadfond share in tez"
            transaction["art_sale"] = True
            transaction["secondary_art_sale"] = True

    # Check if the transaction is connected with the user registry information
    if transaction["entrypoint"] == "registry":
        if transaction["target"] == SMART_CONTRACTS["h=n name registry"]:
            transaction["kind"] = "update h=n registry"
    elif transaction["entrypoint"] == "update_profile":
        if transaction["target"] == SMART_CONTRACTS["FXHASH name registry"]:
            transaction["kind"] = "update FXHASH registry"
    elif transaction["entrypoint"] == "claim_verification":
        if transaction["target"] == SMART_CONTRACTS["versum registry"]:
            transaction["kind"] = "update versum registry"
    elif transaction["entrypoint"] == "update":
        if transaction["target"] == SMART_CONTRACTS["contter registry"]:
            transaction["kind"] = "update contter registry"
    elif transaction["entrypoint"] == "register":
        if transaction["target"] == SMART_CONTRACTS["typed registry"]:
            transaction["kind"] = "update typed registry"

    # Other kind of calls
    if transaction["entrypoint"] == "_charge_materia":
        if transaction["target"] == TOKENS["Materia"]:
            transaction["kind"] = "charge materia"
            transaction["token_id"] = "0"
            transaction["token_editions"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["Materia"]

    if transaction["entrypoint"] == "withdraw_outstanding_tez":
        if transaction["target"] == SMART_CONTRACTS["versum registry"]:
            transaction["kind"] = "withdraw outstanding tez from versum registry"

    if transaction["entrypoint"] in ["wrap", "unwrap", "approve", "getBalance"]:
        if transaction["target"] == SMART_CONTRACTS["wXTZ objkt.com"]:
            transaction["kind"] = "%s objkt.com wXTZ" % transaction["entrypoint"]

    if transaction["entrypoint"] == "update_fee_recipient":
        if transaction["target"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype update fee"
    elif transaction["entrypoint"] == "set_pause":
        if transaction["target"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype set pause"

    if transaction["target"] == SMART_CONTRACTS["Barter marketplace"]:
        transaction["kind"] = "Barter operation"

    if ((transaction["target"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains registrar"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains registrar"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar Commit"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar Commit"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains TLDRegistrar Buy"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains NameRegistry ClaimReverseRecord"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains NameRegistry ClaimReverseRecord"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains NameRegistry CheckAddress"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains NameRegistry CheckAddress"]) or
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains NameRegistry UpdateRecord"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains NameRegistry UpdateRecord"])):
        transaction["kind"] = "tezos domains operation"

    if transaction["entrypoint"] == "renew":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains registrar"]:
            transaction["kind"] = "tezos domain renovation"
            transaction["collect"] = True 
            transaction["token_editions"] = "1"
            transaction["token_address"] = TOKENS["Tezos domain token"]
    elif transaction["entrypoint"] == "balance_of":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains NameRegistry"]:
            transaction["kind"] = "tezos domains operation"

    if ((transaction["target"] == SMART_CONTRACTS["0x5E1F1E contract 1"]) or
        (transaction["target"] == SMART_CONTRACTS["0x5E1F1E contract 2"]) or
        (transaction["target"] == SMART_CONTRACTS["0x5E1F1E contract 3"])):
        transaction["kind"] = "0x5E1F1E operation"

    if transaction["entrypoint"] == "mint":
        if transaction["target"] == TOKENS["0x5E1F1E Mint Access Token"]:
            transaction["kind"] = "0x5E1F1E mint"
            transaction["mint"] = True
            transaction["token_editions"] = 1
            transaction["token_address"] = TOKENS["0x5E1F1E"]
    elif transaction["entrypoint"] == "request_access":
        if transaction["target"] == TOKENS["0x5E1F1E Mint Access Token"]:
            transaction["kind"] = "0x5E1F1E operation"
    elif transaction["entrypoint"] == "be_minted":
        if transaction["target"] == TOKENS["0x5E1F1E"]:
            transaction["kind"] = "0x5E1F1E operation"

    if transaction["entrypoint"] == "share_royalties":
        if transaction["target"] == SMART_CONTRACTS["EmProps Project Contract"]:
            transaction["kind"] = "EmProps operation"

    if ((transaction["target"] == SMART_CONTRACTS["teia multisig"]) or
        (transaction["sender"] == SMART_CONTRACTS["teia multisig"]) or
        ((transaction["target"] == SMART_CONTRACTS["teia core team multisig"]) and (transaction["entrypoint"] is not None)) or
        (transaction["sender"] == SMART_CONTRACTS["teia core team multisig"]) or
        (transaction["target"] == SMART_CONTRACTS["cross marketplace collab multisig"]) or
        (transaction["sender"] == SMART_CONTRACTS["cross marketplace collab multisig"]) or
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 1"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 1"]) or 
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 2"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 2"]) or 
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 3"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 3"]) or
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 4"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 4"])):
        transaction["kind"] = "multisig operation"

    if ((transaction["target"] == SMART_CONTRACTS["Teia multi-option polls prototype"]) or
        (transaction["sender"] == SMART_CONTRACTS["Teia multi-option polls prototype"]) or
        (transaction["target"] == SMART_CONTRACTS["Teia multi-option polls"]) or 
        (transaction["sender"] == SMART_CONTRACTS["Teia multi-option polls"])):
        transaction["kind"] = "Teia polls operation"

    if transaction["entrypoint"] == "claim":
        if transaction["target"] == SMART_CONTRACTS["teia DAO token distributor"]:
            transaction["kind"] = "teia DAO token claim"
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["TEIA"]
        elif transaction["target"] == SMART_CONTRACTS["teia DAO token distributor prototype"]:
            transaction["kind"] = "test teia DAO token claim"
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["testTEIA"]
        elif transaction["target"] == SMART_CONTRACTS["Tezos Domains TED Airdrop contract"]:
            transaction["kind"] = "TED token claim"
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["TED"]

    if transaction["entrypoint"] == "deposit":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains Governance Pool contract"]:
            transaction["kind"] = "TED DAO operation"

    if transaction["entrypoint"] == "mint_tokens":
        if transaction["sender"] == SMART_CONTRACTS["Tezos Domains Governance Pool contract"]:
            transaction["kind"] = "TED DAO operation"
 
    if transaction["entrypoint"] == "withdraw":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains Governance Pool contract"]:
            transaction["kind"] = "TED DAO operation"
 
    if transaction["entrypoint"] == "burn_tokens":
        if transaction["sender"] == SMART_CONTRACTS["Tezos Domains Governance Pool contract"]:
            transaction["kind"] = "TED DAO operation"

    if ((transaction["target"] == SMART_CONTRACTS["Teia DAO governance prototype"]) or
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO governance prototype"]) or
        (transaction["target"] == SMART_CONTRACTS["Teia DAO treasury prototype"]) or 
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO treasury prototype"]) or
        (transaction["target"] == SMART_CONTRACTS["Teia DAO representatives prototype"]) or 
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO representatives prototype"])):
        transaction["kind"] = "Teia DAO prototype operation"

    if ((transaction["target"] == SMART_CONTRACTS["Teia DAO governance"]) or
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO governance"]) or
        (transaction["target"] == SMART_CONTRACTS["Teia DAO treasury"]) or 
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO treasury"]) or
        (transaction["target"] == SMART_CONTRACTS["Teia DAO representatives"]) or 
        (transaction["sender"] == SMART_CONTRACTS["Teia DAO representatives"])):
        transaction["kind"] = "Teia DAO operation"

    if transaction["target"] in [SMART_CONTRACTS["Interactive experiment 1"], SMART_CONTRACTS["Interactive experiment 2"], SMART_CONTRACTS["Interactive experiment 3"], SMART_CONTRACTS["Interactive experiment 4"], SMART_CONTRACTS["Interactive experiment 5"]]:
        transaction["kind"] = "interactive experiment operation"

    if transaction["target"] in [SMART_CONTRACTS["Pakistani Flood donations contract"], SMART_CONTRACTS["Tezos for Iran donations contract"]]:
        if transaction["entrypoint"] is not None:
            transaction["kind"] = "donation contract operation"

    if transaction["entrypoint"] == "sign_letter":
        if transaction["target"] == SMART_CONTRACTS["Solidarity for Iranian Artists - Open letter"]:
            transaction["kind"] = "sing open letter"

    if transaction["target"] in [SMART_CONTRACTS["TezID Controller"], SMART_CONTRACTS["TezID Store"]]:
        transaction["kind"] = "TezID operation"

    if transaction["target"] == SMART_CONTRACTS["teia vote"]:
        transaction["kind"] = "teia vote operation"

    if transaction["target"] in [SMART_CONTRACTS["teia core team vote"], SMART_CONTRACTS["teia core team vote prototype"]]:
        transaction["kind"] = "teia core team vote operation"

    if transaction["target"] in [SMART_CONTRACTS["tezos polls"], SMART_CONTRACTS["tezos polls prototype 1"], SMART_CONTRACTS["tezos polls prototype 2"]]:
        transaction["kind"] = "tezos polls operation"

    if transaction["target"] == SMART_CONTRACTS["h=n DAO"]:
        transaction["kind"] = "h=n DAO operation"

    if transaction["entrypoint"] == "vote":
        if transaction["target"] == SMART_CONTRACTS["h=n DAO II"]:
            transaction["kind"] = "h=n vote"

    if transaction["target"] == SMART_CONTRACTS["tz1and world"]:
        if transaction["entrypoint"] != "get_item":
            transaction["kind"] = "tz1and operation"

    if transaction["entrypoint"] in ["update_issuer", "update_price", "update_reserve"]:
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"], SMART_CONTRACTS["FXHASH tickets minter"]]:
            transaction["kind"] = "FXHASH operation"
    elif transaction["entrypoint"] in ["add", "update"]:
        if transaction["sender"] in [SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
            transaction["kind"] = "FXHASH operation"
    elif transaction["entrypoint"] in ["consume", "generate"]:
        if transaction["sender"] in [SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "FXHASH operation"
        elif transaction["target"] == SMART_CONTRACTS["FXHASH seeds provider"]:
            transaction["kind"] = "FXHASH operation"

    if transaction["entrypoint"] == "burn_supply":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"], SMART_CONTRACTS["FXHASH minter v4"]]:
            transaction["kind"] = "FXHASH operation"

    if transaction["entrypoint"] in ["pay_royalties_xtz", "sign_cocreator"]:
        if transaction["target"] == TOKENS["ITEM"]:
            transaction["kind"] = "versum operation"

    if transaction["entrypoint"] == "batch_fwd_xtz":
        if transaction["sender"] == TOKENS["ITEM"]:
            transaction["kind"] = "versum operation"

    if transaction["entrypoint"] == "check":
        if transaction["sender"] == TOKENS["contter token"]:
            transaction["kind"] = "contter operation"

    if transaction["entrypoint"] == "acquire_royalties":
        if transaction["target"] == SMART_CONTRACTS["akaMetaverse marketplace v1"]:
            transaction["kind"] = "akaSwap operation"

    if transaction["entrypoint"] == "assign_akaDAO":
        if transaction["sender"] == SMART_CONTRACTS["akaMetaverse marketplace v1"]:
            transaction["kind"] = "akaSwap operation"

    if transaction["entrypoint"] == "match_and_transfer":
        if transaction["target"] == SMART_CONTRACTS["rarible marketplace v2"]:
            transaction["kind"] = "rarible operation"
    elif transaction["entrypoint"] in ["do_transfers", "put", "remove"]:
        if transaction["sender"] in [SMART_CONTRACTS["rarible marketplace v2"], SMART_CONTRACTS["rarible Transfer Manager"]]:
            transaction["kind"] = "rarible operation"

    if transaction["entrypoint"] == "default":
        if transaction["target"] in [SMART_CONTRACTS["my tzprofile contract 1"], SMART_CONTRACTS["my tzprofile contract 2"]]:
            transaction["kind"] = "tzprofile operation"

    if transaction["target"] == SMART_CONTRACTS["Ukraine war donations contract"]:
        transaction["donation"] = True

    if transaction["entrypoint"] in ["addOrganization", "addAdmin", "requestToJoinOrganization", "responseToJoinOrganization"]:
        if transaction["target"] in [SMART_CONTRACTS["Tezos community organizations contract 1"], SMART_CONTRACTS["Tezos community organizations contract 2"]]:
            transaction["kind"] = "tezos community organizations operation"

    if transaction["entrypoint"] == "tokenToTezPayment":
        if transaction["target"] in [SMART_CONTRACTS["QuipuSwap hDAO old"], SMART_CONTRACTS["QuipuSwap hDAO"]]:
            transaction["kind"] = "sell hDAO in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["hDAO"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap wUSDC"]:
            transaction["kind"] = "sell wUSDC in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "17"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["wUSDC"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap uUSD"]:
            transaction["kind"] = "sell uUSD in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["uUSD"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap HEH"]:
            transaction["kind"] = "sell HEH in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = "KT1G1cCRNBgQ48mVDjopHjEmTN5Sbtar8nn9"
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap KALAM"]:
            transaction["kind"] = "sell KALAM in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["KALAM"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap QUIPU"]:
            transaction["kind"] = "sell QUIPU in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["QUIPU"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap MTRIA"]:
            transaction["kind"] = "sell Materia in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = TOKENS["Materia"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap kUSD"]:
            transaction["kind"] = "sell kUSD in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_amount"] = int(transaction["parameters"]["amount"])
            transaction["token_address"] = "KT1K9gCRgaLRFKTErYt1wVxA3Frb9FjasjTV"
    elif transaction["entrypoint"] == "tezToTokenPayment":
        if transaction["target"] in [SMART_CONTRACTS["QuipuSwap hDAO old"], SMART_CONTRACTS["QuipuSwap hDAO"]]:
            transaction["kind"] = "buy hDAO in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["hDAO"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap wUSDC"]:
            transaction["kind"] = "buy wUSDC in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "17"
            transaction["token_address"] = TOKENS["wUSDC"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap uUSD"]:
            transaction["kind"] = "buy uUSD in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["uUSD"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap HEH"]:
            transaction["kind"] = "buy HEH in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = "KT1G1cCRNBgQ48mVDjopHjEmTN5Sbtar8nn9"
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap KALAM"]:
            transaction["kind"] = "buy KALAM in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["KALAM"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap QUIPU"]:
            transaction["kind"] = "buy KALAM in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["QUIPU"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap MTRIA"]:
            transaction["kind"] = "buy Materia in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["Materia"]
        elif transaction["target"] == SMART_CONTRACTS["QuipuSwap kUSD"]:
            transaction["kind"] = "buy kUSD in QuipuSwap"
            transaction["collect"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = "KT1K9gCRgaLRFKTErYt1wVxA3Frb9FjasjTV"

    if transaction["sender"] in [SMART_CONTRACTS["QuipuSwap hDAO old"], SMART_CONTRACTS["QuipuSwap hDAO"]]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell hDAO in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["hDAO"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap wUSDC"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell wUSDC in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "17"
            transaction["token_address"] = TOKENS["wUSDC"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap uUSD"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell uUSD in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["uUSD"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap HEH"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell HEH in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = "KT1G1cCRNBgQ48mVDjopHjEmTN5Sbtar8nn9"
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap KALAM"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell KALAM in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["KALAM"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap QUIPU"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell QUIPU in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["QUIPU"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap MTRIA"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell Materia in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = TOKENS["Materia"]
    elif transaction["sender"] == SMART_CONTRACTS["QuipuSwap kUSD"]:
        if transaction["amount"] > 0:
            transaction["kind"] = "sell kUSD in QuipuSwap"
            transaction["collection_sale"] = True
            transaction["token_id"] = "0"
            transaction["token_address"] = "KT1K9gCRgaLRFKTErYt1wVxA3Frb9FjasjTV"

    if transaction["entrypoint"] == "accept_invitation":
        if transaction["target"] == SMART_CONTRACTS["objkt.com Minting Factory"]:
            transaction["kind"] = "accept objkt.com invitation"

    if transaction["entrypoint"] == "enforce_conditions":
        if transaction["target"] == SMART_CONTRACTS["objkt.com Fee Sharing Helper v3"]:
            transaction["kind"] = "distribute objkt.com artists fees"

    if transaction["entrypoint"] == "execute":
        if (transaction["target"] in [SMART_CONTRACTS["3Route v1"], SMART_CONTRACTS["3Route v2"], SMART_CONTRACTS["3Route v3"], SMART_CONTRACTS["3Route v4"]]) and (transaction["sender"] in user_wallets) and (transaction["parameters"]["receiver"] == transaction["sender"]):
            token_in = three_route_tokens[transaction["target"]][transaction["parameters"]["token_in_id"]]
            token_out = three_route_tokens[transaction["target"]][transaction["parameters"]["token_out_id"]]

            if "xtz" in token_in:
                if "fa2" in token_out:
                    transaction["token_id"] = token_out["fa2"]["fa2_id"]
                    transaction["token_address"] = token_out["fa2"]["contract_address"]
                elif "fa12" in token_out:
                    transaction["token_id"] = "0"
                    transaction["token_address"] = token_out["fa12"]["contract_address"]

                if transaction["token_address"] in token_aliases:
                    transaction["kind"] = "buy %s in 3Route" % token_aliases[transaction["token_address"]]
                else:
                    transaction["kind"] = "buy token in 3Route"

                transaction["collect"] = True
                transaction["token_editions"] = None
            elif "xtz" in token_out:
                if "fa2" in token_in:
                    transaction["token_id"] = token_in["fa2"]["fa2_id"]
                    transaction["token_address"] = token_in["fa2"]["contract_address"]
                elif "fa12" in token_in:
                    transaction["token_id"] = "0"
                    transaction["token_address"] = token_in["fa12"]["contract_address"]

                if transaction["token_address"] in token_aliases:
                     transaction["kind"] = "sell %s in 3Route" % token_aliases[transaction["token_address"]]
                else:
                    transaction["kind"] = "sell token in 3Route"

                transaction["collection_sale"] = True
                transaction["token_editions"] = None
            else:
                if "fa2" in token_out:
                    transaction["token_id"] = token_out["fa2"]["fa2_id"]
                    transaction["token_address"] = token_out["fa2"]["contract_address"]
                elif "fa12" in token_out:
                    transaction["token_id"] = "0"
                    transaction["token_address"] = token_out["fa12"]["contract_address"]

                transaction["kind"] = "swap tokens in 3Route"
                transaction["token_editions"] = None

            three_route_operations[transaction["hash"]] = {
                "kind": transaction["kind"],
                "collect": transaction["collect"],
                "collection_sale": transaction["collection_sale"],
                "token_id": transaction["token_id"],
                "token_editions": transaction["token_editions"],
                "token_address": transaction["token_address"]
            }
    elif transaction["hash"] in three_route_operations and (transaction["initiator"] in user_wallets):
        for key, value in three_route_operations[transaction["hash"]].items():
            transaction[key] = value

        transaction["kind"] = "3Route operation"

    # Add the missing token information from the token transfers
    if (transaction["token_id"] is None) and (transaction["token_editions"] is not None) and (transaction["token_address"] is not None):
        cond = (token_transfers["timestamp"] == transaction["timestamp"]) & (
            token_transfers["token_editions"] == str(transaction["token_editions"])) & (
            token_transfers["token_address"] == transaction["token_address"])
        matching_token_transfers = token_transfers[cond]

        if (len(matching_token_transfers) >= 1):
            first_token_transfer = matching_token_transfers.iloc[0]
            transaction["token_id"] = first_token_transfer["token_id"]

    if (transaction["token_editions"] is None) and (transaction["token_id"] is not None) and (transaction["token_address"] is not None):
        cond = (token_transfers["timestamp"] == transaction["timestamp"]) & (
            token_transfers["token_id"] == transaction["token_id"]) & (
            token_transfers["token_address"] == transaction["token_address"])
        matching_token_transfers = token_transfers[cond]

        if (len(matching_token_transfers) >= 1):
            first_token_transfer = matching_token_transfers.iloc[0]
            transaction["token_editions"] = int(first_token_transfer["token_editions"])

    if (transaction["token_id"] is None) and  (transaction["token_editions"] is None) and (transaction["token_address"] is not None):
        cond = (token_transfers["timestamp"] == transaction["timestamp"]) & (
            token_transfers["token_address"] == transaction["token_address"])
        matching_token_transfers = token_transfers[cond]

        if (len(matching_token_transfers) >= 1):
            first_token_transfer = matching_token_transfers.iloc[0]
            transaction["token_id"] = first_token_transfer["token_id"]
            transaction["token_editions"] = int(first_token_transfer["token_editions"])

    if (transaction["token_id"] is not None) and  (transaction["token_editions"] is not None) and (transaction["token_address"] is None):
        cond = (token_transfers["timestamp"] == transaction["timestamp"]) & (
            token_transfers["token_id"] == transaction["token_id"]) & (
            token_transfers["token_editions"] == str(transaction["token_editions"]))
        matching_token_transfers = token_transfers[cond]

        if (len(matching_token_transfers) >= 1):
            first_token_transfer = matching_token_transfers.iloc[0]
            transaction["token_address"] = first_token_transfer["token_address"]

    # Save the unprocessed raw transactions
    if transaction["kind"] is None:
        unprocessed_transactions.append(t)

    # Add the processed transaction
    transactions.append(transaction)

# Process the raw originations
originations = []

for o in raw_originations:
    # Save the most relevant information
    origination = {
        "timestamp": o["timestamp"],
        "level": o["level"],
        "kind": "contract origination",
        "entrypoint": None,
        "parameters": None,
        "initiator": o["initiator"]["address"] if "initiator" in o else None,
        "sender": o["sender"]["address"],
        "target": None,
        "applied": o["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": True,
        "reveal": False,
        "delegation": False,
        "baking": False,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": o["contractBalance"] / 1e6,
        "fees": ((o["bakerFee"] + o["storageFee"] + o["allocationFee"]) / 1e6) if (o["status"] == "applied") else (o["bakerFee"] / 1e6),
        "tez_to_euros": o["quote"]["eur"],
        "tez_to_usd": o["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": o["hash"],
        "comment": ""}

    # Add the processed origination
    originations.append(origination)

# Process the raw reveals
reveals = []

for r in raw_reveals:
    # Save the most relevant information
    reveal = {
        "timestamp": r["timestamp"],
        "level": r["level"],
        "kind": "reveal public key",
        "entrypoint": None,
        "parameters": None,
        "initiator": None,
        "sender": r["sender"]["address"],
        "target": None,
        "applied": r["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": True,
        "delegation": False,
        "baking": False,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": 0,
        "fees": r["bakerFee"] / 1e6,
        "tez_to_euros": r["quote"]["eur"],
        "tez_to_usd": r["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": r["hash"],
        "comment": ""}

    # Add the processed reveal
    reveals.append(reveal)

# Process the raw delegations
delegations = []

for d in raw_delegations:
    # Save the most relevant information
    delegation = {
        "timestamp": d["timestamp"],
        "level": d["level"],
        "kind": "delegation",
        "entrypoint": None,
        "parameters": None,
        "initiator": d["initiator"]["address"] if "initiator" in d else None,
        "sender": d["sender"]["address"],
        "target": None,
        "applied": d["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": True,
        "baking": False,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": 0,
        "fees": d["bakerFee"] / 1e6,
        "tez_to_euros": d["quote"]["eur"],
        "tez_to_usd": d["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": d["hash"],
        "comment": ""}

    # Add the processed delegation
    delegations.append(delegation)

# Process the raw baking operations
bakings = []

for b in raw_bakings:
    # Save the most relevant information
    baking = {
        "timestamp": b["timestamp"],
        "level": b["level"],
        "kind": "baking",
        "entrypoint": None,
        "parameters": None,
        "initiator": None,
        "sender": None,
        "target": b["producer"]["address"],
        "applied": True,
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": False,
        "baking": True,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": (b["reward"] + b["bonus"] + b["fees"]) / 1e6,
        "fees": 0,
        "tez_to_euros": b["quote"]["eur"],
        "tez_to_usd": b["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": b["block"],
        "comment": ""}

    # Add the processed baking
    bakings.append(baking)

# Process the raw endorsing rewards
endorsing_rewards = []

for e in raw_endorsing_rewards:
    # Save the most relevant information
    endorsing_reward = {
        "timestamp": e["timestamp"],
        "level": e["level"],
        "kind": "endorsing reward",
        "entrypoint": None,
        "parameters": None,
        "initiator": None,
        "sender": None,
        "target": e["baker"]["address"],
        "applied": True,
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": False,
        "baking": False,
        "endorsing_reward": True,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": e["received"] / 1e6,
        "fees": 0,
        "tez_to_euros": e["quote"]["eur"],
        "tez_to_usd": e["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": e["block"],
        "comment": ""}

    # Add the processed endorsing rewards
    endorsing_rewards.append(endorsing_reward)

# Process the staking rewards
staking_rewards = []

for s in raw_staking_rewards:
    # Save the most relevant information
    staking_reward = {
        "timestamp": s["timestamp"],
        "level": s["level"],
        "kind": "receive tez from staking",
        "entrypoint": None,
        "parameters": None,
        "initiator": None,
        "sender": s["baker"],
        "target": s["user"],
        "applied": True,
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "primary_art_sale": False,
        "secondary_art_sale": False,
        "collection_sale": False,
        "staking": True,
        "origination": False,
        "reveal": False,
        "delegation": False,
        "baking": False,
        "endorsing_reward": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": s["rewarded_tez"],
        "fees": 0,
        "tez_to_euros": s["quote"]["eur"],
        "tez_to_usd": s["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": s["user"] + "/rewards",
        "comment": ""}

    # Add the processed staking reward
    staking_rewards.append(staking_reward)

# Combine the transactions, originations and reveals in a single array
combined_operations = combine_operations(transactions, originations)
combined_operations = combine_operations(combined_operations, reveals)
combined_operations = combine_operations(combined_operations, delegations)
combined_operations = combine_operations(combined_operations, bakings)
combined_operations = combine_operations(combined_operations, endorsing_rewards)
combined_operations = combine_operations(combined_operations, staking_rewards)

# Apply the operation corrections specified by the user
operation_corrections = read_json_file(os.path.join(data_directory, "input", "operation_corrections.json"))

for operation in combined_operations:
    if operation["hash"] in operation_corrections:
        corrections = operation_corrections[operation["hash"]]

        for key, value in corrections.items():
            if key in operation:
                operation[key] = value

# Get all address aliases
aliases = {}
aliases.update(user_wallets)
aliases.update(baker_wallets)
aliases.update(exchange_wallets)
aliases.update(general_wallets)
aliases.update(burn_wallets)
aliases.update(token_aliases)
aliases.update(smart_contract_aliases)

for token_address in objktcom_collections:
    if token_address not in aliases:
        aliases[token_address] = "objkt.com collection"

for token_address in objktcom_open_editions:
    if token_address not in aliases:
        aliases[token_address] = "objkt.com open edition"

for token_address in editart_collections:
    if token_address not in aliases:
        aliases[token_address] = "editart.xyz collection"

for token_address, token_alias in fa12_tokens.items():
    if token_address not in aliases:
        aliases[token_address] = token_alias

for token_address, token_alias in fa2_tokens.items():
    if token_address not in aliases:
        aliases[token_address] = token_alias

# Save the processed data in a csv file
file_name = "operations_%s.csv" % user_first_wallet
columns = [
    "timestamp", "level", "tez_balance", "kind", "entrypoint", "initiator",
    "sender", "target", "is_initiator", "is_sender", "is_target", "applied",
    "internal", "ignore", "mint", "collect", "active_offer", "art_sale",
    "primary_art_sale", "secondary_art_sale", "collection_sale", "staking",
    "origination", "reveal", "delegation", "baking", "endorsing_reward",
    "prize", "donation", "buy_tez", "sell_tez", "amount", "fees",
    "received_amount", "art_sale_amount", "primary_art_sale_amount",
    "secondary_art_sale_amount", "collection_sale_amount",
    "staking_rewards_amount", "baking_amount", "endorsing_rewards_amount",
    "prize_amount", "buy_tez_amount", "received_amount_others", "spent_amount",
    "collect_amount", "active_offer_amount", "donation_amount",
    "sell_tez_amount", "spent_amount_others", "spent_fees", "tez_to_euros",
    "tez_to_usd", "token_name", "token_id", "token_editions", "token_address",
    "tzkt_link", "comment"]
format = [
    "%s", "%i", "%f", "%s", "%s", "%s", "%s", "%s", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%f", "%f", "%f", "%f", "%f",
    "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f",
    "%f", "%f", "%f", "%f", "%f", "%s", "%s", "%s", "%s", "%s", "%s"]

with open(os.path.join(data_directory, "output", file_name), "w", newline="\n") as output_file:
    writer = csv.writer(output_file)

    # Write the header
    writer.writerow(columns)

    # Loop over the combined operations
    tez_balance = 0

    for op in combined_operations:
        # Check if the user is the initiator, the sender or the target
        is_initiator = op["initiator"] in user_wallets
        is_sender = op["sender"] in user_wallets
        is_target = op["target"] in user_wallets

        # Calculate the different received and spent tez amounts
        applied = op["applied"]
        ignore = op["ignore"]
        amount = op["amount"]
        fees = op["fees"]
        received_amount = amount if (is_target and applied and (not ignore)) else 0
        art_sale_amount = amount if (is_target and applied and (not ignore) and op["art_sale"]) else 0
        primary_art_sale_amount = amount if (is_target and applied and (not ignore) and op["primary_art_sale"]) else 0
        secondary_art_sale_amount = amount if (is_target and applied and (not ignore) and op["secondary_art_sale"]) else 0
        collection_sale_amount = amount if (is_target and applied and (not ignore) and op["collection_sale"]) else 0
        staking_rewards_amount = amount if (is_target and applied and (not ignore) and op["staking"]) else 0
        baking_amount = amount if (is_target and applied and (not ignore) and op["baking"]) else 0
        endorsing_rewards_amount = amount if (is_target and applied and (not ignore) and op["endorsing_reward"]) else 0
        prize_amount = amount if (is_target and applied and (not ignore) and op["prize"]) else 0
        buy_tez_amount = amount if (is_target and applied and (not ignore) and op["buy_tez"]) else 0
        received_amount_others = amount if (is_target and applied and (not ignore) and (not (op["art_sale"] or op["collection_sale"] or op["staking"] or op["baking"] or op["endorsing_reward"] or op["prize"] or op["buy_tez"]))) else 0
        spent_amount = amount if (is_sender and applied and (not ignore) and (not op["active_offer"])) else 0
        collect_amount = amount if (is_sender and applied and (not ignore) and op["collect"]) else 0
        active_offer_amount = amount if (is_sender and applied and (not ignore) and op["active_offer"]) else 0
        donation_amount = amount if (is_sender and applied and (not ignore) and op["donation"]) else 0
        sell_tez_amount = amount if (is_sender and applied and (not ignore) and op["sell_tez"]) else 0
        spent_amount_others = amount if (is_sender and applied and (not ignore) and (not (op["collect"] or op["active_offer"] or op["donation"] or op["sell_tez"]))) else 0
        spent_fees = fees if (is_initiator or is_sender) else 0

        # Calculate the tez balance
        tez_balance += received_amount - spent_amount - active_offer_amount - spent_fees

        # Get the token alias
        token_address = op["token_address"]
        token_alias = ""

        if token_address in token_aliases:
            token_alias = token_aliases[token_address]
        elif token_address in objktcom_collections:
            token_alias = "objkt.com collection"
        elif token_address in objktcom_open_editions:
            token_alias = "objkt.com open edition"
        elif token_address in editart_collections:
            token_alias = "editart.xyz collection"
        elif token_address in aliases:
            token_alias = aliases[token_address]

        token_alias = token_alias.replace(",", " ")

        # Write the operation data in the output file
        data = [
            op["timestamp"],
            op["level"],
            tez_balance,
            op["kind"],
            op["entrypoint"] if op["entrypoint"] is not None else "",
            aliases.get(op["initiator"], op["initiator"]).replace(",", " ") if op["initiator"] is not None else "",
            aliases.get(op["sender"], op["sender"]).replace(",", " ") if op["sender"] is not None else "",
            aliases.get(op["target"], op["target"]).replace(",", " ") if op["target"] is not None else "",
            is_initiator,
            is_sender,
            is_target,
            applied,
            op["internal"],
            ignore,
            op["mint"],
            op["collect"],
            op["active_offer"],
            op["art_sale"],
            op["primary_art_sale"],
            op["secondary_art_sale"],
            op["collection_sale"],
            op["staking"],
            op["origination"],
            op["reveal"],
            op["delegation"],
            op["baking"],
            op["endorsing_reward"],
            op["prize"],
            op["donation"],
            op["buy_tez"],
            op["sell_tez"],
            amount,
            fees,
            received_amount,
            art_sale_amount,
            primary_art_sale_amount,
            secondary_art_sale_amount,
            collection_sale_amount,
            staking_rewards_amount,
            baking_amount,
            endorsing_rewards_amount,
            prize_amount,
            buy_tez_amount,
            received_amount_others,
            spent_amount,
            collect_amount,
            active_offer_amount,
            donation_amount,
            sell_tez_amount,
            spent_amount_others,
            spent_fees,
            op["tez_to_euros"],
            op["tez_to_usd"],
            token_alias,
            op["token_id"] if op["token_id"] is not None else "",
            op["token_editions"] if op["token_editions"] is not None else "",
            token_address if token_address is not None else "",
            "https://tzkt.io/%s" % op["hash"],
            op["comment"]]
        writer.writerow(data)

# Save the unprocessed transactions in a json file
unprocessed_file_name = "unprocessed_transactions_%s.json" % user_first_wallet
save_json_file(os.path.join(data_directory, "output", unprocessed_file_name), unprocessed_transactions)

# Print some details
print("\n We discovered %i operations associated to the user wallets." % len(combined_operations))
print(" You can find the processed information in %s\n" % os.path.join(data_directory, "output", file_name))

if len(unprocessed_transactions) > 0:
    print(" Of those, %i operations could not be processed completely." % len(unprocessed_transactions))
    print(" See %s for more details.\n" % os.path.join(data_directory, "output", unprocessed_file_name))
