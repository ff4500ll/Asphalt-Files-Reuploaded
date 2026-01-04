;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;IMPORTANT HEALTH SETTING (true/false)
StainedHpBar := true

;Change These To Your Graceful Flame Signs
Key1Graceful := "z"
Key2Graceful := "c"
Key3Graceful := "z" 

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;Autoloot Settings (true/false)

PickPurple := false ;<<<<<<<<<<<<< BIG SETTING

;If PickPurple is on, all of these will be picked up
;;================================================;;
;Miscellaneous Items
PickDeepGems := false
PickEnchantStones := true

;Legendary Weapons
PickCryptBlade := true
PickCurvedBlade := true
PickWyrmTooth := true
PickImperialStaff := true

;Maestro Weapons
PickPurpleCloud := false
PickPaleBriar := false
PickCerulianThread := false
;;================================================;;

PickGreen := true ;<<<<<<<<<<<<< BIG SETTING

;If PickGreen is on, all of these will be picked up
;;================================================;;
;Relic Items
PickSmithsAlloy := true
PickSinnersAsh := true <<<<<<<<< I WOULDNT THIS THESE IMAGES (leave green = true)
;;================================================;;

;More Miscellaneous Items
PickBackPacks := false
PickEnchantedItems := false

;Monastery Items
PickMonasteryRobes := false <<<<<<<<< I WOULDNT TRUST THESE IMAGES
PickMonasteryBeads := false <<<<<<<<< I WOULDNT TRUST THESE IMAGES
PickMonasteryCowl := false <<<<<<<<< I WOULDNT TRUST THESE IMAGES

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;Resolution Settings
;DEFAULT SETTINGS ARE SET TO 1920x1080p with 100% scale

;TOP LEFT of <(chest gui)> coords goes here
XTopLeftOfChest := 790
YTopLeftOfChest := 280

;BOTTOM RIGHT of <(chest gui)> coords goes here
XBottomRightOfChest := 1125
YBottomRightOfChest := 800

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;
goto, startscript
;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;Shutdown Hotkeys
$m::
suspend, off
reload
return
$o::
suspend, off
exitapp
return

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;Main Trigger Key
$p::

;=====;=====;=====;=====;

;Start Of Menu Macro

;Turns Off Temporary Tooltip
tooltip, , 15, 725, 18

rejoining:
if (Rejoin = true)
{
Rejoin := false

tooltip, Waiting For Deepwoken To Load, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 40
settimer, failsafe, 1000
WaitingForDeepwoken:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\PressToContinue.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, WaitingForDeepwoken
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming Deepwoken Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 30
settimer, failsafe, 1000
WaitingForDeepwoken2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\PressToContinue.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, WaitingForDeepwoken2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



;Fix Tooltip Position
tooltip, Press "O" To Exit, 15, 745, 19     ; Permanent Tooltip
tooltip, Press "M" To Reload, 15, 765, 20   ; Permanent Tooltip



tooltip, Waiting For "Continue", 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForContinue:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\Continue.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, WaitingForContinue
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming "Continue" Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForContinue2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\Continue.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, WaitingForContinue2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Waiting For "Maestro Toucher" Slot, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForMaestroToucher:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *130 %A_ScriptDir%\Maestro\MaestroToucher.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, XMiddleScreen, YMiddleScreen
loop, 3
{
send {wheeldown}
sleep 500
}
sleep 200
goto, WaitingForMaestroToucher
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming "Maestro Toucher" Slot Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForMaestroToucher2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *130 %A_ScriptDir%\Maestro\MaestroToucher.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, WaitingForMaestroToucher2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Waiting For "Quick Join", 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForQuickJoin:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\QuickJoin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, WaitingForQuickJoin
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming "Quick Join" Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
WaitingForQuickJoin2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\QuickJoin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, %xxx%, %yyy%
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, WaitingForQuickJoin2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17

} ;Rejoined Closing Bracket



