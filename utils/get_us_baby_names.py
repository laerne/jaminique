#!/usr/bin/env python3

# This file is part of Jaminique.
# Copyright (C) 2016 by Nicolas BRACK <nicolas.brack@mail.be>
# 
# Jaminique is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Jaminique is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Jaminique.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from io import BytesIO, TextIOWrapper
import os
import os.path
import re
import sys
import urllib.request as request
from zipfile import ZipFile

#Allow only interactive usage
if __name__ != '__main__':
    raise Exception("This program is intented to be called interactively")

#functions
def keygenerator( sex, year ):
    if sex == "M":
        sex = "male"
    elif sex == "F":
        sex = "female"
    else:
        sex = "no_gender"


    mutable_key = []
    for fieldname in fieldnames:
        if fieldname == 'sex':
            mutable_key.append( sex )
        elif fieldname == 'year':
            mutable_key.append( year )
    return tuple( mutable_key )


dataFilenameRe = re.compile( 'yob([0-9]{4}).txt' )
def isDataFilename( name ):
    match = dataFilenameRe.fullmatch( name )
    if match == None:
        return None
    else:
        return match.group(1)

def dirname( path, n=1 ):
    for i in range(n):
        path = os.path.dirname( path )
    return path


#Constants
dataset_url="https://www.ssa.gov/oact/babynames/names.zip"
destination_dir = os.path.join( dirname( os.path.abspath( sys.argv[0] ), n = 2 ), 'lexicons', 'us_baby_names' )
fieldnames = ('sex','year')


#Parse arguments
argparser = argparse.ArgumentParser()

argparser.add_argument( '-s', '--ignore-sex', action='store_true', default=False,
        help='Do not separate files by different sex.' )
argparser.add_argument( '-y', '--ignore-year', action='store_true', default=False,
        help='Do not separate files by different year.' )
argparser.add_argument( '-d', '--destination-dir', action='store', metavar="PATH",
        help='Set the output directory.  Directory is created if needed.' )
args = argparser.parse_args()


#Configure the constant to user input
fieldnames = tuple()
if not args.ignore_sex: fieldnames += ('sex',)
if not args.ignore_year: fieldnames += ('year',)

if args.destination_dir != None:
    destination_dir = args.destination_dir

#Print settings
print( 'Saving to directory "%s"' % destination_dir )
print( 'Splitting files according to those criteria : %s' % ", ".join( fieldnames ) )


#Build directory if missing
if not os.path.exists( destination_dir ):
    os.mkdir( destination_dir )
elif not os.path.isdir( destination_dir ):
    print( "Destination already exists and is not a directory.", file=sys.stderr )
    sys.exit(1)


#Procedure
reply = request.urlopen( dataset_url )
memfile = BytesIO( reply.read() )

zipdata = ZipFile( memfile )
subpaths = zipdata.namelist()
lexicon = {}

for subpath in subpaths:
    year = isDataFilename( subpath )
    if year == None:
        continue

    subfile = TextIOWrapper( zipdata.open( subpath ), encoding='utf-8' )
    for line in subfile:
        name, sex, count = line.strip().split(',')
        count = int( count )
        key = keygenerator( sex, year )
        if key not in lexicon:
            lexicon[ key ] = []
        lexicon[ key ].append((name,count))

for key in lexicon:
    destination_filename = "us_birth_names-%s.txt" % ("-".join(key))
    destination_path = os.path.join( destination_dir, destination_filename )
    with open( destination_path, 'wt' ) as destination_file:
        for name_and_count in lexicon[key]:
            destination_file.write( "%s:%d\n" % name_and_count )

