;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;DONT TOUCH ANYTHING HERE
tooltip, Press "P" To Start, 300, 520, 2
tooltip, Press "M" To Stop, 300, 540, 3
;DONT TOUCH ANYTHING HERE

;DONT TOUCH ANYTHING HERE
IfWinNotExist, Roblox
{
Run roblox://experiences/start?placeId=4111023553
exitapp
}
;DONT TOUCH ANYTHING HERE

;DONT TOUCH ANYTHING HERE
setkeydelay, 0
setmousedelay, 0
lootcounter := 0
fuckyounigga := false
niggafuckoff := false
locked := false
pause := off
scan := false
;DONT TOUCH ANYTHING HERE

;DONT TOUCH ANYTHING HERE
count := 0
minute := 0
hour := 0
;DONT TOUCH ANYTHING HERE

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Settings (true or false)

;THESE SETTINGS ARE FOR THE HP BAR CHECKING THING
StainedCheck := false
DepthsCheck := true
Disabled := false

;THIS SETTING IS FOR IF YOU ARE IN GAME
rejoined := false

;LIKE BRUH ITS IN THE NAME
TpBellCheck := true

;HIGHEST IS 1300
HigherEqualsLaggier := 500

;Autoloot Settings
Purple := true
Backpack := true
Enchants := false
DeepGems := false
Artifacts := true
EnchantStones := true
MaestroWeapons := true
LegendaryWeapons := true

;leave this at like 300 fuck you all
PickupDelay := 300

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$m::
suspend, off
send {7 up}
send {s up}
reload
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$o::
exitapp
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$i::
exitapp
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$y::
loaded := true
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$l::
send {q down}
sleep 1
send {space down}
sleep 1
send {q up}
send {space up}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$k::
DllCall("mouse_event", "UInt", 0x01, "UInt", 150, "UInt", 0)
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::

if (rejoined := true)
{
Run roblox://experiences/start?placeId=4111023553
}

fuckyou1 := (300 + HigherEqualsLaggier)
fuckyou2 := (1300 - HigherEqualsLaggier)

