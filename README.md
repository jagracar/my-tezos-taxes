# my-tezos-taxes

Some scripts that i use to generate my tezos tax reports.

## Warning

I'm just an astronomer and not a tax expert. Use these scripts at your own
risk. Things might be wrong, so it's better that you double check before
you use this information.

Yes, a lot of things are missing. I will probably not include them if i
never use them (defi), but you are free to extend the scripts to your needs.

## How to run it

Edit [walletTransactions.py](python/walletTransactions.py) with your personal information.

Run the scrip using python3:

```bash
cd my-tezos-taxes/python
python3 walletTransactions.py
```

After few seconds you will find a csv file in the [data directory](data).
