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

# Load the csv files containing all the user token details
file_name = "minted_tokens_%s.csv" % user_first_wallet
minted_tokens = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

file_name = "collected_tokens_%s.csv" % user_first_wallet
collected_tokens = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

file_name = "dropped_tokens_%s.csv" % user_first_wallet
dropped_tokens = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

file_name = "sold_tokens_%s.csv" % user_first_wallet
sold_tokens = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

file_name = "transferred_tokens_%s.csv" % user_first_wallet
transferred_tokens = pd.read_csv(os.path.join(data_directory, "output", file_name), parse_dates=["timestamp"], keep_default_na=False)

# Change the token_id column data type to string
minted_tokens = minted_tokens.astype({"token_id": str})
collected_tokens = collected_tokens.astype({"token_id": str})
dropped_tokens = dropped_tokens.astype({"token_id": str})
sold_tokens = sold_tokens.astype({"token_id": str})
transferred_tokens = transferred_tokens.astype({"token_id": str})

# Load the tax parameters provided by the user
tax_parameters = read_json_file(os.path.join(data_directory, "input", "tax_parameters.json"))
start_date = pd.to_datetime(tax_parameters["start_date"])
end_date = pd.to_datetime(tax_parameters["end_date"])
hold_period = 365 * tax_parameters["hold_period_in_years"]
language = tax_parameters["language"]
fiat_coin = ("euros" if language == "english" else "Euro") if tax_parameters["fiat_coin"] == "eur" else "USD"

# Get the token trades information
token_trades = get_token_trades(collected_tokens, dropped_tokens, sold_tokens, transferred_tokens, hold_period)

# Save the token trades as a csv file
token_trades_file_name = "token_trades_%s.csv" % user_first_wallet
token_trades.to_csv(os.path.join(data_directory, "output", token_trades_file_name), index=False)

# Get the tez exchange gains associated to collect and tez exchange operations
tez_exhange_gains = get_tez_exchange_gains(operations, hold_period)

# Select the data that should be considered for the tax calculations
cond = (operations["timestamp"] >= start_date) & (operations["timestamp"] <= end_date)
operations = operations[cond]
cond = (minted_tokens["timestamp"] >= start_date) & (minted_tokens["timestamp"] <= end_date)
minted_tokens = minted_tokens[cond]
cond = (collected_tokens["timestamp"] >= start_date) & (collected_tokens["timestamp"] <= end_date)
collected_tokens = collected_tokens[cond]
cond = (dropped_tokens["timestamp"] >= start_date) & (dropped_tokens["timestamp"] <= end_date)
dropped_tokens = dropped_tokens[cond]
cond = (sold_tokens["timestamp"] >= start_date) & (sold_tokens["timestamp"] <= end_date)
sold_tokens = sold_tokens[cond]
cond = (transferred_tokens["timestamp"] >= start_date) & (transferred_tokens["timestamp"] <= end_date)
transferred_tokens = transferred_tokens[cond]
cond = (token_trades["sell_timestamp"] >= start_date) & (token_trades["sell_timestamp"] <= end_date) & (token_trades["taxed_gain"] != 0)
token_trades = token_trades[cond]
cond = (tez_exhange_gains["timestamp"] >= start_date) & (tez_exhange_gains["timestamp"] <= end_date)
tez_exhange_gains = tez_exhange_gains[cond]

# Use the correct fiat columns
if fiat_coin in ["euros", "Euro"]:
    tez_to_fiat = operations["tez_to_euros"]
    token_trades_buy_fiat = token_trades["buy_price_euros"]
    token_trades_sell_fiat = token_trades["sell_price_euros"]
    token_trades_gain_fiat = token_trades["taxed_gain_euros"]
    tez_exchange_gain_fiat = tez_exhange_gains["taxed_gain_euros"]
else:
    tez_to_fiat = operations["tez_to_usd"]
    token_trades_buy_fiat = token_trades["buy_price_usd"]
    token_trades_sell_fiat = token_trades["sell_price_usd"]
    token_trades_gain_fiat = token_trades["taxed_gain_usd"]
    tez_exchange_gain_fiat = tez_exhange_gains["taxed_gain_usd"]

