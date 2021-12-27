# -*- coding: utf-8 -*-

from doodle import Doodle
import pandas as pd
import datetime as dt
import re 
from datetime import date, timedelta

# According to the same ISO specification, January 4th is always 
# going to be week 1 of a given year. By the same calculation, +
# the 28th of December is then always in the last week of the year. 
# You can use that to find the last week number of a given year:
def weeks_for_year(year=dt.datetime.now().year):
    last_week = date(year, 12, 28)
    return last_week.isocalendar()[1]

urls = [
    "https://doodle.com/poll/zyuwdmw5s5np5umx", # gennaio 2022
    "https://doodle.com/poll/6a275rvfdyuqmfux", # dicembre 2021
    "https://doodle.com/poll/6c9nrmyeyt5gcih3"  # novembre 2021
    ]

dff = pd.DataFrame(columns=["date", "start", "text"])

for url in reversed(urls):

    d = Doodle(url=url)
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
        df["p_" + str(i) + p] = df["p_" + str(i) + p].apply(lambda x: p.replace(" ", "-") if x == 1 else "")
        i += 1

    # df = df.astype(str).replace('nan', '')
    dff = dff.append(df)
    print(len(dff.index))
df = dff

df["curweek"] = dt.datetime.now()
df["curweek"] = df["curweek"].apply(lambda x: (x + dt.timedelta(days=1)).week)
df = df[["date", "week", "day", "text", "curweek"] + [x for x in df.columns if "p_" in x]]
df["s"] = df[[x for x in df.columns if "p_" in x]].astype(str).replace('nan', '').agg(' '.join, axis=1).apply(lambda x: re.sub(' +', ', ', x.strip()).replace("-", " "))
df = df[df["s"].apply(lambda x: x != "")]
df["s"] = df["s"].apply(lambda x: x if ", " in x else x + " (turno solitario)")

weeks = weeks_for_year() + 1
def next_w(x, week):
    if x + week == weeks:
        return 1
    else:
        return x + week

def turni_coperti(df, week=0):
    turni = df[(df["curweek"].apply(lambda x: next_w(x, week)) == df["week"]) & (~df["s"].str.contains("solitario"))]["s"].count()
    return str(turni) + (" 😔" if turni == 0 else "") 

with open('README.md', "w") as w:
    w.write("Ciao Nasi!\n\n")
    w.write("Link al doodle: " + url + "\n\n")
    w.write("Prossima settimana, turni coperti: " + turni_coperti(df, 1) + "\n")
df[df["curweek"].apply(lambda x: next_w(x, 1)) == df["week"]].apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("README.md", mode='a', index=False, header=False, sep=";")
with open('README.md', "a") as w:
    w.write("\n")
    w.write("Settimana corrente\n")
df[df["curweek"] == df["week"]].apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("README.md", mode='a', index=False, header=False, sep=";")