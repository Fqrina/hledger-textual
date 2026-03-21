# hledger-textual demo
# Generates demo.gif for the README

Output demo.gif

Set Shell zsh
Set Theme "Catppuccin Mocha"
Set FontSize 14
Set Width 1400
Set Height 800
Set Padding 10

# Launch the app with the demo journal
Type "uv run hledger-textual -f examples/demo.journal"
Enter
Sleep 3s

# --- 1. Summary tab ---
Sleep 1s

# --- 2. Transactions tab ---
Type "2"
Sleep 1s

# Scroll down
Down
Down
Down
Sleep 0.5s

# Navigate to previous month
Left
Sleep 1s

# Back to current month
Type "t"
Sleep 1s

# Search
Type "/"
Sleep 0.3s
Type "ac:expenses:food"
Sleep 1s
Escape
Sleep 0.5s

# --- CSV Import ---
Type "i"
Sleep 1s

# File picker: clear default ~/Downloads/ (13 chars) and type the CSV path
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Backspace
Type "examples/bank-export.csv"
Sleep 1s
Enter
Sleep 2s

# Rules Manager opens (no existing rules): Tab to + New and confirm
Tab
Sleep 0.3s
Enter
Sleep 2s

# Wizard Step 1 — CSV Preview with auto-detected columns
Sleep 1s

# Tab to Next button and advance to Step 2
Tab
Sleep 0.2s
Tab
Sleep 0.2s
Enter
Sleep 1s

# Close wizard
Escape
Sleep 0.5s

# --- 3. Recurring tab ---
Type "3"
Sleep 1s

# --- 4. Budget tab ---
Type "4"
Sleep 1s

# Navigate months in budget
Left
Sleep 1s
Left
Sleep 1s
Type "t"
Sleep 1s

# --- 5. Reports tab ---
Type "5"
Sleep 1s

# Toggle chart
Type "c"
Sleep 1s

# --- 6. Accounts tab ---
Type "6"
Sleep 1s

# Drill into an account
Down
Down
Enter
Sleep 1s
Escape
Sleep 0.5s

# --- Back to summary ---
Type "1"
Sleep 1s

# Quit
Type "q"
Sleep 0.5s
