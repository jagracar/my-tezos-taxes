import json
import requests
import pandas as pd

# Trick to be able to print the complete transaction hashes on the console
pd.options.display.max_colwidth = 60

# The main tezos FA2 tokens
TOKENS = {
    "OBJKT": "KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton",
    "Tezzardz": "KT1LHHLso8zQWQWg1HUukajdxxbkGfNoHjh6",
    "GOGOs": "KT1SyPgtiXTaEfBuMZKviWGNHqVrBBEjvtfQ",
    "GOGOs Inventory Item": "KT1Xf44LpwrA7oBcB3VwWTtUBP1eNRaNnWeh",
    "NEONZ": "KT1MsdyBSAMQwzvDH4jt2mxUKJvBSWZuPoRJ",
    "Skeles": "KT1HZVd9Cjc2CMe3sQvXgbxhpJkdena21pih",
    "VesselsGen0": "KT1BfKnSKV6Wx45Cv4yjEYXViwuhmswby8Hp",
    "GENTK v1": "KT1KEa8z6vWXDJrVqtMrAeDVzsvxat3kHaCE",
    "GENTK v2": "KT1U6EHmNxJTkvaWJ4ThczG4FSDaHC21ssvi",
    "ITEM": "KT1LjmAdYQCLBjwv4S2oFkEzyHVkomAf5MrW",
    "tz1and Place": "KT1G6bH9NVDp8tSSz7FzDUnCgbJwQikxtUog",
    "tz1and Item": "KT1TKFWDiMk35c5n94TMmLaYksdXkHuaL112",
    "8bidou 8x8 token": "KT1MxDwChiDwd6WBVs24g1NjERUoK622ZEFp",
    "8bidou 24x24 token": "KT1TR1ErEQPTdtaJ7hbvKTJSa1tsGnHGZTpf",
    "contter token": "KT1J1bx1ynm3UVgT7ymBPCDEtNEYjoMPcsQg",
    "typed token": "KT1J6NY5AU61GzUX51n59wwiZcGJ9DrNTwbK",
    "8scribo token": "KT1Aq1umaV8gcDQmi4CLDk7KeKpoUjFQeg1B",
    "Hash Three Points token": "KT1Fxz4V3LaUcVFpvF8pAAx8G3Z4H7p7hhDg",
    "25FPS token": "KT1Do66uucsbGELYV1sbLwBttCc5Gu6NrKmo",
    "hDAO": "KT1AFA2mwNUMNd4SsujE1YYp29vd8BZejyKW",
    "MATH": "KT18hYjnko76SBVv6TaCT4kU6B32mJk6JWLZ",
    "Materia": "KT1KRvNVubq64ttPbQarxec5XdS6ZQU4DVD2",
    "Tezos domain token": "KT1GBZmSxmnKJXGMdMLbugPfLyUPmuLSMwKS",
    "akaSwap token": "KT1AFq5XorPduoYyWxs5gEyrFK6fVjJVbtCj",
    "TezDAO": "KT1C9X9s5rpVJGxwVuHEVBLYEdAQ1Qw8QDjH",
    "PRJKTNEON": "KT1VbHpQmtkA3D4uEbbju26zS8C42M5AGNjZ",
    "PRJKTNEON FILES": "KT1H8sxNSgnkCeZsij4z76pkXu8BCZNvPZEx",
    "TezoTrooperz - Potions": "KT1W7hHwQeVkPN5yMSm1rPpmjwaHDPQMLMVa",
    "akaSwap token": "KT1AFq5XorPduoYyWxs5gEyrFK6fVjJVbtCj",
    "Art Cardz": "KT1LbLNTTPoLgpumACCBFJzBEHDiEUqNxz5C",
    "Ziggurats": "KT1PNcZQkJXMQ2Mg92HG1kyrcu3auFX5pfd8",
    "Rarible token": "KT18pVpRXKPY2c4U2yFEGSH3ZnhB2kL8kwXS",
    "Les Elefants Terribles token": "KT19BLv8px4VMLduVnYgahqFbsJ19FJXamUG",
    "The Moments token": "KT1CNHwTyjFrKnCstRoMftyFVwoNzF6Xxhpy"
}

