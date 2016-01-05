#
# Copyright (C) 2024 Pau Sanchez
#
# MIT LICENSE
#
import sys
import shutil
import subprocess
import argparse
from datetime import datetime, timedelta

ALPHABET = {
  ' ': [
    '·',
    '·',
    '·',
    '·',
    '·',
  ],
  '.': [
    '·',
    '·',
    '·',
    '·',
    '#',
  ],
  '!': [
    '#',
    '#',
    '#',
    '·',
    '#',
  ],
  'A': [
    '·#·',
    '#·#',
    '###',
    '#·#',
    '#·#',
  ],
  'B': [
    '##·',
    '#·#',
    '##·',
    '#·#',
    '##·',
  ],
  'C': [
    '·##',
    '#··',
    '#··',
    '#··',
    '·##',
  ],
  'D': [
    '###·',
    '#··#',
    '#··#',
    '#··#',
    '###·',
  ],
  'E': [
    '###',
    '#··',
    '##·',
    '#··',
    '###',
  ],
  'F': [
    '###',
    '#··',
    '##·',
    '#··',
    '#··',
  ],
  'G': [
    '·###',
    '#···',
    '#·##',
    '#··#',
    '·##·',
  ],
  'H': [
    '#·#',
    '#·#',
    '###',
    '#·#',
    '#·#',
  ],
  'I': [
    '#',
    '#',
    '#',
    '#',
    '#',
  ],
  'J': [
    '··#',
    '··#',
    '··#',
    '#·#',
    '·#·',
  ],
  'K': [
    '#·#',
    '#·#',
    '##·',
    '#·#',
    '#·#',
  ],
  'L': [
    '#··',
    '#··',
    '#··',
    '#··',
    '###',
  ],
  'M': [
    '#···#',
    '##·##',
    '#·#·#',
    '#···#',
    '#···#',
  ],
  'N': [
    '#···#',
    '##··#',
    '#·#·#',
    '#··##',
    '#···#',
  ],
  'O': [
    '·##·',
    '#··#',
    '#··#',
    '#··#',
    '·##·',
  ],
  'P': [
    '##·',
    '#·#',
    '##·',
    '#··',
    '#··',
  ],
  'Q': [
    '·##·',
    '#··#',
    '#··#',
    '#·##',
    '·###',
  ],
  'R': [
    '##·',
    '#·#',
    '##·',
    '#·#',
    '#·#',
  ],
  'S': [
    '·##',
    '#··',
    '·##',
    '··#',
    '##·',
  ],
  'T': [
    '###',
    '·#·',
    '·#·',
    '·#·',
    '·#·',
  ],
  'U': [
    '#·#',
    '#·#',
    '#·#',
    '#·#',
    '###',
  ],
  'V': [
    '#·#',
    '#·#',
    '#·#',
    '#·#',
    '·#·',
  ],
  'W': [
    '#···#',
    '#···#',
    '#·#·#',
    '#·#·#',
    '·#·#·',
  ],
  'X': [
    '#·#',
    '#·#',
    '·#·',
    '#·#',
    '#·#',
  ],
  'Y': [
    '#·#',
    '#·#',
    '·#·',
    '·#·',
    '·#·',
  ],
  'Z': [
    '###',
    '··#',
    '·#·',
    '#··',
    '###',
  ]
}

def sundayBasedWeekday(dt):
  """ Let's shift 1 day so we start the week on Sunday's
  """
  return (dt.weekday() + 1) % 7

def sundayBasedWeekNumber(dt):
  """ Getting the "right" week index to draw things is tricky, since weeks
  in datetime start on Monday and we want them to start on Sunday, thus
  the index has an offset we need to address
  """
  # NOTE: don't use isocalendar().week (is even worse)
  # NOTE: years that start in sunday, will start on week 1
  first_week = int(datetime(dt.year, 1, 1).strftime('%W'))
  return int(dt.strftime('%W')) - first_week

def isDayActive(activity_matrix, dt):
  """
    Returns True if given date is active on given activity matrix
    and False otherwise.

    Active is determined by character '#'
  """

  # 0-based indexes for both day of week and week_number
  day_of_week = sundayBasedWeekday(dt)
  week_number = sundayBasedWeekNumber(dt)

  # just access as row = day_of_week / column = week_num
  return activity_matrix[day_of_week][week_number] == '#'

def patchActivityMatrix(activity_matrix, dt, char = '!'):
  """ It just patches given date in activity_matrix if it is active
  """
  if not isDayActive(activity_matrix, dt):
    return activity_matrix

  day_of_week = sundayBasedWeekday(dt)
  week_number = sundayBasedWeekNumber(dt)

  patched = activity_matrix[:]
  patched[day_of_week] = patched[day_of_week][:week_number] + char + patched[day_of_week][week_number+1:]
  return patched

