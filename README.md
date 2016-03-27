# Add NSF IDs to PGN

A very rudimentary script for adding NSF IDs (a chess player's internal ID in Norsk Sjakkforbund, the Norwegian Chess Federation) to PGN files.

It's not very flexible because it's made for a very specific use case: [Sjakknytt.no's chess game database](http://www.sjakknytt.no/partier/)

## Usage

`python pgn_add_nsf.py --pgn chess_games.pgn --elo nsf_players.csv`

## Behavior

The above command reads a CSV file of players and their internal ID in NSF (Norsk sjakkforbund; the Norwegian Chess Federation), and adds custom PGN tags (`WhiteNSF` and `BlackNSF`) with their NSF IDs to the PGN.

## Input files

### PGN

The PGN file should contain a number of chess games in the [PGN format](https://en.wikipedia.org/wiki/Portable_Game_Notation). The PGN tags and movetext should be separated by two newlines. Each game should also be separated by two newlines. 

### Player list

The list of NSF players should be a CSV file with ; as the delimiter, which is what NSF uses.

The first field should be the NSF ID, and the second field should be the player's name. No other fields are used.

NSF keeps an updated file with only the currently active players here: http://www.sjakk.no/rating/siste.txt

## Output files

The above command also splits the PGN database in several output files:

* The games where both players have NSF IDs
* The games where no players have NSF IDs
* The games where the white player has an NSF ID but not the black
* The games where the black player has an NSF ID but not the white

## Shortcomings

Names must be identical in the player list and PGN. It's OK if one source uses periods after initials and the other doesn't, and a couple of other minor differences, but we can't assume that "Carlsen, Magnus Øen" and "Carlsen, Magnus" is the same person, for example.

For the same reason, the script simply skips players with non-unique names.

Names are shitty unique identifiers when we don't have a unique NSF ID in the PGN already!
