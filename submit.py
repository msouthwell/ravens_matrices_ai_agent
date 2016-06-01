from __future__ import print_function

import time
import os
import sys
import argparse
import json
from bonnie.submission import Submission

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
  parser = argparse.ArgumentParser(description='Submits code to the Udacity site.')
  parser.add_argument('--assignment', choices = ['P1', 'P2', 'P3', 'error-check'], required=True)
  parser.add_argument('--provider', choices = ['gt', 'udacity'], default = 'gt')
  parser.add_argument('--environment', choices = ['local', 'development', 'staging', 'production'], default = 'production')
  parser.add_argument('--files', type=str, nargs='+', default = [])
  args = parser.parse_args()

  app_data_dir = os.path.abspath(".bonnie")

  files = args.files
  agent_file = 'Agent.py'
  if agent_file not in files:
    files.append(agent_file)

  forbidden_exts = ['.class', '.pyc']
  expected_exts = ['.java', '.py']
  def ext(file):
    _, extension = os.path.splitext(file)
    return extension
  for file in files:
    if ext(file) in forbidden_exts:
      print("Wait! You don't really want to submit a", ext(file), "file! Please submit your .java or .py files only.")
      return
    elif ext(file) not in expected_exts:
      print ("Warning: you're submitting a", ext(file), "file. This may not be what you intend.  Press ctrl-C or cmd-C now to cancel...")
      time.sleep(3.0)

  submission = Submission('cs7637', args.assignment, 
                          filenames = args.files, 
                          environment = args.environment, 
                          provider = args.provider,
                          app_data_dir = app_data_dir)

  while not submission.poll():
    time.sleep(3.0)

  if submission.result():
    result = submission.result()
    if 'Execution' in result.get('Error', {}):
      eprint('Execution error!')
      eprint(result['Error']['Execution'])
    elif 'Build' in result.get('Error', {}):
      eprint('Build error!')
      eprint(result['Error']['Build'])
    else:
      if ('Problems' in result) & ('Sets' in result):
        print('Problem,Correct?,Correct Answer,Agent\'s Answer')
        problems = result['Problems']
        for key in problems:
          problem = problems[key]
          success = '1' if problem['Correct?'] == 'Correct' else '0'
          print(','.join([ '"'+problem['Problem']+'"',success,problem['Correct Answer'],problem['Agent\'s Answer'] ]))
        eprint(json.dumps(result['Sets'], indent=4))
      else:
        eprint(json.dumps(result, indent=4))
  elif submission.error_report():
    error_report = submission.error_report()
    eprint(json.dumps(error_report, indent=4))
  else:
    eprint("Unknown error.")

if __name__ == '__main__':
  main()
