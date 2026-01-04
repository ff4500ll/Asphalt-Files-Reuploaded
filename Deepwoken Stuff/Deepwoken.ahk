#ifWinActive, Roblox
#MaxHotkeysPerInterval 1000000000000
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off

;cooldown = 5000
;universaldelay = 2
;senddelay = 25
;text = grip macro ACTIVATE (i macroed the whole fight)

;~$b::
;sleep %universaldelay%
;send {/ down}
;sleep %universaldelay%
;send {/ up}
;sleep %universaldelay%
;send %text%
;sleep %senddelay%
;send {enter down}
;sleep %universaldelay%
;send {enter up}
;hotkey, b, off
;sleep %cooldown%
;hotkey, b, on
;return

$xbutton1::0
$xbutton2::9

$j::
while getkeystate("j","P")
{
send {q down}
sleep 1
send {space down}
sleep 5
send {q up}
send {space up}
sleep 2000
}
return

$mbutton::
send {w up}
while getkeystate("mbutton","P")
{
send {rbutton down}
sleep 1
send {rbutton up}
sleep 1
send {ctrl down}
sleep 1
send {lbutton down}
sleep 1
send {lbutton up}
send {ctrl up}
sleep 1
}
return

$l:: reload
$z:: 7
$x:: 8

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
settimer, click, 50
gosub, click
return
$lbutton up::
settimer, click, off
return
click:
getkeystate, NIGGAstate, lbutton, p
if NIGGAstate = U
settimer, click, off
send {lbutton down}
sleep 5
send {lbutton up}
return

;*$e::
;settimer, e, 100
;gosub, e
;return
;$e up::
;settimer, e, off
;return
;e:
;GetKeyState, estate, e, p
;if estate = U
;settimer, e, off
;send {e down}
;sleep 50
;send {e up}
;return

*$q::
settimer, q, 100
gosub, q
return
$q up::
settimer, q, off
return
q:
GetKeyState, qstate, q, p
if qstate = U
settimer, q, off
send {q down}
sleep 50
send {q up}
return

,:: suspend
return