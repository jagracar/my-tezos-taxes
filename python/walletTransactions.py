from taxUtils import *

# Define the user wallets
user_wallets = {
    "tz1g6JRCpsEnD2BLiAzPNK3GBD1fKicV9rCx": "my main wallet",
    "tz1abTpHKkdo5YTM1DosZZVx9p8cjv4hMMTB": "my ledger wallet",
    "tz2AXFKh7Bf5rXFGHcrdPf83HfhJ72VUuiMq": "my twitter wallet"}

# Define the user bakers
baker_wallets = {
    "tz1Ywgcavxq9D6hL32Q2AQWHAux9MrWqGoZC": "StakeNow Payouts"}

# Define the timestamp range
timestamp_range = ["2021-01-01T00:00:00Z", "2021-12-31T23:59:59Z"]

# Define the transactions that should not be considered in the tax calculations
transactions_to_ignore = [
    "oo38nLvd5qnabN4fK2N49aWPrnK3JmA8cb6BFfNyzgmZzTaS5jM",  # Buy 1/1 Z.Lieberman
    "onzPve3arjH4rq3neaRsgMbbVBhSRgiSpUtj5eUaYGBaPMKrPg2"]  # Return 1/1 Z.Lieberman

# Define the most known tokens
token = {
    # Tokens
    "OBJKT": "KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton",
    "Tezzardz": "KT1LHHLso8zQWQWg1HUukajdxxbkGfNoHjh6",
    "GOGOs": "KT1SyPgtiXTaEfBuMZKviWGNHqVrBBEjvtfQ",
    "NEONZ": "KT1MsdyBSAMQwzvDH4jt2mxUKJvBSWZuPoRJ",
    "Skeles": "KT1HZVd9Cjc2CMe3sQvXgbxhpJkdena21pih",
    "VesselsGen0": "KT1BfKnSKV6Wx45Cv4yjEYXViwuhmswby8Hp",
    "GENTK v1": "KT1KEa8z6vWXDJrVqtMrAeDVzsvxat3kHaCE",
    "GENTK v2": "KT1U6EHmNxJTkvaWJ4ThczG4FSDaHC21ssvi",
    "ITEM": "KT1LjmAdYQCLBjwv4S2oFkEzyHVkomAf5MrW",
    "tz1and Place token": "KT1G6bH9NVDp8tSSz7FzDUnCgbJwQikxtUog",
    "tz1and Item token": "KT1TKFWDiMk35c5n94TMmLaYksdXkHuaL112",
    "8bidou 24x24 token": "KT1TR1ErEQPTdtaJ7hbvKTJSa1tsGnHGZTpf",
    "contter token": "KT1J1bx1ynm3UVgT7ymBPCDEtNEYjoMPcsQg",
    "typed token": "KT1J6NY5AU61GzUX51n59wwiZcGJ9DrNTwbK",
    "8scribo token": "KT1Aq1umaV8gcDQmi4CLDk7KeKpoUjFQeg1B",
    "Hash Three Points token": "KT1Fxz4V3LaUcVFpvF8pAAx8G3Z4H7p7hhDg",
    "25FPS token": "KT1Do66uucsbGELYV1sbLwBttCc5Gu6NrKmo",
    "hDAO": "KT1AFA2mwNUMNd4SsujE1YYp29vd8BZejyKW",
    "MATH": "KT18hYjnko76SBVv6TaCT4kU6B32mJk6JWLZ",
    "Materia": "KT1KRvNVubq64ttPbQarxec5XdS6ZQU4DVD2"}
token_wallets = {address: name for name, address in token.items()}

