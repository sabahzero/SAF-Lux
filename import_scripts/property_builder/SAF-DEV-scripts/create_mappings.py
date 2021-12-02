#!/usr/bin/env python
# coding: utf-8

from wikidataintegrator import wdi_core, wdi_login, wdi_config
from getpass import getpass
import pandas as pd
import json
import os

wikibase = os.environ["WIKIBASE_HOST"]
api = wikibase+":8080/w/api.php"
sparql = wikibase+":9999/bigdata/namespace/wdq/sparql"
entityUri = wikibase.replace("https:", "http:")+"entity/"

WBUSER = os.environ["MW_ADMIN_NAME"]
WBPASS = os.environ["MW_ADMIN_PASS"]
login = wdi_login.WDLogin(WBUSER, WBPASS, mediawiki_api_url=api)
localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(api,sparql)

df = pd.read_excel("../DM_SAF/DM_SAF_vers.1.0.3_andra.xls", sheet_name="CIDOC", header=2)
df2 = df[~df["English"].isnull()]
qid = dict()
query = "SELECT ?item ?label WHERE {?item rdfs:label ?label }"
wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    qid[row["label"]] =row["item"].replace(entityUri, "")

done = []
for index, row in df2.iterrows():
    if row["English"].strip() in qid.keys():
        try: 
            print(row["English"].strip(), "\t", qid[row["English"].strip()], qid[row["Range"].strip()], qid[row["Domain"].strip()], qid[row["Property"].strip()])
            statements = []
            statements.append(wdi_core.WDItemID(value=qid[row["Range"].strip()], prop_nr=qid["range"]))
            statements.append(wdi_core.WDItemID(value=qid[row["Domain"].strip()], prop_nr=qid["domain"]))
            statements.append(wdi_core.WDItemID(value=qid[row["Property"].strip()], prop_nr=qid["property"]))
            item = localEntityEngine(wd_item_id=qid[row["English"].strip()], data=statements)
            #print(json.dumps(item.get_wd_json_representation(), indent=4))
            item.write(login, entity_type="property")
        except Exception as e: 
            print("error", e)
            continue
