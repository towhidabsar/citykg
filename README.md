# CityKG

## About
Encyclopedic knowledge graphs are often used in the training and development of state-of-the-art AI tasks such as question answering, recommendation systems, and language modeling. Due to the rise in AI for Social Good, these tasks are often focused on city and community development. This added focus requires more contextual and city-specific information that generalized knowledge graphs (DBPedia, Yago, Wikidata.org) often lack. The challenge for the development of city-specific AI models is the lack of such data. To fulfill this lack of specificity in city data, we present CityKG - a collection of city-specific knowledge graphs of over 50 cities worldwide. CityKG provides a comprehensive semantic representation of notable entities present in a city and entities defining concepts specific to a city.

## Pre-Requisites & Execution
This script requires `Python3` to run.

```
git clone https://github.com/towhidabsar/citykg.git
```

To install all the pre-requisites run:
```
pip install -r requirements.txt
```

To get descriptions of all the available commands run:
```
python localwiki.py --help
```


## Run
```
# Number of cities to generate offline pages for - 0 for all cities
python localwiki.py --pages [number of cities]

# List of cities or 'all' for all possible cities from LocalWiki 
python localwiki.py --kg [list of cities]
```

To generate our version of the knowledge graph [CityKG V1](https://github.com/towhidabsar/citykg/blob/main/kg.zip), please run:
```
python localwiki --pages 0

./city.sh 
```


