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

$o::
{
ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\3hp4dvm.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}
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
settimer, Counter, 1000
count = 0
tooltip, 0, 300, 520, 2
loop,
{

loaded := false
settimer, loadchecker, 500
while loaded = false
{
tooltip, Waiting For Campfires, 300, 500, 1
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Scanning Dungeon, 300, 500, 1
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

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
settimer, loopclick, 100
sleep 700
settimer, loopclick, off

tooltip, Astral Wind, 300, 500, 1
settimer, loop3, 100
sleep 300
send {lbutton down}
sleep 100
send {lbutton up}
sleep 300
settimer, loop3, off

tooltip, Gale Trap, 300, 500, 1
settimer, loop4, 100
sleep 500
settimer, loop4, off
sleep 100

tooltip, Triple Parry, 300, 500, 1
send {w down}
sleep 700
send {f down}
sleep 400
send {f up}
sleep 400
send {f down}
sleep 400
send {f up}
sleep 400
send {f down}
sleep 350
send {f up}
sleep 10
send {0 down}
sleep 10
send {0 up}
sleep 10
send {lbutton down}
sleep 10
send {lbutton up}
sleep 10
send {rbutton down}
sleep 10
send {rbutton up}

tooltip, Ariel Attack, 300, 500, 1
send {space down}
sleep 100
send {space up}
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200

tooltip, Tornado, 300, 500, 1
settimer, loop2, 100
sleep 300
send {w up}
sleep 400
settimer, loop2, off
sleep 375

tooltip, Camera Positioning, 300, 500, 1
DllCall("mouse_event", "UInt", 0x01, "UInt", 300, "UInt", 0)

tooltip, Shard Bow, 300, 500, 1
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
settimer, scrollup, 10
send {c down}
sleep 50
send {c up}
sleep 250
settimer, scrollup, off
sleep 250
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -200)
sleep 500
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -400)
sleep 700
click WheelDown
sleep 10
click WheelDown
sleep 10
click WheelDown
sleep 10
click WheelDown
sleep 10
click WheelDown
sleep 10
click WheelDown
sleep 10
click WheelDown
sleep 100

tooltip, Camera Positioning, 300, 500, 1
DllCall("mouse_event", "UInt", 0x01, "UInt", -170, "UInt", 0)
sleep 600

tooltip, Player Positioning, 300, 500, 1
send {d down}
sleep 200

tooltip, Gale Punch, 300, 500, 1
settimer, loop9, 100
sleep 500
send {d up}
settimer, loop9 ,off

tooltip, Blinding Dawn, 300, 500, 1
settimer, loop7, 100
sleep 100
;send {w down}
sleep 400
;send {w up}
sleep 1400
settimer, loop7, off
sleep 1300

tooltip, Astral Wind, 300, 500, 1
settimer, loop3, 100
sleep 1200
settimer, loop3, off
sleep 500

tooltip, Navigating, 300, 500, 1
DllCall("mouse_event", "UInt", 0x01, "UInt", 1150, "UInt", 0)
send {w down}
sleep 1300
send {1 down}
sleep 100
send {1 up}
sleep 100
send {shift down}
sleep 100
send {shift up}
sleep 100
send {tab down}
sleep 100
send {tab up}
sleep 750
send {w up}

tooltip, Chest 1, 300, 500, 1
send {e down}
sleep 10
send {e up}
sleep 700

gosub, imagescan

send {a down}
sleep 300
send {a up}

tooltip, Chest 2, 300, 500, 1
send {e down}
sleep 10
send {e up}
sleep 700

gosub, imagescan

send {a down}
sleep 300
send {a up}

tooltip, Chest 3, 300, 500, 1
send {e down}
sleep 10
send {e up}
sleep 700

gosub, imagescan

send {a down}
sleep 300
send {a up}

tooltip, Chest 4, 300, 500, 1
send {e down}
sleep 10
send {e up}
sleep 700

gosub, imagescan

send {a down}
sleep 400
send {a up}

tooltip, Chest 5, 300, 500, 1
send {e down}
sleep 10
send {e up}
sleep 700

gosub, imagescan

;tooltip, Talk To Ferryman, 300, 500, 1
;send {s down}
;sleep 700
;send {s up}
;send {d down}
;sleep 750
;send {d up}
;send {e down}
;sleep 100
;send {e up}
;sleep 100
;send {1 down}
;sleep 100
;send {1 up}
;sleep 100
;send {2 down}
;sleep 100
;send {2 up}
;sleep 100

tooltip, Leaving Ferryman, 300, 500, 1
send {shift down}
sleep 100
send {shift up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 1150, "UInt", 0)
;DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
send {w down}
sleep 100
send {w up}
sleep 100
send {w down}
sleep 5000
send {w up}

loaded := false
settimer, loadchecker, 500
while loaded = false
{
tooltip, Waiting For Load, 300, 500, 1
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

loaded := false
settimer, loadchecker3, 500
while loaded = false
{
tooltip, Scanning Instance, 300, 500, 1
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 250
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

tooltip, Macro End, 300, 500, 1
sleep 1000

}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

imagescan:

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Moonseye.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Stormseye.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Idol.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\9HP.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\3hp4dvm.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Smith.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Enchants.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Insignia.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Blessed.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Umbral.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Wind.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Wayward.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Blue.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Bloodless.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 300
}

ImageSearch, xxx, yyy, 700, 200, 1250, 800, *10 %A_ScriptDir%\Ferryman\Exit.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

scrollup:
click WheelUp
return

scrolldown:
click WheelDown
return

loopclick:
{
send {lbutton down}
sleep 50
send {lbutton up}
}
return

loop2:
{
send {2 down}
sleep 50
send {2 up}
}
return

loop3:
{
send {3 down}
sleep 50
send {3 up}
}
return

loop4:
{
send {4 down}
sleep 50
send {4 up}
}
return

loop7:
{
send {7 down}
sleep 50
send {7 up}
}
return

loop9:
{
send {9 down}
sleep 50
send {9 up}
}
return

counter:
count++
tooltip, %count%, 300, 520, 2
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loadchecker:
ImageSearch, xxx, yyy, 800, 580, 1125, 630, *40 %A_ScriptDir%\Ferryman\PressKeyToBegin.png
if (ErrorLevel = 0)
{
settimer, loadchecker, off
loaded := true
}
return

loadchecker2:
ImageSearch, xxx, yyy, 450, 0, 560, 20, *40 %A_ScriptDir%\Ferryman\Dungeon.png
if (ErrorLevel = 0)
{
settimer, loadchecker2, off
loaded := true
}
return

loadchecker3:
ImageSearch, xxx, yyy, 550, 950, 750, 1079, *60 %A_ScriptDir%\Ferryman\Sword.png
if (ErrorLevel = 0)
{
settimer, loadchecker3, off
loaded := true
}
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