# Define the most known smart contracts
sc = {
    # Token minters
    "Tezzardz minter": "KT1DdxmJujm3u2ZNkYwV24qLBJ6iR7sc58B9",
    "GOGOs minter": "KT1CExkW5WoKqoiv5An6uaZzN6i2Q3mxcqpW",
    "NEONZ minter": "KT1QMAN7pWrR7fdiiMZ8mtVMMeFw2nADcVAH",
    "Skeles minter": "KT1AvxTNETj3U4b3wKYxkX6CKya1EgLZezv8",
    "VesselsGen0 minter": "KT1U1GDQDE7C9DNfE9iSojsKfWf5zUXdSVde",
    "FXHASH minter v1": "KT1AEVuykWeuuFX7QkEAMNtffzwhe1Z98hJS",
    "FXHASH minter v2": "KT1XCoGnfupWk7Sp8536EfrxcP73LmT68Nyr",
    "FXHASH minter v3": "KT1BJC12dG17CVvPKJ1VYaNnaT5mzfnUTwXv",
    "25FPS minter": "KT1Q2jUJnrvrrhi4gBpZVLm37nyCqaFNtK7X",
    # Marketplaces
    "h=n marketplace v1": "KT1Hkg5qeNhfwpKW4fXvq7HGZB9z2EnmCCA9",
    "h=n marketplace v2": "KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn",
    "teia marketplace prototype 1": "KT1VYEphkUaRgSqiEePADXEV6B9fxraWQETk",
    "teia marketplace prototype 2": "KT1DEcMs5t5SNKE3oVRk3MwGRrswuDaWJ6nq",
    "teia marketplace": "KT1PHubm9HtyQEJ4BBpMTVomq6mhbfNZ9z5w",
    "objkt.com marketplace v1": "KT1FvqJwEDWb1Gwc55Jd1jjTHRVWbYKUUpyq",
    "objkt.com marketplace v2": "KT1WvzYHCNBvDSdwafTHv7nJ1dWmZ8GCYuuC",
    "FXHASH marketplace v1": "KT1Xo5B7PNBAeynZPmca4bRh6LQow4og1Zb9",
    "FXHASH marketplace v2": "KT1GbyoDi7H1sfXmimXpptZJuCdHMh66WS9u",
    "versum marketplace": "KT1GyRAJNdizF1nojQz62uGYkx8WFRUJm9X5",
    "8bidou marketplace": "KT1AHBvSo828QwscsjDjeUuep7MgApi8hXqA",
    "contter marketplace I": "KT1WBmegTu1CJi4Q9ZNQT47gtbuqVjwmUUQZ",
    "contter marketplace II": "KT1SEKxDMTNRpQnb5o2pyiYBKyrH9a8FiB4k",
    "typed marketplace": "KT1VoZeuBMJF6vxtLqEFMoc4no5VDG789D7z",
    "8scribo marketplace": "KT19vw7kh7dzTRxFUZNWu39773baauzNWtzj",
    "Barter marketplace": "KT1XtJ6k51y7HpLFLTNv2wBYFhfVMZ6ow3Sz",
    # Other
    "h=n name registry": "KT1My1wDZHDGweCrJnQJi3wcFaS67iksirvj",
    "FXHASH name registry": "KT1Ezht4PDKZri7aVppVGT4Jkw39sesaFnww",
    "versum registry": "KT1NUrzs7tiT4VbNPqeTxgAFa4SXeV1f3xe9",
    "contter registry": "KT1Hv7keNNq3KEhbr6fWQZvJq93mSmYF9zSf",
    "h=n OBJKT-hDAO curation": "KT1TybhR7XraG75JFYKSrh7KnxukMBT5dor6",
    "Tezos Domains TLDRegistrar": "KT1Mqx5meQbhufngJnUAGEGpa4ZRxhPSiCgB",
    "Tezos Domains registrar": "KT1EVYBj3f1rZHNeUtq4ZvVxPTs77wuHwARU",
    "Tezos Domains TLDRegistrar Commit": "KT1P8n2qzJjwMPbHJfi4o8xu6Pe3gaU3u2A3",
    "Tezos Domains TLDRegistrar Buy": "KT191reDVKrLxU9rjTSxg53wRqj6zh8pnHgr",
    "Tezos Domains NameRegistry": "KT1GBZmSxmnKJXGMdMLbugPfLyUPmuLSMwKS",
    "Tezos Domains NameRegistry ClaimReverseRecord": "KT1TnTr6b2YxSx2xUQ8Vz3MoWy771ta66yGx",
    "Tezos Domains NameRegistry UpdateRecord": "KT1H1MqmUM4aK9i1833EBmYCCEfkbt6ZdSBc",
    "teia multisig": "KT1PKBTVmdxfgkFvSeNUQacYiEFsPBw16B4P",
    "teia multisig prototype 1": "KT1Cecn3A2A4i9EmSqug45iyzUUQc4F7C9yM",
    "teia multisig prototype 2": "KT1QmSmQ8Mj8JHNKKQmepFqQZy7kDWQ1ek69",
    "teia multisig prototype 3": "KT1RtYAfoiFNkgZxQJmkSAEyQitfEQHyX3Cb",
    "teia multisig prototype 4": "KT1BVekM6Y4ykN2uEW9FFxuZ4nY8QuY19Pb6",
    "teia vote": "KT1FtGBdmmzxeV1cbGP2v7RYWtwm27s9zfEa",
    "tz1and auctions": "KT1WmMn55RjXwk5Xb4YE6asjy5BvMiEsB6nA",
    "tz1and world": "KT1EuSjJgQRGXM18TEu1WaMRyshPSkSCg11n",
    "Breadfond 1": "KT1AyAhwyjwmbZKVdDnZNcQDgprXpCpmSNFu",
    "Breadfond 2": "KT1XRu5sjuBxiFbaPeUkPUGy8zJmPEbuxaFx",
    "Breadfond 3": "KT1Bgz17GRSkoNN1WfRka24VZm5ffXMep67G",
    "Interactive experiment 1": "KT1CiUSxDpfAeuCYubpZ75v6RFvGHwVBajDt",
    "Interactive experiment 2": "KT1JP5Zobg2ymQUtqNrAqDMUAUUPnar9UbV4",
    "my tzprofile contract 1": "KT1C3ygBBp9Y6sBpFHuqw4PABC1wuABmUy1t",
    "my tzprofile contract 2": "KT1DCrMtizELFpUviaX4KoNKJkN2uJ7t6oHM"}
