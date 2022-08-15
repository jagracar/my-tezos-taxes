import os.path
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from taxUtils import *

pd.set_option('display.max_rows', None)

## This utility script tells you how many transactions are not yet categorised

# Define the data directory
data_directory = "../data"
 
# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "user_wallets.json"))

# Load the csv file containing all the user operations
file_name = "operations_%s.csv" % list(user_wallets.keys())[0]
operations = pd.read_csv(os.path.join(data_directory, file_name), parse_dates=["timestamp"], keep_default_na=False)

# Change the kind column data type to categorical
operations["kind"] = pd.Categorical(operations["kind"])

cond = (operations["kind"] == "")
missing_kinds = operations[cond]
print("Tx types requiring attention")
print(missing_kinds.groupby(["target", "entrypoint"])["hash"].count().to_string(index=True))
