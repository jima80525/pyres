@echo OFF
REM \Python27\Scripts\pylint --rcfile pylint.rc pyres\*.py
REM
REM echo Running test
REM \Python27\python -m unittest discover -s test
REM \Python27\python main.py -a http://rss.sciam.com/sciam/60-second-psych --start-date 03/13/14
REM \Python27\python main.py -a http://rss.sciam.com/sciam/60-second-psych
\Python27\python main.py -a http://rss.sciam.com/sciam/60-second-psych --start-date 05/14/14
