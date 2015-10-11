#!python
'''

Author: John Wang 
License: MIT

Reference: http://codeeval.com/public_sc/48/

CLI Usage:

  challenge-48.py file.dat [munkres|lapjv]

Class Usage:

  mfile = MatchFile('file.dat')
  mfile.print_ss()

External Libraries:

  (1): numpy:   http://pypi.python.org/pypi/numpy
  (2): pyLAPJV: http://pypi.python.org/pypi/pyLAPJV/0.3
  (3): munkres: http://pypi.python.org/pypi/munkres

'''
import os
import sys
import numpy
import LAPJV
from munkres import Munkres

class Letters:
  def __init__(self):
    self.vowels     = {v:1 for v in list('aeiouy')}
    self.consonants = {c:1 for c in list('bcdfghjklmnpqrstvwxz')}

class Item:
  def __init__(self,letters,item_string):
    v_count = 0
    c_count = 0
    v_dict  = letters.vowels
    c_dict  = letters.consonants
    for l in list(item_string.lower()):
      if c_dict.get(l,False):
        c_count += 1
      elif v_dict.get(l,False):
        v_count += 1
    l_count = v_count + c_count
    self.letter_count = l_count
    self.vowel_count  = v_count
    self.consonant_count = c_count
    self.letter_count_is_even     = True if l_count % 2 == 0 else False
    self.letter_count_factors_set = set([f for f in range(2,l_count+1) if l_count % f==0]) if l_count > 1 else set([])

class MatchPair:
  def __init__(self,product,customer):
    self.product  = product
    self.customer = customer

  def ss(self):
    if self.product.letter_count_is_even:
      ss = float(self.customer.vowel_count) * 1.5
    else:
      ss = float(self.customer.consonant_count)

    if (
      self.product.letter_count_factors_set  &
      self.customer.letter_count_factors_set
    ): ss *= 1.5

    return ss

class MatchSet:
  def __init__(self,deal_string,lap_library='lapjv'):
    parts   = deal_string.split(';')
    custs   = parts[0].split(',')
    prods   = parts[1].split(',')
    letters = Letters()
    self.customers  = [Item(letters,name) for name in custs]
    self.products   = [Item(letters,name) for name in prods]
    self.multiplier = 100
    if lap_library == 'munkres':
      self.lap_library = lap_library
      self.max_val     = sys.maxint
    else:
      self.lap_library = 'lapjv'
      self.max_val     = 2147483647

  def best_ss_lapjv(self,cost_matrix):
    a          = numpy.array(cost_matrix)
    jv_results = LAPJV.lap(a)
    max_val    = self.max_val
    multiplier = self.multiplier
    wip_ss     = 0
    for p_idx, c_idx in enumerate(jv_results[1]):
      cost     = cost_matrix[p_idx][c_idx]
      ss       = max_val - cost
      wip_ss  += ss
    match_ss   = float(wip_ss) / float(multiplier)
    return match_ss

  def best_ss_munkres(self,cost_matrix):
    m          = Munkres()
    indexes    = m.compute(cost_matrix)
    max_val    = self.max_val
    multiplier = self.multiplier
    wip_ss     = 0
    for p_idx, c_idx in indexes:
      cost     = cost_matrix[p_idx][c_idx]
      ss       = max_val - cost
      wip_ss  += ss
    match_ss   = float(wip_ss) / float(multiplier)
    return match_ss

  def best_ss(self):
    c_list      = self.customers
    p_list      = self.products
    c_count     = len(c_list)
    p_count     = len(p_list)
    pc_diff     = p_count - c_count

    cost_matrix = []
    lap_library = self.lap_library
    multiplier  = self.multiplier
    max_val     = self.max_val

    for p_idx in range(0,p_count):
      matrix_row = []
      for c_idx in range(0,c_count):
        ss = MatchPair(p_list[p_idx],c_list[c_idx]).ss()
        ss = int(ss * multiplier)
        if ss > max_val:
          sys.exit('Error: ss (%s) is greater than cost matrix max_val (%s)' % (ss,max_val))
        cost = max_val - ss
        matrix_row.append(cost)

      if lap_library == 'lapjv' and pc_diff > 0:
        for i in range(0,pc_diff):
          matrix_row.append(max_val)

      cost_matrix.append(matrix_row)

    if lap_library == 'lapjv' and pc_diff < 0:
      empty_row = []
      for i in range(0,c_count):
        empty_row.append(max_val)
      for i in range(0,pc_diff*-1):
        cost_matrix.append(empty_row)

    if lap_library == 'lapjv':
      match_ss = self.best_ss_lapjv(cost_matrix)
    elif lap_library == 'munkres':
      match_ss = self.best_ss_munkres(cost_matrix)
    return match_ss

class MatchFile:
  def __init__(self,file_path,lap_library):
    self.file_path = file_path

  def print_ss(self):
    if not os.path.exists(self.file_path):
      sys.exit('Error: Input file %s was not found!' % self.file_path)

    file = open(self.file_path)
    while 1:
      line = file.readline()
      if not line:
        break
      print "{0:.2f}".format(MatchSet(line,lap_library).best_ss())

if len(sys.argv) < 2:
  sys.exit('Usage: python challenge-48.py [input_file]')

lap_library = None
if len(sys.argv) == 3:
  lap_library = sys.argv[2]

MatchFile(sys.argv[1], lap_library).print_ss()