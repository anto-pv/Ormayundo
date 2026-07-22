# Ormayundo demo — render with:  vhs demo.tape   (or the Docker one-liner in demo/README)
Output ormayundo-demo.gif

Set FontSize 22
Set Width 1080
Set Height 560
Set Padding 28
Set Theme "Catppuccin Mocha"
Set TypingSpeed 55ms

# launch the REPL off-screen so the recording starts clean
Hide
Type "python3 -i replay.py"
Enter
Sleep 800ms
Show

Type `remember("Priya leads the Atlas project.")`
Sleep 300ms
Enter
Sleep 1200ms

Type `remember("Arun works on the Atlas project.")`
Sleep 300ms
Enter
Sleep 1200ms

Type `remember("The Atlas project runs on PostgreSQL.")`
Sleep 300ms
Enter
Sleep 1400ms

Type `print(recall("Who works on the project that uses PostgreSQL?"))`
Sleep 300ms
Enter
Sleep 2800ms
Sleep 2s
