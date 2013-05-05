@echo OFF
\Python27\Scripts\pylint --rcfile pylint.rc pyres\db.py
REM \Python27\Scripts\pylint --rcfile pylint.rc pyres\feeder.py
REM
\Python27\python -m unittest discover -s test

