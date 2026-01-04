;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

tooltip, Press "P" To Start, 300, 520, 2
tooltip, Press "I" To AutoLoot, 300, 540, 3
tooltip, Press "M" To Stop, 300, 560, 5

#ifWinActive, Roblox
setkeydelay, 0
setmousedelay, 0
locked = false
pause = off

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Loot Settings (true or false)

Purple := false
Enchants := true
DeepGems := false
Artifacts :=  true
EnchantStones := true
MaestroWeapons := false
LegendaryWeapons := true

PickupDelay := 150

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$m::
suspend, off
send {7 up}
send {s up}
reload
return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$o::
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -250)
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$i::
gosub, lootchest
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$y::
loaded := true
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::
tooltip, Loading, 300, 480, 4
settimer, counter, 1000
loop,
{
tooltip, Failure Points: 0/3, 300, 580, 6

tooltip, Press "I" To AutoLoot, 300, 540, 3
send {e down}
sleep 100
send {e up}

loaded := false
settimer, loadchecker, 500
while loaded = false
{
tooltip, Waiting For Maestro Text (Press Y To Skip), 300, 500, 1
tooltip, (Talk To Maestro), 300, 520, 2
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 500
send {1 down}
sleep 100
send {1 up}

loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Waiting For "Press To Begin" (Press Y To Skip), 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
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
tooltip, Waiting For World (Press Y To Skip), 300, 500, 1
tooltip, (Loading Character), 300, 520, 2
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

tooltip, Maestro Touching In Progress, 300, 500, 1
send {shift down}
sleep 100
send {shift up}
sleep 500
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 100
tooltip, (Walking To Maestro), 300, 520, 2
send {w down}
sleep 3300
send {w up}
sleep 100
tooltip, (Shadow Seekers), 300, 520, 2
send {7 down}
sleep 100
send {7 up}
sleep 1000
tooltip, (Talk To Maestro), 300, 520, 2
send {e down}
sleep 100
send {e up}
sleep 100
tooltip, (Begin The Fight), 300, 520, 2
send {1 down}
sleep 100
send {1 up}
sleep 100
tooltip, (Moonwalk Away), 300, 520, 2
send {s down}
sleep 4000
tooltip, (Crit), 300, 520, 2
tooltip, Failure Points: 1/3, 300, 580, 6
settimer, loopr, 100
sleep 700
send {s up}
sleep 300
settimer, loopr, off
sleep 500
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
tooltip, (Relentless Flames), 300, 520, 2
settimer, loop3, 100
sleep 800
tooltip, (Moonwalk), 300, 520, 2
send {s down}
sleep 200
settimer, loop3, off
sleep 900
tooltip, (Stop Moonwalk), 300, 520, 2
send {s up}
sleep 800
tooltip, (Jump), 300, 520, 2
send {space down}
sleep 100
send {space up}
sleep 700
send {s down}
tooltip, (Stalling With Flame Ballista), 300, 520, 2
settimer, loop2, 100
sleep 1000
settimer, loop2, off
sleep 3000
send {s down}
tooltip, Failure Points: 2/3, 300, 580, 6
tooltip, (Feint M1), 300, 520, 2
settimer, loopclick, 100
sleep 500
settimer, loopclick, off
tooltip, (Shadow Seekers), 300, 520, 2
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -250)
settimer, loop7, 100
sleep 1500
settimer, loop7, off
sleep 1000
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 250)
sleep 3000
tooltip, (Crit), 300, 520, 2
tooltip, Failure Points: 3/3, 300, 580, 6
settimer, loopr, 100
sleep 900
tooltip, (Stop Moonwalk), 300, 520, 2
send {s up}
sleep 600
settimer, loopr, off
tooltip, Failure Points: Passed, 300, 580, 6
tooltip, (Fire Eruption), 300, 520, 2
settimer, loop4, 100
sleep 2000
settimer, loop4, off

tooltip, Maestro Has Been Touched, 300, 500, 1
tooltip, (Time To Loot), 300, 520, 2
sleep 500

tooltip, Walking To Chest, 300, 500, 1
settimer, loope, 100
send {tab down}
sleep 50
send {tab up}
sleep 50
send {w down}
sleep 50
send {w up}
sleep 50
send {w down}
sleep 100
send {shift down}
sleep 100
send {shift up}
sleep 1500
settimer, loope, off
send {w up}

tooltip, Looting Chest, 300, 500, 1
sleep 1000
gosub, lootchest
sleep 500

tooltip, Leaving Dungeon, 300, 500, 1
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
sleep 250
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

loaded := false
settimer, loadchecker2, 500
while loaded = false
{
tooltip, Waiting For "Press To Begin" (Press Y To Skip), 300, 500, 1
tooltip, (Loading Screen), 300, 520, 2
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

sleep 500
send {lbutton down}
sleep 100
send {lbutton up}

loaded := false
settimer, loadchecker4, 500
while loaded = false
{
tooltip, Waiting For World (Press Y To Skip), 300, 500, 1
tooltip, (Loading Character), 300, 520, 2
sleep 500
}
loaded = true
tooltip, Loaded, 300, 500, 1

tooltip, Restarting Macro, 300, 500, 1
tooltip, (Looping), 300, 520, 2
sleep 1000
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

lootchest:
mousemove, 300, 420

;;;Purple

if (Purple = true)
{
tooltip, Searching For Purple, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Purple.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Artifacts

if (Artifacts = true)
{
tooltip, Searching For Artifacts, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Smith.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *40 %A_ScriptDir%\Maestro\SinnersAsh.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Legendary Weapons

if (LegendaryWeapons = true)
{
tooltip, Searching For Legendary Weapons, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Wyrmtooth.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\ImperialStaff.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Crypt.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Curved.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Enchants

if (Enchants = true)
{
tooltip, Searching For Enchants, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Enchants.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Enchant Stones

if (EnchantStones = true)
{
tooltip, Searching For Enchant Stones, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\EnchantStone.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Maestro Weapons

if (MaestroWeapons = true)
{
tooltip, Searching For Maestro Weapons, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\PaleBriar.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\PurpleCloud.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}

ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\CeruleanThread.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Deep Gems

if (DeepGems = true)
{
tooltip, Searching For Deep Gems, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Gem.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep %PickupDelay%
mousemove, 300, 420
sleep %PickupDelay%
gosub, lootchest
}
}

;;;Exit
tooltip, Searching Complete, 300, 540, 3
ImageSearch, xxx, yyy, 800, 280, 1130, 800, *10 %A_ScriptDir%\Maestro\Exit.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loopclick:
send {lbutton down}
sleep 50
send {lbutton up}
return

loopr:
send {r down}
sleep 50
send {r up}
return

loope:
send {e down}
sleep 50
send {e up}
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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

loadchecker:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\MaestroEvengarde.png
if (ErrorLevel = 0)
{
settimer, loadchecker, off
loaded := true
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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

counter:
count++
tooltip, %count%, 300, 480, 4
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