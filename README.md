# overpower_team_builder
Some modules to help build teams for the OverPower CCG.

The primary module allows a user to point to a CSV file of data with columns
'Character', 'Energy', 'Fighting', 'Strength', 'Intellect', 'Threat', and 'Special'
and specify a primary power stat for the team.

The code then builds all possible 16-rank teams of a given stat with at least 3 level-8 characters,
one level 7/8 character, and at least one character with an inherent ability or special card that
allows them to play from reserve.

## Usage
For example, to see all possible "Strength" teams, run:

```
from op_teams import make_overpower_teams
csvfile = 'data/characters.csv'
make_overpower_teams(csvfile, 'Strength')
```

Pass `save=True` to `make_overpower_teams` to save to a CSV file.