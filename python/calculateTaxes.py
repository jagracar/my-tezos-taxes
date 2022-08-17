import os.path
import numpy as np
import pandas as pd
from taxUtils import *

# Define the data directory
data_directory = "../data"
 
# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "user_wallets.json"))

# Load the parameters that should be used for the tax calculation
tax_parameters = read_json_file(os.path.join(data_directory, "tax_parameters.json"))

# Load the csv file containing all the user operations
file_name = "operations_%s.csv" % list(user_wallets.keys())[0]
operations = pd.read_csv(os.path.join(data_directory, file_name), parse_dates=["timestamp"], keep_default_na=False)

# Change the kind column data type to categorical
operations["kind"] = pd.Categorical(operations["kind"])

# Use the correct tez to fiat column
fiat_coin = "USD" if tax_parameters["fiat_coin"] == "usd" else "euros"
tez_to_fiat = operations["tez_to_usd"] if fiat_coin == "USD" else operations["tez_to_euros"]

# Check the tez amount received by the user
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"]
operations["received_amount"] = np.where(cond, operations["amount"], 0)
operations["received_amount_fiat"] = operations["received_amount"] * tez_to_fiat

# Check the tez amount received by the user from sales coming from their own art
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"] & operations["art_sale"]
operations["art_sale_amount"] = np.where(cond, operations["amount"], 0)
operations["art_sale_amount_fiat"] = operations["art_sale_amount"] * tez_to_fiat

# Check the tez amount received by the user from sales from their collected NFTs
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"] & operations["collection_sale"]
operations["collection_sale_amount"] = np.where(cond, operations["amount"], 0)
operations["collection_sale_amount_fiat"] = operations["collection_sale_amount"] * tez_to_fiat

# Check the tez amount received by the user from different kinds of prizes
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"] & operations["prize"]
operations["prize_amount"] = np.where(cond, operations["amount"], 0)
operations["prize_amount_fiat"] = operations["prize_amount"] * tez_to_fiat

# Check the tez amount received by the user from staking rewards
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"] & operations["staking"]
operations["staking_rewards_amount"] = np.where(cond, operations["amount"], 0)
operations["staking_rewards_amount_fiat"] = operations["staking_rewards_amount"] * tez_to_fiat

# Check the tez amount received by the user from other reasons
# (ignore operations should not be counted)
cond = operations["is_target"] & ~operations["ignore"] & ~operations["art_sale"] & ~operations["collection_sale"] & ~operations["prize"] & ~operations["staking"]
operations["received_amount_others"] = np.where(cond, operations["amount"], 0)
operations["received_amount_others_fiat"] = operations["received_amount_others"] * tez_to_fiat

# Check the tez amount spent by the user
# (ignore operations should not be counted)
cond = operations["is_sender"] & ~operations["ignore"]
operations["spent_amount"] = np.where(cond, operations["amount"], 0)
operations["spent_amount_fiat"] = operations["spent_amount"] * tez_to_fiat

# Check the tez amount spent by the user collecting NFTs
# (ignore operations should not be counted)
cond = operations["is_sender"] & ~operations["ignore"] & operations["collect"]
operations["collect_amount"] = np.where(cond, operations["amount"], 0)
operations["collect_amount_fiat"] = operations["collect_amount"] * tez_to_fiat

# Check the tez amount spent by the user in donations
# (ignore operations should not be counted)
cond = operations["is_sender"] & ~operations["ignore"] & operations["donation"]
operations["donation_amount"] = np.where(cond, operations["amount"], 0)
operations["donation_amount_fiat"] = operations["donation_amount"] * tez_to_fiat

# Check the tez amount spent by the user by other reasons
# (ignore operations should not be counted)
cond = operations["is_sender"] & ~operations["ignore"] & ~operations["collect"] & ~operations["donation"]
operations["spent_amount_others"] = np.where(cond, operations["amount"], 0)
operations["spent_amount_others_fiat"] = operations["spent_amount_others"] * tez_to_fiat

# Check the fees spent by the user
# (ignore operations count because the fees were always spent)
cond = operations["is_initiator"] | operations["is_sender"]
operations["spent_fees"] = np.where(cond, operations["fees"], 0)
operations["spent_fees_fiat"] = operations["spent_fees"] * tez_to_fiat

# Select the operations that should be considered for the tax calculations
start_date = tax_parameters["start_date"]
end_date = tax_parameters["end_date"]
cond = (
    (operations["timestamp"] >= pd.to_datetime(start_date)) & 
    (operations["timestamp"] <= pd.to_datetime(end_date)))
