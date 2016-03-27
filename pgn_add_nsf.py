#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A very rudimentary script for reading an NSF database of players and a PGN database,
# and add PGN tags to the PGN database containing the players' NSF ID. Also splits the
# PGN database in two: One containing the games where both players have NSF IDs, and
# one containing the games where one or none have NSF IDs (for manual lookup).
# 
# Does not handle players with non-unique names, as without an NSF ID in the PGN we
# have no way of discerning who is who.

import csv
import re
import logging
import argparse

parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-p', '--pgn', help='Input file name for PGN database', required=True)
requiredNamed.add_argument('-e', '--elo', help='Input file name for player database', required=True)
args = parser.parse_args()

logging.basicConfig(filename='%s.log' % (__file__),level=logging.INFO)
pgn_in = args.pgn
nsf_file = args.elo
pgn_out_nsf = open('%s_both_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')
pgn_out_white_nsf = open('%s_white_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')
pgn_out_black_nsf = open('%s_black_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')
pgn_out_no_nsf = open('%s_no_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')

nsf_players = {}

players_same_name = []

# Read NSF players from CSV file
with open(nsf_file, 'rb') as csvfile:
    csvfile.readline()
    csvfile.readline()
    nsf_reader = csv.reader(csvfile, delimiter=';')
    for row in nsf_reader:
        if nsf_players.get(row[1]):
            players_same_name.append(row[1])
            logging.warning('Found duplicate name: %s' % row[1])
        nsf_players[row[1]] = row[0]

    # We remove all names that are shared because we can't trust it's the correct person
    # names are not unique so this is a piss poor data source really
    players_same_name = list(set(players_same_name))
    for name in players_same_name:
        del nsf_players[name]
        logging.info('Removing duplicate names: %s' % name)
    players_same_name = None

# Read games from PGN database and write NSF ID
with open(pgn_in, 'r') as f:
    line = f.readline()
    lineno = 1
    logging.debug("%s %s" % (lineno, line))

    while line:
        # Read a game
        pgn_game = []
        colors_with_nsf = {'White': False, 'Black': False}
        nsf = ''

        # Read PGN tags and add NSF ID tags where available
        while line not in ['\n', '\r\n']:
            pgn_game.append(line)
    
            m = re.search('\[(White|Black) "(.*)"\]', line)
            
            if m:
                color = m.group(1)
                name = m.group(2).replace(',', '') # NSF bruker ikke komma mellom etter- og fornavn
    
                try:
                    nsf = nsf_players[name]
                except:
                    logging.info('%s player not found in NSF database: %s' % (color, name))
                    try:
                        if name == name.replace('.', ''):
                            line = f.readline()
                            lineno += 1
                            logging.debug("%s %s" % (lineno, line))
                            continue
                        else:
                            name = name.replace('.', '')
                            nsf = nsf_players[name]
                    except:
                        logging.info('%s player not found in NSF database: %s' % (color, name))
                        line = f.readline()
                        lineno += 1
                        logging.debug("%s %s" % (lineno, line))
                        continue

                logging.info('%s player found in NSF database: %s (%s)' % (color, name, nsf))
                colors_with_nsf[color] = True
                newline = '\n'

                if line.endswith('\r\n'):
                    newline = '\r\n'

                pgn_game.append('[%sNSF "%s"]%s' % (color, nsf, newline))

            line = f.readline()
            lineno += 1
            logging.debug("%s %s" % (lineno, line))
    
        # We have read the PGN tags
        assert line in ['\n', '\r\n']
        pgn_game.append(line)
        line = f.readline()
        lineno += 1
        logging.debug("%s %s" % (lineno, line))

        # Read movetext
        while line and line not in ['\n', '\r\n']:
            pgn_game.append(line)
            line = f.readline()
            lineno += 1
            logging.debug("%s %s" % (lineno, line))

        # We have read a game, read the next one
        assert line in ['\n', '\r\n'] or not line

        if colors_with_nsf['Black'] and colors_with_nsf['White']:
            pgn_file = pgn_out_nsf
        elif colors_with_nsf['Black'] and not colors_with_nsf['White']:
            pgn_file = pgn_out_black_nsf
        elif colors_with_nsf['White'] and not colors_with_nsf['Black']:
            pgn_file = pgn_out_white_nsf
        else:
            pgn_file = pgn_out_no_nsf

        for l in pgn_game:
            pgn_file.write(l)

        if line in ['\n', '\r\n']:
            pgn_file.write(line)

        line = f.readline()
        lineno += 1
        logging.debug("%s %s" % (lineno, line))

pgn_out_nsf.close()
pgn_out_no_nsf.close()
pgn_out_white_nsf.close()
pgn_out_black_nsf.close()
