import rdflib
from wikidataintegrator import wdi_core, wdi_login
from getpass import getpass
import pandas as pd
import os
import traceback

wikibase = os.environ["WIKIBASE_HOST"]
api = wikibase+":8080/w/api.php"
sparql = wikibase+":9999/bigdata/namespace/wdq/sparql"
entityUri = wikibase.replace("https:", "http:")+"entity/"

WBUSER = os.environ["MW_ADMIN_NAME"]
WBPASS = os.environ["MW_ADMIN_PASS"]
login = wdi_login.WDLogin(WBUSER, WBPASS, mediawiki_api_url=api)

localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(api,sparql)

def createProperty(login=login, wdprop=None, lulabel="", enlabel="", frlabel="", delabel="", description="", property_datatype=""):
    if wdprop== None:
        s = []
    else:
        s = [wdi_core.WDUrl(wdprop, prop_nr="P1")]
    localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(api,sparql)
    item = localEntityEngine(data=s)
    item.set_label(lulabel, lang="lb")
    item.set_label(enlabel, lang="en")
    item.set_label(delabel, lang="de")
    item.set_label(frlabel, lang="fr")
    item.set_description(description, lang="en")
    
    print(item.write(login, entity_type="property", property_datatype=property_datatype))

cidoc = rdflib.Graph()
cidoc.load("https://raw.githubusercontent.com/erlangen-crm/ecrm/master/ecrm_current.owl", format="xml")

propertyID = dict()
## TODO adapt prefix namespaces to align with local wikibase at SAFLux
query = "PREFIX wdt: <http://{}.wiki.opencura.com/prop/direct/> SELECT ?item ?label WHERE {{?item rdfs:label ?label }}".format(wbstack)
wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    propertyID[row["label"]] =row["item"].replace(entityUri, "")
    
qid = dict()
## TODO adapt prefix namespaces to align with local wikibase at SAFLux
query = "PREFIX wdt: <http://{}.wiki.opencura.com/prop/direct/> SELECT ?item ?label WHERE {{?item rdfs:label ?label }}".format(wbstack)
wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    qid[row["label"]] =row["item"].replace(entityUri, "")


query = "SELECT ?cidoc ?label WHERE {?cidoc rdf:type <http://www.w3.org/2002/07/owl#Class> ; rdfs:label ?label .}"
for row in cidoc.query(query):
    #print(str(row[0]), str(row[1]), " ".join(str(row[1]).split(" ")[1:]))
    statements=[]
    statements.append(wdi_core.WDItemID(value=qid["Class"], prop_nr=propertyID["instance of"]))
    statements.append(wdi_core.WDUrl(value=str(row[0]).replace("http://erlangen-crm.org/current/", "http://www.cidoc-crm.org/cidoc-crm/"), prop_nr=propertyID['exact match']))
    item = localEntityEngine(new_item=True, data=statements)
    item.set_label(" ".join(str(row[1]).split(" ")), lang="en")
    #item.set_aliases([str(row[1]), str(row[1]).replace(" ", "_")], lang="en")
    print(item.write(login))

#propertyClasses
query = "SELECT ?cidoc ?label WHERE {?cidoc rdf:type <http://www.w3.org/2002/07/owl#ObjectProperty> ; rdfs:label ?label .}"
for row in cidoc.query(query):
    print(str(row[0]), str(row[1]), " ".join(str(row[1]).split(" ")[1:]))
    statements=[]
    statements.append(wdi_core.WDItemID(value=qid["Property"], prop_nr=qid["instance of"]))
    statements.append(wdi_core.WDUrl(value=str(row[0]).replace("http://erlangen-crm.org/current/", "http://www.cidoc-crm.org/cidoc-crm/"), prop_nr=propertyID["exact match"]))
    item = localEntityEngine(new_item=True, data=statements)
    item.set_label(" ".join(str(row[1]).split(" ")), lang="en")
    #item.set_aliases([str(row[1]), str(row[1]).replace(" ", "_")], lang="en")
    try:
        print(item.write(login))
    except:
        print("ERROR: "+str(row[1]))
        continue

## TODO adapt prefix namespaces to align with local wikibase at SAFLux
query = "PREFIX wdt: <http://{}.wiki.opencura.com/prop/direct/> SELECT * WHERE {{?item wdt:P3 ?uri .}}".format(wbstack)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    qid[row["uri"]] =row["item"].replace(entityUri, "")

missing_classes = ['R8 consists of', "E13 Attribute assignement", 'E52 Time-span', 'P48 has prefered identifier', 'P107 has current or former member of']
for missing_class in missing_classes:
    statements=[]
    statements.append(wdi_core.WDItemID(value=qid["Class"], prop_nr=propertyID["instance of"]))
    statements.append(wdi_core.WDUrl(value="http://www.cidoc-crm.org/cidoc-crm/"+ missing_class.replace(" ", "_"), prop_nr=propertyID['exact match']))
    item = localEntityEngine(new_item=True, data=statements)
    item.set_label(missing_class , lang="en")
    print(item.write(login))





