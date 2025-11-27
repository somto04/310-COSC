from datetime import datetime
from pydriller import Repository

nov_start = datetime(2024, 11, 1)
nov_end   = datetime(2024, 11, 30, 23, 59, 59)

for commit in Repository('https://github.com/somto04/310-COSC-CTRL-ALT-DEFEAT.git', since=nov_start, to=nov_end).traverse_commits():
    print(commit.hash, commit.insertions, commit.deletions)



