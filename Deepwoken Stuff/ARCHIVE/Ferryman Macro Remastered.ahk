#ifWinActive, Roblox
CoordMode Pixel
setkeydelay, 0
setmousedelay, 0
pause = off
tooltip, reloaded, 300, 500, 1

$xbutton1::0
$xbutton2::9

$m::
suspend, off
reload
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$i::
{
loaded := true
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::

send {tab down}
sleep 100
send {tab up}
ImageSearch, xxx, yyy, 25, 150, 700, 1000, *50 %A_ScriptDir%\Ferryman\Campfire.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
}
send {tab down}
sleep 100
send {tab up}
send {shift down}
sleep 100
send {shift up}

PressToBegin:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Ferryman\PressToBegin.png
if (ErrorLevel = 0)
{
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
sleep 200
goto, PressToBegin
}

tooltip, Confirming "Press To Begin" Has Loaded, 15, 665, 15
PressToBegin2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Ferryman\PressToBegin.png
if (ErrorLevel = 0)
{
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, PressToBegin2
}

CharacterLoad:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Ferryman\Loadering.png
if (ErrorLevel = 1)
{
sleep 200
goto, CharacterLoad
}

sleep 500
tooltip, Camera Orientation, 300, 500, 1
send {shift down}
sleep 50
send {shift up}
sleep 50
DllCall("mouse_event", "UInt", 0x01, "UInt", 1300, "UInt", 0)
sleep 100

tooltip, Player Positioning, 300, 500, 1
send {w down}
sleep 1000
send {w up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", -95, "UInt", 0)
sleep 100

tooltip, Start The Fight, 300, 500, 1
send {1 down}
sleep 100
send {1 up}
sleep 500
send {h down}
sleep 100
send {e down}
sleep 100
send {e up}
sleep 1000
send {1 down}
sleep 100
send {1 up}
sleep 100
send {h up}
sleep 100

tooltip, Regen Ether, 300, 500, 1
send {lbutton down}
sleep 200
send {lbutton down}
sleep 500

tooltip, Astral Wind, 300, 500, 1
send {3 down}
sleep 100
send {3 up}
sleep 100
send {lbutton down}
sleep 100
send {lbutton up}
sleep 750

tooltip, Gale Trap, 300, 500, 1
send {4 down}
sleep 500
send {4 up}

return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$mbutton::
while getkeystate("mbutton","P")
{
send {q down}
sleep 5
send {q up}
sleep 5
send {space down}
sleep 5
send {space up}
sleep 140
send {rbutton down}
sleep 50
send {rbutton up}
sleep 1050
}
return

~$e::
sleep 250
while getkeystate("e","P")
{
send {e down}
sleep 10
send {e up}
sleep 10
}
return

~$tab::
suspend, off
if pause = off
{
pause = on
tooltip, Paused
suspend, on
return
}
if pause = on
{
pause = off
tooltip
return
}
return

~$/::
if pause = off
{
pause = on
tooltip, Paused
suspend, on
return
}
else
return
return

~$esc::
~$enter::
suspend, off
pause = off
tooltip
return

$lbutton::
settimer, click, 20
gosub, click
return
$lbutton up::
settimer, click, off
return
click:
send {lbutton}
return

,:: suspend
return