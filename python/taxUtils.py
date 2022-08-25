import json
import requests
import numpy as np
import pandas as pd

# Trick to be able to print the complete transaction hashes on the console
pd.options.display.max_colwidth = 80

# The main tezos FA2 tokens
TOKENS = {
    "OBJKT": "KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton",
    "Tezzardz": "KT1LHHLso8zQWQWg1HUukajdxxbkGfNoHjh6",
    "GOGOs": "KT1SyPgtiXTaEfBuMZKviWGNHqVrBBEjvtfQ",
    "GOGOs Inventory Item": "KT1Xf44LpwrA7oBcB3VwWTtUBP1eNRaNnWeh",
    "NEONZ": "KT1MsdyBSAMQwzvDH4jt2mxUKJvBSWZuPoRJ",
    "NEONZ Facez": "KT1PwTyUGt7XNYWxmgaQEiXuJS5VzBnigYPM",
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
    "akaDAO": "KT1AM3PV1cwmGRw28DVTgsjjsjHvmL6z4rGh",
    "Art Cardz": "KT1LbLNTTPoLgpumACCBFJzBEHDiEUqNxz5C",
    "Ziggurats": "KT1PNcZQkJXMQ2Mg92HG1kyrcu3auFX5pfd8",
    "Rarible token": "KT18pVpRXKPY2c4U2yFEGSH3ZnhB2kL8kwXS",
    "Les Elefants Terribles token": "KT19BLv8px4VMLduVnYgahqFbsJ19FJXamUG",
    "The Moments token": "KT1CNHwTyjFrKnCstRoMftyFVwoNzF6Xxhpy",
    "wUSDC": "KT18fp5rcTW7mbWDmzFwjLDUhs5MeJmagDSZ"
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
    "objkt.com Dutch Auctions Old": "KT1ET45vnyEFMLS9wX1dYHEs9aCN3twDEiQw",
    "objkt.com Dutch Auctions v1": "KT1QJ71jypKGgyTNtXjkCAYJZNhCKWiHuT2r",
    "objkt.com Dutch Auctions v2": "KT1XXu88HkNzQRHNgAf7Mnq68LyS9MZJNoHP",
    "objkt.com Minting Factory": "KT1Aq4wWmVanpQhq4TTfjZXB5AjFpx15iQMM",
    "FXHASH marketplace v1": "KT1Xo5B7PNBAeynZPmca4bRh6LQow4og1Zb9",
    "FXHASH marketplace v2": "KT1GbyoDi7H1sfXmimXpptZJuCdHMh66WS9u",
    "versum marketplace": "KT1GyRAJNdizF1nojQz62uGYkx8WFRUJm9X5",
    "rarible marketplace v2": "KT198mqFKkiWerXLmMCw69YB1i6yzYtmGVrC",
    "8bidou marketplace I": "KT1BvWGFENd4CXW5F3u4n31xKfJhmBGipoqF",
    "8bidou marketplace II": "KT1AHBvSo828QwscsjDjeUuep7MgApi8hXqA",
    "contter marketplace I": "KT1WBmegTu1CJi4Q9ZNQT47gtbuqVjwmUUQZ",
    "contter marketplace II": "KT1SEKxDMTNRpQnb5o2pyiYBKyrH9a8FiB4k",
    "typed marketplace": "KT1VoZeuBMJF6vxtLqEFMoc4no5VDG789D7z",
    "akaMetaverse marketplace v1": "KT1HGL8vx7DP4xETVikL4LUYvFxSV19DxdFN",
    "akaMetaverse marketplace v2": "KT1Qieo8hJWj2rHFfe8BRqnMHXYga9av89GJ",
    "akaMetaverse marketplace v2.1": "KT1Dn3sambs7KZGW88hH2obZeSzfmCmGvpFo",
    "8scribo marketplace": "KT19vw7kh7dzTRxFUZNWu39773baauzNWtzj",
    "Barter marketplace": "KT1XtJ6k51y7HpLFLTNv2wBYFhfVMZ6ow3Sz",
    # Other
    "h=n name registry": "KT1My1wDZHDGweCrJnQJi3wcFaS67iksirvj",
    "h=n DAO": "KT1NrAnSjrjp3Bycaw8YKPrDq2aXUTHhq8MF",
    "h=n DAO II": "KT1Skxv2g3dnWf3mmciSeNvhthHqZJgG8Y6h",
    "h=n OBJKT-hDAO curation": "KT1TybhR7XraG75JFYKSrh7KnxukMBT5dor6",
    "FXHASH name registry": "KT1Ezht4PDKZri7aVppVGT4Jkw39sesaFnww",
    "FXHASH pricing contract v1": "KT1FHzHxuMaNLYG8LdniY45M6RCfkF3AoXFh",
    "FXHASH pricing contract v2": "KT1EzLrXRCXij42pKfbZPn48PuxrnVki1aYY",
    "versum registry": "KT1NUrzs7tiT4VbNPqeTxgAFa4SXeV1f3xe9",
    "contter registry": "KT1Hv7keNNq3KEhbr6fWQZvJq93mSmYF9zSf",
    "typed registry": "KT1QSERFwHZcQfUf6ZruTSLMBfzitRs6ixmP",
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
    "rarible Transfer Manager": "KT1HTmwHGvxYgACDr1oJhMNZGzxHCAnNHaHi",
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
    "QuipuSwap hDAO": "KT1QxLqukyfohPV5kPkw97Rs6cw1DDDvYgbB",
    "QuipuSwap wUSDC": "KT1U2hs5eNdeCpHouAvQXGMzGFGJowbhjqmo"
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


def save_json_file(file_name, data, compact=False):
    """Saves some data as a json file.

    Parameters
    ----------
    file_name: str
        The complete path to the json file where the data will be saved.
    data: object
        The data to save.
    compact: bool, optional
        If True, the json file will be saved in a compact form. Default is
        False.

    """
    with open(file_name, "w", encoding="utf-8") as json_file:
        if compact:
            json.dump(data, json_file, indent=None, separators=(",", ":"))
        else:
            json.dump(data, json_file, indent=4)


def get_token_link(token_alias, token_id, token_address):
    """Returns the web link to a given token.

    Parameters
    ----------
    token_alias: str
        The token alias.
    token_id: str
        The token id.
    token_address: str
        The token contract address.

    Returns
    -------
    str
        The token web link.

    """
    # Return if there is not enough information to build the link
    if (token_id is None) or (token_address is None):
        return ""

    # Return the correct token link
    tokens_to_exclude = [
        "hDAO", "Materia", "wUSDC", "MATH", "TezDAO", "tz1and Place",
        "tz1and Item", "contter token"]

    if token_alias == "OBJKT":
        return "https://teia.art/objkt/%s" % token_id
    elif token_alias == "objkt.com collection":
        return "http://objkt.com/asset/%s/%s" % (token_address, token_id)
    elif token_alias in ["GENTK v1", "GENTK v2"]:
        return "https://www.fxhash.xyz/gentk/%s" % token_id
    elif token_alias == "ITEM":
        return "https://versum.xyz/token/versum/%s" % token_id
    elif token_alias == "8bidou 8x8 token":
        return "https://www.8bidou.com/item/?id=%s" % token_id
    elif token_alias == "8bidou 24x24 token":
        return "https://www.8bidou.com/g_item/?id=%s" % token_id
    elif token_alias == "8scribo token":
        return "https://8scribo.xyz/haikus/%s" % token_id
    elif (token_alias in TOKENS) and (token_alias not in tokens_to_exclude):
        return "http://objkt.com/asset/%s/%s" % (token_address, token_id)
    else:
        return ""


def get_query_result(url, parameters=None, timeout=60):
    """Executes the given query and returns the result.

    Parameters
    ----------
    url: str
        The url to the server API.
    parameters: dict, optional
        The query parameters. Default is None.
    timeout: float, optional
        The query timeout in seconds. Default is 60 seconds.

    Returns
    -------
    object
        The query result.

    """
    response = requests.get(url=url, params=parameters, timeout=timeout)

    if response.status_code == requests.codes.ok:
        return response.json()

    return None


def get_graphql_query_result(url, query, timeout=60):
    """Executes the given GraphQL query and returns the result.

    Parameters
    ----------
    url: str
        The url to the GraphQL server API.
    query: dict
        The GraphQL query.
    timeout: float, optional
        The query timeout in seconds. Default is 60 seconds.

    Returns
    -------
    object
        The query result.

    """
    response = requests.post(url=url, data=json.dumps(query), timeout=timeout)

    if response.status_code == requests.codes.ok:
        return response.json()

    return None


def get_tzkt_query_result(url, parameters=None, timeout=60):
    """Executes the given tzkt query and returns the result.

    Parameters
    ----------
    url: str
        The url to the tzkt server API.
    parameters: dict, optional
        The query parameters. Default is None.
    timeout: float, optional
        The query timeout in seconds. Default is 60 seconds.

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


def get_teztok_query_result(query, kind, timeout=60):
    """Executes the given teztok query and returns the result.

    Parameters
    ----------
    query: dict
        The GraphQL query.
    kind: str
        The kind of teztok query.
    timeout: float, optional
        The query timeout in seconds. Default is 60 seconds.

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
        "quote": "eur,usd"}

    return get_tzkt_query_result(url, parameters)