# The main tezos tokens mint prices in tez
TOKENS_MINT_PRICE = {
    TOKENS["Tezzardz"]: 15,
    TOKENS["GOGOs"]: 15,
    TOKENS["NEONZ"]: 20,
    TOKENS["Skeles"]: 5,
    TOKENS["VesselsGen0"]: 15,
    TOKENS["Hash Three Points token"]: 5,
    TOKENS["25FPS token"]: 113
}

# The main tezos smart contracts
SMART_CONTRACTS = {
    # Token minters
    "Tezzardz minter": "KT1DdxmJujm3u2ZNkYwV24qLBJ6iR7sc58B9",
    "GOGOs minter": "KT1CExkW5WoKqoiv5An6uaZzN6i2Q3mxcqpW",
    "NEONZ minter": "KT1QMAN7pWrR7fdiiMZ8mtVMMeFw2nADcVAH",
    "Skeles minter": "KT1AvxTNETj3U4b3wKYxkX6CKya1EgLZezv8",
    "VesselsGen0 minter": "KT1U1GDQDE7C9DNfE9iSojsKfWf5zUXdSVde",
    "FXHASH minter v1": "KT1AEVuykWeuuFX7QkEAMNtffzwhe1Z98hJS",
    "FXHASH minter v2": "KT1XCoGnfupWk7Sp8536EfrxcP73LmT68Nyr",
    "FXHASH minter v3": "KT1BJC12dG17CVvPKJ1VYaNnaT5mzfnUTwXv",
    "typed minter": "KT1CK9RnWZGnejBeT6gJfgvf4p7f1NwhP9wS",
    "25FPS minter": "KT1Q2jUJnrvrrhi4gBpZVLm37nyCqaFNtK7X",
    # Marketplaces
    "h=n marketplace v1": "KT1Hkg5qeNhfwpKW4fXvq7HGZB9z2EnmCCA9",
    "h=n marketplace v2": "KT1HbQepzV1nVGg8QVznG7z4RcHseD5kwqBn",
    "teia marketplace prototype 1": "KT1VYEphkUaRgSqiEePADXEV6B9fxraWQETk",
    "teia marketplace prototype 2": "KT1DEcMs5t5SNKE3oVRk3MwGRrswuDaWJ6nq",
    "teia marketplace": "KT1PHubm9HtyQEJ4BBpMTVomq6mhbfNZ9z5w",
    "objkt.bid Legacy": "KT1Dno3sQZwR5wUCWxzaohwuJwG3gX1VWj1Z",
    "objkt.com marketplace v1": "KT1FvqJwEDWb1Gwc55Jd1jjTHRVWbYKUUpyq",
    "objkt.com marketplace v2": "KT1WvzYHCNBvDSdwafTHv7nJ1dWmZ8GCYuuC",
    "objkt.com English Auctions Old": "KT1Wvk8fon9SgNEPQKewoSL2ziGGuCQebqZc",
    "objkt.com English Auctions v1": "KT1XjcRq5MLAzMKQ3UHsrue2SeU2NbxUrzmU",
    "objkt.com English Auctions v2": "KT18p94vjkkHYY3nPmernmgVR7HdZFzE7NAk",
    "objkt.com Dutch Auctions v1": "KT1QJ71jypKGgyTNtXjkCAYJZNhCKWiHuT2r",
    "objkt.com Dutch Auctions v2": "KT1XXu88HkNzQRHNgAf7Mnq68LyS9MZJNoHP",
    "objkt.com Minting Factory": "KT1Aq4wWmVanpQhq4TTfjZXB5AjFpx15iQMM",
    "FXHASH marketplace v1": "KT1Xo5B7PNBAeynZPmca4bRh6LQow4og1Zb9",
    "FXHASH marketplace v2": "KT1GbyoDi7H1sfXmimXpptZJuCdHMh66WS9u",
    "versum marketplace": "KT1GyRAJNdizF1nojQz62uGYkx8WFRUJm9X5",
    "8bidou marketplace I": "KT1BvWGFENd4CXW5F3u4n31xKfJhmBGipoqF",
    "8bidou marketplace II": "KT1AHBvSo828QwscsjDjeUuep7MgApi8hXqA",
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
    "wXTZ objkt.com": "KT1TjnZYs5CGLbmV6yuW169P8Pnr9BiVwwjz",
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
    "Interactive experiment 3": "KT1Nih5GpH763Bov23KZYS1R1R3ZWgGaAVfw",
    "my tzprofile contract 1": "KT1C3ygBBp9Y6sBpFHuqw4PABC1wuABmUy1t",
    "my tzprofile contract 2": "KT1DCrMtizELFpUviaX4KoNKJkN2uJ7t6oHM",
    "TezID Store": "KT1RaNxxgmVRXpyu927rbBFq835pnQk6cfvM",
    "TezID Controller": "KT1KbV8dBrkFopgjcCc4qb2336fcGgTvRGRC",
    "Ukraine war donations contract": "KT1DWnLiUkNtAQDErXxudFEH63JC6mqg3HEx",
    "QuipuSwap hDAO old": "KT1Qm3urGqkRsWsovGzNb2R81c3dSfxpteHG",
    "QuipuSwap hDAO": "KT1QxLqukyfohPV5kPkw97Rs6cw1DDDvYgbB"
}


