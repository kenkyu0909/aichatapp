' Run a command in the background with no console window.
' Usage: wscript launch_hidden.vbs "<command>" [args...]
Option Explicit

Dim shell, cmd, i
If WScript.Arguments.Count = 0 Then
    WScript.Quit 1
End If

cmd = ""
For i = 0 To WScript.Arguments.Count - 1
    If i > 0 Then cmd = cmd & " "
    cmd = cmd & """" & WScript.Arguments(i) & """"
Next

Set shell = CreateObject("WScript.Shell")
' 0 = hidden window, False = do not wait for the process to finish.
shell.Run cmd, 0, False