def get_user_reveals(user_wallets):
    """Returns the complete list of user reveals.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    list
        A python list with the user reveals.

    """
    url = "https://api.tzkt.io/v1/operations/reveals"
    parameters = {
        "sender.in": ",".join(user_wallets),
        "quote": "eur,usd"}

    return get_tzkt_query_result(url, parameters)


def get_user_delegations(user_wallets):
    """Returns the complete list of user delegations.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    list
        A python list with the user delegations.

    """
    url = "https://api.tzkt.io/v1/operations/delegations"
    parameters = {
        "anyof.initiator.sender.in": ",".join(user_wallets),
        "quote": "eur,usd"}

    return get_tzkt_query_result(url, parameters)


def combine_operations(operations_1, operations_2):
    """Combines two lists of operations by increasing block level.

    Parameters
    ----------
    operations_1: list
        The first list of operations.
    operations_2: list
        The second list of operations.

    Returns
    -------
    list
        A python list with the combined operations.

    """
    combined_operations = []
    counter = 0
    o_2 = operations_2[counter] if counter < len(operations_2) else None

    for o_1 in operations_1:
        while o_2 is not None and o_2["level"] <= o_1["level"]:
            combined_operations.append(o_2)
            counter += 1
            o_2 = operations_2[counter] if counter < len(operations_2) else None

        combined_operations.append(o_1)

    return combined_operations


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


