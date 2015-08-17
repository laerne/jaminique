#!/usr/bin/env python3
import re
import glob
import os
import os.path
import argparse
import sys
import fileinput


argparser = argparse.ArgumentParser()

argparser.add_argument( '-S', '--state', action='store', default='*',
        help='' )
argparser.add_argument( '-s', '--sex', action='store', default='M,F',
        help='' )
argparser.add_argument( '-y', '--birth-year', action='store', default='*',
        help='' )
        
args = argparser.parse_args()

def patterns_for_bounds( lower, upper ):
    if not lower or not upper:
        assert lower == ''
        assert upper == ''
        return ''
    lower_1st = int(lower[0])
    upper_1st = int(upper[0])
    diff_1st = upper_1st - lower_1st
    if diff_1st == 0: #first number is equal
        subpatterns = patterns_for_bounds( lower[1:], upper[1:] )
        patterns = lower[0] + subpatterns
    elif diff_1st >= 1:
        n = len( lower ) - 1
        #if n <= 0:
        #    patterns = '[%d-%d]' % ( lower_1st, upper_1st )
        #else:
        lower_subpatterns = patterns_for_bounds( lower[1:], '9'*(len(upper)-1) )
        upper_subpatterns = patterns_for_bounds( '0'*(len(lower)-1), upper[1:] )
        patterns = '(' + lower[0] + lower_subpatterns
        if diff_1st >= 2:
            if diff_1st == 2:
                assert lower_1st+1 == upper_1st-1
                middle_pattern = '%d'%(lower_1st+1)
            else:
                middle_pattern = '[%d-%d]' % (lower_1st+1,upper_1st-1)
            if n == 1:
                middle_pattern += '[0-9]'
            elif n >= 2:
                middle_pattern += '[0-9]{%d}' % (n,)
            patterns += '|' + middle_pattern
        patterns += '|' + upper[0] + upper_subpatterns + ')'
    return patterns
    

def compile_num_range( pattern ):
    intervals = pattern.split(',')
    re_pattern = ''
    for interval in intervals:
        if interval == '*':
            re_pattern += '|.*'
            continue
        bounds = interval.split('-')
        if len( bounds ) == 1: #single date
            re_pattern += '|' + interval
            continue
        if len(bounds[0]) < len(bounds[1]):
            bounds[0] = '0' * (len(bounds[1]) - len(bounds[0])) + bounds[0]
        pattern = patterns_for_bounds( bounds[0], bounds[1] )
        re_pattern+='|' + pattern
    re_pattern = re_pattern[1:]
    return re.compile( re_pattern )
        
        
            

def compile_category( pattern ):
    return re.compile( '|'.join( pattern.split(',') ) )

year_re = compile_num_range( args.birth_year )
sex_re = compile_category( args.sex )
filepattern = args.state
if filepattern.find(',') >= 0:
    filepattern = '{' + filepattern + '}'
filepattern += '.data.txt'



txt_dir = os.path.dirname(sys.argv[0])
if txt_dir:
    os.chdir(txt_dir)
txt_dir = '.'

names = {}
data_filenames = glob.glob(filepattern)
for line in fileinput.input( data_filenames ):
    state, sex, year, name, count = line.strip().split(',')
    if not year_re.fullmatch( year ) or not sex_re.fullmatch( sex ):
        continue
    count = int(count)
    if name in names:
        names[name] += count
    else:
        names[name] = count

for name, count in names.items():
    print( "%s:%d" % (name,count) )
