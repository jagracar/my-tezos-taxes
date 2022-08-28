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

# Get the user raw transactions and originations information
raw_transactions = get_user_transactions(user_wallets)
raw_originations = get_user_originations(user_wallets)
raw_reveals = get_user_reveals(user_wallets)
raw_delegations = get_user_delegations(user_wallets)

# Get the user mints, swaps, collects, auction bids, art sales and collection sales
user_mints = get_user_mints(user_wallets)
user_swaps = get_user_swaps(user_wallets)
user_collects = get_user_collects(user_wallets)
user_auction_bids = get_user_auction_bids(user_wallets)
user_art_sales = get_user_art_sales(user_wallets)
user_collection_sales = get_user_collection_sales(user_wallets)

# Get the list of FA2 contracts associated to the objkt.com collections
objktcom_collections = get_objktcom_collections()

# Get the list of FA1.2 and FA2 tokens
fa12_tokens = get_fa12_tokens()
fa2_tokens = get_fa2_tokens()

# Get the main tezos tokens and smart contract aliases
token_aliases = {address: name for name, address in TOKENS.items()}
smart_contract_aliases = {address: alias for alias, address in SMART_CONTRACTS.items()}

# Define the burn addresses
burn_addresses = ["tz1burnburnburnburnburnburnburjAYjjX"]