def get_user_tez_balance(user_wallets):
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
    # Get the historical tez balance for each of the user wallets
    tez_balances = []

    for wallet in user_wallets:
        url = "https://api.tzkt.io/v1/accounts/%s/balance_history" % wallet
        parameters = {
            "step": 1,
            "quote": "eur,usd"}
        query_result = get_tzkt_query_result(url, parameters)
        tez_balances.append({item["level"]: item for item in query_result})

    # Get all the block levels for which we have some balance information
    levels = []

    for tez_balance in tez_balances:
        levels += list(tez_balance.keys())

    # Remove block level duplications and make sure they are sorted
    levels = list(set(levels))
    levels.sort()

    # Calculate the combined tez balance
    combined_tez_balance = [{"level": level, "timestamp": None, "balance": 0, "quote": None} for level in levels]

    for tez_balance in tez_balances:
        previous_balance_amount = 0

        for balance in combined_tez_balance:
            level = balance["level"]

            if level in tez_balance:
                balance["timestamp"] = tez_balance[level]["timestamp"]
                balance["quote"] = tez_balance[level]["quote"]
                previous_balance_amount = tez_balance[level]["balance"] / 1e6

            balance["balance"] += previous_balance_amount

    return combined_tez_balance


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


def get_user_active_offers(user_wallets):
    """Returns the complete list of user active offers.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.

    Returns
    -------
    dict
        A python dictionary with user active offers.

    """
    query = """
        query UserActiveOffers {
            offers(where: {buyer_address: {_in: ["%s"]}, status: {_eq: "active"}}, limit: **LIMIT**, offset: **OFFSET**) {
                type
                offer_id
                bid_id
                token_id
                fa2_address
            }
        }
    """ % ('","'.join(user_wallets))
    active_offers = get_teztok_query_result({"query": query}, kind="offers")

    offers = {}

    for offer in active_offers:
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

    # Get the fulfilled and active offers
    fulfilled_offers = get_user_fulfilled_offers(user_wallets)
    active_offers = get_user_active_offers(user_wallets)

    # Indicate which offers were fulfilled and which are still active
    for collect in collects:
        offer_id = collect["offer_id"] if collect["offer_id"] is not None else collect["bid_id"]
        collect["fulfilled_offer"] = None
        collect["active_offer"] = None

        if offer_id is not None:
            token_id = collect["token_id"]
            token_address = collect["fa2_address"]

            if token_address in fulfilled_offers and token_id in fulfilled_offers[token_address]:
                 collect["fulfilled_offer"] = offer_id in fulfilled_offers[token_address][token_id]

            if token_address in active_offers and token_id in active_offers[token_address]:
                 collect["active_offer"] = offer_id in active_offers[token_address][token_id]

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
    auction_bids = get_teztok_query_result({"query": query}, kind="events")

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
    """Tries to fix any missing token information using the user token
    transfers.

    Parameters
    ----------
    tokens: object
        The pandas data frame with the token information.
    token_transfers: object
        The pandas data frame with the user token transfers.
    kind: str
        The kind of transfers to look at: mint, send, receive or burn.

    Returns
    -------
    object
        The pandas data frame with the fixed token information.

    """
    # Make a copy of the original data frame
    tokens = tokens.copy()

    # Add the missing token information
    def get_token_information(token):
        token_name = token["token_name"]
        token_id = token["token_id"]
        token_editions = token["token_editions"]
        token_address = token["token_address"]

        # Check if there is some missing information
        if (token_id == "") or (token_editions == "") or (token_address == ""):
            # Get the associated unused token token_transfer at the same timestamp
            cond = ~token_transfers["used"] & token_transfers[kind] & (
                token_transfers["timestamp"] == token["timestamp"])

            if token_id != "":
                cond &= token_transfers["token_id"] == token_id

            if token_editions != "":
                cond &= token_transfers["token_editions"] == token_editions

            if token_address != "":
                cond &= token_transfers["token_address"] == token_address

            # Select operations at any later time if necessary
            if (cond.sum() == 0) and (token_address != ""):
                cond = ~token_transfers["used"] & token_transfers[kind] & (
                    token_transfers["timestamp"] > token["timestamp"]) & (
                    token_transfers["token_address"] == token_address)

                if token_id != "":
                    cond &= token_transfers["token_id"] == token_id

                if token_editions != "":
                    cond &= token_transfers["token_editions"] == int(token_editions)

            # Make sure there is only one match
            if cond.sum() == 1:
                # Get the token information from the token transfer
                token_transfer = token_transfers[cond].iloc[0]
                token_name = token_transfer["token_name"]
                token_id = token_transfer["token_id"]
                token_editions = token_transfer["token_editions"]
                token_address = token_transfer["token_address"]

                # Set the token transfer as used
                token_transfers.loc[cond, "used"] = True

        return token_name, token_id, token_editions, token_address

    # Obtain any missing token information
    tokens[["token_name", "token_id", "token_editions", "token_address"]] = tokens.apply(
        get_token_information, axis=1, result_type="expand")

    return tokens


