import pandas as pd 
import requests
import json
import sys
from tqdm import tqdm
from typing import Tuple


# read
df = pd.read_csv(sys.argv[1])
print("using file {}".format(sys.argv[1]))

# preprocess
df["MY discount"] = [0 for i in range(len(df))]
df["MY webprice"] = df["PP"]
df["MY equal"] = [False for i in range(len(df))]
df["MY error"] = [False for i in range(len(df))]

df["TW webprice"] = df["PP"]
df["TW equal"] = [False for i in range(len(df))]
df["TW error"] = [False for i in range(len(df))]

# helper
def parse_id(url: str) -> Tuple[str, str]:
    shopid, itemid = url.split("-")[-1].split(".")[1:]
    return shopid, itemid
    
# main
for i in tqdm(range(len(df))):
    # MY
    url = df["MY Link"][i]
    try:
        shopid, itemid = parse_id(url)
        r = requests.get("https://shopee.com.my/api/v2/item/get?shopid={}&itemid={}".format(shopid, itemid))
        item = json.loads(r.content)["item"]
        models = item["models"]

        equal = False
        for m in models:
            p = m["price"] * 10e-6

            if abs(df["PP"][i] - p) < 10e-5:
                equal = True
                break
            else:
                # print(df["PP"][i], p)
                pass

        models = list(map(lambda m: "{}: {:.2f}".format(m["name"], m["price"]*10e-6), models))
        models = ", ".join(models)
        df.loc[i, "MY webprice"] = models

        df.loc[i, "MY equal"] = equal
        df.loc[i, "MY discount"] = item["show_discount"]
        
    except:
        df.loc[i, "MY error"] = True
        df.loc[i, "MY webprice"] = 0
        df.loc[i, "MY equal"] = False
        df.loc[i, "MY discount"] = 0
    
    # TW
    url = df["TW link"][i]
    try:
        shopid, itemid = parse_id(url)
        r = requests.get("https://shopee.tw/api/v2/item/get?shopid={}&itemid={}".format(shopid, itemid))
        models = json.loads(r.content)["item"]["models"]

        equal = False
        for m in models:
            p = int(m["price"] * 10e-6)

            if abs(df["TWpromotion price"][i] - p) < 10e-5:
                equal = True
                break
            else:
                # print(df["TWpromotion price"][i], p)
                pass

        models = list(map(lambda m: "{}: {:.2f}".format(m["name"], m["price"]*10e-6), models))
        models = ", ".join(models)
        df.loc[i, "TW webprice"] = models

        df.loc[i, "TW equal"] = equal
        
    except:
        df.loc[i, "TW error"] = True
        df.loc[i, "TW webprice"] = 0
        df.loc[i, "TW equal"] = False
    
# postprocess
full_filename = filename.strip(".csv") + "_full.csv"
df.to_csv(full_filename)

df_filter = df[
    (df["TW equal"] == False) |
    (df["MY equal"] == False) |
    (df["MY error"] == True) |
    (df["TW error"] == True) |
    ( (df["SIP"] == "OLD") & (df["MY discount"] <= 10) )
]

filtered_filename = filename.strip(".csv") + "_filtered.csv"
df_filter.to_csv(filtered_filename)