settimer, counter, 1000
tooltip, Loading, 300, 480, 4
tooltip, Total Item Counter: %lootcounter%, 300, 560, 17
tooltip, , , , 6
loop,
{

settimer, loop1, off
settimer, loope, off

returntostart:
if (rejoined = true)
{

settimer, failsafe, off
settimer, failsafe15, off
settimer, failsafe20, off
settimer, failsafe40, off
settimer, failsafeEXTRA, off

failcount := 0
settimer, failsafe, 1000
loaded := false
settimer, loadchecker7, 500
while loaded = false
{
tooltip, Waiting For "Press To Continue" , 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 59)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe, off
tooltip, Loaded, 300, 500, 1

mousemove, 1200, 550

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

sleep 500

failcount := 0
settimer, failsafe, 1000
loaded := false
settimer, loadchecker8, 500
while loaded = false
{
tooltip, Waiting For "Continue" , 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 59)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe, off
tooltip, Loaded, 300, 500, 1

click, 960, 600
sleep 250

mousemove, 800, 200
sleep 250

failcount := 0
settimer, failsafe40, 1000
loaded := false
settimer, loadchecker6, 1000
while loaded = false
{
tooltip, Finding Character, 300, 500, 1
tooltip, (Maestro Toucher), 300, 520, 2
sleep 1000
if (failcount > 39)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe40, off
tooltip, Loaded, 300, 500, 1

returntosender:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *130 %A_ScriptDir%\Maestro\MaestroToucher.png
if (ErrorLevel = 1)
{
sleep 500
goto returntosender
}

tooltip, Found Character, 300, 500, 1
tooltip, (Found Maestro Toucher), 300, 520, 2

sleep 100
mousemove, %xxx%, %yyy%,
sleep 100
click, %xxx%, %yyy%

sleep 1000

ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *130 %A_ScriptDir%\Maestro\MaestroToucher.png
if (ErrorLevel = 0)
{
sleep 500
goto returntosender
}

returntosender69420:
failcount := 0
settimer, failsafe15, 1000
loaded := false
settimer, loadchecker10, 500
while loaded = false
{
tooltip, Waiting For "Quick Join" , 300, 500, 1
tooltip, (Loading), 300, 520, 2
sleep 500
if (failcount > 14)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe15, off
tooltip, Loaded, 300, 500, 1

sleep 1000

ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\ErrorCode773.png
if (ErrorLevel = 0)
{
click, 960, 600
sleep 100
click, 960, 600
sleep 500
goto returntosender69420
}

failcount := 0
settimer, failsafe40, 1000
loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Waiting For "Press To Begin" (Press Y To Skip), 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 39)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe40, off
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

rejoined := false
}

failcount := 0
settimer, failsafe, 1000
loaded := false
settimer, loadchecker9, 500
while loaded = false
{
tooltip, Waiting For Character, 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 59)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe, off
tooltip, Loaded, 300, 500, 1

fuckyounigga := true

sleep 1000

ImageSearch, xxxxx, yyyyy, 710, 900, 1210, 940, *40 %A_ScriptDir%\Maestro\Hpbar.png
if (ErrorLevel = 0)
{
send {shift down}
sleep 10
send {shift up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 150, "UInt", 0)
sleep 10
}
if (ErrorLevel = 1)
{
send {tab down}
sleep 100
send {tab up}
sleep 400
beforecampfire:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *80 %A_ScriptDir%\Maestro\Campfire.png
If (ErrorLevel = 1)
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *30 %A_ScriptDir%\Maestro\Wood.png
sleep 100
if (ErrorLevel = 0)
{
mousemove, %xxx%, %yyy%
sleep 100
send {lbutton down}
sleep 100
mousemove, 190, 100
sleep 100
send {lbutton up}
sleep 100
loop, 2
{
click, 270, 90
sleep 1500
click, 960, 530
sleep 100
mousemove, 835, 600
sleep 500
send {lbutton down}
sleep 100
mousemove, 1060, 585
sleep 100
send {lbutton up}
sleep 100
send {lbutton down}
sleep 100
send {lbutton up}
sleep 1000
goto, beforecampfire
}
}
If (ErrorLevel = 1)
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *30 %A_ScriptDir%\Maestro\Stick.png
if (ErrorLevel = 0)
{
mousemove, %xxx%, %yyy%
sleep 100
send {lbutton down}
sleep 100
mousemove, 190, 100
sleep 100
send {lbutton up}
sleep 100
loop, 2
{
click, 270, 90
sleep 1500
click, 960, 530
sleep 100
mousemove, 835, 600
sleep 500
send {lbutton down}
sleep 100
mousemove, 1060, 585
sleep 100
send {lbutton up}
sleep 100
send {lbutton down}
sleep 100
send {lbutton up}
sleep 1000
goto, beforecampfire
}
}
if (ErrorLevel = 1)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
reload
}
}
}
sleep 100
mousemove, %xxx%, %yyy%
sleep 100
click, %xxx%, %yyy%
sleep 100
send {s down}
sleep 325
send {s up}
sleep 100
click, 970, 850
sleep 100
click, 970, 850
sleep 100
click, 970, 850
sleep 100
click, 970, 850
sleep 100
click, 970, 850
sleep 1000
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *30 %A_ScriptDir%\Maestro\ProduceSpark.png
click, %xxx%, %yyy%
sleep 1000

send {e down}
sleep 100
send {e up}

send {tab down}
sleep 100
send {tab up}
sleep 100

failcount := 0
settimer, failsafeEXTRA, 1000
loaded := false
settimer, loadchecker5, 500
while loaded = false
{
tooltip, Healing, 300, 500, 1
tooltip, (Sitting On Campfire), 300, 520, 2
sleep 50
if (failcount > 14)
{
send {e down}
sleep 100
send {e up}
sleep 200
send {w down}
sleep 350
send {w up}
sleep 10
send {s down}
sleep 25
send {s up}
send {shift down}
sleep 10
send {shift up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 150, "UInt", 0)
sleep 10
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
settimer, failsafeEXTRA, off
goto, returntostart
}
}
loaded = true
settimer, failsafeEXTRA, off
tooltip, Loaded, 300, 500, 1