def get_minted_tokens(operations, token_transfers):
    """Returns the list of tokens minted by the user.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    token_transfers: object
        The pandas data frame with the user token transfers.

    Returns
    -------
    object
        A pandas data frame with the tokens minted by the user.

    """
    # Get the user minted tokens from the mint operations
    cond = operations["is_sender"] & operations["applied"] & ~operations["ignore"] & operations["mint"]
    minted_tokens = operations[cond].copy()
    minted_tokens = minted_tokens.reset_index(drop=True)

    # Set the associated token transfers as used
    for _, token in minted_tokens.iterrows():
        cond = token_transfers["mint"] & token_transfers["receive"] & (
            token_transfers["timestamp"] == token["timestamp"]) & (
            token_transfers["token_id"] == token["token_id"]) & (
            token_transfers["token_editions"] == token["token_editions"]) & (
            token_transfers["token_address"] == token["token_address"])

        if cond.sum() == 1:
            token_transfers.loc[cond, "used"] = True

    # Try to fix any missing token information using the user token transfers
    minted_tokens = fix_missing_token_information(minted_tokens, token_transfers, kind="mint")

    # Add a column with the token links
    minted_tokens["token_link"] = minted_tokens.apply(
        lambda t: get_token_link(t["token_name"], t["token_id"], t["token_address"]), axis=1)

    # Reorder the columns
    columns = [
        "timestamp", "kind", "token_name", "token_id", "token_editions",
        "token_address", "token_link", "tzkt_link"]

    return minted_tokens[columns].copy()


def split_multiple_collects(collected_tokens):
    """Splits multiple collect operations in several single collect operations.

    Parameters
    ----------
    collected_tokens: object
        The pandas data frame with the user collected tokens.

    Returns
    -------
    object
        A pandas data frame with the splitted multiple collect operations.

    """
    # Get the multiple edition collects
    cond = ~collected_tokens["token_editions"].isin(["", "1"]) & (
        ~collected_tokens["token_name"].isin(["hDAO", "MATH", "Materia", "TezDAO", "akaDAO", "wUSDC"]))
    multiple_edition_collects = collected_tokens[cond]

    # Split the multiple edition collects and add them to the single edition collects
    combined_collects = collected_tokens[~cond].copy()

    for i in range(len(multiple_edition_collects)):
        # Get the multiple edition collect
        multiple_edition_collect = multiple_edition_collects.iloc[[i]]
        token_editions = int(multiple_edition_collect["token_editions"].iloc[0])

        # Create a single edition collect
        single_edition_collect = multiple_edition_collect.copy()
        single_edition_collect["token_editions"] = "1"
        single_edition_collect["collect_amount"] /= token_editions

        # Add one single edition collect for each collected edition
        while token_editions > 0:
            combined_collects = pd.concat([combined_collects, single_edition_collect.copy()])
            token_editions -= 1

    # Sort the data frame by the time stamp
    combined_collects = combined_collects.sort_values(by="timestamp")
    combined_collects = combined_collects.reset_index(drop=True)

    return combined_collects


def fix_token_ids_from_mints(collected_tokens, token_transfers):
    """Tries to fix any missing token id from a list of collected minted tokens.

    Parameters
    ----------
    collected_tokens: object
        The pandas data frame with the user collected tokens.
    token_transfers: object
        The pandas data frame with the user token transfers.

    Returns
    -------
    object
        A pandas data frame with the fixed user collected tokens.

    """
    # Get the row indices of the tokens that are only missing the token id
    cond = (collected_tokens["token_id"] == "") & (
        collected_tokens["token_editions"] == "1") & (
        collected_tokens["token_address"] != "")
    indices = collected_tokens.index[cond].to_numpy()

    # Loop over the indices and try to get the token id from the token transfers
    for index in indices:
        # Select only recent unused mints
        timestamp = collected_tokens.loc[index, "timestamp"]
        token_address = collected_tokens.loc[index, "token_address"]
        cond = ~token_transfers["used"] & token_transfers["mint"] & (
            token_transfers["token_address"] == token_address) & (
            token_transfers["timestamp"] >= timestamp) & (
            (token_transfers["timestamp"] - timestamp).dt.days < 2)

        if cond.sum() > 0:
            # Use the token id from the first matching token transfer
            first_matched_index = token_transfers.index[cond][0]
            collected_tokens.loc[index, "token_id"] = token_transfers.loc[first_matched_index, "token_id"]

            # Set the token transfer as used
            token_transfers.loc[first_matched_index, "used"] = True

    return collected_tokens