# Print some details
if language == "english":
    print("\n Summary for the period between %s and %s." % (start_date, end_date))
    print(" %i operations were found for that period." % len(operations))

    print("\n Total amount of tez received by the user wallets: %.2f tez (%.2f %s).\n" % (
        operations["received_amount"].sum(), (operations["received_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) bought in exchanges." % (
        operations["buy_tez_amount"].sum(), (operations["buy_tez_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from primary sales of the user minted art." % (
        operations["primary_art_sale_amount"].sum(), (operations["primary_art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from secondary sales of the user minted art." % (
        operations["secondary_art_sale_amount"].sum(), (operations["secondary_art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from reselling NFTs minted by other artists." % (
        operations["collection_sale_amount"].sum(), (operations["collection_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from prizes (hackathons, community rewards, etc)." % (
        operations["prize_amount"].sum(), (operations["prize_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from staking rewards." % (
        operations["staking_rewards_amount"].sum(), (operations["staking_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from baking." % (
        operations["baking_amount"].sum(), (operations["baking_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from endorsing rewards." % (
        operations["endorsing_rewards_amount"].sum(), (operations["endorsing_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) came from other sources." % (
        operations["received_amount_others"].sum(), (operations["received_amount_others"] * tez_to_fiat).sum(), fiat_coin))

    print("\n Total amount of tez spent with the user wallets: %.2f tez (%.2f %s).\n" % (
        (operations["spent_amount"] + operations["active_offer_amount"] + operations["spent_fees"]).sum(),
        ((operations["spent_amount"] + operations["active_offer_amount"] + operations["spent_fees"]) * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) sold in exchanges." % (
        operations["sell_tez_amount"].sum(), (operations["sell_tez_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) were spent collecting other artists art." % (
        operations["collect_amount"].sum(), (operations["collect_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) are still in active offers to collect other artists art." % (
        operations["active_offer_amount"].sum(), (operations["active_offer_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) were spent in donations." % (
        operations["donation_amount"].sum(), (operations["donation_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) were spent in transaction fees." % (
        operations["spent_fees"].sum(), (operations["spent_fees"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) were spent in other uses." % (
        operations["spent_amount_others"].sum(), (operations["spent_amount_others"] * tez_to_fiat).sum(), fiat_coin))

    print("\n NFT operations associated to the user wallets:\n")

    if minted_tokens.size > 0:
        print("   Minted %i tokens." % (minted_tokens["token_id"] + minted_tokens["token_address"]).unique().size)

    if collected_tokens.size > 0:
        print("   Collected %i tokens from other artists." % (collected_tokens["token_id"] + collected_tokens["token_address"]).unique().size)

    if dropped_tokens.size > 0:
        print("   Received %i tokens as free drops." % (dropped_tokens["token_id"] + dropped_tokens["token_address"]).unique().size)

    if sold_tokens.size > 0:
        print("   Sold %i tokens collected from other artists." % (sold_tokens["token_id"] + sold_tokens["token_address"]).unique().size)

    if transferred_tokens.size > 0:
        print("   Burned or transferred to other users %i tokens." % (transferred_tokens["token_id"] + transferred_tokens["token_address"]).unique().size)

    print("\n Taxable gains:\n")
    print("   %.2f tez (%.2f %s) from sales of the user minted art." % (
        operations["art_sale_amount"].sum(), (operations["art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))

    if token_trades_gain_fiat.sum() > 0:
        print("   %.2f tez (%.2f %s) from trades of NFTs minted by other artists." % (
            token_trades["taxed_gain"].sum(), token_trades_gain_fiat.sum(), fiat_coin))

    print("   %.2f tez (%.2f %s) from prizes (hackathons, community rewards, etc)." % (
        operations["prize_amount"].sum(), (operations["prize_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) from staking rewards." % (
        operations["staking_rewards_amount"].sum(), (operations["staking_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) from baking." % (
        operations["baking_amount"].sum(), (operations["baking_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) from endorsing rewards." % (
        operations["endorsing_rewards_amount"].sum(), (operations["endorsing_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))

    if tez_exchange_gain_fiat.sum() > 0:
        print("   %.2f %s from tez exchange gains associated to tez exchange operations (using the FIFO method)." % (
            tez_exchange_gain_fiat.sum(), fiat_coin))

    print("\n Possible tax-deductible losses:\n")
    print("   %.2f tez (%.2f %s) from tezos transaction fees." % (
        operations["spent_fees"].sum(), (operations["spent_fees"] * tez_to_fiat).sum(), fiat_coin))

    if operations["donation_amount"].sum() > 0:
        print("   %.2f tez (%.2f %s) from donations." % (
            operations["donation_amount"].sum(), (operations["donation_amount"] * tez_to_fiat).sum(), fiat_coin))

    if token_trades_gain_fiat.sum() < 0:
        print("   %.2f tez (%.2f %s) from trades of NFTs minted by other artists." % (
            abs(token_trades["gain"].sum()), abs(token_trades_gain_fiat.sum()), fiat_coin))

    if tez_exchange_gain_fiat.sum() < 0:
        print("   %.2f %s from tez exchange losses associated to tez exchange operations (using the FIFO method)." % (
            abs(tez_exchange_gain_fiat.sum()), fiat_coin))

    print("\n You can find the token trades information in %s\n" % os.path.join(data_directory, "output", token_trades_file_name))
elif language == "german":
    print("\nFür den Zeitraum vom %s bis %s wurden %i Transaktionen berücksichtigt." % (start_date, end_date, len(operations)))

    print("\n Summe der eingenommenen Tezos: %.2f tez (%.2f %s).\n" % (
        operations["received_amount"].sum(), (operations["received_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) auf einer Handelsplattform gekauft." % (
        operations["buy_tez_amount"].sum(), (operations["buy_tez_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Erstverkauf selbst geprägter Kunst." % (
        operations["primary_art_sale_amount"].sum(), (operations["primary_art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Zweitverkauf selbst geprägter Kunst." % (
        operations["secondary_art_sale_amount"].sum(), (operations["secondary_art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Verkäufe von Werken anderer Künstler." % (
        operations["collection_sale_amount"].sum(), (operations["collection_sale_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Preise (Hackathons, Vergütungen durch eine Community, etc.)." % (
        operations["prize_amount"].sum(), (operations["prize_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Staking." % (
        operations["staking_rewards_amount"].sum(), (operations["staking_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Baking." % (
        operations["baking_amount"].sum(), (operations["baking_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Einkünfte durch Endorsing Rewards." % (
        operations["endorsing_rewards_amount"].sum(), (operations["endorsing_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) aus anderen Quellen." % (
        operations["received_amount_others"].sum(), (operations["received_amount_others"] * tez_to_fiat).sum(), fiat_coin))

    print("\n Summe der ausgegebenen Tezos: %.2f tez (%.2f %s).\n" % (
        (operations["spent_amount"] + operations["active_offer_amount"] + operations["spent_fees"]).sum(),
        ((operations["spent_amount"] + operations["active_offer_amount"] + operations["spent_fees"]) * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Ausgaben auf einer Handelsplattform." % (
        operations["sell_tez_amount"].sum(), (operations["sell_tez_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Ausgaben für Käufe von Werken anderer Künstler." % (
        operations["collect_amount"].sum(), (operations["collect_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) sind aktuelle Gebote für Werke anderer Künstler." % (
        operations["active_offer_amount"].sum(), (operations["active_offer_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) wurden gespendet." % (
        operations["donation_amount"].sum(), (operations["donation_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Ausgaben für Transaktionsgebühren." % (
        operations["spent_fees"].sum(), (operations["spent_fees"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) Ausgaben für andere Zwecke." % (
        operations["spent_amount_others"].sum(), (operations["spent_amount_others"] * tez_to_fiat).sum(), fiat_coin))

    print("\n NFT-Transaktionen der eigenen Wallets:\n")

    if minted_tokens.size > 0:
        print("   %i Token geprägt." % (minted_tokens["token_id"] + minted_tokens["token_address"]).unique().size)

    if collected_tokens.size > 0:
        print("   %i Token anderer Künstler erworben." % (collected_tokens["token_id"] + collected_tokens["token_address"]).unique().size)

    if dropped_tokens.size > 0:
        print("   %i Token kostenlos erhalten." % (dropped_tokens["token_id"] + dropped_tokens["token_address"]).unique().size)

    if sold_tokens.size > 0:
        print("   %i Token anderer Künstler verkauft." % (sold_tokens["token_id"] + sold_tokens["token_address"]).unique().size)

    if transferred_tokens.size > 0:
        print("   %i Token wurden geburned oder verschickt." % (transferred_tokens["token_id"] + transferred_tokens["token_address"]).unique().size)

    print("\n Steuerpflichtige Einnahmen:\n")
    print("   %.2f tez (%.2f %s) durch Verkäufe eigener NFTs." % (
        operations["art_sale_amount"].sum(), (operations["art_sale_amount"] * tez_to_fiat).sum(), fiat_coin))

    if token_trades_gain_fiat.sum() > 0:
        print("   %.2f tez (%.2f %s) durch Handel mit Werken anderer Künstler." % (
            token_trades["taxed_gain"].sum(), token_trades_gain_fiat.sum(), fiat_coin))

    print("   %.2f tez (%.2f %s) durch Preise (Hackathons, Vergütungen durch eine Community, etc)." % (
        operations["prize_amount"].sum(), (operations["prize_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) durch Staking." % (
        operations["staking_rewards_amount"].sum(), (operations["staking_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) durch Baking." % (
        operations["baking_amount"].sum(), (operations["baking_amount"] * tez_to_fiat).sum(), fiat_coin))
    print("   %.2f tez (%.2f %s) durch Endorsing Rewards." % (
        operations["endorsing_rewards_amount"].sum(), (operations["endorsing_rewards_amount"] * tez_to_fiat).sum(), fiat_coin))

    if tez_exchange_gain_fiat.sum() > 0:
        print("   %.2f %s durch Einkünfte auf einer Handelsplattform (mittels FIFO Methode)." % (
            tez_exchange_gain_fiat.sum(), fiat_coin))

    print("\n Möglicherweise steuerpflichtige Ausgaben:\n")
    print("   %.2f tez (%.2f %s) durch Tezos Transaktionsgebühren." % (
        operations["spent_fees"].sum(), (operations["spent_fees"] * tez_to_fiat).sum(), fiat_coin))

    if operations["donation_amount"].sum() > 0:
        print("   %.2f tez (%.2f %s) durch Spenden." % (
            operations["donation_amount"].sum(), (operations["donation_amount"] * tez_to_fiat).sum(), fiat_coin))

    if token_trades_gain_fiat.sum() < 0:
        print("   %.2f tez (%.2f %s) durch Handel mit Werken anderer Künstler." % (
            abs(token_trades["gain"].sum()), abs(token_trades_gain_fiat.sum()), fiat_coin))

    if tez_exchange_gain_fiat.sum() < 0:
        print("   %.2f %s Verluste auf einer Handelsplattform (mittels FIFO Methode)." % (
            abs(tez_exchange_gain_fiat.sum()), fiat_coin))

    print("\n Details zu den Transaktionen finden sich in folgender Tabelle: %s\n" % os.path.join(data_directory, "output", token_trades_file_name))

if True:
    print(" Global effective gains or losses (using the FIFO method for tez and NFTs):\n")
    print("   Bought tez for %.2f %s" % (
        ((operations["sell_tez_amount"] + operations["collect_amount"] ) * tez_to_fiat).sum() - tez_exchange_gain_fiat.sum() + token_trades_buy_fiat.sum(), fiat_coin))
    print("   Sold tez for %.2f %s" % (
        ((operations["sell_tez_amount"] + operations["collect_amount"] + operations["art_sale_amount"]) * tez_to_fiat).sum() + token_trades_sell_fiat.sum(), fiat_coin))
    print("   Gains/losses: %.2f %s\n" % (
        (operations["art_sale_amount"] * tez_to_fiat).sum() + tez_exchange_gain_fiat.sum() + token_trades_gain_fiat.sum(), fiat_coin))
