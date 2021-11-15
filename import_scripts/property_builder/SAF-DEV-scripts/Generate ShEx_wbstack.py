#!/usr/bin/env python
# coding: utf-8

# In[1]:


import rdflib
from wikidataintegrator import wdi_core, wdi_login
import os
from getpass import getpass
import pandas as pd
import sys
import traceback
from ShExJSG import Schema, ShExC
from ShExJSG.ShExJ import Shape, IRIREF, TripleConstraint, NodeConstraint, EachOf
from pyjsg.jsglib.loader import is_valid
from rdflib import Namespace, Graph, RDFS

wbstack = "wbpython"
wikibase = "https://{}.wiki.opencura.com/".format(wbstack)
api = "https://{}.wiki.opencura.com/w/api.php".format(wbstack)
sparql = "https://{}.wiki.opencura.com/query/sparql".format(wbstack)
entityUri = wikibase.replace("https:", "http:")+"entity/"
cidocUri = "http://www.cidoc-crm.org/cidoc-crm/"

WBUSER = "Andrawaag"
WBPASS = os.environ["MW_ADMIN_PASS"]
login = wdi_login.WDLogin(WBUSER, WBPASS, mediawiki_api_url=api)
localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(api,sparql)

qid = dict()
query = "PREFIX wdt: <http://{}.wiki.opencura.com/prop/direct/> SELECT ?item ?label WHERE {{?item rdfs:label ?label }}".format(wbstack)
wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    qid[row["label"]] =row["item"].replace(entityUri, "")

properties = []
query = "SELECT * WHERE {?prop a wikibase:Property ;}"
wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql)
for index, row in wdi_core.WDItemEngine.execute_sparql_query(query, as_dataframe = True, endpoint=sparql).iterrows():
    properties.append(row["prop"].replace(entityUri, ""))

query = f"""
    PREFIX wde: <{wikibase.replace("https:", "http:")}prop/direct/>
    SELECT * WHERE {{
       ?wikibaseprop wde:{qid["domain"]} ?domain ;
                    wde:{qid["range"]} ?range ;
                    wde:{qid["property"]} ?property .
       ?domain wde:{qid["exact match"]} ?cidocdomain ; rdfs:label ?domainlabel .
       ?range wde:{qid["exact match"]} ?cidocrange ; rdfs:label ?rangelabel .
       ?property wde:{qid["exact match"]} ?cidocproperty ; rdfs:label ?propertylabel .
      }} ORDER BY ?wikibaseprop
"""
results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=sparql, as_dataframe=True)
mappings = results.replace(entityUri,'', regex=True)

shexOutput = f"""
        PREFIX wdt: <{wikibase}prop/direct/>
        PREFIX wd: <{wikibase}entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX saflux: <{wikibase}entity/>
        PREFIX p: <{wikibase}prop/>
        PREFIX crm: <{cidocUri}>
"""

for prop_id in properties:
    prop = localEntityEngine(wd_item_id=prop_id, core_props="")
    prop_dict = prop.get_wd_json_representation()
    values = []
    for lang in prop_dict["labels"].keys():
        values.append("\""+prop_dict["labels"][lang]["value"]+"\"@"+lang)

    tuple_mappings = mappings[mappings["wikibaseprop"]==prop_id]
    if len(tuple_mappings) == 0:
         shexOutput += f"""
            wdt:{prop_id} {{
            rdfs:label [{" ".join(values)}]+;
            }}"""
    else:
        shexOutput += f"""
            wdt:{prop_id} {{
              rdfs:label [{" ".join(values)}]+;
              wdt:{qid["domain"]} {{ rdfs:label [ "{tuple_mappings.iloc[0]["domainlabel"]}"@en] ; # domain
              wdt:{qid["exact match"]} [cidoc:{tuple_mappings.iloc[0]["cidocdomain"].replace(cidocUri, "").replace("http://erlangen-crm.org/current/", "")}] ;}};
              wdt:{qid["range"]} {{ rdfs:label [ "{tuple_mappings.iloc[0]["rangelabel"]}"@en ] ; # range
              wdt:{qid["exact match"]} [ cidoc:{tuple_mappings.iloc[0]["cidocrange"].replace(cidocUri, "").replace("http://erlangen-crm.org/current/", "")} ]  ;}};
              wdt:{qid["property"]} {{ rdfs:label [ "{tuple_mappings.iloc[0]["propertylabel"]}"@en ] ; # property
              wdt:{qid["exact match"]} [cidoc:{tuple_mappings.iloc[0]["cidocproperty"].replace(cidocUri, "").replace("http://erlangen-crm.org/current/", "")}]  ;}};
        }}
        """