def get_collected_tokens(operations, token_transfers):
    """Returns the list of tokens collected by the user.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    token_transfers: object
        The pandas data frame with the user token transfers.

    Returns
    -------
    object
        A pandas data frame with the tokens collected by the user.

    """
    # Get the user collected tokens from the collect operations
    cond = operations["is_sender"] & operations["applied"] & ~operations["ignore"] & operations["collect"]
    collected_tokens = operations[cond].copy()
    collected_tokens = collected_tokens.reset_index(drop=True)

    # Set the associated token transfers as used
    for i, token in collected_tokens.iterrows():
        cond = token_transfers["receive"] & (
            token_transfers["timestamp"] == token["timestamp"]) & (
            token_transfers["token_id"] == token["token_id"]) & (
            token_transfers["token_editions"] == token["token_editions"]) & (
            token_transfers["token_address"] == token["token_address"])

        if cond.sum() == 1:
            token_transfers.loc[cond, "used"] = True

    # Try to fix any missing token information using the user token transfers
    collected_tokens = fix_missing_token_information(collected_tokens, token_transfers, kind="mint")
    collected_tokens = fix_missing_token_information(collected_tokens, token_transfers, kind="receive")

    # Split multiple collects into single collects
    collected_tokens = split_multiple_collects(collected_tokens)

    # Try to fix the missing token ids from some of the minted tokens
    collected_tokens = fix_token_ids_from_mints(collected_tokens, token_transfers)

    # Use better column names
    collected_tokens = collected_tokens.rename(columns={"collect_amount": "buy_price"})

    # Calculate the buy price in the different fiat coins
    collected_tokens["buy_price_euros"] = collected_tokens["buy_price"] * collected_tokens["tez_to_euros"]
    collected_tokens["buy_price_usd"] = collected_tokens["buy_price"] * collected_tokens["tez_to_usd"]

    # Add a column with the token links
    collected_tokens["token_link"] = collected_tokens.apply(
        lambda t: get_token_link(t["token_name"], t["token_id"], t["token_address"]), axis=1)

    # Reorder the columns
    columns = [
        "timestamp", "kind", "token_name", "token_id", "token_editions",
        "token_address", "token_link", "buy_price", "buy_price_euros",
        "buy_price_usd", "tzkt_link"]

    return collected_tokens[columns].copy()


def get_dropped_tokens(operations, token_transfers, collected_tokens):
    """Returns the list of tokens dropped to the user.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    token_transfers: object
        The pandas data frame with the user token transfers.
    collected_tokens: object
        The pandas data frame with the user collected tokens.

    Returns
    -------
    object
        A pandas data frame with the tokens collected by the user.

    """

    # Check if a token transfer is associated with a drop
    def check_is_drop(token_transfer):
        # Make sure that the token transfer has not been used already
        if token_transfer["used"]:
            return False

        # Drops can only be receive transfers
        if not token_transfer["receive"]:
            return False

        # Check if there is an operation triggered by the user for this token
        # with the same time stamp
        token_id = token_transfer["token_id"]
        token_editions = str(token_transfer["token_editions"])
        token_address = token_transfer["token_address"]
        cond = operations["is_sender"] & (
            operations["timestamp"] == token_transfer["timestamp"]) & (
            operations["token_id"] == token_id) & (
            operations["token_editions"] == token_editions) & (
            operations["token_address"] == token_address)

        if cond.sum() > 0:
            return False

        # Check if the token is in the list of collected tokens
        cond = (
            collected_tokens["token_id"] == token_id) & (
            collected_tokens["token_editions"] == token_editions) & (
            collected_tokens["token_address"] == token_address)

        if cond.sum() > 0:
            return False
        else:
            return True

    # Get the transfers associated to a token drop
    is_drop = token_transfers.apply(check_is_drop, axis=1)
    dropped_token_transfers = token_transfers[is_drop].copy()
    dropped_token_transfers = dropped_token_transfers.reset_index(drop=True)

    # Update the token transfers used column
    token_transfers.loc[is_drop, "used"] = True

    # Reorder the columns
    columns = [
        "timestamp", "from", "to", "token_name", "token_id", "token_editions",
        "token_address", "token_link"]

    return dropped_token_transfers[columns].copy()


def get_sold_tokens(operations, token_transfers):
    """Returns the list of tokens sold by the user.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    token_transfers: object
        The pandas data frame with the user token transfers.

    Returns
    -------
    object
        A pandas data frame with the tokens sold by the user.

    """
    # Get the user sold tokens from the collection_sale operations
    cond = operations["is_target"] & operations["applied"] & ~operations["ignore"] & operations["collection_sale"]
    sold_tokens = operations[cond].copy()
    sold_tokens = sold_tokens.reset_index(drop=True)

    # Set the associated token transfers as used
    for i, token in sold_tokens.iterrows():
        cond = token_transfers["send"] & (
            token_transfers["timestamp"] == token["timestamp"]) & (
            token_transfers["token_id"] == token["token_id"]) & (
            token_transfers["token_editions"] == token["token_editions"]) & (
            token_transfers["token_address"] == token["token_address"])

        if cond.sum() == 1:
            token_transfers.loc[cond, "used"] = True

    # Try to fix any missing token information using the user token transfers
    sold_tokens = fix_missing_token_information(sold_tokens, token_transfers, kind="send")

    # Use better column names
    sold_tokens = sold_tokens.rename(columns={"collection_sale_amount": "sell_price"})

    # Calculate the sell price in the different fiat coins
    sold_tokens["sell_price_euros"] = sold_tokens["sell_price"] * sold_tokens["tez_to_euros"]
    sold_tokens["sell_price_usd"] = sold_tokens["sell_price"] * sold_tokens["tez_to_usd"]

    # Add a column with the token links
    sold_tokens["token_link"] = sold_tokens.apply(
        lambda t: get_token_link(t["token_name"], t["token_id"], t["token_address"]), axis=1)

    # Reorder the columns
    columns = [
        "timestamp", "kind", "token_name", "token_id", "token_editions",
        "token_address", "token_link", "sell_price", "sell_price_euros",
        "sell_price_usd", "tzkt_link"]

    return sold_tokens[columns].copy()