def drawMatrix(matrix):
  print("-"*53)
  for lines in matrix:
    print (lines.replace('·', ' ').replace('_', ' '))
  print("-"*53)
  return

def _run(command, **kwargs):
  return subprocess.run(command, capture_output = True, **kwargs)

def activityFromGit(year, repo_path):
  """
  Draws activity based on git commits in given repository

  E.g:

  _····················································
  ··##··##··###··#·#···#··###···#··##····#···#·###·###·
  ·#···#··#·#··#·#·##··#·#······#·#······#···#·#···#···
  ·#···#··#·#··#·#·#·#·#·#·##···#··##····#···#·##··##·
  ·#···#··#·#··#·#·#··##·#··#···#····#···#···#·#···#··
  ··##··##··###··#·#···#··##····#··##····###·#·#···###
  ····················································
  """
  start_date = datetime(year, 1, 1)
  end_date = datetime(year, 12, 31)

  # for simplicity, let's create a matrix with all days of week
  activity_matrix = [
    '', # Sun
    '', # Mon
    '', # Tue
    '', # Wed
    '', # Thu
    '', # Fri
    '', # Sat
  ]

  # let's fill in first few days with spaces
  first_day = sundayBasedWeekday(start_date)
  while first_day > 0:
    first_day -= 1
    activity_matrix[first_day] += '_'

   # print all commit dates in 'YYYY-MM-DD' format
  commit_dates = _run(['git', 'log', '--oneline', '--format=%as'], cwd = repo_path)
  commit_dates = set(commit_dates.stdout.decode('utf-8').split())

  # now let's fill each of the days
  current_date = start_date
  while current_date <= end_date:
    hasActivity = current_date.date().isoformat() in commit_dates

    day_of_week = sundayBasedWeekday(current_date)
    activity_matrix[day_of_week] += '#' if hasActivity else '·'
    current_date += timedelta(days=1)

  return activity_matrix

def activityCommitToGit(year, activity_matrix, commits_per_day, gradient):
  """ Iterate through all days in given year and perform a commit for
  each day in the activity matrix that there is activity.

  IMPORTANT:
     commits_per_day = is the amount of commits that will be done on
                       each day (gradient sits on top of this value)

     gradient = ['left2right', 'right2left', 'top2bottom', 'bottom2top']

  Gradients are a way of doing more commits depending on the week of the year
  (left to right or right to left), or depending on the day of the week
  (top2bottom or bottom2top).

  NOTE: Gradients can generate a lot of commits
  """
  fname = 'dummy.txt'

  # let's start clean
  shutil.rmtree('.git')
  _run(['git', 'init'])
  _run(['git', 'add', '.']) # add all files in the folder

  start_date = datetime(year, 1, 1)
  end_date = datetime(year, 12, 31)

  name  = _run(['git', 'config', 'user.name']).stdout.strip()
  email = _run(['git', 'config', 'user.email']).stdout.strip()

  # start Jan 1st at 12:00h
  current_date = start_date + timedelta(hours=12)
  while current_date <= end_date:

    if isDayActive(activity_matrix, current_date):
      # do N commits or do gradient based on the week-index?
      ncommits = 0

      if gradient == 'left2right':
        ncommits = sundayBasedWeekNumber(current_date)
      elif gradient == 'right2left':
        ncommits = 53 - sundayBasedWeekNumber(current_date)
      elif gradient == 'top2bottom':
        ncommits = sundayBasedWeekday(current_date)
      elif gradient == 'bottom2top':
        ncommits = 7 - sundayBasedWeekday(current_date)

      # do N commits each day
      for n in range(commits_per_day + ncommits):
        with open(fname, 'w+t') as f:
          patched = patchActivityMatrix(activity_matrix, current_date)
          for line in patched:
            f.write(line + "\n")
          f.write(f'\nDay {current_date.isoformat()} is active! Commit #{n}')

        _run(['git', 'add', fname])
        a = _run(
          ['git', 'commit', '-m', f'Commit for {current_date.date().isoformat()} n{n}'],
          env = {
           'GIT_AUTHOR_NAME': name,
           'GIT_AUTHOR_EMAIL': email,
           'GIT_AUTHOR_DATE': current_date.isoformat(),
           'GIT_COMMITTER_NAME': name,
           'GIT_COMMITTER_EMAIL': email,
           'GIT_COMMITTER_DATE': current_date.isoformat(),
          },
        )

    current_date += timedelta(days=1)

  return


