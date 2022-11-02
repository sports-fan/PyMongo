from django.shortcuts import render
from django.http import HttpResponse
import json
import pymongo
import datetime
import pytz

client = pymongo.MongoClient('mongodb://localhost:27017/myTestApp')
#Define DB Name
dbname = client['admin']

#Define Collection
collection = dbname['teen_harvests_mainnet']



# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my <u>Django App</u> project!</h1>")

def hello_world(request):
    return HttpResponse("Hello, world!")

def create(request):
    print("Ok")
    with open('teen_harvests_mainnet.json') as f:
        data = json.load(f)
    
    print(data)
    collection.insert_many(data)
    details = collection.find({})

    for r in details:
        print(r)
    
    return HttpResponse('OK')

datetime = datetime.datetime

def bap_teens_levels(request):
    def calculate_levels(wallet_address, token_ids):
        date = datetime.now(pytz.utc)  # Current time in UTC
        cst_date = date.astimezone(pytz.timezone("US/Central"))  # Current time in CST

        projection = {
            "token_id": 1,
            "date_harvested": 1,
        }

        pipeline = [
            {"$match": {
                "wallet_address": wallet_address,
                # "token_id": {"$in": token_ids},
            }},
            # {"$sort": {"date_harvested": -1}},
            # {"$project": projection},
        ]
        print("collection", collection)

        while True:
            try:
                data = collection.aggregate(
                    [
                        {"$match": {
                            "wallet_address": wallet_address,
                            # "token_id": {"$in": token_ids},
                        }},
                        # {"$sort": {"date_harvested": -1}},
                        # {"$project": projection},
                    ],
                    allowDiskUse=True,
                )
                data = list(data)
                print(data)
                break

            except:
                # logger.error(f"Error getting teen harvests for {wallet_address} ({', '.join(token_ids)})", exc_info=True)
                sleep(1)
        print('1111', data)
        harvests = {token_id: [] for token_id in token_ids}
        for harvest in data:
            token_id = harvest["token_id"]
            harvests[token_id].append(harvest)

        tokens_data = {}
        for token_id, harvests in harvests.items():
            harvest_dates = [harvest["date_harvested"] for harvest in harvests]
            if harvest_dates:
                latest_harvest_date = harvest_dates[0]
                latest_harvest_date_cst = latest_harvest_date.astimezone(pytz.timezone("US/Central"))
                harvested_today = latest_harvest_date_cst.date() == cst_date.date()
            else:
                harvested_today = False

            cumulative_days = len(harvests)
            consecutive_days = 0

            for i, harvest in enumerate(harvests):
                date_harvested = harvest["date_harvested"]
                date_harvested_cst = date_harvested.astimezone(pytz.timezone("US/Central"))
                date_harvested_date = date_harvested_cst.date()

                if i == 0:
                    if date_harvested_date == cst_date.date():
                        consecutive_days = 1
                    elif date_harvested_date == cst_date.date() - timedelta(days=1):
                        consecutive_days = 1

                else:
                    previous_harvest = harvests[i - 1]
                    previous_date_harvested = previous_harvest["date_harvested"]
                    previous_date_harvested_cst = previous_date_harvested.astimezone(pytz.timezone("US/Central"))
                    previous_date_harvested_date = previous_date_harvested_cst.date()

                    if date_harvested_date == previous_date_harvested_date - timedelta(days=1):
                        if consecutive_days != 0:
                            consecutive_days += 1
                    else:
                        break

            if consecutive_days >= 14:
                level = 3
            elif consecutive_days >= 7:
                level = 2
            else:
                level = 1

            if level == 1:
                meth_amount = 1
            elif level == 2:
                meth_amount = 2
            elif level == 3:
                meth_amount = 4
            else:
                meth_amount = 0

            if consecutive_days >= 14:
                days_until_next_level = None
            elif consecutive_days >= 7:
                days_until_next_level = 14 - consecutive_days
            else:
                days_until_next_level = 7 - consecutive_days

            # logger.debug(f"Wallet: {wallet_address} | Token ID: {token_id:<5} | Level: {level} | METH: {meth_amount} | Consecutive Days: {consecutive_days:<2} | Cumulative Days: {cumulative_days}")

            token_data = {
                "level": level,
                "meth_amount": meth_amount,
                "consecutive_days": consecutive_days,
                "days_until_next_level": days_until_next_level,
                "cumulative_days": cumulative_days,
                "harvest_dates": [str(harvest_date) for harvest_date in harvest_dates],
                "harvested_today": harvested_today,
            }
            print(token_data)

            tokens_data[token_id] = token_data

        return tokens_data
    params = request.GET

    wallet_address = params.get("wallet_address")
    teen_ids = params.get("teen_ids").split(',')
    print(teen_ids)

    # Validate wallet_address
    # if not wallet_address:
    #     message = "Missing mandatory parameter: wallet_address"
    #     logger.warning(message)
    #     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # if w3_mainnet.isAddress(wallet_address):
    #     if w3_mainnet.isChecksumAddress(wallet_address):
    #         pass
    #     else:
    #         wallet_address = w3_mainnet.toChecksumAddress(wallet_address)
    # else:
    #     message = f"Invalid wallet_address: {wallet_address}"
    #     logger.warning(message)
    #     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # # Validate teen_ids
    # if not teen_ids:
    #     message = "Missing mandatory parameter: teen_ids"
    #     logger.warning(message)
    #     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # if isinstance(teen_ids, str):
    #     teen_ids = [teen_ids]
    # elif isinstance(teen_ids, list):
    #     pass
    # else:
    #     message = "Invalid teen_ids: must be a string or a list of strings"
    #     logger.warning(message)
    #     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # if all([isinstance(teen_id, str) for teen_id in teen_ids]):
    #     pass
    # else:
    #     message = "Invalid teen_ids: must be a string or a list of strings"
    #     logger.warning(message)
    #     return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # # Validate network
    # if network:
    #     if network not in ["mainnet", "goerli"]:
    #         message = f"Invalid network: {network} (must be mainnet or goerli)"
    #         logger.warning(message)
    #         return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     network = "mainnet"

    levels = calculate_levels(wallet_address, teen_ids)

    data = {
        "wallet_address": wallet_address,
        "levels": levels
    }

    return HttpResponse(data)
