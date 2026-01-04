#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

$m:: reload
return

$p::
loop,
{
send {lbutton down}
sleep 4000
send {lbutton up}
sleep 2000
send {space down}
sleep 100
send {space up}
sleep 3400
}
return