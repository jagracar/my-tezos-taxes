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

# Load the csv file containing all the user token trades
file_name = "token_trades_%s.csv" % user_first_wallet
token_trades = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["buy_timestamp", "sell_timestamp"], keep_default_na=False)

# Load the tax parameters provided by the user
tax_parameters = read_json_file(os.path.join(data_directory, "input", "tax_parameters.json"))
start_date = pd.to_datetime(tax_parameters["start_date"])
end_date = pd.to_datetime(tax_parameters["end_date"])
hold_period = 365 * tax_parameters["hold_period_in_years"]
language = tax_parameters["language"]
fiat_coin = ("euros" if language == "english" else "Euro") if tax_parameters["fiat_coin"] == "eur" else "USD"

# Get the tez exchange gains associated to collect and tez exchange operations
tez_exhange_gains = get_tez_exchange_gains(operations, hold_period)

# Select the data that should be considered for the tax calculations
cond = (operations["timestamp"] >= start_date) & (operations["timestamp"] <= end_date)
operations = operations[cond]
cond = (token_trades["sell_timestamp"] >= start_date) & (token_trades["sell_timestamp"] <= end_date)
token_trades = token_trades[cond]
cond = (tez_exhange_gains["timestamp"] >= start_date) & (tez_exhange_gains["timestamp"] <= end_date)
tez_exhange_gains = tez_exhange_gains[cond]

# Use the correct fiat columns
if fiat_coin in ["euros", "Euro"]:
    tez_to_fiat = "tez_to_euros"
    taxed_gain_fiat = "taxed_gain_euros"
    token_taxed_gain_fiat = "token_taxed_gain_euros"
else:
    tez_to_fiat = "tez_to_usd"
    taxed_gain_fiat = "taxed_gain_usd"
    token_taxed_gain_fiat = "token_taxed_gain_usd"

# Save the tax information in the operations data frame
operations[taxed_gain_fiat] = tez_exhange_gains[taxed_gain_fiat]
operations[token_taxed_gain_fiat] = 0.0

for i, token in token_trades.iterrows():
    cond = operations["timestamp"] == token["sell_timestamp"]
    cond &= operations["token_id"] == str(token["token_id"])
    cond &= operations["token_address"] == token["token_address"]
    operations.loc[cond, token_taxed_gain_fiat] = token[taxed_gain_fiat]

operations[token_taxed_gain_fiat] += operations["art_sale_amount"] * operations[tez_to_fiat]

# Group operations that are associated to the same operation hash
operation_groups = operations.iloc[[0]]
group_counter = 0
counter = 1
n_operations = len(operations)
bool_keywords = [
    "internal", "ignore", "mint", "collect", "active_offer", "art_sale",
    "collection_sale", "staking", "origination", "reveal", "delegation",
    "prize", "donation", "buy_tez", "sell_tez"]
amount_keywords = [
    "received_amount", "art_sale_amount", "collection_sale_amount",
    "staking_rewards_amount", "prize_amount", "buy_tez_amount",
    "received_amount_others", "spent_amount", "collect_amount",
    "active_offer_amount", "donation_amount", "sell_tez_amount",
    "spent_amount_others", "spent_fees", taxed_gain_fiat, token_taxed_gain_fiat]

while counter < n_operations:
    # Get the next operation
    operation = operations.iloc[counter]

    # Check if the operation link coincides with the current operation group
    if operation["tzkt_link"] == operation_groups.iloc[group_counter]["tzkt_link"]:
        # Add the operation information to the grouped operation
        operation_groups.loc[group_counter, "tez_balance"] = operation["tez_balance"]

        for keyword in bool_keywords:
            operation_groups.loc[group_counter, keyword] |= operation[keyword]

        for keyword in amount_keywords:
            operation_groups.loc[group_counter, keyword] += operation[keyword]

        if (operation_groups.loc[group_counter, "token_id"] == "" and 
            operation_groups.loc[group_counter, "token_address"] == ""):
            operation_groups.loc[group_counter, "token_id"] = operation["token_id"]
            operation_groups.loc[group_counter, "token_address"] = operation["token_address"]
    else:
        operation_groups = pd.concat(
            [operation_groups, operations.iloc[[counter]]], ignore_index=True)
        group_counter += 1

    # Increase the counter
    counter += 1

# Add a column with the token link
def create_token_link(operation):
    token_id = operation["token_id"]
    token_address = operation["token_address"]

    if token_id != "" and token_address != "":
        if token_address in TOKEN_NAMES:
            token_name = TOKEN_NAMES[token_address]

            return get_token_link(token_name, token_id, token_address)

    return ""

