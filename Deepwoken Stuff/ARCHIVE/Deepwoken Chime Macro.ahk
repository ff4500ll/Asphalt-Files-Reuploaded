;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

#ifWinActive, Roblox
setmousedelay, 0
setkeydelay, 0
pause = off
breakmacro := false

settimer, 1secondscan, 1000
tooltip, No Combo Active, 15, 540, 11

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$xbutton1::0
$xbutton2::9

$y::e

$mbutton::
while getkeystate("mbutton","P")
{
send {q down}
sleep 10
send {q up}
sleep 10
send {space down}
sleep 10
send {space up}
sleep 135
send {rbutton down}
sleep 50
send {rbutton up}
sleep 1100
}
return

$l:: reload
$m:: exitapp

~$tab::
suspend, off
if pause = off
{
pause = on
tooltip, Paused, , , 20
suspend, on
return
}
if pause = on
{
pause = off
tooltip, , , , 20
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
tooltip, , , , 20
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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loopclick:
send {lbutton down}
sleep 50
send {lbutton up}
return

looprightclick:
send {rbutton down}
sleep 50
send {rbutton up}
return

loopcrit:
send {r down}
sleep 50
send {r up}
return

loop2:
send {2 down}
sleep 50
send {2 up}
return

loop3:
send {3 down}
sleep 50
send {3 up}
return

loop4:
send {4 down}
sleep 50
send {4 up}
return

loop5:
send {5 down}
sleep 50
send {5 up}
return

loop6:
send {6 down}
sleep 50
send {6 up}
return

loop7:
send {7 down}
sleep 50
send {7 up}
return

loop8:
send {8 down}
sleep 50
send {8 up}
return

loop9:
send {9 down}
sleep 50
send {9 up}
return

loop0:
send {0 down}
sleep 50
send {0 up}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

1secondscan:

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\Sword.png
If (ErrorLevel = 0)
{
togglestate := false
tooltip, Sword, 15, 580, 1
}
Else If (ErrorLevel = 1)
{
togglestate := true
tooltip, Sword (UNEQUIPPED), 15, 580, 1
tooltip, , , , 2
tooltip, , , , 3
tooltip, , , , 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 10
tooltip, , , , 11
tooltip, , , , 12
tooltip, , , , 13
return
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\GaleLunge.png
If (ErrorLevel = 0)
{
tooltip, GaleLunge, 15, 600, 2
GaleLungeAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, GaleLunge (Cooldown), 15, 600, 2
GaleLungeAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\AstralWind.png
If (ErrorLevel = 0)
{
tooltip, AstralWind, 15, 620, 3
AstralWindAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, AstralWind (Cooldown), 15, 620, 3
AstralWindAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\TwisterKicks.png
If (ErrorLevel = 0)
{
tooltip, TwisterKicks, 15, 640, 4
TwisterKicksAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, TwisterKicks (Cooldown), 15, 640, 4
TwisterKicksAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\RisingWind.png
If (ErrorLevel = 0)
{
tooltip, RisingWind, 15, 660, 5
RisingWindAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, RisingWind (Cooldown), 15, 660, 5
RisingWindAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\WindPassage.png
If (ErrorLevel = 0)
{
tooltip, WindPassage, 15, 680, 6
WindPassageAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, WindPassage (Cooldown), 15, 680, 6
WindPassageAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\Revenge.png
If (ErrorLevel = 0)
{
tooltip, Revenge, 15, 700, 7
RevengeAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, Revenge (Cooldown), 15, 700, 7
RevengeAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\ShoulderBash.png
If (ErrorLevel = 0)
{
tooltip, ShoulderBash, 15, 720, 8
ShoulderBashAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, ShoulderBash (Cooldown), 15, 720, 8
ShoulderBashAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\ChampionsWhirlthrow.png
If (ErrorLevel = 0)
{
tooltip, ChampionsWhirlthrow, 15, 740, 9
ChampionsWhirlthrowAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, ChampionsWhirlthrow (Cooldown), 15, 740, 9
ChampionsWhirlthrowAvailable := false
}

ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\Taunt.png
If (ErrorLevel = 0)
{
tooltip, Taunt, 15, 760, 10
TauntAvailable := true
}
Else If (ErrorLevel = 1)
{
tooltip, Taunt (Cooldown), 15, 760, 10
TauntAvailable := false
}

return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

turnitoff:
send {w up}
send {a up}
send {s up}
send {d up}
settimer, loopclick, off
settimer, looprightclick, off
settimer, loopcrit, off
settimer, loop2, off
settimer, loop3, off
settimer, loop4, off
settimer, loop5, off
settimer, loop6, off
settimer, loop7, off
settimer, loop8, off
settimer, loop9, off
settimer, loop0, off
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$e::

if (togglestate = true)
{
send {e down}
keywait e
send {e up}
return
}

comboactivated := false
breakmacro := false

settimer, 1secondscan, off

regenerate:
Random, Var, 1, 4
tooltip, %Var%, 15, 520, 12
gosub, combo%Var%

if (comboactivated = false)
{
sleep 10
goto, regenerate
}

keywait e
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$e up::
breakmacro := true
comboactivated := true
gosub, turnitoff
tooltip, No Combo Active, 15, 540, 11
gosub, 1secondscan
settimer, 1secondscan, 1000
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

combo1:
If (RisingWindAvailable = true) && (ShoulderBashAvailable = true)
{

comboactivated := true
tooltip, Combo 1, 15, 540, 11

send {ctrl down}
sleep 10
send {rbutton down}
sleep 100
send {ctrl up}
send {rbutton up}
sleep 300

if (breakmacro = true)
{
return
}

send {5 down}
sleep 10
send {5 up}

if (breakmacro = true)
{
return
}

settimer, loop5, 100
while (RisingWindAvailable = true)
{
if (breakmacro = true)
{
return
}
ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\RisingWind.png
If (ErrorLevel = 1)
{
tooltip, RisingWind (Cooldown), 15, 660, 5
RisingWindAvailable := false
}
sleep 200
}
settimer, loop5, off
sleep 1000

if (breakmacro = true)
{
return
}

settimer, loopcrit, 100
sleep 1000
settimer, loopcrit, off

if (breakmacro = true)
{
return
}

settimer, loop8, 100
while (ShoulderBashAvailable = true)
{
if (breakmacro = true)
{
return
}
ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\ShoulderBash.png
If (ErrorLevel = 1)
{
tooltip, ShoulderBash (Cooldown), 15, 660, 8
ShoulderBashAvailable := false
}
sleep 200
}
settimer, loop8, off
sleep 1000

settimer, 1secondscan, 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

combo2:
If (TwisterKicksAvailable = true)
{

comboactivated := true
tooltip, Combo 2, 15, 540, 11

send {lbutton down}
sleep 10
send {rbutton down}
sleep 10
send {lbutton up}
send {rbutton up}
sleep 100

if (breakmacro = true)
{
return
}

settimer, loop4, 100
while (TwisterKicksAvailable = true)
{
if (breakmacro = true)
{
return
}
ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\TwisterKicks.png
If (ErrorLevel = 1)
{
tooltip, TwisterKicks (Cooldown), 15, 640, 4
TwisterKicksAvailable := false
}
sleep 200
}
settimer, loop4, off

settimer, 1secondscan, 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

combo3:
If (GaleLungeAvailable = true)
{

comboactivated := true
tooltip, Combo 3, 15, 540, 11

settimer, loopclick, 100
sleep 100
settimer, looprightclick, 100
sleep 500
settimer, loopclick, off
settimer, looprightclick, off

if (breakmacro = true)
{
return
}

settimer, loop2, 100
while (GaleLungeAvailable = true)
{
if (breakmacro = true)
{
return
}
ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\GaleLunge.png
If (ErrorLevel = 1)
{
tooltip, GaleLunge (Cooldown), 15, 620, 3
GaleLungeAvailable := false
}
sleep 200
}
settimer, loop2, off

settimer, 1secondscan, 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

combo4:
If (ChampionsWhirlthrowAvailable = true)
{

comboactivated := true
tooltip, Combo 1, 15, 540, 11

settimer, loop9, 100
while (ChampionsWhirlthrowAvailable = true)
{
if (breakmacro = true)
{
return
}
ImageSearch, xxx, yyy, 600, 1000, 1320, 1075, *5 %A_ScriptDir%\Kyrscleave\ChampionsWhirlthrow.png
If (ErrorLevel = 1)
{
tooltip, ChampionsWhirlthrow (Cooldown), 15, 740, 9
ChampionsWhirlthrowAvailable := false
}
sleep 200
}
settimer, loop9, off

settimer, 1secondscan, 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;