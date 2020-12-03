from dhooks import Webhook, Embed
from datetime import datetime, timezone
import requests
import time
import json

userSettings = json.loads(open("settings.json", "r").read())
webhookURL = userSettings["webhook"]
userID = userSettings["userID"]

hook = Webhook(webhookURL)

txidCounter = int(input("How many TXIDs do you want to check? "))

TEMP_txid = []
for TXIDs in range(txidCounter):
    txidInput = input(f"TXID no. {TXIDs + 1}: ")
    checkTXID = requests.get(
        f"https://mempool.space/api/tx/{txidInput}/status")
    checkTXID = checkTXID.text.lower()
    while "invalid" in checkTXID:
        txidInput = input(f"Invalid input, try again. TXID no. {TXIDs + 1}: ")
        checkTXID = requests.get(
            f"https://mempool.space/api/tx/{txidInput}/status")
        checkTXID = checkTXID.text.lower()
    TEMP_txid.append(txidInput)

txid = []
for uniqueTXID in TEMP_txid:
    if uniqueTXID not in txid:
        txid.append(uniqueTXID)

if txidCounter != 0:
    interval = input(
        "How frequently do you want to check the blockchain? (in seconds) ")
else:
    exit()

if interval == "" or interval.isnumeric() == False:
    print("Invalid/no input. As default, the interval will be set to 60 seconds.")
    interval = 60
else:
    interval = float(interval)
    if (interval < 30):
        print(
            f"{interval} seconds may create Discord restrictions or overload the API; changed to 30 seconds to remain safe.")
        interval = 30

btcLogo = "https://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/48/Bitcoin-BTC-icon.png"
hookRequest = requests.get(webhookURL).json()

def utcToLocal(timeFormat):
    return timeFormat.replace(tzinfo=timezone.utc).astimezone(tz=None)

while len(txid) > 0:
    for confirmation in txid:
        getConfirm = requests.get(
            f"https://api.blockcypher.com/v1/btc/main/txs/{confirmation}").json()
        if (getConfirm["confirmations"] == 0):
            pass
        else:
            hook.send(f"<@{userID}>")
            txidLink = f"[This](https://www.blockchain.com/btc/tx/{confirmation} ' ')"
            confirmationEmbed = Embed(
                description = f"{txidLink} transaction has been confirmed.",
                color = 0xE69138)
            if hookRequest["avatar"] == None:
                confirmationEmbed.set_author(
                    name = hookRequest["name"])
            else:
                webhookAvatar = f"https://cdn.discordapp.com/avatars/{hookRequest['id']}/{hookRequest['avatar']}.png"
                confirmationEmbed.set_author(
                    name = hookRequest["name"], icon_url = webhookAvatar)
            confirmedTime = getConfirm["confirmed"]
            confirmedTime = datetime.strptime(confirmedTime, "%Y-%m-%dT%H:%M:%SZ")
            confirmedTime = utcToLocal(confirmedTime)
            confirmedTime = datetime.strftime(confirmedTime, "%m-%d-%Y %I:%M:%S %p")
            fees = getConfirm["fees"] / 100000000
            confirmationEmbed.add_field(name = "Confirmed on", value = str(confirmedTime), inline = True)
            confirmationEmbed.add_field(name = "Transaction fee", value = str(fees) + " BTC", inline = True)
            confirmationEmbed.add_field(name = "TXID/Hash", value = f"[{confirmation}](https://www.blockchain.com/btc/tx/{confirmation} 'TXID/Hash')", inline = False)
            confirmationEmbed.set_thumbnail(btcLogo)
            hook.send(embed = confirmationEmbed)
            txid.remove(confirmation)
    time.sleep(interval)