def get_transferred_tokens(operations, token_transfers, minted_tokens):
    """Returns the list of tokens transferred by the user to other users.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    token_transfers: object
        The pandas data frame with the user token transfers.
    minted_tokens: object
        The pandas data frame with the user minted tokens.

    Returns
    -------
    object
        A pandas data frame with the tokens transferred by the user.

    """

    # Check if a token transfer is associated with a user initiated transfer
    def check_is_user_transfer(token_transfer):
        # Make sure that the token transfer has not been used already
        if token_transfer["used"]:
            return False

        # User transfers can only be send transfers
        if not token_transfer["send"]:
            return False

        # Check if the token is in the list of minted tokens
        cond = (
            minted_tokens["token_id"] == token_transfer["token_id"]) & (
            minted_tokens["token_address"] == token_transfer["token_address"])

        if cond.sum() > 0:
            return False

        # Check if there is a transfer operation sent by the user with the same
        # time stamp
        cond = operations["is_sender"] & ~operations["ignore"] & (
            operations["entrypoint"] == "transfer") & (
            operations["timestamp"] == token_transfer["timestamp"])

        if cond.sum() == 1:
            return True
        else:
            return False

    # Get the transfers associated to a user token transfer
    is_user_transfer = token_transfers.apply(check_is_user_transfer, axis=1)
    transferred_tokens = token_transfers[is_user_transfer].copy()
    transferred_tokens = transferred_tokens.reset_index(drop=True)

    # Update the token transfers used column
    token_transfers.loc[is_user_transfer, "used"] = True

    # Reorder the columns
    columns = [
        "timestamp", "from", "to", "token_name", "token_id", "token_editions",
        "token_address", "token_link"]

    return transferred_tokens[columns].copy()


def get_incoming_tokens(collected_tokens, dropped_tokens):
    """Returns the list of user incoming tokens.

    Parameters
    ----------
    collected_tokens: object
        The pandas data frame with the user collected tokens.
    dropped_tokens: object
        The pandas data frame with the tokens dropped to the user.

    Returns
    -------
    object
        A pandas data frame with the user incoming tokens.

    """
    # Select the relevant columns from the collected tokens
    columns = ["timestamp", "token_name", "token_id", "token_editions",
       "token_address", "token_link", "buy_price", "buy_price_euros",
       "buy_price_usd"]
    collected_tokens = collected_tokens[columns].copy()

    # Select the relevant columns from the dropped tokens
    columns = ["timestamp", "token_name", "token_id", "token_editions",
       "token_address", "token_link"]
    dropped_tokens = dropped_tokens[columns].copy()

    # Add the missing columns to the dropped tokens data frame
    dropped_tokens["buy_price"] = 0.0
    dropped_tokens["buy_price_euros"] = 0.0
    dropped_tokens["buy_price_usd"] = 0.0

    # Remove any entry in the collected and dropped tokens that is missing the
    # token id or the token address information
    cond = (collected_tokens["token_id"] != "") & (collected_tokens["token_address"] != "")
    collected_tokens = collected_tokens[cond]
    cond = (dropped_tokens["token_id"] != "") & (dropped_tokens["token_address"] != "")
    dropped_tokens = dropped_tokens[cond]

    # Get the user incoming tokens combining the collected and dropped tokens
    incoming_tokens = pd.concat([collected_tokens, dropped_tokens])
    incoming_tokens = incoming_tokens.sort_values(by="timestamp")
    incoming_tokens = incoming_tokens.reset_index(drop=True)

    # Assume one edition in entries missing the token editions information
    incoming_tokens.loc[incoming_tokens["token_editions"] == "", "token_editions"] = "1"

    # Change the token editions column type to int
    incoming_tokens["token_editions"] = incoming_tokens["token_editions"].astype(int)

    # Rename the time stamp column
    incoming_tokens = incoming_tokens.rename(columns={"timestamp": "buy_timestamp"})

    return incoming_tokens


def get_outgoing_tokens(sold_tokens, transferred_tokens):
    """Returns the list of user outgoing tokens.

    Parameters
    ----------
    sold_tokens: object
        The pandas data frame with the user sold tokens.
    transferred_tokens: object
        The pandas data frame with the user transferred tokens.

    Returns
    -------
    object
        A pandas data frame with the user outgoing tokens.

    """
    # Select the relevant columns from the sold tokens
    columns = ["timestamp", "token_name", "token_id", "token_editions",
       "token_address", "token_link", "sell_price", "sell_price_euros",
       "sell_price_usd"]
    sold_tokens = sold_tokens[columns].copy()

    # Select the relevant columns from the transferred tokens
    columns = ["timestamp", "token_name", "token_id", "token_editions",
       "token_address", "token_link"]
    transferred_tokens = transferred_tokens[columns].copy()

    # Add the missing columns to the transferred tokens data frame
    transferred_tokens["sell_price"] = 0.0
    transferred_tokens["sell_price_euros"] = 0.0
    transferred_tokens["sell_price_usd"] = 0.0

    # Add a column to indicate if the token was sold or not
    sold_tokens["sold"] = True
    transferred_tokens["sold"] = False

    # Get the user outgoing tokens combining the sold and transferred tokens
    outgoing_tokens = pd.concat([sold_tokens, transferred_tokens])
    outgoing_tokens = outgoing_tokens.sort_values(by="timestamp")
    outgoing_tokens = outgoing_tokens.reset_index(drop=True)

    # Assume one edition in entries missing the token editions information
    outgoing_tokens.loc[outgoing_tokens["token_editions"] == "", "token_editions"] = "1"

    # Change the token editions column type to int
    outgoing_tokens["token_editions"] = outgoing_tokens["token_editions"].astype(int)

    # Rename the time stamp column
    outgoing_tokens = outgoing_tokens.rename(columns={"timestamp": "sell_timestamp"})

    return outgoing_tokens


