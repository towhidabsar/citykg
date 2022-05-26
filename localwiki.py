import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import unquote
import re
import numpy as np
import os
import stanza
from stanza.server import CoreNLPClient
import networkx as nx
import matplotlib.pyplot as plt
import argparse
import time
import sys

def sanitize_entity(e, city):
    # print(f'Sanitizing {e}')
    e = unquote(e)
    e = e.replace(f'https://localwiki.org/{city}/','')
    e = e.replace('_',' ')
    # print(e)
    return e

def build_kg(city, pages):
    print(f'Loading all entities for {city} in the LocalWiki data')
    pages['related'] = pages.apply(lambda x: localApi.get_all_entities(x, city, pages['name'].values), axis=1)
    print(f'Finished loading entities')
    with CoreNLPClient(
      properties={
          'annotators': ['openie','tokenize','ssplit','pos','lemma','depparse','natlog', 'ner'],
      },
      timeout=60000,
      endpoint='http://localhost:9001',
      memory='6G') as client:
      print('triples loading')
      triples = pd.DataFrame(pages.apply(lambda x: localApi.label_relations(x, city, client), axis=1))
      print(triples)

      pages.to_json(f'data/{city}/{city}_nodelist.json', orient='records', lines=True)
      kg = []
      for t in triples[0].tolist():
          kg = kg + t
      kg = pd.DataFrame(kg)
      kg.to_json(f'data/{city}/{city}_edgelist.json',orient='records', lines=True)
    
def main(city, output_cities_file):
    localApi = LocalWikiApi(output_cities_file)
    print(f'Loading pages from LocalWikiApi for {city}')
    pages = localApi.get_city_pages(city)
    print('Finished loading pages')
    print(f'Loading all entities for {city} in the LocalWiki data')
    pages['related'] = pages.apply(lambda x: localApi.get_all_entities(x, city, pages['name'].values), axis=1)
    print(f'Finished loading entities')
    with CoreNLPClient(
        properties={
            'annotators': ['openie','tokenize','ssplit','pos','lemma','depparse','natlog', 'ner'],
        },
        timeout=60000,
        endpoint='http://localhost:9001',
        memory='6G') as client:
        print('triples loading')
        triples = pd.DataFrame(pages.apply(lambda x: localApi.label_relations(x, city, client), axis=1))
        print(triples)

        pages.to_json(f'{city}_nodelist.json', orient='records', lines=True)
        kg = []
        for t in triples[0].tolist():
            kg = kg + t
        kg = pd.DataFrame(kg)
        kg.to_json(f'{city}_edgelist.json',orient='records', lines=True)

def save_json_file(df, city, file='', out_folder='', verbose = False):
  out_folder = os.path.join(os.getcwd(), out_folder)
  if not os.path.isdir(out_folder):
    os.mkdir(out_folder)
  out = os.path.join(out_folder, f'{city}_{file}.json')
  df.to_json(out, orient='records', lines=True)