if (rejoined = true)
{
send {e down}
sleep 100
send {e up}
sleep 200
send {w down}
sleep 350
send {w up}
sleep 10
send {s down}
sleep 25
send {s up}
sleep 10
send {shift down}
sleep 10
send {shift up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 150, "UInt", 0)
sleep 10
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
settimer, failsafeEXTRA, off
goto, returntostart
}

ihatecampfires:
send {e down}
sleep 100
send {e up}
sleep 500

ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\AntiCampfire.png
if (ErrorLevel = 0)
{
goto, ihatecampfires
sleep 500
}

send {w down}
sleep 350
send {w up}
sleep 10
send {s down}
sleep 25
send {s up}
sleep 10
send {shift down}
sleep 10
send {shift up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 150, "UInt", 0)
sleep 10
}

tooltip, Press "I" To AutoLoot, 300, 540, 3
settimer, loope, 1000
sleep 100
send {e down}
sleep 100
send {e up}
sleep 100

failcount := 0
settimer, failsafe20, 1000
loaded := false
settimer, loadchecker, 500
while loaded = false
{
tooltip, Waiting For Maestro Text (Press Y To Skip), 300, 500, 1
tooltip, (Talk To Maestro), 300, 520, 2
sleep 500
send {w down}
send {a down}
sleep 10
send {w up}
send {a up}
if (failcount > 19)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
settimer, loope, off
goto, returntostart
}
}
settimer, loope, off
loaded = true
settimer, failsafe20, off
tooltip, Loaded, 300, 500, 1

if (rejoined = true)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
goto, returntostart
}

settimer, loop1, 1000
sleep 100
send {1 down}
sleep 100
send {1 up}
sleep 100

returntosenderer:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\MaestroEvengarde.png
if (ErrorLevel = 0)
{
sleep 500
goto, returntosenderer
}
if (ErrorLevel = 1)
{
settimer, loop1, off
}

fuckyounigga := false

failcount := 0
settimer, failsafe40, 1000
loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Waiting For "Press To Begin" (Press Y To Skip), 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 39)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe40, off
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

failcount := 0
settimer, failsafe, 1000
loaded := false
settimer, loadchecker3, 500
while loaded = false
{
tooltip, Waiting For World (Press Y To Skip), 300, 500, 1
tooltip, (Loading Character), 300, 520, 2
sleep 500
if (failcount > 59)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe, off
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

tooltip, Maestro Touching In Progress, 300, 500, 1
send {shift down}
sleep 100
send {shift up}
sleep 200
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 100

tooltip, (Walking To Maestro), 300, 520, 2
send {w up}
sleep 50
send {w down}
sleep 200
send {1 down}
sleep 100
send {1 up}
sleep 3000
send {w up}
sleep 100

tooltip, (Hold Crit), 300, 520, 2
send {r down}
sleep 100

tooltip, (Talk To Maestro), 300, 520, 2
send {e down}
sleep 100
send {e up}
sleep 500
tooltip, (Begin The Fight), 300, 520, 2
send {1 down}
sleep 100
send {1 up}
sleep 100

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Release Crit), 300, 520, 2
sleep 1500
send {r up}

scan := true

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Relentless Flames), 300, 520, 2
settimer, loop3, 100
send {w down}
sleep 500
;send {s down}
sleep 500
;send {s up}
settimer, loop3, off
send {w up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 2000
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 1000

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Fire Eruption), 300, 520, 2
settimer, loop4, 100
sleep 1500
settimer, loop4, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Charge Flame Ballista), 300, 520, 2
settimer, loop2, 100
sleep 1500
settimer, loop2, off
gosub, imbored

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Release Flame Ballista), 300, 520, 2
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50

if (rejoined = true)
{
goto, returntostart
}

DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
tooltip, (Crit), 300, 520, 2
settimer, loopr, 100
sleep 1000
settimer, loopr, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Relentless Flames), 300, 520, 2
settimer, loop3, 100
send {w down}
sleep 500
;send {s down}
sleep 500
;send {s up}
settimer, loop3, off
send {w up}
;DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 2000
;DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 1000

