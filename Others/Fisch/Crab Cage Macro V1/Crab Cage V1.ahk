#SingleInstance Force

;======================;

wifi := "Ethernet 2"
disconnecttime := 3000

collectdelay := 650

; netsh interface show interface

;======================;

$r:: reload

$y::
setkeydelay, 0
setbatchlines, 0
while getkeystate("y","P")
{
send {click}
}
return

$p::
setkeydelay, 1
tooltip, pausing wifi
send netsh interface set interface "%wifi%" disable
sleep 250
send {enter}
sleep 100
send netsh interface set interface "%wifi%" enable
sleep %disconnecttime%
send {enter}
tooltip
sleep 100
WinActivate, Roblox
setkeydelay, 0
setbatchlines, 0
tooltip, clicking (r = reload & m = exit)
loop,
{
send {click}
}
return

$e::
tooltip, collecting (r = reload & m = exit)
loop,
{
send {e down}
sleep %collectdelay%
send {e up}
sleep 50
}
return

$m:: exitapp