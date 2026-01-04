#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0

$z::9
return
$x::0
return
$r::-
return
$c::=
return
$t::8
return

$p::
send {rbutton}
sleep 100
send /
sleep 20
send snail
sleep 100
send {enter}
return

$o::
send {rbutton}
sleep 100
send /
sleep 20
send skycastle
sleep 100
send {enter}
return

~$/:: ; chat pause
if on = false
{
on = true
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
on = false
return

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2:: ; block climb
send {f down}
send {space}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

,:: suspend ; default suspend key