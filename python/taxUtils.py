import json
import requests


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


def get_objktcom_collections():
    """Returns the complete list of objkt.com collection addresses.

    Returns
    -------
    list
        A python list with the objkt.com collection addresses.

    """
    objktcom_collections = []

    while True:
        url = "https://api.tzkt.io/v1/bigmaps/24157/keys"
        parameters = {
            "limit": 10000,
            "select": "value",
            "offset": len(objktcom_collections)}
        objktcom_collections += [collection["contract"] for collection in get_query_result(url, parameters)]

        if len(objktcom_collections) != parameters["offset"] + parameters["limit"]:
            break

    return objktcom_collections


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
    url = "https://api.teztok.com/v1/graphql"
    query = """
        query UserMints {
            events(where: {artist_address: {_in: ["%s"]}, type: {_like: "%s"}}, order_by: {timestamp: asc}, limit: 10000) {
                type
                timestamp
                ophash
                token {
                      artist_address
                      token_id
                      symbol
                      platform
                      fa2_address
                      editions
                }
            }
        }
    """ % ('","'.join(user_wallets), "%MINT%")
    mints = get_graphql_query_result(url, {"query": query})["data"]["events"]

    return {mint["ophash"]: mint for mint in mints}


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
    url = "https://api.teztok.com/v1/graphql"
    query = """
        query UserFulfilledOffers {
            offers(where: {buyer_address: {_in: ["%s"]}, status: {_eq: "fulfilled"}}, limit: 10000) {
                type
                offer_id
                bid_id
            }
        }
    """ % ('","'.join(user_wallets))
    fulfilled_offers = get_graphql_query_result(url, {"query": query})["data"]["offers"]

    offers = {}

    for offer in fulfilled_offers:
        if offer["type"] not in offers:
            offers[offer["type"]] = []

        offers[offer["type"]].append(offer["offer_id"] if offer["offer_id"] is not None else offer["bid_id"])

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
    # Get the user collects
    url = "https://api.teztok.com/v1/graphql"
    query = """
        query UserCollects {
            events(where: {buyer_address: {_in: ["%s"]}}, order_by: {timestamp: asc}, limit: 10000) {
                type
                timestamp
                ophash
                amount
                price
                implements
                offer_id
                bid_id
                token {
                    artist_address
                    token_id
                    symbol
                    platform
                    fa2_address
                    editions
                }
            }
        }
    """ % ('","'.join(user_wallets))
    collects = get_graphql_query_result(url, {"query": query})["data"]["events"]

    # Get the fulfilled offers
    fulfilled_offers = get_user_fulfilled_offers(user_wallets)

    # Indicate which offers were fulfilled
    for collect in collects:
        collect["offer_fulfilled"] = False

        if collect["offer_id"] is not None or collect["bid_id"] is not None:
            if collect["type"] in fulfilled_offers:
                if collect["offer_id"] is not None:
                    collect["offer_fulfilled"] = collect["offer_id"] in fulfilled_offers[collect["type"]]
                else:
                    collect["offer_fulfilled"] = collect["bid_id"] in fulfilled_offers[collect["type"]]

    return {collect["ophash"]: collect for collect in collects}


def get_user_art_sales(user_wallets):
    """Returns the complete list of user sale operations for tokens that the user
    has minted.

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
        fa2_address = mint["token"]["fa2_address"]
        token_id = mint["token"]["token_id"]

        if fa2_address not in minted_tokens:
            minted_tokens[fa2_address] = []

        minted_tokens[fa2_address].append(token_id)

    # Get the user art sales
    art_sales = []

    for fa2_address, token_ids in minted_tokens.items():
        url = "https://api.teztok.com/v1/graphql"
        query = """
            query UserArtSales {
                events(where: {seller_address: {_in: ["%s"]}, implements: {_is_null: true}, _or: [{fa2_address: {_eq: "%s"}, token_id: {_in: ["%s"]}}]}, order_by: {timestamp: asc}, limit: 10000) {
                    type
                    timestamp
                    ophash
                    amount
                    price
                    implements
                    token {
                        artist_address
                        token_id
                        symbol
                        platform
                        fa2_address
                        editions
                    }
                }
            }
        """ % ('","'.join(user_wallets), fa2_address, '","'.join(token_ids))
        art_sales += get_graphql_query_result(url, {"query": query})["data"]["events"]

        url = "https://api.teztok.com/v1/graphql"
        query = """
            query UserArtSales {
                events(where: {implements: {_eq: "SALE"}, _or: [{fa2_address: {_eq: "%s"}, token_id: {_in: ["%s"]}}]}, order_by: {timestamp: asc}, limit: 10000) {
                    type
                    timestamp
                    ophash
                    amount
                    price
                    implements
                    token {
                        artist_address
                        token_id
                        symbol
                        platform
                        fa2_address
                        editions
                    }
                }
            }
        """ % (fa2_address, '","'.join(token_ids))
        art_sales += get_graphql_query_result(url, {"query": query})["data"]["events"]

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
    url = "https://api.teztok.com/v1/graphql"
    query = """
        query UserCollectionSales {
            events(where: {seller_address: {_in: ["%s"]}, token: {artist_address: {_nin: ["%s"]}}}, order_by: {timestamp: asc}, limit: 10000) {
                type
                timestamp
                ophash
                amount
                price
                implements
                token {
                    artist_address
                    token_id
                    symbol
                    platform
                    fa2_address
                    editions
                }
            }
        }
    """ % ('","'.join(user_wallets), '","'.join(user_wallets))
    collection_sales = get_graphql_query_result(url, {"query": query})["data"]["events"]

    return {sale["ophash"]: sale for sale in collection_sales}


def get_user_transactions(user_wallets, timestamp_range):
    """Returns the complete list of user transactions.

    Parameters
    ----------
    user_wallets: list
        The user wallet addresses.
    timestamp_range: list
        The timestamp range for the transactions.

    Returns
    -------
    list
        A python list with the user transactions.

    """
    transactions = []

    while True:
        url = "https://api.tzkt.io/v1/operations/transactions"
        parameters = {
            "anyof.initiator.sender.target.in": ",".join(user_wallets),
            "timestamp.gt": timestamp_range[0],
            "timestamp.lt": timestamp_range[1],
            "status": "applied",
            "limit": 10000,
            "offset": len(transactions),
            "quote": "Eur"}
        transactions += get_query_result(url, parameters)

        if len(transactions) != parameters["offset"] + parameters["limit"]:
            break

    return transactions
