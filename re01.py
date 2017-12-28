#!/usr/bin/python

import re

pattern = re.compile(r'hello')

print 'Pattern is: ' + str(pattern) 

m = ''
while(m != 'exit'):
    m = str(raw_input('Input match string: '))
    if pattern.match(m):
        print pattern.match(m).group()
        print pattern.match(m).groups()
    else:
        print 'Match failed!'