tax_operations = operations[cond]

# Print some details
print("\n Summary for the period between %s and %s." % (start_date, end_date))
print(" %i operations were found for that period." % len(tax_operations))
print("\n Total amount of tez received by the user wallets: %.2f tez (%.2f %s).\n" % (
    tax_operations["received_amount"].sum(), tax_operations["received_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) came from sales of the user minted art." % (
    tax_operations["art_sale_amount"].sum(), tax_operations["art_sale_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) came from reselling NFTs minted by other artists." % (
    tax_operations["collection_sale_amount"].sum(), tax_operations["collection_sale_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) came from prizes (hackathons, community rewards, etc)." % (
    tax_operations["prize_amount"].sum(), tax_operations["prize_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) came from staking rewards." % (
    tax_operations["staking_rewards_amount"].sum(), tax_operations["staking_rewards_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) came from other sources." % (
    tax_operations["received_amount_others"].sum(), tax_operations["received_amount_others_fiat"].sum(), fiat_coin))
print("\n Total amount of tez spent with the user wallets: %.2f tez (%.2f %s).\n" % (
    tax_operations["spent_amount"].sum() + tax_operations["spent_fees"].sum(), tax_operations["spent_amount_fiat"].sum() + tax_operations["spent_fees_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) were spent collecting other artists art." % (
    tax_operations["collect_amount"].sum(), tax_operations["collect_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) were spent in donations." % (
    tax_operations["donation_amount"].sum(), tax_operations["donation_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) were spent in transaction fees." % (
    tax_operations["spent_fees"].sum(), tax_operations["spent_fees_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) were spent in other uses." % (
    tax_operations["spent_amount_others"].sum(), tax_operations["spent_amount_others_fiat"].sum(), fiat_coin))

# Load the csv file containing all the user token transfers
file_name = "token_transfers_%s.csv" % list(user_wallets.keys())[0]
token_transfers = pd.read_csv(os.path.join(data_directory, file_name), parse_dates=["timestamp"], keep_default_na=False)

# Get the information about the minted tokens
cond = operations["is_sender"] & ~operations["ignore"] & operations["mint"]
columns = ["token_name", "token_id", "token_editions", "token_address", "kind",
           "timestamp"]
minted_tokens = operations[cond][columns].copy()
minted_tokens = minted_tokens.reset_index(drop=True)
minted_tokens = fix_missing_token_information(minted_tokens, token_transfers, kind="mint")

# Get the information about the collected tokens
cond = operations["is_sender"] & ~operations["ignore"] & operations["collect"]
columns = ["token_name", "token_id", "token_editions", "token_address", "kind",
           "collect_amount", "collect_amount_fiat", "timestamp"]
collected_tokens = operations[cond][columns].copy()
collected_tokens = collected_tokens.reset_index(drop=True)
collected_tokens = fix_missing_token_information(collected_tokens, token_transfers, kind="mint")

# Get the information about the sold tokens from other artists
cond = operations["is_target"] & ~operations["ignore"] & operations["collection_sale"]
columns = ["token_name", "token_id", "token_editions", "token_address", "kind",
           "collection_sale_amount", "collection_sale_amount_fiat", "timestamp"]
sold_tokens = operations[cond][columns].copy()
sold_tokens = sold_tokens.reset_index(drop=True)
sold_tokens = fix_missing_token_information(sold_tokens, token_transfers, kind="send")

# Check when the sold tokens were collected and their collected price
collect_timestamps = []
collect_amounts = []
collect_amounts_fiat = []

for index, token in sold_tokens.iterrows():
    token_id = token["token_id"]
    token_address = token["token_address"]

    # Check if the token was collected
    cond = ((collected_tokens["token_id"] == token_id) & 
            (collected_tokens["token_address"] == token_address))

    if cond.sum() > 0:
        selected_tokens = collected_tokens[cond]
        collect_timestamps.append(selected_tokens["timestamp"].values[0])
        collect_amounts.append(selected_tokens["collect_amount"].values[0])
        collect_amounts_fiat.append(selected_tokens["collect_amount_fiat"].values[0])
    else:
        # Check if the token was dropped for free
        cond = ((token_transfers["token_id"] == token_id) & 
                (token_transfers["token_address"] == token_address) & 
                (token_transfers["receive"]))

        if cond.sum() > 0:
            transfers = token_transfers[cond]
            collect_timestamps.append(transfers["timestamp"].values[0])
            collect_amounts.append(0)
            collect_amounts_fiat.append(0)
        else:
            # This should not happen
            # Assume the token was dropped for free
            collect_timestamps.append(token["timestamp"])
            collect_amounts.append(0)
            collect_amounts_fiat.append(0)

sold_tokens["collect_amount"] = collect_amounts
sold_tokens["collect_amount_fiat"] = collect_amounts_fiat
sold_tokens["collect_timestamp"] = pd.to_datetime(collect_timestamps, utc=True)

# Calculate the sale gains and the hold time
sold_tokens["sale_gains"] = sold_tokens["collection_sale_amount"] - sold_tokens["collect_amount"]
sold_tokens["sale_gains_fiat"] = sold_tokens["collection_sale_amount_fiat"] - sold_tokens["collect_amount_fiat"]
sold_tokens["token_hold_time"] = sold_tokens["timestamp"] - sold_tokens["collect_timestamp"]

# Check if the sales are tax free because the user hold the tokens long enough
sold_tokens["tax_free"] = sold_tokens["token_hold_time"].dt.days > 365 * tax_parameters["hold_period_in_years"]

# Print some details
print("\n NFT operations associated to the user wallets:\n")

cond = ((minted_tokens["timestamp"] >= pd.to_datetime(start_date)) & 
        (minted_tokens["timestamp"] <= pd.to_datetime(end_date)))
print("   Minted %i tokens." % len(minted_tokens[cond]))

cond = ((collected_tokens["timestamp"] >= pd.to_datetime(start_date)) & 
        (collected_tokens["timestamp"] <= pd.to_datetime(end_date)))
print("   Collected %i tokens from other artists." % len(collected_tokens[cond]))

cond = ((sold_tokens["timestamp"] >= pd.to_datetime(start_date)) & 
        (sold_tokens["timestamp"] <= pd.to_datetime(end_date)))
print("   Sold %i tokens collected from other artists." % len(sold_tokens[cond]))

print("\n Taxable gains:\n")

cond = ((sold_tokens["timestamp"] >= pd.to_datetime(start_date)) & 
        (sold_tokens["timestamp"] <= pd.to_datetime(end_date)) & 
        (~sold_tokens["tax_free"]))
print("   %.2f tez (%.2f %s) from sales of the user minted art." % (
    tax_operations["art_sale_amount"].sum(), tax_operations["art_sale_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) from trades of NFTs minted by other artists." % (
    sold_tokens[cond]["sale_gains"].sum(), sold_tokens[cond]["sale_gains_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) from prizes (hackathons, community rewards, etc)." % (
    tax_operations["prize_amount"].sum(), tax_operations["prize_amount_fiat"].sum(), fiat_coin))
print("   %.2f tez (%.2f %s) from staking rewards." % (
    tax_operations["staking_rewards_amount"].sum(), tax_operations["staking_rewards_amount_fiat"].sum(), fiat_coin))
print("")

"""
##########
cond = operations["received_amount"] > 0
buy = operations["received_amount"][cond].to_numpy()
buy_timestamp = operations["timestamp"][cond].to_numpy()
buy_exchange = operations["tez_to_euros"][cond].to_numpy()

cond = (operations["spent_amount"] > 0) | (operations["spent_fees"] > 0)
spend = operations["spent_amount"][cond].to_numpy()
fees = operations["spent_fees"][cond].to_numpy()
spend_timestamp = operations["timestamp"][cond].to_numpy()
is_collect = operations["collect_amount"][cond].to_numpy() > 0
spend_exchange = operations["tez_to_euros"][cond].to_numpy()

accumulated_gains_euros = 0

for i in range(0, len(spend)):
    fee_value = fees[i]

    while fee_value > 0:
        if fee_value < buy[0]:
            buy[0] -= fee_value
            fee_value = 0
        elif fee_value >= buy[0]:
            fee_value -= buy[0]
            buy = buy[1:]
            buy_timestamp = buy_timestamp[1:]
            buy_exchange = buy_exchange[1:]

    spend_value = spend[i]

    while spend_value > 0:
        if spend_value < buy[0]:
            gain_euros = spend_value * (spend_exchange[i] - buy_exchange[0])
            accumulated_gains_euros += gain_euros
            buy[0] -= spend_value
            spend_value = 0
        elif spend_value >= buy[0]:
            gain_euros = buy[0] * (spend_exchange[i] - buy_exchange[0])
            accumulated_gains_euros += gain_euros
            spend_value -= buy[0]
            buy = buy[1:]
            buy_timestamp = buy_timestamp[1:]
            buy_exchange = buy_exchange[1:]
"""