class LocalWikiApi:
  def __init__(self, filename):
    self.url = 'https://localwiki.org/api/v4/'
    self.city_table = self.load_city_table(filename)

  def load_city_table(self, file):
    if os.path.exists(file):
      return pd.read_json(file,orient='records', lines=True)
    else:
      return self.generate_city_table(file)

  def generate_city_table(self, file):
    # req_url = f'{self.url}/regions/?limit=100'
    city_list = []
    response = requests.get(req_url)
    while response != None:
      region_list = response.json()['results']
      for region in region_list:
        city_list.append(region)
      if response.json()['next'] != None:
        print(response.json()['next'])
        response = requests.get(response.json()['next'])
      else:
        response = None
    city_table = pd.DataFrame(city_list)
    city_table.to_json(file, orient='records', lines=True)
    return city_table

  def get_all_pages(self):
    print('Loading all pages')
    self.city_table.apply(lambda x: self.save_city_pages(row=x), axis=1)

  def save_city_pages(self, row=None, i=None):
    sys.stdout.flush()
    if i != None:
      row = self.city_table.iloc[i]
    city = row['slug']
    print(f'Loading pages from LocalWikiApi for {city}')
    pages = self.get_city_pages(city)
    # pages.to_json(f'{city}_pages.json', orient='records', lines=True)
    save_json_file(pages, city, file='pages', out_folder=f'data/{city}')
    print(f'Finished loading pages and saved to {city}_pages.json')

  def get_city_pages(self, city_name):
    nodelist = pd.DataFrame()
    print('city_name')
    print(city_name)
    regions = self.city_table[self.city_table['full_name'] == city_name]
    if len(regions) <= 0:
      regions = self.city_table[self.city_table['slug'] == city_name]

    region = regions.iloc[0]
    slug = region['slug']
    req_url = f'{self.url}/pages/?region__slug={slug}'
    
    response = requests.get(req_url)
    # print(response.json()['results'][1])
    res_count = 0
    while response != None:
      if response.status_code != 200 and res_count <= 10:
        print('Waiting for proper status code')
        print(response.status_code)
        sys.stdout.flush()
        time.sleep(2)
        response = requests.get(req_url)
        res_count += 1
      else:
        for entity_page in response.json()['results']:
          # entity = entity_page['name']
          # url = entity_page['url']
          # entities[entity] = entity_page
          nodelist = nodelist.append(entity_page, ignore_index=True)
        if response.json()['next'] != None:
          response = response = requests.get(response.json()['next'])
        else:
          response = None
    return nodelist

  def sanitize_entity(e, city):
    # print(f'Sanitizing {e}')
    e = unquote(e)
    e = e.replace(f'https://localwiki.org/{city}/','')
    e = e.replace('_',' ')
    # print(e)
    return e

  def get_all_entities(self, content, city, entities):
    content = content['content']
    soup = BeautifulSoup(content)
    ner = []
    for link in soup.find_all('a'):
      u = link.get('href')
      if u != None:
        e = sanitize_entity(u, city)
        if e in entities:
          ner.append(e)
    return ner

  def label_relations(self, content, city, nlpclient):
    print(content)
    html = content['content']
    soup = BeautifulSoup(html)
    e1 = content['name']
    document = ""
    triples = []
    # map(lambda x: x.text, soup.find_all('p'))
    for p in soup.find_all('p'):
    # document = '\n'.join(soup.find_all('p', text=True))
      ann = nlpclient.annotate(p.text)
      en_a = []
      for a in soup.find_all('a'):
        label = a.text
        entity = a.get('href')
        if entity != None:
          entity = sanitize_entity(entity, city)
          en_a.append(entity)
      for s in ann.sentence:
        en_array = en_a
        for en in s.mentions:
          en_array.append(en.entityMentionText)
        for t in s.openieTriple:
          subject = t.subject
          relation = t.relation
          obj = t.object
          if subject in en_array or obj in en_array:
            # print(f'{subject} -- {relation} -- {obj}')
            triples.append({'subject': subject, 'relation': relation, 'object': obj})
            # triples.append((subject, relation, obj))
    return triples


if __name__ == '__main__':
  print('Starting')
  parser = argparse.ArgumentParser()
  parser.add_argument('--cities', help='The city or cities to build the knowledge graph for')
  parser.add_argument('--ocf', nargs='?', const='cities.json', type=str, help='The file where the list of cities and their slug is stored. If it does not exist then it is generated')
  parser.add_argument('--pages', help='Generate only the offline pages.')
  parser.add_argument('--kg', help='Run in distributed mode. Does not send any API requests. Need to provide the json file of city pages generated by --pages')
  args = parser.parse_args()
  # cities = args.cities.split(',')
  output_cities_file = args.ocf if args.ocf != None else 'cities.json'
  print(args)
  if args.cities != None:
    print('Normal workflow')
    cities = args.cities.split(',')
    stanza.install_corenlp()
    stanza.install_corenlp(dir="corenlp")
    for city in cities:
      main(city, output_cities_file)
  if args.pages != None:
    print('Generating all pages')
    print(args.pages)
    if args.pages == '0':
      localApi = LocalWikiApi(output_cities_file)
      localApi.get_all_pages()
    else:
      localApi = LocalWikiApi(output_cities_file)
      localApi.save_city_pages(i=int(args.pages))
  if args.kg != None:
    print(args.kg)
  # elif args.distributed != None: 
  #   print('Distrbuted setting')
  #   distrbuted = args.distrbuted.split(',')
  #   city = distrbuted[0]
  #   pages = pd.read_json(distrbuted[1],orient='records', lines=True)
  #   build_kg(city, pages)


    # cities = sys.argv[1].split(',')
    # output_cities_file = sys.argv[2] if len(sys.argv) > 1 else 'cities.json'
    # stanza.install_corenlp()
    # stanza.install_corenlp(dir="corenlp")
    # # only one city
    # if len(cities) == 1:
    #     print(cities)
    #     main(cities[0], output_cities_file)
    # elif len(cities) > 1:
    #     for city in cities:
    #         print(city)
    #         main(city, output_cities_file)
    
