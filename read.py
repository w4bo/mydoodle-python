# -*- coding: utf-8 -*-

from doodle import Doodle
import pandas as pd
import datetime as dt
import re 
from datetime import date, timedelta

def transcode(x):
    if "Matteo F" in x:
        return "Matteo Francia"
    elif "Antonio" in x:
        return "Antonio Castagnola"
    elif "Laura" in x:
        return "Laura Tarsitano"
    elif "Gabriella" in x:
        return "Gabriella"
    elif "Silvia Pimpinella" in x:
        return "Silvia Severi"
    else:
        return x

# According to the same ISO specification, January 4th is always 
# going to be week 1 of a given year. By the same calculation, +
# the 28th of December is then always in the last week of the year. 
# You can use that to find the last week number of a given year:
def weeks_for_year(year=dt.datetime.now().year):
    last_week = date(year, 12, 28)
    return last_week.isocalendar()[1]

urls = [
    "https://doodle.com/poll/hstku4b2yav7vsv5", # marzo 2022
    "https://doodle.com/poll/5ran7iwhqx9mbki4", # febbraio 2022
    "https://doodle.com/poll/zyuwdmw5s5np5umx", # gennaio 2022
    "https://doodle.com/poll/6a275rvfdyuqmfux", # dicembre 2021
    "https://doodle.com/poll/6c9nrmyeyt5gcih3"  # novembre 2021
    ]

dff = pd.DataFrame(columns=["date", "start", "text"])

for url in reversed(urls):

    d = Doodle(url=url)
    df = pd.DataFrame(d.options, columns=["date", "start", "text"])
    df["week"] = df["date"].apply(lambda x: (x + dt.timedelta(days=1)).week)
    df["month"] = df["date"].apply(lambda x: x.month)

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
    0
    i = 0
    for p, preferences in d.participants:
        p = transcode(p)
        df["p" + str(i) + "_" + p] = preferences
        df["p" + str(i) + "_" + p] = df["p" + str(i) + "_" + p].apply(lambda x: p.replace(" ", "-") if x == 1 else "")
        i += 1

    # df = df.astype(str).replace('nan', '')
    dff = dff.append(df)
    print(len(dff.index))

df = dff
df["curweek"] = dt.datetime.now()
df["curweek"] = df["curweek"].apply(lambda x: (x + dt.timedelta(days=1)).week)
df["curmonth"] = df["curweek"].apply(lambda x: dt.datetime.now().month)
df = df[["date", "month", "week", "day", "text", "curmonth", "curweek"] + [x for x in df.columns if "_" in x]]
df["s"] = df[[x for x in df.columns if "_" in x]].astype(str).replace('nan', '').agg(' '.join, axis=1).apply(lambda x: re.sub(' +', ', ', x.strip()).replace("-", " "))
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

with open('turni_settimanali.txt', "w") as w:
    w.write("Ciao Nasi!\n\n")
    w.write("Link al doodle: " + url + "\n\n")
    w.write("Prossima settimana, turni coperti: " + turni_coperti(df, 1) + "\n")
df[df["curweek"].apply(lambda x: next_w(x, 1)) == df["week"]].apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("turni_settimanali.txt", mode='a', index=False, header=False, sep=";")
with open('turni_settimanali.txt', "a") as w:
    w.write("\n")
    w.write("Settimana corrente\n")
df[df["curweek"] == df["week"]].apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("turni_settimanali.txt", mode='a', index=False, header=False, sep=";")

# Turni mensili
df_month = df[(df["curmonth"] == df["month"]) & (~df["s"].str.contains("solitario"))]
df_month.apply(lambda x: "- " + x["day"] + " " + str(x["date"].strftime("%d/%m")) + " " +  x["text"] + " " + x["s"], axis=1).to_csv("turni_mensili.txt", mode='w', index=False, header=False, sep=";")

s = """
Ciao Nasi!

Ecco i turni mensili:
{mensili}
Chi ha fatto almeno un turno deve (il prima possibile):
- Confermarne la correttezza rispondendo a questa e-mail
- Inviare il RIMBORSO KM ed eventuale RIMBORSO SCONTRINO

Un paio di statistiche:
- I clown attivi sono {attivi}
- I turni coperti sono {turni}

Grazie

PS. 
- Mantenete il doodle aggiornato (e.g., quando salta un turno)
- Modificate il doodle *senza* duplicare le vostre votazioni (e.g., quando cancellate/aggiungete turni)
"""

turni = df_month.shape[0]
attivi = len(set([x.split("_")[1] for x in df_month.columns if "_" in x and df_month[x].fillna("").apply(lambda x: 0 if x == "" else 1).sum() > 0]))
with open("turni_mensili.txt", 'r') as f:
    a = f.read()

with open("turni_mensili.txt", 'w') as f:
    f.write(s.format(mensili=a, attivi=attivi, turni=turni))
