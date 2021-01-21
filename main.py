from dhooks import Webhook, Embed
from datetime import datetime, timezone
import requests
import time
import json
import concurrent.futures

try:
    user_settings = json.loads(open("settings.json", "r").read())
    webhook_url = user_settings["webhook"]
    user_id = user_settings["userID"]
except Exception as err:
    print(f"[ {err} ] \n($) Unable to load 'settings.json' file.")
    exit()

hook = Webhook(webhook_url)
hook_request = requests.get(webhook_url).json()

btc_logo = "https://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/48/Bitcoin-BTC-icon.png"

class Checker:
    def __init__(self, txid_amount, timer):
        self.txid_amount = txid_amount
        self.timer = timer
        self.TEMP_txid = []
        self.txid = []

    def checking_unique(self):
        for unique_TXID in self.TEMP_txid:
            if unique_TXID not in self.txid:
                self.txid.append(unique_TXID)

    def grab_TXID(self, txid_amount):
        if txid_amount != 0:
            for TXIDs in range(txid_amount):
                txid_input = input(f"Enter TXID no. {TXIDs + 1}: ")
                check_TXID = requests.get(f"https://mempool.space/api/tx/{txid_input}/status").text.lower()
                while "invalid" in check_TXID:
                    txid_input = input(f"Invalid input, try again. Enter TXID no. {TXIDs + 1}: ")
                    check_TXID = requests.get(f"https://mempool.space/api/tx/{txid_input}/status").text.lower()
                self.TEMP_txid.append(txid_input)
            self.checking_unique()
        else:
            exit()

    def checking_interval(self, timer, txid_amount):
        if txid_amount != 0:
            self.timer = int(self.timer)
            if self.timer < 30:
                print(f"{timer} second/s may create Discord restrictions or overload the API; changed to 30 seconds to remain safe.")
                self.timer = 30
                print(f"[INTERVAL] Set to {self.timer} seconds.")
            else:
                pass
        else:
            exit()

    def utc_to_local(self, time_format):
        return time_format.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def avatar_check(self, webhook_request, confirmed_embed):
        if webhook_request["avatar"] == None:
            confirmed_embed.set_author(
                name = webhook_request["name"])
        else:
            webhook_avatar = f"https://cdn.discordapp.com/avatars/{webhook_request['id']}/{webhook_request['avatar']}.png"
            confirmed_embed.set_author(
                name = webhook_request["name"],
                icon_url = webhook_avatar
            )

    def fix_time(self, confirmation_time):
        confirmation_time = datetime.strptime(confirmation_time, "%Y-%m-%dT%H:%M:%SZ")
        confirmation_time = self.utc_to_local(confirmation_time)
        confirmation_time = datetime.strftime(confirmation_time, "%m-%d-%Y %I:%M:%S %p")
        return confirmation_time

    def checking(self):
        while len(self.txid) > 0:
            for confirmation in self.txid:
                get_confirm = requests.get(f"https://api.blockcypher.com/v1/btc/main/txs/{confirmation}").json()
                if (get_confirm["confirmations"] == 0):
                    pass
                else:
                    hook.send(f"<@{user_id}>")
                    confirmation_embed = Embed(
                        description = f"[This](https://www.blockchain.com/btc/tx/{confirmation} ' ') transaction has been confirmed.",
                        color = 0xE69138)
                    
                    self.avatar_check(hook_request, confirmation_embed)
                    
                    confirmed_time = get_confirm["confirmed"]
                    confirmed_time = self.fix_time(confirmed_time)

                    fees = get_confirm["fees"] / 100000000

                    confirmation_embed.add_field(
                        name = "Confirmed on", value = str(confirmed_time),
                        inline = True)
                    confirmation_embed.add_field(
                        name = "Transaction fee", value = str(fees) + " BTC",
                        inline = True)
                    confirmation_embed.add_field(
                        name = "TXID/Hash",
                        value = f"[{confirmation}](https://www.blockchain.com/btc/tx/{confirmation} 'TXID/Hash')",
                        inline = False)
                    
                    confirmation_embed.set_thumbnail(btc_logo)
                    
                    hook.send(embed = confirmation_embed)
                    
                    self.txid.remove(confirmation)
            (print("[FINISHED] All listed TXID/s have at least 1 confirmation."), exit()) if len(self.txid) == 0 else time.sleep(int(self.timer))

        print("[FINISHED] All listed TXID/s have at least 1 confirmation.")
        

txid_counter = input("How many TXID/s do you want to check? ")

if txid_counter.isnumeric() == True and int(txid_counter) != 0:
    txid_counter = int(txid_counter)
    try:
        interval = int(input("How frequently should the TXID/s be checked? (in seconds) "))
        checker = Checker(txid_counter, interval)
        checker.grab_TXID(txid_counter)
        checker.checking_interval(interval, txid_counter)
        checker.checking()
    except Exception as err:
        print("\n" + f"{err}".capitalize())
        print("Invalid/no input. Please input appropriate numerical value.")
        exit()
else:
    exit()
