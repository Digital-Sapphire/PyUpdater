@ECHO OFF
CLS
ECHO 1. Clean
ECHO 2. Install Dev Dependencies
ECHO 3. Run Tests
ECHO 4. Generate docs
ECHO.

CHOICE /C 1234 /M "Enter your choice:"

:: Note - list ERRORLEVELS in decreasing order
IF ERRORLEVEL 4 GOTO Docs
IF ERRORLEVEL 3 GOTO TEST
IF ERRORLEVEL 2 GOTO Install
IF ERRORLEVEL 1 GOTO Clean

:Clean
ECHO cleaning temp items
python dev\clean.py
GOTO End

:Install
ECHO Installing development dependencies
pip install -r requirements	 --upgrade
pip install -r dev\requirements.txt --upgrade
GOTO End

:Docs
ECHO Creating Docs
mkdocs build --clean
GOTO End

:Test
ECHO Starting Test
python dev\clean.py
tox
GOTO End

:End