def get_token_trades(collected_tokens, dropped_tokens, sold_tokens, transferred_tokens, hold_period):
    """Returns the list of tokens trades done by the user.

    Parameters
    ----------
    collected_tokens: object
        The pandas data frame with the user collected tokens.
    dropped_tokens: object
        The pandas data frame with the tokens dropped to the user.
    sold_tokens: object
        The pandas data frame with the user sold tokens.
    transferred_tokens: object
        The pandas data frame with the user transferred tokens.
    hold_period: int
        The minimum holding time in days for the gains to be tax free.

    Returns
    -------
    object
        A pandas data frame with the user token trades.

    """
    # Get the user incoming and outgoing tokens
    incoming_tokens = get_incoming_tokens(collected_tokens, dropped_tokens)
    outgoing_tokens = get_outgoing_tokens(sold_tokens, transferred_tokens)

    # Get the necessary numpy arrays
    n_trades = len(outgoing_tokens)
    buy_timestamp = outgoing_tokens["sell_timestamp"].to_numpy().copy()
    buy_price = np.full(n_trades, 0.0)
    buy_price_euros = np.full(n_trades, 0.0)
    buy_price_usd = np.full(n_trades, 0.0)
    gain = np.full(n_trades, 0.0)
    gain_euros = np.full(n_trades, 0.0)
    gain_usd = np.full(n_trades, 0.0)
    taxed_gain = np.full(n_trades, 0.0)
    taxed_gain_euros = np.full(n_trades, 0.0)
    taxed_gain_usd = np.full(n_trades, 0.0)

    for i, token in outgoing_tokens.iterrows():
        # Get the sell information
        sell_timestamp = token["sell_timestamp"]
        sell_editions = token["token_editions"]
        sell_price_per_edition = token["sell_price"] / sell_editions
        sell_price_per_edition_euros = token["sell_price_euros"] / sell_editions
        sell_price_per_edition_usd = token["sell_price_usd"] / sell_editions

        # Check if the token is owed by the user at that time
        cond = (incoming_tokens["token_id"] == token["token_id"]) & (
            incoming_tokens["token_editions"] > 0) & (
            incoming_tokens["token_address"] == token["token_address"]) & (
            incoming_tokens["buy_timestamp"] <= sell_timestamp)

        if cond.sum() > 0:
            # Loop over the owned editions and calculate the combined buy price
            indices = incoming_tokens.index[cond].to_numpy()

            for index in indices:
                # Get the buy information
                buy_editions = incoming_tokens.loc[index, "token_editions"]
                buy_price_per_edition = incoming_tokens.loc[index, "buy_price"] / buy_editions
                buy_price_per_edition_euros = incoming_tokens.loc[index, "buy_price_euros"] / buy_editions
                buy_price_per_edition_usd = incoming_tokens.loc[index, "buy_price_usd"] / buy_editions

                # Calculate the traded gains
                traded_editions = min(sell_editions, buy_editions)
                buy_timestamp[i] = incoming_tokens.loc[index, "buy_timestamp"]
                buy_price[i] += traded_editions * buy_price_per_edition
                buy_price_euros[i] += traded_editions * buy_price_per_edition_euros
                buy_price_usd[i] += traded_editions * buy_price_per_edition_usd
                gain[i] += traded_editions * (sell_price_per_edition - buy_price_per_edition)
                gain_euros[i] += traded_editions * (sell_price_per_edition_euros - buy_price_per_edition_euros)
                gain_usd[i] += traded_editions * (sell_price_per_edition_usd - buy_price_per_edition_usd)

                # Check if the gains are taxable
                if (sell_timestamp - incoming_tokens.loc[index, "buy_timestamp"]).days <= hold_period:
                    taxed_gain[i] += traded_editions * (sell_price_per_edition - buy_price_per_edition)
                    taxed_gain_euros[i] += traded_editions * (sell_price_per_edition_euros - buy_price_per_edition_euros)
                    taxed_gain_usd[i] += traded_editions * (sell_price_per_edition_usd - buy_price_per_edition_usd)

                # Update the incoming tokens information
                incoming_tokens.loc[index, "token_editions"] -= traded_editions
                incoming_tokens.loc[index, "buy_price"] -= traded_editions * buy_price_per_edition
                incoming_tokens.loc[index, "buy_price_euros"] -= traded_editions * buy_price_per_edition
                incoming_tokens.loc[index, "buy_price_usd"] -= traded_editions * buy_price_per_edition

                # Update the sell editions
                sell_editions -= traded_editions

                # Exit the loop if all the sell editions were taken into account
                if sell_editions == 0:
                    break

        # Check if there are still some sell editions to take into account
        if sell_editions > 0:
            # Assume that the token editions were bought for free just before selling them
            buy_timestamp[i] = sell_timestamp
            gain[i] += sell_editions * sell_price_per_edition
            gain_euros[i] += sell_editions * sell_price_per_edition_euros
            gain_usd[i] += sell_editions * sell_price_per_edition_usd
            taxed_gain[i] += sell_editions * sell_price_per_edition
            taxed_gain_euros[i] += sell_editions * sell_price_per_edition_euros
            taxed_gain_usd[i] += sell_editions * sell_price_per_edition_usd

    # Build the token trades data frame from the sold tokens data frame
    token_trades = outgoing_tokens.copy()
    token_trades["buy_timestamp"] = buy_timestamp
    token_trades["buy_price"] = buy_price
    token_trades["buy_price_euros"] = buy_price_euros
    token_trades["buy_price_usd"] = buy_price_usd
    token_trades["gain"] = gain
    token_trades["gain_euros"] = gain_euros
    token_trades["gain_usd"] = gain_usd
    token_trades["taxed_gain"] = taxed_gain
    token_trades["taxed_gain_euros"] = taxed_gain_euros
    token_trades["taxed_gain_usd"] = taxed_gain_usd
    token_trades = token_trades[token_trades["sold"]]

    # Reorder the columns
    columns = [
        "token_name", "token_id", "token_editions", "token_address",
        "token_link", "buy_timestamp", "sell_timestamp", "buy_price",
        "sell_price", "gain", "taxed_gain", "buy_price_euros",
        "sell_price_euros", "gain_euros", "taxed_gain_euros", "buy_price_usd",
        "sell_price_usd", "gain_usd", "taxed_gain_usd"]

    return token_trades[columns].copy()