def read_json_file(file_name):
    """Reads a json file from disk.

    Parameters
    ----------
    file_name: str
        The complete path to the json file.

    Returns
    -------
    object
        The content of the json file.

    """
    with open(file_name, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def get_query_result(url, parameters=None, timeout=30):
    """Executes the given query and returns the result.

    Parameters
    ----------
    url: str
        The url to the server API.
    parameters: dict, optional
        The query parameters. Default is None.
    timeout: float, optional
        The query timeout in seconds. Default is 30 seconds.

    Returns
    -------
    object
        The query result.

    """
    response = requests.get(url=url, params=parameters, timeout=timeout)

    if response.status_code == requests.codes.ok:
        return response.json()

    return None


def get_graphql_query_result(url, query, timeout=30):
    """Executes the given GraphQL query and returns the result.

    Parameters
    ----------
    url: str
        The url to the GraphQL server API.
    query: dict
        The GraphQL query.
    timeout: float, optional
        The query timeout in seconds. Default is 30 seconds.

    Returns
    -------
    object
        The query result.

    """
    response = requests.post(url=url, data=json.dumps(query), timeout=timeout)

    if response.status_code == requests.codes.ok:
        return response.json()

    return None


def get_tzkt_query_result(url, parameters=None, timeout=30):
    """Executes the given tzkt query and returns the result.

    Parameters
    ----------
    url: str
        The url to the tzkt server API.
    parameters: dict, optional
        The query parameters. Default is None.
    timeout: float, optional
        The query timeout in seconds. Default is 30 seconds.

    Returns
    -------
    object
        The query result.

    """
    # Edit the provided query parameters
    parameters = {} if parameters is None else parameters.copy()
    parameters["limit"] = 10000

    # Iterate to get the complete query result
    result = []

    while True:
        parameters["offset"] = len(result)
        result += get_query_result(url, parameters, timeout)

        if len(result) != (parameters["offset"] + parameters["limit"]):
            break

    return result


def get_teztok_query_result(query, kind, timeout=30):
    """Executes the given teztok query and returns the result.

    Parameters
    ----------
    query: dict
        The GraphQL query.
    kind: str
        The kind of teztok query.
    timeout: float, optional
        The query timeout in seconds. Default is 30 seconds.

    Returns
    -------
    object
        The query result.

    """
    # Define url to the teztok GraphQL server API
    url = "https://api.teztok.com/v1/graphql"

    # Edit the provided query
    query = query.copy()
    limit = 10000
    query_string = query["query"].replace("**LIMIT**", str(limit))

    # Iterate to get the complete query result
    result = []

    while True:
        offset = len(result)
        edited_query = query.copy()
        edited_query["query"] = query_string.replace("**OFFSET**", str(offset)) 
        result += get_graphql_query_result(url, edited_query, timeout)["data"][kind]

        if len(result) != (offset + limit):
            break

    return result


def get_fa12_tokens():
    """Returns the complete list of tezos FA1.2 tokens.

    Returns
    -------
    list
        A python list with the tezos FA1.2 tokens.

    """
    url = "https://api.tzkt.io/v1/tokens"
    parameters = {
        "standard": "fa1.2",
        "tokenId": "0"}
    fa12_tokens = [entry["contract"] for entry in get_tzkt_query_result(url, parameters)]

    return {token["address"]: token["alias"] if "alias" in token else "FA1.2 token" for token in fa12_tokens}


def get_fa2_tokens():
    """Returns the complete list of tezos FA2 tokens.

    Returns
    -------
    list
        A python list with the tezos FA2 tokens.

    """
    url = "https://api.tzkt.io/v1/tokens"
    parameters = {"standard": "fa2",
                  "tokenId": "0"}
    fa2_tokens = [entry["contract"] for entry in get_tzkt_query_result(url, parameters)]

    return {token["address"]: token["alias"] if "alias" in token else "FA2 token" for token in fa2_tokens}


def get_objktcom_collections():
    """Returns the complete list of objkt.com collection addresses.

    Returns
    -------
    list
        A python list with the objkt.com collection addresses.

    """
    url = "https://api.tzkt.io/v1/bigmaps/24157/keys"
    parameters = {"select": "value"}
    objktcom_collections = get_tzkt_query_result(url, parameters)

    return [collection["contract"] for collection in objktcom_collections]


def get_user_transactions(user_wallets):
    """Returns the complete list of user transactions.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    list
        A python list with the user transactions.

    """
    url = "https://api.tzkt.io/v1/operations/transactions"
    parameters = {
        "anyof.initiator.sender.target.in": ",".join(user_wallets),
        "status": "applied",
        "quote": "eur,usd"}

    return get_tzkt_query_result(url, parameters)


def get_user_originations(user_wallets):
    """Returns the complete list of user contract originations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    list
        A python list with the user contract originations.

    """
    url = "https://api.tzkt.io/v1/operations/originations"
    parameters = {
        "anyof.initiator.sender.in": ",".join(user_wallets),
        "status": "applied",
        "quote": "eur,usd"}

    return get_tzkt_query_result(url, parameters)


def get_user_token_transfers(user_wallets):
    """Returns the complete list of token transfers associated to the user.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    list
        A python list with the token transfers associated to the user.

    """
    url = "https://api.tzkt.io/v1/tokens/transfers"
    parameters = {"anyof.from.to.in": ",".join(user_wallets)}

    return get_tzkt_query_result(url, parameters)


def get_user_historical_balance(user_wallets):
    """Returns the user historical tez balance.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with the user historical tez balance.

    """
    # Get the historical balance for each of the user wallets
    historical_balances = []

    for wallet in user_wallets:
        url = "https://api.tzkt.io/v1/accounts/%s/balance_history" % wallet
        parameters = {
            "step": 1,
            "quote": "eur,usd"}
        query_result = get_tzkt_query_result(url, parameters)
        historical_balances.append({item["level"]: item for item in query_result})

    # Get all the block levels for which we have some balance information
    levels = []

    for wallet_balances in historical_balances:
        levels += list(wallet_balances.keys())

    # Remove block level duplications and make sure they are sorted
    levels = list(set(levels))
    levels.sort()

    # Calculate the combined historical wallet balances
    combined_balances = [{"level": level, "timestamp": None, "balance": 0, "quote": None} for level in levels]

    for wallet_balances in historical_balances:
        previous_balance_amount = 0

        for balance in combined_balances:
            level = balance["level"]

            if level in wallet_balances:
                balance["timestamp"] = wallet_balances[level]["timestamp"]
                balance["quote"] = wallet_balances[level]["quote"]
                previous_balance_amount = wallet_balances[level]["balance"] / 1e6

            balance["balance"] += previous_balance_amount

    return combined_balances


def get_user_mints(user_wallets):
    """Returns the complete list of user mint operations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user mint operations information.

    """
    query = """
        query UserMints {
            events(where: {artist_address: {_in: ["%s"]}, type: {_like: "%%MINT%%", _nlike: "%%MINT_ISSUER%%"}, implements: {_is_null: true}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                timestamp
                ophash
                token_id
                editions
                fa2_address
            }
        }
    """ % '","'.join(user_wallets)
    mints = get_teztok_query_result({"query": query}, kind="events")

    return {mint["ophash"]: mint for mint in mints}


def get_user_swaps(user_wallets):
    """Returns the complete list of user swap operations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user swap operations information.

    """
    query = """
        query UserSwaps {
            events(where: {seller_address: {_in: ["%s"]}, implements: {_is_null: true}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                timestamp
                ophash
                ask_id
                auction_id
                bid_id
                offer_id
                swap_id
                token_id
                editions
                amount
                fa2_address
                price
            }
        }
    """ % ('","'.join(user_wallets))
    swaps = get_teztok_query_result({"query": query}, kind="events")

    return {swap["ophash"]: swap for swap in swaps}


def get_user_fulfilled_offers(user_wallets):
    """Returns the complete list of user fulfilled offers.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user fulfilled offers.

    """
    query = """
        query UserFulfilledOffers {
            offers(where: {buyer_address: {_in: ["%s"]}, status: {_eq: "fulfilled"}}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                offer_id
                bid_id
                token_id
                fa2_address
            }
        }
    """ % ('","'.join(user_wallets))
    fulfilled_offers = get_teztok_query_result({"query": query}, kind="offers")

    offers = {}

    for offer in fulfilled_offers:
        token_id = offer["token_id"]
        token_address = offer["fa2_address"]

        if token_address not in offers:
            offers[token_address] = {}

        if token_id not in offers[token_address]:
            offers[token_address][token_id] = []

        offers[token_address][token_id].append(
            offer["offer_id"] if offer["offer_id"] is not None else offer["bid_id"])

    return offers


def get_user_collects(user_wallets):
    """Returns the complete list of user collect operations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user collect operations information.

    """
    # Get the user collect operations
    query = """
        query UserCollects {
            events(where: {buyer_address: {_in: ["%s"]}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                timestamp
                ophash
                implements
                offer_id
                bid_id
                token_id
                editions
                amount
                fa2_address
                price
            }
        }
    """ % ('","'.join(user_wallets))
    collects = get_teztok_query_result({"query": query}, kind="events")

    # Get the fulfilled offers
    fulfilled_offers = get_user_fulfilled_offers(user_wallets)

    # Indicate which offers were fulfilled
    for collect in collects:
        offer_id = collect["offer_id"] if collect["offer_id"] is not None else collect["bid_id"]
        collect["offer_fulfilled"] = None

        if offer_id is not None:
            token_id = collect["token_id"]
            token_address = collect["fa2_address"]

            if token_address in fulfilled_offers and token_id in fulfilled_offers[token_address]:
                 collect["offer_fulfilled"] = offer_id in fulfilled_offers[token_address][token_id]

    return {collect["ophash"]: collect for collect in collects}


def get_user_won_auctions(user_wallets):
    """Returns the complete list of user won auction operations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user won auction operations information.

    """
    query = """
        query UserWonAuctions {
            events(where: {buyer_address: {_in: ["%s"]}, implements: {_eq: "SALE"}, auction_id: {_is_null: false}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                auction_id
                token_id
                fa2_address
            }
        }
    """ % ('","'.join(user_wallets))
    won_auctions = get_teztok_query_result({"query": query}, kind="events")

    auctions = {}

    for auction in won_auctions:
        token_id = auction["token_id"]
        token_address = auction["fa2_address"]

        if token_address not in auctions:
            auctions[token_address] = {}

        if token_id not in auctions[token_address]:
            auctions[token_address][token_id] = []

        auctions[token_address][token_id].append(auction["auction_id"])

    return auctions


def get_user_auction_bids(user_wallets):
    """Returns the complete list of user auction bid operations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user auction bid operations information.

    """
    # Get the user auction bid operations
    query = """
        query UserAuctionBids {
            events(where: {bidder_address: {_in: ["%s"]}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                timestamp
                ophash
                auction_id
                token_id
                fa2_address
                bid
            }
        }
    """ % ('","'.join(user_wallets))
    auction_bids = get_teztok_query_result({"query": query}, kind="events", timeout=60)

    # Get the won auctions
    won_auctions = get_user_won_auctions(user_wallets)

    # Indicate which auctions were won
    for bid in auction_bids:
        token_id = bid["token_id"]
        token_address = bid["fa2_address"]
        bid["won_auction"] = False

        if token_address in won_auctions and token_id in won_auctions[token_address]:
            bid["won_auction"] = bid["auction_id"] in won_auctions[token_address][token_id]

    return {bid["ophash"]: bid for bid in auction_bids}


def get_user_art_sales(user_wallets):
    """Returns the complete list of user sale operations for tokens that the
    user has minted.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user art sale operations information.

    """
    # Get the tokens that the user has minted
    mints = get_user_mints(user_wallets)
    minted_tokens = {}

    for mint in mints.values():
        token_address = mint["fa2_address"]

        if token_address not in minted_tokens:
            minted_tokens[token_address] = []

        minted_tokens[token_address].append(mint["token_id"])

    # Get the user art sales for each minted token
    art_sales = []

    for token_address, token_ids in minted_tokens.items():
        query = """
            query UserArtSales {
                events(where: {implements: {_eq: "SALE"}, fa2_address: {_eq: "%s"}, token_id: {_in: ["%s"]}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                    type
                    timestamp
                    ophash
                    token_id
                    amount
                    fa2_address
                    price
                }
            }
        """ % (token_address, '","'.join(token_ids))
        art_sales += get_teztok_query_result({"query": query}, kind="events")

    return {sale["ophash"]: sale for sale in art_sales}


def get_user_collection_sales(user_wallets):
    """Returns the complete list of user sale operations of tokens that the user
    collected.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user collection sale operations information.

    """
    query = """
        query UserCollectionSales {
            events(where: {seller_address: {_in: ["%s"]}, implements: {_eq: "SALE"}, token: {artist_address: {_nin: ["%s"]}}}, order_by: {timestamp: asc}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                timestamp
                ophash
                token_id
                amount
                fa2_address
                price
            }
        }
    """ % ('","'.join(user_wallets), '","'.join(user_wallets))
    collection_sales = get_teztok_query_result({"query": query}, kind="events")

    return {sale["ophash"]: sale for sale in collection_sales}


def fix_missing_token_information(tokens, token_transfers, kind):
    # Try to fix the missing information using the token transfers details
    for index, token in tokens.iterrows():
        if token["token_id"] == "":
            token_address = token["token_address"]
            timestamp = token["timestamp"]

            if token_address != "":
                cond = ((token_transfers["token_address"] == token_address) & 
                        (token_transfers["timestamp"] == timestamp))

                if cond.sum() == 0:
                    cond = ((token_transfers["token_address"] == token_address) & 
                            (token_transfers[kind]))
            else:
                cond = token_transfers["timestamp"] == timestamp

            if cond.sum() == 1:
                transfers = token_transfers[cond]
                tokens.loc[index, "token_name"] = transfers["token_name"].values[0]
                tokens.loc[index, "token_id"] = transfers["token_id"].values[0]
                tokens.loc[index, "token_editions"] = str(transfers["token_editions"].values[0])
                tokens.loc[index, "token_address"] = transfers["token_address"].values[0]

    return tokens
