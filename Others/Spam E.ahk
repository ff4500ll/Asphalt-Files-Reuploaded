#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1

$e::
while getkeystate("e","P")
{
send e
sleep 1
}
return