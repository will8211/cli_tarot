#!/usr/bin/env python3

import quantumrandom
import requests
import textwrap
from lxml import html
import random
import re

#Get string from user

question = input('Question: ')
lucky_number = sum([x for x in map(ord, question)])

#print('Lucky number:', lucky_number) #DEBUG

#Get a random interger

try:
    print('Connecting to quantum random number generator...')
    ran = int(quantumrandom.randint(0, 78))
except:
    print('Failed, falling back to pseudo-random number generator...')
    ran = int(random.randint(0, 77))

#print('Random integer:', ran) #DEBUG

#Combine two numners to get card index

i = (ran + lucky_number) % 78

#print('Card index:', i) #DEBUG

## Major Arcana

if i < 22:
    card = "maj" + str(i).zfill(2)

## Minor Arcana

else:
    if i < 36:
        suit = "w"
        n = str(i-21)
    elif i < 50:
        suit = "c"
        n = str(i-35)
    elif i < 64:
        suit = "s"
        n = str(i-49)
    else:
        suit = "p"
        n = str(i-63)
    
## Convert card number to letters for face cards
    
    if n == '1':
        n = 'a'
    elif n == '11':
        n = 'pg'
    elif n == '12':
        n = 'kn'
    elif n == '13':
        n = 'qn'
    elif n == '14':
        n = 'kg'
        
    card = suit + n

## Make request and setup xpath

print('Retrieving card description...\n')
uri = "http://www.learntarot.com/" + card + ".htm"
try:
    r = requests.get(uri)
except:
    print('No internet connection, exiting...')
    exit()
tree = html.fromstring(r.text)
x = tree.xpath

## Save text by xpath

title = x('//h1/text()')[0]
keywords = x('//ul[1]/li//text()') 
divider = '=' * 70
action_terms_raw = x('//dl/dt//text()')
action_definitions_raw = x('//dd//text()')
boldwords = x('//dl/dt/b/text()')

## Process action section

action_terms = ''.join(action_terms_raw).split('\r\n')[:-1]
action_definitions_list = ''.join(action_definitions_raw).split('\r\n')

action_definitions = []
sublist = []
for i in range(len(action_definitions_list)):
    if action_definitions_list[i] != '':
        sublist.append(action_definitions_list[i])
    else:
        action_definitions.append(sublist)
        sublist = []

## Apply bold words

b = '\033[1m'
bb = '\033[0m'

for i in range(len(action_terms)):
    action_terms[i] = action_terms[i].replace(boldwords[i], 
                                              b + boldwords[i] + bb)

## Get description

lines = r.text.split('\n')
desc_html = []
mark = False
for line in lines:
    if '<HR>' in line:
        mark = False
    if mark:
        desc_html.append(line)
    if 'DESCRIPTION' in line:
        mark = True

## Convert html formatting to bash formatting

description = []
for line in desc_html:
    # <a>
    mod = re.sub('\<[aA].*?\>', '\033[4m', line)
    mod = re.sub('(.)\<\/[aA]\>', '\g<1>\033[24m', mod)
    # <i>
    mod = re.sub('\<[iI].*?\>', '\033[1m', mod)
    mod = re.sub('(.)\<\/[iI]\>', '\g<1>\033[0m', mod)
    # <b>
    mod = re.sub('\<[bB]\>', '\033[1m', mod)
    mod = re.sub('(.)\<\/[bB]\>', '\g<1>\033[0m', mod)
    # <BR>
    mod = re.sub('\<BR\>', '', mod)
    # [note]
    mod = re.sub('\[.*\]', '', mod) 
    description.append(mod)

## Print it all out

print(title, '\n')

for i in range(len(keywords)):
    print('•', keywords[i])

print('\n' + divider)
print('ACTIONS\n')

for i in range(len(action_terms)):
    print(action_terms[i])
    for j in action_definitions[i]:
        print("    ", j)
    print("")

print(divider)
print('DESCRIPTION\n')

for line in description:
    if not line.startswith('<') and not line.startswith('See also'):
        print(textwrap.fill(line), '\n')
