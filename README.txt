Event Business Ad Optimizer
=========================

A Streamlit web application to help media buyers make ad spend decisions for event businesses.

Requirements
-----------
1. Python 3.7 or higher
2. Required Python packages:
   - streamlit
   - pathlib

Installation
-----------
1. Move the event_optimizer folder to your desktop for easy access
2. Install Python from https://www.python.org/downloads/
2. Open a terminal/command prompt
3. Install required packages by running:
   pip install streamlit pathlib

Creating a Desktop Shortcut
-------------------------
Windows Users:
1. Move the event_optimizer folder to your desktop
2. Right-click on launch_optimizer.bat
3. Select "Create shortcut"
4. Right-click the new shortcut and select "Properties"
5. Click "Change Icon"
6. Click "Browse" and select icon.svg in the event_optimizer folder
7. Click "OK" to save the icon
8. Move the shortcut to your desktop
9. Double-click the shortcut to run the application

macOS/Linux Users:
1. Move the event_optimizer folder to your desktop
2. Open Terminal
3. Navigate to the event_optimizer folder:
   cd ~/Desktop/event_optimizer
4. Make the launch script executable:
   chmod +x launch_optimizer.sh
5. Create an application shortcut:
   - Right-click on your desktop
   - Select "Create Shortcut" or "New Launcher"
   - Set the command to: ~/Desktop/event_optimizer/launch_optimizer.sh
   - Click the default icon and browse to select icon.svg
   - Name it "Event Optimizer" and save

Running the Application
---------------------
1. Double-click your newly created desktop shortcut
2. The application will open in your default web browser
   (If it doesn't open automatically, visit http://localhost:8501)

Alternative Method (Command Line):
1. Open a terminal/command prompt
2. Navigate to the event_optimizer directory
3. Run: streamlit run "Event Optimizer.py"

Using the Application
-------------------
1. Enter your business parameters in the left panel
2. View financial projections and metrics in the right panel
3. Use the scenario management tools to save and compare different scenarios
4. Click the Help button (❔) in the top right for detailed explanations of all metrics

Files
-----
- Event Optimizer.py: Main application file
- launch_optimizer.bat: Windows launcher script
- launch_optimizer.sh: macOS/Linux launcher script
- icon.svg: Application icon
- README.txt: This instruction file
- requirements.txt: Required Python packages
- scenarios/: Directory for saved scenarios (created automatically)

Support
-------
If you encounter any issues, please ensure all requirements are properly installed and you're using the correct Python version.
