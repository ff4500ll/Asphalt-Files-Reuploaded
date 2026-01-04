#SingleInstance Force
#ifWinActive, Roblox
setkeydelay, -1
setbatchlines, -1
setmousedelay, -1

WinActivate, Roblox
tooltip, m = close, 200, 400, 1
tooltip, hold p = start, 200, 420, 2
tooltip, hold y = autoclick, 200, 440, 3

$y::
while getkeystate("y","P")
{
send {click}
}
keywait y
return

$p::
Run, %comspec% /c ipconfig /release,, Hide
Run, %comspec% /c ipconfig /renew,, Hide
sleep 200
loop, 150
{
send {click}
sleep 1
}
return

$e::
tooltip, SPAMMING E (press m to exit), , , 4
loop,
{
send {e down}
sleep 700
send {e up}
sleep 50
}
return

$m:: exitapp