$m::
tooltip, ok, 1, 1
sleep 21600000
send {alt up}
sleep 100
DetectHiddenWindows, Off
WinGet, mylist, list
Loop % mylist
WinClose % "ahk_id " mylist%A_Index% ; space after ahk_id
sleep 10000
shutdown, 9
return

; 43200000 = 12 hours
; 21600000 = 6 hours
; 18000000 = 5 hours
; 14400000 = 4 hours