if (rejoined = true)
{
settimer, loop4, off
goto, returntostart
}

tooltip, (Fire Eruption), 300, 520, 2
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
settimer, loop4, 100
sleep 1500
settimer, loop4, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Eclipse Kick), 300, 520, 2
settimer, loop5, 100
sleep 1300
settimer, loop5, off

if (rejoined = true)
{
goto, returntostart
}

sleep 500 ;savethispointfuckheresearchctrlf
tooltip, (Shadow Assault), 300, 520, 2
settimer, loop6, 100
sleep 1000
settimer, loop6, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Crit), 300, 520, 2
settimer, loopr, 100
sleep 1000
settimer, loopr, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Relentless Flames), 300, 520, 2
settimer, loop3, 100
sleep 500
;send {s down}
sleep 500
;send {s up}
settimer, loop3, off
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 2000
;DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)

sleep 1000
tooltip, (Charge Flame Ballista), 300, 520, 2
settimer, loop2, 100
sleep 1500
settimer, loop2, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, (Release Flame Ballista), 300, 520, 2
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50

tooltip, (Fire Eruption), 300, 520, 2
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
settimer, loop4, 100
sleep 1500
settimer, loop4, off

sleep 1000
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
tooltip, Maestro Has Been Touched, 300, 500, 1
tooltip, (Time To Loot), 300, 520, 2
sleep 100

if (rejoined = true)
{
goto, returntostart
}

tooltip, Walking To Chest, 300, 500, 1
sleep 500
send {s down}
sleep 1000
send {s up}
sleep 500
send {tab down}
sleep 50
send {tab up}
sleep 50
send {shift down}
sleep 50
send {shift up}
sleep 50
settimer, loope, 100
send {w down}
sleep 2000
send {w up}
settimer, loope, off

if (rejoined = true)
{
goto, returntostart
}

tooltip, Looting Chest, 300, 500, 1
sleep 2500
gosub, lootchest
sleep 500

if (rejoined = true)
{
goto, returntostart
}

tooltip, Leaving Dungeon, 300, 500, 1
send {shift down}
sleep 100
send {shift up}
sleep 200
;DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 50
tooltip, (Sprinting To Portal), 300, 520, 2
send {w down}
sleep 50
send {w up}
sleep 50
send {w down}
sleep 1000
tooltip, (Slide Jump), 300, 520, 2
send {ctrl down}
sleep 50
send {space down}
sleep 50
send {ctrl up}
send {space up}
sleep 1750
tooltip, (Repositioning), 300, 520, 2
send {d down}
sleep 100
send {d up}
sleep 500
tooltip, (Slide Jump), 300, 520, 2
send {ctrl down}
sleep 50
send {space down}
sleep 50
send {ctrl up}
send {space up}
sleep 2500
send {w up}

failcount := 0
settimer, failsafe15, 1000
loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Waiting For "Press To Begin" (Press Y To Skip), 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
if (failcount > 14)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe15, off
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

failcount := 0
settimer, failsafe, 1000
loaded := false
settimer, loadchecker4, 500
while loaded = false
{
tooltip, Waiting For World (Press Y To Skip), 300, 500, 1
tooltip, (Loading Character), 300, 520, 2
sleep 500
if (failcount > 59)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
goto, returntostart
}
}
loaded = true
settimer, failsafe, off
tooltip, Loaded, 300, 500, 1

tooltip, Restarting Macro, 300, 500, 1
tooltip, (Looping), 300, 520, 2
sleep 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

lootchest:
mousemove, 1111, 333

;;;Purple

if (Purple = true)
{
tooltip, Searching For Purple, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Purple.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
gosub, lootchest
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
}
}

;;;Artifacts