# Process the raw transactions
transactions = []
unprocessed_transactions = []

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
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": False,
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
        elif transaction["target"] in objktcom_collections:
            transaction["kind"] = "objkt.com collection mint"
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
        elif transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
            transaction["kind"] = "FXHASH mint"
            transaction["mint"] = False
            transaction["collect"] = True
        elif transaction["target"] in [TOKENS["GENTK v1"], TOKENS["GENTK v2"]]:
            transaction["kind"] = "FXHASH mint"
            transaction["mint"] = False
            transaction["collect"] = True
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
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
            transaction["kind"] = "create FXHASH collection"
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
                        if ttt[to_key] in burn_addresses:
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
                        if ttt["to_"] in burn_addresses:
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
        elif transaction["target"] in fa2_tokens:
            transaction["token_address"] = transaction["target"]

            for tt in transaction["parameters"]:
                if tt["from_"] in user_wallets:
                    transaction["kind"] = "send " + fa2_tokens[transaction["target"]]
                    transaction["token_id"] = tt["txs"][0]["token_id"]
                    transaction["token_editions"] = int(tt["txs"][0]["amount"])

                    for ttt in tt["txs"]:
                        if ttt["to_"] in burn_addresses:
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

                if transaction["parameters"]["to"] in burn_addresses:
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
        elif transaction["target"] in fa2_tokens:
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["kind"] = "add %s operators" % fa2_tokens[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["kind"] = "remove %s operators" % fa2_tokens[transaction["target"]]
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
    elif transaction["entrypoint"] == "update_operators_for_all":
        if transaction["target"] in TOKENS["Rarible token"]:
            transaction["kind"] = "update %s operators" % token_aliases[transaction["target"]]
    elif transaction["entrypoint"] == "add_adhoc_operators":
        if transaction["target"] in token_aliases:
            transaction["kind"] = "update %s adhoc operators" % token_aliases[transaction["target"]]
            transaction["token_id"] = transaction["parameters"][0]["token_id"]
            transaction["token_editions"] = None
            transaction["token_address"] = transaction["target"]

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
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com swap"
    elif transaction["entrypoint"] == "retract_ask":
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com cancel swap"
    elif transaction["entrypoint"] == "listing":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH swap"
    elif transaction["entrypoint"] == "offer":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH swap"
    elif transaction["entrypoint"] == "listing_cancel":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH cancel swap"
    elif transaction["entrypoint"] == "cancel_offer":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH cancel swap"
    elif transaction["entrypoint"] == "create_swap":
        if transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum swap"

    # Check if the transaction is connected with bids or offers
    if transaction["entrypoint"] == "bid":
        if transaction["target"] in [SMART_CONTRACTS["objkt.bid Legacy"], SMART_CONTRACTS["objkt.com marketplace v1"]]:
            transaction["kind"] = "objkt.com offer"
        elif transaction["target"] in [SMART_CONTRACTS["objkt.com English Auctions Old"], SMART_CONTRACTS["objkt.com English Auctions v1"], SMART_CONTRACTS["objkt.com English Auctions v2"]]:
            transaction["kind"] = "objkt.com bid in English auction"
        elif transaction["target"] == SMART_CONTRACTS["versum marketplace"]:
            transaction["kind"] = "versum bid in auction"
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
        if transaction["target"] == SMART_CONTRACTS["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com offer"
        elif transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH offer"
    elif transaction["entrypoint"] == "retract_offer":
        if transaction["target"] == SMART_CONTRACTS["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com cancel offer"
    elif transaction["entrypoint"] == "offer_cancel":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH cancel offer"
    elif transaction["entrypoint"] == "fulfill_offer":
        if transaction["target"] == SMART_CONTRACTS["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] == "offer_accept":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
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

    # Check if the transaction is connected with collects
    if transaction["entrypoint"] == "collect":
        if transaction["target"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n collect"
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
        if transaction["target"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com collect"
    elif transaction["entrypoint"] == "listing_accept":
        if transaction["target"] == SMART_CONTRACTS["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH collect"
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

    # Check if the transaction is connected with sells
    if (transaction["entrypoint"] is None) and (not transaction["internal"]) and (transaction["target"] in user_wallets):
        if transaction["sender"] in [SMART_CONTRACTS["h=n marketplace v1"], SMART_CONTRACTS["h=n marketplace v2"]]:
            transaction["kind"] = "h=n sell"
        elif transaction["sender"] == SMART_CONTRACTS["teia marketplace"]:
            transaction["kind"] = "teia sell"
        elif transaction["sender"] in [SMART_CONTRACTS["teia marketplace prototype 1"], SMART_CONTRACTS["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype sell"
        elif transaction["sender"] in [SMART_CONTRACTS["objkt.com marketplace v1"], SMART_CONTRACTS["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com sell"
        elif transaction["sender"] in [SMART_CONTRACTS["FXHASH marketplace v1"], SMART_CONTRACTS["FXHASH marketplace v2"]]:
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
        elif transaction["sender"] in [SMART_CONTRACTS["Breadfond 1"], SMART_CONTRACTS["Breadfond 2"], SMART_CONTRACTS["Breadfond 3"]]:
            transaction["kind"] = "Breadfond share in tez"

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

    if transaction["entrypoint"] in ["wrap", "unwrap", "approve"]:
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
        (transaction["sender"] == SMART_CONTRACTS["Tezos Domains NameRegistry UpdateRecord"]) or
        (transaction["target"] == SMART_CONTRACTS["Tezos Domains NameRegistry UpdateRecord"])):
        transaction["kind"] = "tezos domains operation"

    if transaction["entrypoint"] == "renew":
        if transaction["target"] == SMART_CONTRACTS["Tezos Domains registrar"]:
            transaction["kind"] = "tezos domain renovation"
            transaction["token_editions"] = "1"
            transaction["token_address"] = TOKENS["Tezos domain token"]

    if ((transaction["target"] == SMART_CONTRACTS["teia multisig"]) or
        (transaction["sender"] == SMART_CONTRACTS["teia multisig"]) or
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 1"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 1"]) or 
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 2"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 2"]) or 
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 3"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 3"]) or
        (transaction["target"] == SMART_CONTRACTS["teia multisig prototype 4"]) or 
        (transaction["sender"] == SMART_CONTRACTS["teia multisig prototype 4"])):
        transaction["kind"] = "Multisig operation"

    if transaction["target"] in [SMART_CONTRACTS["Interactive experiment 1"], SMART_CONTRACTS["Interactive experiment 2"], SMART_CONTRACTS["Interactive experiment 3"]]:
        transaction["kind"] = "Interactive experiment operation"

    if transaction["target"] in [SMART_CONTRACTS["TezID Controller"], SMART_CONTRACTS["TezID Store"]]:
        transaction["kind"] = "TezID operation"

    if transaction["target"] == SMART_CONTRACTS["teia vote"]:
        transaction["kind"] = "teia vote"

    if transaction["target"] == SMART_CONTRACTS["h=n DAO"]:
        transaction["kind"] = "h=n DAO operation"

    if transaction["entrypoint"] == "vote":
        if transaction["target"] == SMART_CONTRACTS["h=n DAO II"]:
            transaction["kind"] = "h=n vote"

    if transaction["target"] == SMART_CONTRACTS["tz1and world"]:
        if transaction["entrypoint"] != "get_item":
            transaction["kind"] = "tz1and operation"

    if transaction["entrypoint"] in ["update_issuer", "update_price", "update_reserve"]:
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v1"], SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
            transaction["kind"] = "FXHASH operation"
    elif transaction["entrypoint"] in ["add", "update"]:
        if transaction["sender"] in [SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
            transaction["kind"] = "FXHASH operation"

    if transaction["entrypoint"] == "burn_supply":
        if transaction["target"] in [SMART_CONTRACTS["FXHASH minter v2"], SMART_CONTRACTS["FXHASH minter v3"]]:
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

    if transaction["entrypoint"] == "accept_invitation":
        if transaction["target"] == SMART_CONTRACTS["objkt.com Minting Factory"]:
            transaction["kind"] = "accept objkt.com invitation"

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
        "collection_sale": False,
        "staking": False,
        "origination": True,
        "reveal": False,
        "delegation": False,
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
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": True,
        "delegation": False,
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
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": True,
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
        "hash": r["hash"],
        "comment": ""}

    # Add the processed delegation
    delegations.append(delegation)

# Combine the transactions, originations and reveals in a single array
combined_operations = combine_operations(transactions, originations)
combined_operations = combine_operations(combined_operations, reveals)
combined_operations = combine_operations(combined_operations, delegations)

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
aliases.update(token_aliases)
aliases.update(smart_contract_aliases)
aliases.update({address: "Burn address" for address in burn_addresses})

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
    "collection_sale", "staking", "origination", "reveal", "delegation",
    "prize", "donation", "buy_tez", "sell_tez", "amount", "fees",
    "received_amount", "art_sale_amount", "collection_sale_amount",
    "staking_rewards_amount", "prize_amount", "buy_tez_amount",
    "received_amount_others", "spent_amount", "collect_amount",
    "active_offer_amount", "donation_amount", "sell_tez_amount",
    "spent_amount_others", "spent_fees", "tez_to_euros", "tez_to_usd",
    "token_name", "token_id", "token_editions", "token_address", "tzkt_link",
    "comment"]
format = [
    "%s", "%i", "%f", "%s", "%s", "%s", "%s", "%s", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f",
    "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%s", "%s", "%s",
    "%s", "%s", "%s"]

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
        collection_sale_amount = amount if (is_target and applied and (not ignore) and op["collection_sale"]) else 0
        staking_rewards_amount = amount if (is_target and applied and (not ignore) and op["staking"]) else 0
        prize_amount = amount if (is_target and applied and (not ignore) and op["prize"]) else 0
        buy_tez_amount = amount if (is_target and applied and (not ignore) and op["buy_tez"]) else 0
        received_amount_others = amount if (is_target and applied and (not ignore) and (not (op["art_sale"] or op["collection_sale"] or op["staking"] or op["prize"] or op["buy_tez"]))) else 0
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
            aliases.get(op["sender"], op["sender"]).replace(",", " "),
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
            op["collection_sale"],
            op["staking"],
            op["origination"],
            op["reveal"],
            op["delegation"],
            op["prize"],
            op["donation"],
            op["buy_tez"],
            op["sell_tez"],
            amount,
            fees,
            received_amount,
            art_sale_amount,
            collection_sale_amount,
            staking_rewards_amount,
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