def get_tez_exchange_gains(operations, hold_period):
    """Returns the gains associated to the exchange of tez to fiat.
    
    This method uses a FIFO (first in, first out) approach.

    Parameters
    ----------
    operations: object
        The pandas data frame with the user operations.
    hold_period: int
        The minimum holding time in days for the gains to be tax free.

    Returns
    -------
    object
        A pandas data frame with the tez exchange gains.

    """
    # Get the necessary numpy arrays
    timestamp = operations["timestamp"].to_numpy().copy()
    received_amount = operations["received_amount"].to_numpy().copy()
    spent_amount = operations["spent_amount"].to_numpy().copy()
    offer_amount = operations["active_offer_amount"].to_numpy().copy()
    fees_amount = operations["spent_fees"].to_numpy().copy()
    tez_to_euros = operations["tez_to_euros"].to_numpy().copy()
    tez_to_usd = operations["tez_to_usd"].to_numpy().copy()
    is_collect = (operations["collect_amount"] > 0).to_numpy().copy()
    is_sell_tez = (operations["sell_tez_amount"] > 0).to_numpy().copy()
    gain_euros = np.full(len(spent_amount), 0.0)
    gain_usd = np.full(len(spent_amount), 0.0)
    taxed_gain_euros = np.full(len(spent_amount), 0.0)
    taxed_gain_usd = np.full(len(spent_amount), 0.0)

    # Calculate the tez exchange gains
    counter = 0

    for i in range(len(spent_amount)):
        # Process the fees_amount as a normal expense with no gains
        while fees_amount[i] > 0:
            # Calculate the amount to subtract
            subtract_amount = fees_amount[i]

            if subtract_amount > received_amount[counter]:
                subtract_amount = received_amount[counter]

            # Subtract the amount
            fees_amount[i] -= subtract_amount
            received_amount[counter] -= subtract_amount

            # Check if all the tez from the "first in" operation have been used
            if received_amount[counter] == 0:
                counter += 1

        # Process the active offers as a normal expense with no gains
        while offer_amount[i] > 0:
            # Calculate the amount to subtract
            subtract_amount = offer_amount[i]

            if subtract_amount > received_amount[counter]:
                subtract_amount = received_amount[counter]

            # Subtract the amount
            offer_amount[i] -= subtract_amount
            received_amount[counter] -= subtract_amount

            # Check if all the tez from the "first in" operation have been used
            if received_amount[counter] == 0:
                counter += 1

        # Process the spent_amount tez amount
        while spent_amount[i] > 0:
            # Calculate the amount to subtract
            subtract_amount = spent_amount[i]

            if subtract_amount > received_amount[counter]:
                subtract_amount = received_amount[counter]

            # Subtract the amount
            spent_amount[i] -= subtract_amount
            received_amount[counter] -= subtract_amount

            # Check if it is a collect or tez sell operation
            if is_collect[i] or is_sell_tez[i]:
                # Calculate the gains from the tez exchanges
                new_gain_euros = subtract_amount * (tez_to_euros[i] - tez_to_euros[counter])
                new_gain_usd = subtract_amount * (tez_to_usd[i] - tez_to_usd[counter])
                gain_euros[i] += new_gain_euros
                gain_usd[i] += new_gain_usd

                # Check if the gains are taxable
                if (timestamp[i] - timestamp[counter]).days <= hold_period:
                    taxed_gain_euros[i] += new_gain_euros
                    taxed_gain_usd[i] += new_gain_usd

            # Check if all the tez from the "first in" operation have been used
            if received_amount[counter] == 0:
                counter += 1

    # Build a data frame from the numpy arrays
    tez_exchange_gains = pd.DataFrame({
        "timestamp": timestamp,
        "tez_to_euros": tez_to_euros,
        "tez_to_usd": tez_to_usd,
        "gain_euros": gain_euros,
        "gain_usd": gain_usd,
        "taxed_gain_euros": taxed_gain_euros,
        "taxed_gain_usd": taxed_gain_usd})

    return tez_exchange_gains