;dont touch this
ReZeroStartingLifeinAnotherWorld:



;Refresh Tooltip Locations
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Enchant Stones: %EnchantStonesCounter%, 15, 385, 2
tooltip, Crypt Blades: %CryptBladeCounter%, 15, 405, 3
tooltip, Curved Blades: %CurvedBladeCounter%, 15, 425, 4
tooltip, Wyrm Tooths: %WyrmToothCounter%, 15, 445, 5
tooltip, Imperial Staffs: %ImperialStaffCounter%, 15, 465, 6
tooltip, Greem Items: %GreenCounter%, 15, 485, 7
tooltip, Smiths Alloys: %SmithsAlloyCounter%, 15, 505, 8
tooltip, Sinners Ashes: %SinnersAshCounter%, 15, 525, 9
tooltip, Enchanted Items: %EnchantedItemsCounter%, 15, 545, 10
tooltip, Fails: %FailSafeActivationCounter%, 15, 585, 12
tooltip, Success: %SuccessCounter%, 15, 605, 13
tooltip, W/L Percent: %PercentageMATHSTUFF%`%, 15, 625, 14



;Dem Maths
;Formula = (100/total) * win
PercentageMATHSTUFF := ((100/(FailSafeActivationCounter + SuccessCounter)) * SuccessCounter)
PercentageMATHSTUFF := Round(PercentageMATHSTUFF, 2)
tooltip, W/L Percent: %PercentageMATHSTUFF%`%, 15, 625, 14



;VERY BASIC EMERGENCY SHUTDOWN
if (FailSafeActivationCounter > 100)
{
winclose, roblox
reload
}



tooltip, Waiting For "Press To Begin" To Load, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 40
settimer, failsafe, 1000
PressToBegin:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\PressToBegin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, PressToBegin
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming "Press To Begin" Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
PressToBegin2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\PressToBegin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, PressToBegin2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Waiting For Character To Load, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
CharacterLoad:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\%PartBar%.png
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, CharacterLoad
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Shift Lock (Anti-Clip), 15, 665, 15
send {shift down}
sleep 100
send {shift up}
sleep 100



tooltip, Waiting For Maestro Text (Spamming E), 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
MaestroText:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\DeathChecker.png
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
send {e down}
sleep 100
send {e up}
sleep 1000
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Maestro\AntiCampfire.png
if (ErrorLevel = 0)
{
WinClose, Roblox
Rejoin := true
Run roblox://experiences/start?placeId=4111023553
settimer, failsafe, off
goto, rejoining
}
goto, MaestroText
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Entering Maestro Dungeon (Spamming 1), 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
MaestroText2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\DeathChecker.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
send {1 down}
sleep 100
send {1 up}
sleep 1000
goto, MaestroText2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Waiting For "Press To Begin" To Load, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 40
settimer, failsafe, 1000
PressToBeginDUPLICATE:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\PressToBegin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 100
}
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, PressToBeginDUPLICATE
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Confirming "Press To Begin" Has Loaded, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
PressToBeginDUPLICATE2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\PressToBegin.png
if (ErrorLevel = 0)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
mousemove, 1300, 550
send {lbutton down}
sleep 100
send {lbutton up}
sleep 200
goto, PressToBeginDUPLICATE2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Waiting For Character To Load, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 15
settimer, failsafe, 1000
CharacterLoad2:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\%PartBar%.png
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, CharacterLoad2
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17

;=====;=====;=====;=====;

;Start Of Dungeon Macro

tooltip, Turning Around, 15, 665, 15
send {shift down}
sleep 200
send {shift up}
sleep 200
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)



tooltip, Walking Off Forcefield, 15, 665, 15
send {w down}
sleep 400
send {1 down}
sleep 200
send {1 up}
sleep 400
send {w up}



