#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1

$m::exitapp
$o::reload

$p::
tooltip, running
loop,
{
send {s down}
send {shift down}
sleep 300
send {shift up}
send {space down}
sleep 200
send {space up}
send {s up}
send {w down}
sleep 300
send {w up}
send {mbutton}
sleep 50
send {ctrl}
sleep 250
}
return