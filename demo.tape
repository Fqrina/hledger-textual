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
Sleep 2s

# --- 2. Transactions tab ---
Type "2"
Sleep 2s

# Scroll down a bit
Down
Down
Down
Sleep 1s

# Navigate to previous month
Left
Sleep 1.5s

# Back to current month
Type "t"
Sleep 1.5s

# --- 3. Open help panel ---
Type "?"
Sleep 2.5s
Escape
Sleep 1s

# --- 4. Recurring tab ---
Type "3"
Sleep 2s

# --- 5. Budget tab ---
Type "4"
Sleep 2s

# Navigate months in budget
Left
Sleep 1.5s
Left
Sleep 1.5s
Type "t"
Sleep 1.5s

# --- 6. Reports tab ---
Type "5"
Sleep 2s

# Toggle chart
Type "c"
Sleep 2s

# --- 7. Accounts tab ---
Type "6"
Sleep 2s

# Drill into first account
Down
Down
Enter
Sleep 2s
Escape
Sleep 1s

# --- 8. Back to summary ---
Type "1"
Sleep 2s

# Quit
Type "q"
Sleep 1s