tooltip, Checking Health, 15, 665, 15
failsafeCOUNT := 0
failsafeMAX := 30
settimer, failsafe, 1000
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\%FullBar%.png
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
send {7 down}
sleep 100
send {7 up}
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send {%Key1Graceful% down}
sleep 100
send {%Key1Graceful% up}
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send {%Key2Graceful% down}
sleep 100
send {%Key2Graceful% up}
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send {%Key3Graceful% down}
sleep 100
send {%Key3Graceful% up}
sleep 3000
send {e down}
sleep 100
send {e up}
sleep 100
CheckingHealth:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\%FullBar%.png
if (ErrorLevel = 1)
{
   if (Rejoin = true)
   {
   goto, rejoining
   }
sleep 200
goto, CheckingHealth
}
send {e down}
sleep 100
send {e up}
sleep 1000
}
settimer, failsafe, off
tooltip, FailSafe: PASSED, 15, 705, 17



tooltip, Walking To Maestro, 15, 665, 15
send {w down}
sleep 2300
send {w up}
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Hold Crit, 15, 665, 15
send {r down}
sleep 500
send {e down}
sleep 250
send {e up}
sleep 250
send {1 down}
sleep 250
send {1 up}
sleep 1750
send {r up}
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Toggle AutoLog, 15, 665, 15
Fighting := true
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Relentless, 15, 665, 15
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
send {3 down}
sleep 100
send {3 up}
send {s down}
sleep 750
send {s up}
sleep 1200
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 1550
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Fire Eruption, 15, 665, 15
send {2 down}
sleep 100
send {2 up}
sleep 1500
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Taunt, 15, 665, 15
send {6 down}
sleep 100
send {6 up}
sleep 1000
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Hold Crit, 15, 665, 15
send {r down}
sleep 3000
send {r up}
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Fire Forge, 15, 665, 15
send {5 down}
sleep 100
send {5 up}
sleep 500
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Sinister Halo, 15, 665, 15
send {4 down}
sleep 100
send {4 up}
sleep 1500
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Relentless, 15, 665, 15
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
send {3 down}
sleep 100
send {3 up}
send {s down}
sleep 750
send {s up}
sleep 1200
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
sleep 1550
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Fire Eruption, 15, 665, 15
send {2 down}
sleep 100
send {2 up}
sleep 2500
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Open Inventory (FailSafe), 15, 665, 15
send {tab down}
sleep 200
send {tab up}
sleep 1000
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Toggle AutoLog, 15, 665, 15
Fighting := false
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Open Chest, 15, 665, 15
DllCall("mouse_event", "UInt", 0x01, "UInt", 1200, "UInt", 0)
settimer, openchest, 100
send {w down}
sleep 1000
send {w up}
settimer, openchest, off
   if (Rejoin = true)
   {
   goto, rejoining
   }



tooltip, Toggle Shiftlock, 15, 665, 15
send {shift down}
sleep 100
send {shift up}



tooltip, Looting Chest, 15, 665, 15
mousemove, 1300, 550
sleep 250
gosub, timetoloot
sleep 250



tooltip, Leaving Dungeon, 15, 665, 15
send {shift down}
sleep 200
send {shift up}
sleep 200
send {w down}
sleep 50
send {w up}
sleep 50
send {w down}
sleep 1000
send {ctrl down}
sleep 50
send {space down}
sleep 50
send {ctrl up}
send {space up}
sleep 1750
send {d down}
sleep 100
send {d up}
sleep 500
send {ctrl down}
sleep 50
send {space down}
sleep 50
send {ctrl up}
send {space up}
sleep 2500
send {w up}



goto, ReZeroStartingLifeinAnotherWorld



return

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

timetoloot:
if (PickPurple = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Purple.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickDeepGems = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Gem.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickEnchantStones = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\EnchantStone.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
EnchantStonesCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Enchant Stones: %EnchantStonesCounter%, 15, 385, 2
goto, timetoloot
}
}

