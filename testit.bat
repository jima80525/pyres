@echo OFF
\Python27\Scripts\pylint --rcfile pylint.rc pyres\*.py
REM
REM echo Running test
REM \Python27\python -m unittest discover -s test
\Python27\python main.py %*