mappings_shex_file = open("mappings_v1.0.3_temp.shex", "w")
mappings_shex_file.write(shexOutput)
mappings_shex_file.close()
print(shexOutput)

shexOutput = f"""
PREFIX saflux: <{wikibase}entity/>
PREFIX p: <{wikibase}prop/>
PREFIX ps: <{wikibase}prop/statement/>  
PREFIX pq: <{wikibase}prop/qualifier/>
PREFIX pr: <{wikibase}prop/reference/>
PREFIX wdt: <{wikibase}prop/direct/>
PREFIX wd: <{wikibase}entity/>
PREFIX cidoc: <{cidocUri}>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

shexOutput += f"""
saflux:person {{
  p:{qid["name"]} @saflux:{qid["name"]}_name ; 
  p:{qid["alternative name"]} @saflux:{qid["alternative name"]}_alternative_name * ;
  p:{qid["place of birth"]} @saflux:{qid["place of birth"]}_place_of_birth ? ;
  p:{qid["date of birth"]} @saflux:{qid["date of birth"]}_date_of_birth ? ;
  p:{qid["place of death"]} @saflux:{qid["place of death"]}_place_of_death ? ;
  p:{qid["date of death"]} @saflux:{qid["date of death"]}_date_of_death ? ;
  p:{qid["gender"]} @saflux:{qid["gender"]}_gender ;
  p:{qid["profession"]} @saflux:{qid["profession"]}_profession ? ;
  p:{qid["activity"]} @saflux:{qid["activity"]}_activity + ;
  p:{qid["AFL identifier"]} @saflux:{qid["AFL identifier"]}_AFL_identifier ;
  p:{qid["ISNI"]} @saflux:{qid["ISNI"]}_ISNI ? ;
  p:{qid["VIAF"]} @saflux:{qid["VIAF"]}_VIAF ? ;
  p:{qid["ARK"]} @saflux:{qid["ARK"]}_ARK ? ;
  
}}

saflux:{qid["name"]}_name {{
  ps:{qid["name"]} xsd:string ;
  pq:{qid["numeration"]} xsd:string ? ;
  pq:{qid["title"]} xsd:string ? ;
  prov:wasDerivedFrom @saflux:reference +
}}

saflux:{qid["alternative name"]}_alternative_name {{
  ps:{qid["alternative name"]} xsd:string ;
  pq:{qid["numeration"]} xsd:string ? ;
  pq:{qid["title"]} xsd:string ? ;
  prov:wasDerivedFrom @saflux:reference +
}}

saflux:{qid["place of birth"]}_place_of_birth {{
  ps:{qid["place of birth"]} xsd:string ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["date of birth"]}_date_of_birth {{
  (ps:{qid["date of birth"]} xsd:edtf,
   ps:{qid["date of birth"]} xsd:dateTime+) ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["place of death"]}_place_of_death {{
  ps:{qid["place of death"]} xsd:string ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["date of death"]}_date_of_death {{
  (ps:{qid["date of birth"]} xsd:edtf,
   ps:{qid["date of birth"]} xsd:dateTime+ )
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["gender"]}_gender {{
  ps:{qid["gender"]} [
                        wd:{qid["male"]} 
                        wd:{qid["female"]}
                        wd:{qid["not known"]}
                        wd:{qid["not applicable"]}
                     ]
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["profession"]}_profession {{
  ps:{qid["profession"]} xsd:string ; 
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["activity"]}_activity {{
  ps:{qid["activity"]} xsd:string ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["AFL identifier"]}_AFL_identifier {{
  ps:{qid["AFL identifier"]} xsd:string ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["ISNI"]}_ISNI {{
  ps:{qid["ISNI"]} /[0-9]4 [0-9]4 [0-9]4 [0-9]4/ ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["VIAF"]}_VIAF {{
  ps:{qid["VIAF"]} xsd:string ;
  prov:wasDerivedFrom @saflux:reference + ;
}}
saflux:{qid["ARK"]}_ARK {{
  ps:{qid["ARK"]} IRI ;
  prov:wasDerivedFrom @saflux:reference + ;
}}

saflux:reference {{
 (pr:{qid["source of information - url"]} IRI) OR  
 (pr:{qid["source of information - text"]} xsd:string) OR 
 (pr:{qid["source of information - url"]} IRI ; pr:{qid["source of information - text"]} xsd:string)
}}

"""

luxsaf_shex_file = open("wikbase_v1.0.3_temp.shex", "w")
luxsaf_shex_file.write(shexOutput)
luxsaf_shex_file.close()
print(shexOutput)



