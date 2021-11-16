## create_properties.py ##
This script extracts the properties expressed in the DM Rules file to build the Wikibase properties. This scripts intends to run one time in an empty wikibase. Subsequent edits need to be done directy on Wikibase.

## import_cidoc_crm.py ##
This script imports CIDOC CRM's classes and properties. Each class and property is expressed as a Wikibase item. This scripts requires that the previous script, ```create_properties.py``` to have run successfully.

## create_mappings.py ##
This script create mappings expressed in the DM Rules between the Wikibase model and CIDOC CRM. This script follows on ```import_cidoc_crm.py``` and requires that that script ran successfully.

## generate_shex.py ## 
This script generates two Shape Expressions. 1. the ShEx describing the property model to the populated Wikibase and 2. the ShEx describing the mapping between CIDOC CRM and that Wikibase model as described in the DM Rules file