sc_wallets = {address: name for name, address in sc.items()}

# Get the list of FA2 contracts associated to the objkt.com collections
objktcom_collections = get_objktcom_collections()

# Combine all the wallets aliases
wallets = {}
wallets.update(user_wallets)
wallets.update(baker_wallets)
wallets.update(token_wallets)
wallets.update(sc_wallets)
wallets.update({"tz1burnburnburnburnburnburnburjAYjjX": "Burn address"})

# Get the user mints, collects, art sales and collection sales
user_mints = get_user_mints(user_wallets)
user_collects = get_user_collects(user_wallets)
user_art_sales = get_user_art_sales(user_wallets)
user_collection_sales = get_user_collection_sales(user_wallets)

# Get the user raw transactions information
raw_transactions = get_user_transactions(user_wallets, timestamp_range)

# Process the transactions
transactions = []

for i, t in enumerate(raw_transactions): 
    # Get the operation hash
    hash = t["hash"]

    # Save the most relevant information
    transaction = {
        "counter": i,
        "timestamp": t["timestamp"],
        "hash": hash,
        "initiator": t["initiator"]["address"] if "initiator" in t else None,
        "sender": t["sender"]["address"],
        "target": t["target"]["address"],
        "entrypoint": t["parameter"]["entrypoint"] if "parameter" in t else None,
        "parameters": t["parameter"]["value"] if "parameter" in t else None,
        "amount": t["amount"] / 1e6,
        "fees": (t["bakerFee"] + t["storageFee"] + t["allocationFee"]) / 1e6,
        "exchange": t["quote"]["eur"]}

    # Calculate the transaction amount and fees in euros
    transaction["amount_in_euros"] = transaction["amount"] * transaction["exchange"]
    transaction["fees_in_euros"] = transaction["fees"] * transaction["exchange"]

    # Check if it's an internal transaction between the user wallets
    transaction["internal"] = (
        ((transaction["sender"] in user_wallets) and (transaction["target"] in user_wallets)) or
        ((transaction["initiator"] in user_wallets) and (transaction["target"] in user_wallets)))

    # Check if the transaction should be ignored from the calculations
    transaction["ignore"] = hash in transactions_to_ignore or transaction["internal"]

    # Add the information from the know user transactions
    transaction["kind"] = None
    transaction["mint"] = None
    transaction["collect"] = None
    transaction["art_sale"] = None
    transaction["collection_sale"] = None
    transaction["token_id"] = None
    transaction["token_address"] = None

    if hash in user_mints:
        mint = user_mints[hash]
        transaction["mint"] = True
        transaction["collect"] = False
        transaction["art_sale"] = False
        transaction["collection_sale"] = False
        transaction["token_id"] = mint["token"]["token_id"]
        transaction["token_address"] = mint["token"]["fa2_address"]

    if hash in user_collects:
        collect = user_collects[hash]
        transaction["mint"] = False
        transaction["collect"] = collect["implements"] == "SALE" or collect["offer_fulfilled"]
        transaction["art_sale"] = False
        transaction["collection_sale"] = False
        transaction["token_id"] = collect["token"]["token_id"]
        transaction["token_address"] = collect["token"]["fa2_address"]

        # Ignore transactions associated to offers that were not fulfilled
        if collect["offer_id"] is not None or collect["bid_id"] is not None:
            if not collect["offer_fulfilled"]:
                transaction["ignore"] = True

    if hash in user_art_sales:
        sale = user_art_sales[hash]
        transaction["mint"] = False
        transaction["collect"] = False
        transaction["art_sale"] = sale["implements"] == "SALE"
        transaction["collection_sale"] = False
        transaction["token_id"] = sale["token"]["token_id"]
        transaction["token_address"] = sale["token"]["fa2_address"]

    if hash in user_collection_sales:
        sale = user_collection_sales[hash]
        transaction["mint"] = False
        transaction["collect"] = False
        transaction["art_sale"] = False
        transaction["collection_sale"] = sale["implements"] == "SALE"
        transaction["token_id"] = sale["token"]["token_id"]
        transaction["token_address"] = sale["token"]["fa2_address"]

    # Check if it is a simple tez transaction
    if transaction["entrypoint"] is None and transaction["amount"] > 0:
        if transaction["internal"]:
            transaction["kind"] = "internal tez transfer"
        elif transaction["sender"] in user_wallets:
            transaction["kind"] = "send tez"
        elif transaction["target"] in user_wallets:
            if transaction["sender"] in baker_wallets:
                transaction["kind"] = "receive tez from staking"
            else:
                transaction["kind"] = "receive tez"
        else:
            transaction["kind"] = "secondary tez transfer"

    # Check if the transaction is connected with a mint
    if transaction["entrypoint"] == "mint_OBJKT":
        transaction["kind"] = "h=n mint"
        transaction["mint"] = True
        transaction["token_address"] = token["OBJKT"]
    elif transaction["entrypoint"] == "mint_haiku":
        transaction["kind"] = "8scribo mint"
        transaction["mint"] = True
        transaction["token_address"] = token["8scribo token"]
    elif transaction["entrypoint"] == "mint_token":
        if transaction["target"] == sc["contter marketplace II"]:
            transaction["kind"] = "contter mint"
            transaction["mint"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["contter token"]
    elif transaction["entrypoint"] == "default":
        if transaction["target"] == sc["25FPS minter"]:
            transaction["kind"] = "25FPS mint"
            transaction["collect"] = True
            transaction["token_address"] = token["25FPS token"]
    elif transaction["entrypoint"] == "mint":
        if transaction["target"] == token["OBJKT"]:
            transaction["kind"] = "h=n mint"
            transaction["mint"] = True
            transaction["token_address"] = token["OBJKT"]
        elif transaction["target"] == token["contter token"]:
            transaction["kind"] = "contter mint"
            transaction["mint"] = True
            transaction["token_address"] = token["contter token"]
        elif transaction["target"] == sc["GOGOs minter"]:
            transaction["kind"] = "GOGOs mint"
            transaction["collect"] = True
            transaction["token_address"] = token["GOGOs"]
        elif transaction["target"] == token["GOGOs"]:
            transaction["kind"] = "GOGOs mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["GOGOs"]
        elif transaction["target"] == sc["NEONZ minter"]:
            transaction["kind"] = "NEONZ mint"
            transaction["collect"] = True
            transaction["token_address"] = token["NEONZ"]
        elif transaction["target"] == token["NEONZ"]:
            transaction["kind"] = "NEONZ mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["NEONZ"]
        elif transaction["target"] == token["Hash Three Points token"]:
            transaction["kind"] = "Hash Three Points mint"
            transaction["collect"] = True
            transaction["token_address"] = token["Hash Three Points token"]
        elif transaction["target"] == sc["FXHASH minter v1"]:
            transaction["kind"] = "FXHASH mint"
            transaction["collect"] = True
            transaction["token_address"] = token["GENTK v1"]
        elif transaction["target"] == sc["FXHASH minter v2"]:
            transaction["kind"] = "FXHASH mint"
            transaction["collect"] = True
            transaction["token_address"] = token["GENTK v1"]
        elif transaction["target"] == sc["FXHASH minter v3"]:
            transaction["kind"] = "FXHASH mint"
            transaction["collect"] = True
            transaction["token_address"] = token["GENTK v2"]
        elif transaction["target"] == token["GENTK v1"]:
            transaction["kind"] = "FXHASH mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["GENTK v1"]
        elif transaction["target"] == token["GENTK v2"]:
            transaction["kind"] = "FXHASH mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["GENTK v2"]
        elif transaction["target"] == sc["VesselsGen0 minter"]:
            transaction["kind"] = "VesselsGen0 mint"
            transaction["collect"] = True
            transaction["token_address"] = token["VesselsGen0"]
        elif transaction["target"] == token["VesselsGen0"]:
            transaction["kind"] = "VesselsGen0 mint"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["VesselsGen0"]
    elif transaction["entrypoint"] == "hDAO_batch":
        transaction["kind"] = "hDAO mint"
        transaction["collect"] = True
        transaction["token_id"] = 0
        transaction["token_address"] = token["hDAO"]
    elif transaction["entrypoint"] == "claim_materia":
        transaction["kind"] = "Materia mint"
        transaction["collect"] = True
        transaction["token_id"] = 0
        transaction["token_address"] = token["Materia"]
    elif (transaction["entrypoint"] == "buy") and (transaction["target"] == sc["Skeles minter"]):
        transaction["kind"] = "Skeles mint"
        transaction["collect"] = True
        transaction["token_address"] = token["Skeles"]

    # Check if the transaction is connected with a token transfer
    if transaction["entrypoint"] == "transfer":
        if transaction["target"] in token_wallets:
            transaction["token_id"] = transaction["parameters"][0]["txs"][0]["token_id"]
            transaction["token_address"] = transaction["target"]

            if transaction["parameters"][0]["from_"] in user_wallets:
                transaction["kind"] = "send " + token_wallets[transaction["target"]]
            else:
                transaction["kind"] = "receive " + token_wallets[transaction["target"]]
        elif transaction["target"] in objktcom_collections:
            transaction["token_id"] = transaction["parameters"][0]["txs"][0]["token_id"]
            transaction["token_address"] = transaction["target"]

            if transaction["parameters"][0]["from_"] in user_wallets:
                transaction["kind"] = "send objkt.com collection token"
            else:
                transaction["kind"] = "receive objkt.com collection token"

    # Check if the transaction is connected with a token update operator
    if transaction["entrypoint"] == "update_operators":
        if transaction["target"] in token_wallets:
            transaction["kind"] = "update %s operators" % token_wallets[transaction["target"]]
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
        elif transaction["target"] in objktcom_collections:
            transaction["kind"] = "update objkt.com collection operators"
            transaction["token_address"] = transaction["target"]

            if "add_operator" in transaction["parameters"][0]:
                transaction["token_id"] = transaction["parameters"][0]["add_operator"]["token_id"]
            else:
                transaction["token_id"] = transaction["parameters"][0]["remove_operator"]["token_id"]
    elif transaction["entrypoint"] == "add_adhoc_operators":
        if transaction["target"] in token_wallets:
            transaction["kind"] = "update %s adhoc operators" % token_wallets[transaction["target"]]
            transaction["token_id"] = transaction["parameters"][0]["token_id"]
            transaction["token_address"] = transaction["target"]

    # Check if the transaction is connected with hDAO curation in h=n
    if transaction["entrypoint"] == "curate":
        if transaction["target"] in [sc["h=n marketplace v1"], sc["h=n OBJKT-hDAO curation"]]:
            transaction["kind"] = "curate OBJKT using hDAO"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = token["OBJKT"]
    elif transaction["entrypoint"] == "claim_hDAO":
        if transaction["target"] == sc["h=n OBJKT-hDAO curation"]:
            transaction["kind"] = "claim hDAO from curation"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = token["OBJKT"]

    # Check if the transaction is connected with swaps
    if transaction["entrypoint"] == "swap":
        if transaction["target"] in [sc["h=n marketplace v1"], sc["h=n marketplace v2"]]:
            transaction["kind"] = "h=n swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = token["OBJKT"]
        elif transaction["target"] == sc["teia marketplace"]:
            transaction["kind"] = "teia swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] == sc["8scribo marketplace"]:
            transaction["kind"] = "8scribo swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = transaction["parameters"]["fa2"]
    elif transaction["entrypoint"] == "cancel_swap":
        if transaction["target"] in [sc["h=n marketplace v1"], sc["h=n marketplace v2"]]:
            transaction["kind"] = "h=n cancel swap"
        elif transaction["target"] == sc["teia marketplace"]:
            transaction["kind"] = "teia cancel swap"
        elif transaction["target"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype cancel swap"
        elif transaction["target"] == sc["8scribo marketplace"]:
            transaction["kind"] = "8scribo cancel swap"
    elif transaction["entrypoint"] == "ask":
        if transaction["target"] == sc["objkt.com marketplace v1"]:
            transaction["kind"] = "objkt.com swap"
            transaction["token_id"] = transaction["parameters"]["objkt_id"]
            transaction["token_address"] = transaction["parameters"]["fa2"]
        elif transaction["target"] == sc["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com swap"
            transaction["token_id"] = transaction["parameters"]["token"]["token_id"]
            transaction["token_address"] = transaction["parameters"]["token"]["address"]
    elif transaction["entrypoint"] == "retract_ask":
        if transaction["target"] in [sc["objkt.com marketplace v1"], sc["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com cancel swap"
    elif transaction["entrypoint"] == "listing":
        if transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH swap"
            transaction["token_id"] = transaction["parameters"]["gentk"]["id"]
            transaction["token_address"] = token["GENTK v1"] if transaction["parameters"]["gentk"]["id"] == "0" else token["GENTK v2"]
    elif transaction["entrypoint"] == "listing_cancel":
        if transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH cancel swap"
                
    # Check if the transaction is connected with bid or offers
    if transaction["entrypoint"] == "bid":
        if transaction["target"] == sc["objkt.com marketplace v1"]:
            transaction["kind"] = "objkt.com offer"
    elif transaction["entrypoint"] == "retract_bid":
        if transaction["target"] == sc["objkt.com marketplace v1"]:
            transaction["kind"] = "objkt.com cancel offer"
    elif transaction["entrypoint"] == "fulfill_bid":
        if transaction["target"] == sc["objkt.com marketplace v1"]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] == "offer":
        if transaction["target"] == sc["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com offer"
        elif transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH offer"
    elif transaction["entrypoint"] == "retract_offer":
        if transaction["target"] == sc["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com cancel offer"
    elif transaction["entrypoint"] == "offer_cancel":
        if transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH cancel offer"
    elif transaction["entrypoint"] == "fulfill_offer":
        if transaction["target"] == sc["objkt.com marketplace v2"]:
            transaction["kind"] = "objkt.com accept offer"
    elif transaction["entrypoint"] == "offer_accept":
        if transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH accept offer"

    # Check if the transaction is connected with collects
    if transaction["entrypoint"] == "collect":
        if transaction["target"] in [sc["h=n marketplace v1"], sc["h=n marketplace v2"]]:
            transaction["kind"] = "h=n collect"
            transaction["collect"] = True
        elif transaction["target"] == sc["teia marketplace"]:
            transaction["kind"] = "teia collect"
            transaction["collect"] = True
        elif transaction["target"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype collect prototype"
            transaction["collect"] = True
        elif transaction["target"] == sc["FXHASH marketplace v1"]:
            transaction["kind"] = "FXHASH collect"
            transaction["collect"] = True
        elif transaction["target"] == sc["contter marketplace I"]:
            transaction["kind"] = "contter collect"
            transaction["collect"] = True
            transaction["token_address"] = token["contter token"]
        elif transaction["target"] == sc["contter marketplace II"]:
            transaction["kind"] = "contter collect"
            transaction["collect"] = True
            transaction["token_id"] = transaction["parameters"]["token_id"]
            transaction["token_address"] = token["contter token"]
        elif transaction["target"] == sc["typed marketplace"]:
            transaction["kind"] = "typed collect"
            transaction["collect"] = True
        elif transaction["target"] == sc["8scribo marketplace"]:
            transaction["kind"] = "8scribo collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "fulfill_ask":
        if transaction["target"] in [sc["objkt.com marketplace v1"], sc["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "listing_accept":
        if transaction["target"] == sc["FXHASH marketplace v2"]:
            transaction["kind"] = "FXHASH collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "collect_swap":
        if transaction["target"] == sc["versum marketplace"]:
            transaction["kind"] = "versum collect"
            transaction["collect"] = True
    elif transaction["entrypoint"] == "get_item":
        if transaction["target"] == sc["tz1and world"]:
            transaction["kind"] = "tz1and collect"
            transaction["collect"] = True
            transaction["token_address"] = token["tz1and Item token"]
    elif transaction["entrypoint"] == "bid":
        if transaction["target"] == sc["tz1and auctions"]:
            transaction["kind"] = "tz1and collect"
            transaction["collect"] = True
            transaction["token_address"] = token["tz1and Place token"]
    elif transaction["entrypoint"] == "buy":
        if transaction["target"] == sc["8bidou marketplace"]:
            transaction["kind"] = "8bidou collect"
            transaction["collect"] = True

    # Check if the transaction is connected with sells
    if (transaction["entrypoint"] is None) and (not transaction["internal"]) and (transaction["target"] in user_wallets):
        if transaction["sender"] in [sc["h=n marketplace v1"], sc["h=n marketplace v2"]]:
            transaction["kind"] = "h=n sell"
        elif transaction["sender"] == sc["teia marketplace"]:
            transaction["kind"] = "teia sell"
        elif transaction["sender"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype sell"
        elif transaction["sender"] in [sc["objkt.com marketplace v1"], sc["objkt.com marketplace v2"]]:
            transaction["kind"] = "objkt.com sell"
        elif transaction["sender"] in [sc["FXHASH marketplace v1"], sc["FXHASH marketplace v2"]]:
            transaction["kind"] = "FXHASH sell"
        elif transaction["sender"] == sc["versum marketplace"]:
            transaction["kind"] = "versum sell"
        elif transaction["sender"] == sc["8bidou marketplace"]:
            transaction["kind"] = "8bidou sell"
        elif transaction["sender"] == sc["contter marketplace II"]:
            transaction["kind"] = "contter sell"
        elif transaction["sender"] == sc["typed marketplace"]:
            transaction["kind"] = "typed sell"
        elif transaction["sender"] == sc["8scribo marketplace"]:
            transaction["kind"] = "8scribo sell"
        elif transaction["sender"] in [sc["Breadfond 1"], sc["Breadfond 2"], sc["Breadfond 3"]]:
            transaction["kind"] = "Breadfond share in tez"

    # Check if the transaction is connected with user registry information
    if transaction["entrypoint"] == "registry":
        if transaction["target"] == sc["h=n name registry"]:
            transaction["kind"] = "update h=n registry"
    elif transaction["entrypoint"] == "update_profile":
        if transaction["target"] == sc["FXHASH name registry"]:
            transaction["kind"] = "update FXHASH registry"
    elif transaction["entrypoint"] == "claim_verification":
        if transaction["target"] == sc["versum registry"]:
            transaction["kind"] = "update versum registry"
    elif transaction["entrypoint"] == "update":
        if transaction["target"] == sc["contter registry"]:
            transaction["kind"] = "update contter registry"

    # Other kind of calls
    if transaction["entrypoint"] == "update_fee_recipient":
        if transaction["target"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype update fee"
    elif transaction["entrypoint"] == "set_pause":
        if transaction["target"] in [sc["teia marketplace prototype 1"], sc["teia marketplace prototype 2"]]:
            transaction["kind"] = "teia prototype set pause"

    if transaction["target"] == sc["Barter marketplace"]:
        transaction["kind"] = "Barter operation"

    if ((transaction["sender"] == sc["Tezos Domains TLDRegistrar"]) or
        (transaction["target"] == sc["Tezos Domains TLDRegistrar"]) or
        (transaction["sender"] == sc["Tezos Domains registrar"]) or
        (transaction["target"] == sc["Tezos Domains registrar"]) or
        (transaction["sender"] == sc["Tezos Domains TLDRegistrar Commit"]) or
        (transaction["target"] == sc["Tezos Domains TLDRegistrar Commit"]) or
        (transaction["sender"] == sc["Tezos Domains TLDRegistrar Buy"]) or
        (transaction["target"] == sc["Tezos Domains TLDRegistrar Buy"]) or
        (transaction["sender"] == sc["Tezos Domains NameRegistry"]) or
        (transaction["target"] == sc["Tezos Domains NameRegistry"]) or
        (transaction["sender"] == sc["Tezos Domains NameRegistry ClaimReverseRecord"]) or
        (transaction["target"] == sc["Tezos Domains NameRegistry ClaimReverseRecord"]) or
        (transaction["sender"] == sc["Tezos Domains NameRegistry UpdateRecord"]) or
        (transaction["target"] == sc["Tezos Domains NameRegistry UpdateRecord"])):
        transaction["kind"] = "tezos domains operation"

    if ((transaction["target"] == sc["teia multisig"]) or
        (transaction["sender"] == sc["teia multisig"]) or
        (transaction["target"] == sc["teia multisig prototype 1"]) or 
        (transaction["sender"] == sc["teia multisig prototype 1"]) or 
        (transaction["target"] == sc["teia multisig prototype 2"]) or 
        (transaction["sender"] == sc["teia multisig prototype 2"]) or 
        (transaction["target"] == sc["teia multisig prototype 3"]) or 
        (transaction["sender"] == sc["teia multisig prototype 3"]) or
        (transaction["target"] == sc["teia multisig prototype 4"]) or 
        (transaction["sender"] == sc["teia multisig prototype 4"])):
        transaction["kind"] = "Multisig operation"

    if ((transaction["target"] == sc["Interactive experiment 1"]) or
        (transaction["target"] == sc["Interactive experiment 2"])):
        transaction["kind"] = "Interactive experiment operation"

    if transaction["target"] == sc["teia vote"]:
        transaction["kind"] = "teia vote"

    if transaction["target"] == sc["tz1and world"]:
        if transaction["entrypoint"] != "get_item":
            transaction["kind"] = "tz1and operation"

    if transaction["entrypoint"] == "pay_royalties_xtz":
        if transaction["target"] == token["ITEM"]:
            transaction["kind"] = "versum operation"

    if transaction["entrypoint"] == "batch_fwd_xtz":
        if transaction["sender"] == token["ITEM"]:
            transaction["kind"] = "versum operation"

    if transaction["entrypoint"] == "check":
        if transaction["sender"] == token["contter token"]:
            transaction["kind"] = "contter operation"

    if transaction["entrypoint"] == "default":
        if transaction["target"] in [sc["my tzprofile contract 1"], sc["my tzprofile contract 2"]]:
            transaction["kind"] = "tzprofile operation"

    # Add the processed transaction
    transactions.append(transaction)

# Save the processed data in a csv file
file_name = "../data/%s_processed_trasactions.csv" % list(user_wallets.keys())[0]
columns = [
    "timestamp", "initiator", "sender", "target", "kind", "mint", "collect",
    "art_sale", "collection_sale", "internal", "ignore", "amount", "fees",
    "tez_to_euros", "token_id", "token_address", "entrypoint", "hash"]
format = [
    "%s", "%s", "%s", "%s", "%s", "%r", "%r", "%r", "%r", "%r", "%r", "%f",
    "%f", "%f", "%s", "%s", "%s", "%s"]

with open(file_name, "w") as file:
    # Write the header
    file.write(",".join(columns) + "\n")

    # Loop over the transactions
    for t in transactions:
        # Write the transaction data in the output file
        data = (
            t["timestamp"],
            wallets.get(t["initiator"], t["initiator"]) if t["initiator"] is not None else "",
            wallets.get(t["sender"], t["sender"]),
            wallets.get(t["target"], t["target"]),
            t["kind"],
            t["mint"] if t["mint"] is not None else False,
            t["collect"] if t["collect"] is not None else False,
            t["art_sale"] if t["art_sale"] is not None else False,
            t["collection_sale"] if t["collection_sale"] is not None else False,
            t["internal"],
            t["ignore"],
            t["amount"],
            t["fees"],
            t["exchange"],
            t["token_id"] if t["token_id"] is not None else "",
            t["token_address"] if t["token_address"] is not None else "",
            t["entrypoint"] if t["entrypoint"] is not None else "",
            t["hash"])
        text = ",".join(format) % data
        file.write(text + "\n")
