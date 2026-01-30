@echo off
echo Creating suspect_detection_system project structure...

REM Root directory
mkdir suspect_detection_system
cd suspect_detection_system

REM Root files
type nul > config.py
type nul > app.py
type nul > requirements.txt

REM core/
mkdir core
type nul > core\watchlist.py
type nul > core\recognition.py
type nul > core\alerts.py
type nul > core\camera.py

REM gui/
mkdir gui
mkdir gui\templates
type nul > gui\templates\dashboard.html

mkdir gui\static
mkdir gui\static\css
type nul > gui\static\css\dashboard.css

mkdir gui\static\js
type nul > gui\static\js\dashboard.js

REM data/
mkdir data
type nul > data\watchlist.csv
type nul > data\watchlist_embeddings.pkl
type nul > data\cases.csv

mkdir data\images
mkdir data\images\PersonID_XXX

REM logs/
mkdir logs
type nul > logs\detections.log
type nul > logs\alerts.log
type nul > logs\system.log
type nul > logs\audit.log

REM evidence/
mkdir evidence
mkdir evidence\alert_frames
mkdir evidence\suspect_traces

REM utils/
mkdir utils
type nul > utils\add_person.py
type nul > utils\build_embeddings.py
type nul > utils\analyze_video.py

echo Project structure created successfully!
pause