if (PickCryptBlade = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Crypt.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
CryptBladeCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Crypt Blades: %CryptBladeCounter%, 15, 405, 3
goto, timetoloot
}
}

if (PickCurvedBlade = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Curved.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
CurvedBladeCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Curved Blades: %CurvedBladeCounter%, 15, 425, 4
goto, timetoloot
}
}

if (PickWyrmTooth = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Wyrmtooth.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
WyrmToothCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Wyrm Tooths: %WyrmToothCounter%, 15, 445, 5
goto, timetoloot
}
}

if (PickImperialStaff = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\ImperialStaff.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
ImperialStaffCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Imperial Staffs: %ImperialStaffCounter%, 15, 465, 6
goto, timetoloot
}
}

if (PickPurpleCloud = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\PurpleCloud.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickPaleBriar = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\PaleBriar.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickCerulianThread = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\CeruleanThread.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickGreen = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Green.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
GreenCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Greem Items: %GreenCounter%, 15, 485, 7
goto, timetoloot
}
}

if (PickSmithsAlloy = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Smith.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
SmithsAlloyCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Smiths Alloys: %SmithsAlloyCounter%, 15, 505, 8
goto, timetoloot
}
}

if (PickSinnersAsh = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\SinnersAsh.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
SinnersAshCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Sinners Ashes: %SinnersAshCounter%, 15, 525, 9
goto, timetoloot
}
}

if (PickBackPacks = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Backpack.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickEnchantedItems = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Enchants.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
EnchantedItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
tooltip, Enchanted Items: %EnchantedItemsCounter%, 15, 545, 10
goto, timetoloot
}
}

if (PickMonasteryRobes = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\MonasteryRobes.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickMonasteryBeads = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\MonasteryBeads.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (PickMonasteryCowl = true)
{
ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\MonasteryCowl.png
if (ErrorLevel = 0)
{
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250
TotalItemsCounter++
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1
goto, timetoloot
}
}

if (SingleToggle = true)
{
SingleToggle := false
mousemove, XMiddleScreen, YMiddleScreen
loop, 10
{
send {wheeldown}
sleep 100
}
mousemove, 1300, 550
sleep 250
goto, timetoloot
}
SingleToggle := true

ImageSearch, xxx, yyy, XTopLeftOfChest, YTopLeftOfChest, XBottomRightOfChest, YBottomRightOfChest, *20 %A_ScriptDir%\Maestro\Exit.png
click, %xxx%, %yyy%
sleep 250
mousemove, 1300, 550
sleep 250

SuccessCounter++
tooltip, Success: %SuccessCounter%, 15, 605, 13

return

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

;FailSafe Subroutine
failsafe:
failsafeCOUNT++
tooltip, FailSafe: %failsafeCOUNT%/%failsafeMAX%, 15, 705, 17
if (failsafeCOUNT >= failsafeMAX)
{
WinClose, Roblox
Rejoin := true
Run roblox://experiences/start?placeId=4111023553
settimer, failsafe, off
settimer, openchest, off
FailSafeActivationCounter++
tooltip, Fails: %FailSafeActivationCounter%, 15, 585, 12
}
return

;AutoLog Subroutine
runtime:
if (Fighting = true)
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *40 %A_ScriptDir%\Maestro\%FullBar%.png
if (ErrorLevel = 1)
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *60 %A_ScriptDir%\Maestro\DeathChecker.png
if (ErrorLevel = 1)
{
WinClose, Roblox
Rejoin := true
Fighting := false
Run roblox://experiences/start?placeId=4111023553
settimer, failsafe, off
settimer, openchest, off
FailSafeActivationCounter++
tooltip, Fails: %FailSafeActivationCounter%, 15, 585, 12
}
}
}
Second++
if (Second >= 60)
{
Minute++
Second := 0
}
if (Minute >= 60)
{
Hour++
Minute := 0
}
tooltip, RunTime: %Hour%h %Minute%m %Second%s, 15, 685, 16
return