def activityMatrixFromText(text, alphabet):
  # let's do a 5x1 matrix to avoid writing in first week
  matrix = ['·']*5

  warnings = []

  # we always start on first row
  for char in text.upper():
    # draw char in matrix plus a space
    char_matrix = alphabet.get(char, None)
    if not char_matrix:
      print (f"ERROR: Cannot draw character {char}. Missing in input alphabet. Skipping")
      continue

    for row, char_line in enumerate(char_matrix):
      matrix[row] += char_line + '·'

    if len(matrix[0]) > 52:
      warnings.append(f"WARNING: Character '{char}' is outside the drawing canvas!")

  if warnings:
    print("-"*80)
    print("\n".join(warnings))
    print("-"*80)
    print("")

  # add top and bottom rows
  matrix = [''] + matrix + ['']

  # NOTE: adjust length to 53 columns (max nweeks per year)
  for i in range(7):
    matrix[i] += '·' * 53
    matrix[i] = matrix[i][:53]

  return matrix

def main():
  # original hand-made drawing before introducing the alphabet :D
  drawing_matrix = [
    ###########################################################################
    #
    # Hey you! Yes, I'm talking to you!
    #
    # DRAW ANYTHING YOU'D LIKE HERE.
    #
    # If you don't pass --message option this is what is going to be "drawn"
    # on the git repository. You can use gradients even :)
    #
    # Have a nice day! ;)
    #
    ###########################################################################
    '·····················································', # Sun
    '··##··##··###··#·#···#··###···#··##····#···#·###·###·', # Mon
    '·#···#··#·#··#·#·##··#·#······#·#······#···#·#···#···', # Tue
    '·#···#··#·#··#·#·#·#·#·#·##···#··##····#···#·##··##··', # Wed
    '·#···#··#·#··#·#·#··##·#··#···#····#···#···#·#···#···', # Thu
    '··##··##··###··#·#···#··##····#··##····###·#·#···###·', # Fri
    '·····················································', # Sat
  ]

  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Create a git repository that will draw on the activity contributions matrix like the one shown on GitHub/GitLab',
    epilog=f"""Examples:

  Visualize given message (no commits):\n
    $ python {sys.argv[0]} --year {datetime.now().year-1} --m "coding is life"

  Create commits! (rewrites history):\n
    $ python {sys.argv[0]} --year {datetime.now().year-1} --message "coding is life" --commit

  Create commits using a gradient! (rewrites history):\n
    $ python {sys.argv[0]} --year {datetime.now().year-1} --message "coding is life" --commit --gradient top2bottom

  Draw given repository activity on the screen (for given year):\n
    $ python {sys.argv[0]} --year {datetime.now().year-1} --draw --repo /path/to/repo/

NOTE: If you'd like to use your own hand-made drawing, it's easy. Just edit
this python script. Have a look at main function. Have fun!
_
""",
  )
  parser.add_argument('--year', '-y', type=int, default=datetime.now().year,
                      help=f'Specify the year (default: {datetime.now().year})')

  parser.add_argument('--message', '-m', default='',
                      help='Specify the message to draw (default: "")')

  parser.add_argument('--commit', action="store_true",
                      help='Recreates repository with a new commit history')

  parser.add_argument('--commits-per-day', '-c', type=int, default='1',
                      help='Use with --comit. Commits per day (default: 1)')

  parser.add_argument('--gradient', default="",
                      help="""
Use with --commit. Generates a gradient of commits (min value = commits per day).

Valid values: left2right | right2left | top2bottom | bottom2top

All these values go from lower intensity (less commits) to higher intensity (more commits)

NOTE: it can generate lots of commits (few thousands)""")

  parser.add_argument('--draw', action="store_true",
                      help='Visualizes commit history as an activity matrix')

  parser.add_argument('--repo',
                      default='.', # cwd by default
                      help='Path to the repository to be visualized')

  args = parser.parse_args()

  if args.message:
    drawing_matrix = activityMatrixFromText(args.message, ALPHABET)

  if args.commit or not args.draw:
    print("Activity canvas to draw:")
    drawMatrix(drawing_matrix)

  if args.commit:
    print ("\nPerforming git commits...")
    activityCommitToGit(
      args.year,
      drawing_matrix,
      commits_per_day = args.commits_per_day,
      gradient = args.gradient,
    )
    print ("  Done!\n")
    args.draw = True

  if args.draw:
    print ("Activity from git commits:")
    activity_matrix = activityFromGit(args.year, args.repo)
    drawMatrix(activity_matrix)

  return

if __name__ == '__main__':
  main()

