# Competition ranking
CLI: python3 rank.py INPUT.tsv OUTPUT.json
Columns team,player,score. Keep each player's maximum integer score within each
team. Rank descending by score; ties share competition rank and leave gaps
(scores 9,9,7 get ranks 1,1,3). Break display ties by player name ascending.
JSON maps alphabetically ordered team names to lists of {player,score,rank}.
TSV quoting is standard. Preserve input. Empty header-only input produces {}.
