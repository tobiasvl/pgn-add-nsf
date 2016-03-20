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

logging.basicConfig(filename='%s.log' % (__file__),level=logging.DEBUG)
pgn_in = 'NewGame.pgn'
nsf_file = 'elo.csv'
pgn_out_nsf = open('%s_with_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')
pgn_out_no_nsf = open('%s_missing_nsf_id.pgn' % (pgn_in.split('.')[0]), 'w')

nsf_players = {}

players_same_name = []

games_missing = 0
games_with = 0

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
        while line != '\n':
            pgn_game.append(line)
    
            m = re.search('\[(White|Black) "(.*)"\]', line)
            
            if m:
                color = m.group(1)
                name = m.group(2).replace(',', '') # NSF bruker ikke komma mellom etter- og fornavn
    
                try:
                    nsf = nsf_players[name]
                except:
                    logging.debug('Player not found in NSF database: %s' % name)
                    line = f.readline()
                    lineno += 1
                    logging.debug("%s %s" % (lineno, line))
                    continue
                    try:
                        nsf = nsf_players[name.replace('.', '')]
                    except:
                        logging.debug('Player not found in NSF database: %s' % name)
                        line = f.readline()
                        lineno += 1
                        logging.debug("%s %s" % (lineno, line))
                        continue
    
                colors_with_nsf[color] = True
                pgn_game.append('[%sNSF "%s"]\n' % (color, nsf))

            line = f.readline()
            lineno += 1
            logging.debug("%s %s" % (lineno, line))
    
        # We have read the PGN tags
        assert line == '\n'
        pgn_game.append(line)
        line = f.readline()
        lineno += 1
        logging.debug("%s %s" % (lineno, line))

        # Read movetext
        while line and line != '\n':
            pgn_game.append(line)
            line = f.readline()
            lineno += 1
            logging.debug("%s %s" % (lineno, line))

        # We have read a game, read the next one
        assert line == '\n' or not line

        if colors_with_nsf['Black'] and colors_with_nsf['White']:
            games_with += 1
            for l in pgn_game:
                pgn_out_nsf.write(l)

            pgn_out_nsf.write('\n')
        else:
            games_missing += 1
            for l in pgn_game:
                pgn_out_no_nsf.write(l)

            pgn_out_no_nsf.write('\n')

        # TODO Handle poorly formatted PGN files:
        # * two blank lines in a row
        # * comment with two blank lines on each side

        line = f.readline()
        lineno += 1
        logging.debug("%s %s" % (lineno, line))

pgn_out_nsf.close()
pgn_out_no_nsf.close()

logging.debug(games_with)
logging.debug(games_missing)
