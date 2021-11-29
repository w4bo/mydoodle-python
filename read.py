from doodle import Doodle
import pandas as pd
import datetime as dt
import re 

d = Doodle(url="https://doodle.com/poll/6c9nrmyeyt5gcih3")
# d = Doodle(url="https://doodle.com/poll/6a275rvfdyuqmfux")
df = pd.DataFrame(d.options, columns=["date", "start", "text"])
df["week"] = df["date"].apply(lambda x: (x + dt.timedelta(days=1)).week)

def e2i(x):
    if "Mon" in x:
        return "Lun"
    elif "Tue" in x:
        return "Mar"
    elif "Wed" in x:
        return "Mer"
    elif "Thu" in x:
        return "Gio"
    elif "Fri" in x:
        return "Ven"
    elif "Sat" in x:
        return "Sab"
    elif "Sun" in x:
        return "Dom"

df['day'] = df[['date']].apply(lambda x: e2i(dt.datetime.strftime(x['date'], '%A')), axis=1)
i = 0
for p, preferences in d.participants:
    df["p_" + str(i) + p] = preferences
    df["p_" + str(i) + p] = df["p_" + str(i) + p].apply(lambda x: p.replace(" ", "") if x == 1 else "")
    i += 1
df["curweek"] = dt.datetime.now()
df["curweek"] = df["curweek"].apply(lambda x: (x + dt.timedelta(days=1)).week)
df = df[df["curweek"] == df["week"]]
df = df[["date", "week", "day", "text"] + [x for x in df.columns if "p_" in x]]
df["s"] = df[[x for x in df.columns if "p_" in x]].agg(' '.join, axis=1).apply(lambda x: re.sub(' +', ' ', x).strip())
df = df[df["s"].apply(lambda x: x != "")]
print(df[["week", "date", "day", "text", "s"]].to_markdown())
df.apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("README.md", index=False, header=False)