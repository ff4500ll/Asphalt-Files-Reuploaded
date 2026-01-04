#ifWinActive, Roblox ; focus roblox
setkeydelay, 0
setmousedelay, 0
on = false

$z::9 ; main spell
return
$x::0 ; heavy hitter
return
$r::- ; spammable
return
$c::= ; sub spell
return
$t::8 ; spammable
return

~$/:: ; chat pause
if on = false
{
on = true
tooltip, macro paused ah just saying
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
tooltip
on = false
return

$q:: ; auto dash
settimer, dash, 100
gosub, dash
return
$q up::
settimer, dash, off
send {q up}
return
dash:
send {q down}
sleep 50
send {q up}
return

$mbutton::
settimer, click, 50
gosub, click
return
$mbutton up::
settimer, click, off
return
click:
getkeystate, NIGGAstate, mbutton, p
if NIGGAstate = U
settimer, click, off
send {lbutton down}
sleep 5
send {lbutton up}
return

$xbutton2:: ; snap ignis macro
send {rbutton}
sleep 50
send 3
sleep 100
send {lbutton}
return

$xbutton1:: ; spell run
send {g up}
sleep 10
send {w up}
sleep 10
send {w down}
send {w up}
send {lbutton}
sleep 10
send {w down}
return

,:: suspend ; default suspend key