;Loop E Subroutine
openchest:
send {e down}
sleep 50
send {e up}
return

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;

startscript:

;Start Clock
settimer, runtime, 1000

;Anti Double-Check
if (PickPurple = true)
{
PickEnchantStones := false
PickCryptBlade := false
PickCurvedBlade := false
PickWyrmTooth := false
PickImperialStaff := false
PickPurpleCloud := false
PickPaleBriar := false
PickCerulianThread := false
}

;Anti Double-Check
if (PickGreen = true)
{
PickSmithsAlloy := false
PickSinnersAsh := false
}

;Default Variables (do not touch unless you know what you are doing)
Rejoin := true
Hour := 0
Minute := 0
Second := 0
Fighting := false
SingleToggle := true
TotalItemsCounter := 0
FailSafeActivationCounter := 0
SuccessCounter := 0
EnchantStonesCounter := 0
CryptBladeCounter := 0
CurvedBladeCounter := 0
WyrmToothCounter := 0
ImperialStaffCounter := 0
GreenCounter := 0
SmithsAlloyCounter := 0
SinnersAshCounter := 0
EnchantedItemsCounter := 0
PercentageMATHSTUFF := 0

;Math
XMiddleScreen := (A_ScreenWidth/2)
YMiddleScreen := (A_ScreenHeight/2)

;Stained Toggle
if (StainedHpBar = false)
{
PartBar := "Loadering"
FullBar := "HpBar"
}
else
{
PartBar := "Stained"
FullBar := "StainedHpBar"
}

;Closes All Roblox Instanced
loop, 10
{
WinClose, Roblox
sleep 100
}

;Opens Deepwoken
Run roblox://experiences/start?placeId=4111023553

;AHK Settings
setkeydelay, 0
setmousedelay, 0

;Starting Tooltips
tooltip, Total Items: %TotalItemsCounter%, 15, 365, 1           ; Total Items Tooltip
tooltip, Enchant Stones: %EnchantStonesCounter%, 15, 385, 2     ; Enchant Stones Tooltip
tooltip, Crypt Blades: %CryptBladeCounter%, 15, 405, 3          ; Crypt Blade Tooltip
tooltip, Curved Blades: %CurvedBladeCounter%, 15, 425, 4        ; Curved Blade Tooltip
tooltip, Wyrm Tooths: %WyrmToothCounter%, 15, 445, 5            ; Wyrm Tooth Tooltip
tooltip, Imperial Staffs: %ImperialStaffCounter%, 15, 465, 6    ; Imperial Staff Tooltip
tooltip, Greem Items: %GreenCounter%, 15, 485, 7                ; Green Tooltip
tooltip, Smiths Alloys: %SmithsAlloyCounter%, 15, 505, 8        ; Smiths Alloy Tooltip
tooltip, Sinners Ashes: %SinnersAshCounter%, 15, 525, 9         ; Sinners Ash Tooltip
tooltip, Enchanted Items: %EnchantedItemsCounter%, 15, 545, 10  ; Enchanted Items Tooltip

tooltip, Fails: %FailSafeActivationCounter%, 15, 585, 12        ; Fails
tooltip, Success: %SuccessCounter%, 15, 605, 13                 ; Success
tooltip, W/L Percent: %PercentageMATHSTUFF%`%, 15, 625, 14        ; Percent

tooltip, Waiting, 15, 665, 15                                   ; Current Action Tooltip
tooltip, RunTime: 0h 0m 0s, 15, 685, 16                         ; RunTime Tooltip
tooltip, Waiting, 15, 705, 17                                   ; FailSafe Tooltip
tooltip, Press "P" To Start, 15, 725, 18                        ; Temporary Tooltip
tooltip, Press "O" To Exit, 15, 745, 19                         ; Permanent Tooltip
tooltip, Press "M" To Reload, 15, 765, 20                       ; Permanent Tooltip
return

;==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==;