if (Artifacts = true)
{
tooltip, Searching For Artifacts, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Smith.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *90 %A_ScriptDir%\Maestro\SinnersAsh.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Legendary Weapons

if (LegendaryWeapons = true)
{
tooltip, Searching For Legendary Weapons, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Wyrmtooth.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\ImperialStaff.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Crypt.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Curved.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Enchants

if (Enchants = true)
{
tooltip, Searching For Enchants, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Enchants.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Enchant Stones

if (EnchantStones = true)
{
tooltip, Searching For Enchant Stones, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\EnchantStone.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Maestro Weapons

if (MaestroWeapons = true)
{
tooltip, Searching For Maestro Weapons, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\PaleBriar.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\PurpleCloud.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\CeruleanThread.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Deep Gems

if (DeepGems = true)
{
tooltip, Searching For Deep Gems, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Gem.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Scroll Down Chest
loop, 10
{
click WheelDown
sleep 100
}

;;;Backpack

if (Backpack = true)
{
tooltip, Searching For Backpacks, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Backpack.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 1111, 333
sleep %PickupDelay%
lootcounter++
tooltip, Session Item Counter: %lootcounter%, 300, 560, 17
gosub, lootchest
}
}

;;;Exit
tooltip, Searching Complete, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *20 %A_ScriptDir%\Maestro\Exit.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loopclick:
if (niggafuckoff = true)
{
send {lbutton up}
return
}
send {lbutton down}
sleep 50
send {lbutton up}
return

loop1:
if (niggafuckoff = true)
{
send {1 up}
return
}
send {1 down}
sleep 50
send {1 up}
return

loopr:
if (niggafuckoff = true)
{
send {r up}
return
}
send {r down}
sleep 50
send {r up}
return

loope:
if (niggafuckoff = true)
{
send {e up}
return
}
send {e down}
sleep 50
send {e up}
return

loop2:
if (niggafuckoff = true)
{
send {2 up}
return
}
send {2 down}
sleep 50
send {2 up}
return

loop3:
if (niggafuckoff = true)
{
send {3 up}
return
}
send {3 down}
sleep 50
send {3 up}
return

loop4:
if (niggafuckoff = true)
{
send {4 up}
return
}
send {4 down}
sleep 50
send {4 up}
return

loop5:
if (niggafuckoff = true)
{
send {5 up}
return
}
send {5 down}
sleep 50
send {5 up}
return

loop6:
if (niggafuckoff = true)
{
send {6 up}
return
}
send {6 down}
sleep 50
send {6 up}
return

loop7:
if (niggafuckoff = true)
{
send {7 up}
return
}
send {7 down}
sleep 50
send {7 up}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loadchecker:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\MaestroEvengarde.png
if (ErrorLevel = 0)
{
settimer, loadchecker, off
loaded := true
}
if (ErrorLevel = 1)
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\AntiCampfire.png
if (ErrorLevel = 0)
{
scan := false
rejoined := true
settimer, loadchecker, off
loaded := true
}
}
return

loadchecker2:
ImageSearch, xxx, yyy, 800, 580, 1125, 630, *40 %A_ScriptDir%\Maestro\PressToBegin.png
if (ErrorLevel = 0)
{
settimer, loadchecker2, off
loaded := true
}
return

loadchecker3:
ImageSearch, xxx, yyy, 450, 0, 560, 20, *60 %A_ScriptDir%\Maestro\Dungeon.png
if (ErrorLevel = 0)
{
settimer, loadchecker3, off
loaded := true
}
return

loadchecker4:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\Weapon.png
if (ErrorLevel = 0)
{
settimer, loadchecker4, off
loaded := true
}
return

loadchecker5:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\HpBar.png
if (ErrorLevel = 0)
{
settimer, loadchecker5, off
loaded := true
}
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\AntiCampfire.png
if (ErrorLevel = 1)
{
scan := false
rejoined := true
settimer, loadchecker5, off
loaded := true
}
return

loadchecker6:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *130 %A_ScriptDir%\Maestro\MaestroToucher.png
if (ErrorLevel = 0)
{
settimer, loadchecker6, off
loaded := true
}
if (ErrorLevel = 1)
{
click WheelDown
sleep 500
}
return

loadchecker7:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\PressToContinue.png
if (ErrorLevel = 0)
{
settimer, loadchecker7, off
loaded := true
}
return

loadchecker8:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\Continue.png
if (ErrorLevel = 0)
{
settimer, loadchecker8, off
loaded := true
}
return

loadchecker9:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\Loadering.png
if (ErrorLevel = 0)
{
settimer, loadchecker9, off
loaded := true
}
return

loadchecker10:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\QuickJoin.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
settimer, loadchecker10, off
loaded := true
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

counter:
count++
if (count > 59)
{
count := 0
minute++
if (minute > 59)
{
hour++
minute := 0
}
}
tooltip, RunTime: %hour%h %minute%m %count%s, 300, 480, 4

if (TpBellCheck = true)
{
if (fuckyounigga = true)
{
ImageSearch, xxxxxx, yyyyyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\Maestro\TpBell.png
if (ErrorLevel = 0)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
reload
}
}
}

if (StainedCheck = true)
{
ImageSearch, xxxxxx, yyyyyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\Maestro\Stained.png
if (ErrorLevel = 0)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
reload
}
}

if (DepthsCheck = true)
{
ImageSearch, xxxxxx, yyyyyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\Maestro\Depths.png
if (ErrorLevel = 0)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
reload
}
}

if (disabled = false)
{
if (scan = true)
{
if (StainedCheck = false)
{
{
ImageSearch, xxxxx, yyyyy, 710, 900, 1210, 940, *50 %A_ScriptDir%\Maestro\StainedHpBar.png
if (ErrorLevel = 0)
{
return
}
if (ErrorLevel = 1)
{
ImageSearch, xxxxxx, yyyyyy, 710, 720, 900, 750, *60 %A_ScriptDir%\Maestro\DeathChecker.png
if (ErrorLevel = 0)
{
scan := false
return
}
if (ErrorLevel = 1)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
}
}
}
}
else if (StainedCheck = true)
{
ImageSearch, xxxxx, yyyyy, 710, 900, 1210, 940, *50 %A_ScriptDir%\Maestro\Hpbar.png
if (ErrorLevel = 0)
{
return
}
if (ErrorLevel = 1)
{
ImageSearch, xxxxxx, yyyyyy, 710, 720, 900, 750, *60 %A_ScriptDir%\Maestro\DeathChecker.png
if (ErrorLevel = 0)
{
scan := false
return
}
if (ErrorLevel = 1)
{
niggafuckoff := true
{
send {esc down}
sleep 10
send {esc up}
sleep 10
send {l down}
sleep 10
send {l up}
sleep 10
send {enter down}
sleep 10
send {enter up}
sleep 10
Run roblox://experiences/start?placeId=4111023553
sleep 10
}
niggafuckoff := false
sleep 10
send {w up}
send {a up}
send {s up}
send {d up}
send {1 up}
send {2 up}
send {3 up}
send {4 up}
send {5 up}
send {6 up}
send {7 up}
send {r up}
scan := false
rejoined := true
}
}
}
}
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

failsafe:
failcount++
tooltip, FailSafe: %failcount%/60, 300, 460, 20
return

failsafeEXTRA:
failcount++
tooltip, FailSafe: %failcount%/15, 300, 460, 20
return

failsafe15:
failcount++
tooltip, FailSafe: %failcount%/15, 300, 460, 20
return

failsafe20:
failcount++
tooltip, FailSafe: %failcount%/20, 300, 460, 20
return

failsafe40:
failcount++
tooltip, FailSafe: %failcount%/40, 300, 460, 20
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

imbored:
send {shift down}
sleep 10
send {shift up}
sleep 10
settimer, fuckoffretard, 500
sleep 4000
settimer, fuckoffretard, off
send {shift down}
sleep 10
send {shift up}
sleep 10
return

fuckoffretard:
mousemove, 900, 600
sleep 125
mousemove, 960, 450
sleep 125
mousemove, 1015, 600
sleep 125
mousemove, 900, 515
sleep 125
mousemove, 1015, 515
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$r::
settimer, loopr, 100
keywait r
settimer, loopr, off
return

$2::
settimer, loop2, 100
keywait 2
settimer, loop2, off
return

$3::
settimer, loop3, 100
keywait 3
settimer, loop3, off
return

$4::
settimer, loop4, 100
keywait 4
settimer, loop4, off
return

$5::
settimer, loop5, 100
keywait 5
settimer, loop5, off
return

$6::
settimer, loop6, 100
keywait 6
settimer, loop6, off
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;