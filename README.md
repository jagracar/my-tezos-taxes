# my-tezos-taxes

Some scripts that i use to generate my tezos tax reports.

## Warning

I'm just an astronomer and not a tax expert. Use these scripts at your own
risk. Things might be wrong, so it's better that you double check before
you use this information.

Yes, a lot of things are missing. I will probably not include them if i
never use them (DeFi), but you are free to extend the scripts to your needs.

## How to run it

Edit [user_wallets.json](data/user_wallets.json) and
[baker_wallets.json](data/baker_wallets.json) with your personal information.

Edit [tax_parameters.json](data/tax_parameters.json) with your country specific tax
parameters.

Add any needed operation correction to [operation_corrections.json](data/operation_corrections.json).

Run the scripts using python3:

```bash
cd my-tezos-taxes/python
python3 walletOperations.py
python3 tokenTransfers.py
python3 calculateTaxes.py
```

After few seconds you will have the tax report and some csv files will be saved in the [data directory](data).