operation_groups["token_link"] = operation_groups.apply(create_token_link, axis=1)

# Add a column with the operation tax kind
operation_groups["tax_kind"] = "other" if language == "english" else "anderes"
operation_groups.loc[operation_groups["mint"], "tax_kind"] = "mint NFT" if language == "english" else "NFT prägen"
operation_groups.loc[operation_groups["staking"], "tax_kind"] = "staking rewards"
operation_groups.loc[operation_groups["collect"], "tax_kind"] = "buy NFT" if language == "english" else "NFT kaufen"
operation_groups.loc[operation_groups["art_sale"], "tax_kind"] = "sell NFT" if language == "english" else "NFT verkaufen"
operation_groups.loc[operation_groups["collection_sale"], "tax_kind"] = "sell NFT" if language == "english" else "NFT verkaufen"
operation_groups.loc[operation_groups["prize"], "tax_kind"] = "prize" if language == "english" else "Preis"
operation_groups.loc[operation_groups["buy_tez"], "tax_kind"] = "buy XTZ" if language == "english" else "XTZ kaufen"
operation_groups.loc[operation_groups["sell_tez"], "tax_kind"] = "sell XTZ for " + fiat_coin if language == "english" else "XTZ verkaufen"

# Select only tax relevant operations
cond = ~operation_groups["ignore"]
cond &= ~operation_groups["internal"]
cond &= operation_groups["applied"]
operation_groups = operation_groups[cond]

# Build the latex table with all the transactions
table = "\\begin{longtable}{llrrrrrcc}\n"
table += "\\hiderowcolors\n"
table += "\\toprule[0.1mm]\n"

if language == "english":
    table += "Date & Kind & \\multicolumn{1}{r}{Received} & \\multicolumn{1}{r}{Sent}  & \\multicolumn{1}{r}{XTZ price}           & \\multicolumn{1}{r}{Gains/Losses}       & \\multicolumn{1}{r}{Fees}                & NFT  & Transaction \\\\\n"
    table += "     &      & \\multicolumn{1}{r}{(XTZ)}    & \\multicolumn{1}{r}{(XTZ)} & \\multicolumn{1}{r}{(" + fiat_coin + ")} & \\multicolumn{1}{r}{(" + fiat_coin +")} & \\multicolumn{1}{r}{(" + fiat_coin + ")} &      &             \\\\\n"
else:
    table += "Datum & Art & \\multicolumn{1}{r}{Erhalten} & \\multicolumn{1}{r}{Gesendet} & \\multicolumn{1}{r}{XTZ Preis}           & \\multicolumn{1}{r}{Gewinne/Verluste}   & \\multicolumn{1}{r}{Gebühren}            & NFT  & Transaktion \\\\\n"
    table += "      &     & \\multicolumn{1}{r}{(XTZ)}    & \\multicolumn{1}{r}{(XTZ)}    & \\multicolumn{1}{r}{(" + fiat_coin + ")} & \\multicolumn{1}{r}{(" + fiat_coin +")} & \\multicolumn{1}{r}{(" + fiat_coin + ")} &      &             \\\\\n"

table += "\\midrule[0.1mm]\n"
table += "\\endhead\n"
table += "\\showrowcolors\n"

for i, operation in operation_groups.iterrows():
    tax_fiat = (
        operation[taxed_gain_fiat] + operation[token_taxed_gain_fiat] +
        (operation["staking_rewards_amount"] + operation["prize_amount"]) * operation[tez_to_fiat])
    table += "%s & %s & %f & %f & %f & %f & %f & %s & %s \\tabularnewline\n" % (
        operation["timestamp"],
        operation["tax_kind"],
        operation["received_amount"],
        operation["spent_amount"],
        operation[tez_to_fiat],
        tax_fiat,
        operation["spent_fees"] * operation[tez_to_fiat],
        "\\href{" + operation["token_link"] + "}{NFT}" if (operation["tax_kind"] != "other" and operation["token_link"] != "") else "",
        "\\href{" + operation["tzkt_link"] + ("}{transaction}" if language == "english" else "}{Transaktion}"))

table += "\\bottomrule[0.1mm]\n"
table += "\\end{longtable}\n"

# Insert the table inside the latex template
with open(os.path.join(data_directory, "input", "transactions_template.tex"), "r") as file:
    template = file.read()

pdflatex_content = template.replace("% INSERT_TABLES_HERE", table)

# Replace any underscore character with spaces
pdflatex_content = pdflatex_content.replace("_", " ")

# Save the pdflatex file
with open(os.path.join(data_directory, "output", "transactions.tex"), "w") as file:
    file.write(pdflatex_content)
