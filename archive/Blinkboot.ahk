#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1

$m::exitapp
$o::reload

$p::
loop,
{
count++
tooltip, running %count%
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -500)
sleep 100
send q
send {s up}
send {shift up}
sleep 100
sleep 250
send {mbutton}
sleep 50
send {ctrl}
sleep 250
send {lbutton}
sleep 215
send {mbutton}
sleep 50
send {ctrl}
sleep 150
send {s down}
send {shift down}
sleep 100
;send z
}
return

; every cycle = 10965ms
; 1 loop = 1265ms
; 250 loop = 327215ms
; 2750 loop = 1 hour
; 2.4m = 26m per hour (624m per 24h)

$l::
tooltip, running
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -1000)
loop,
{

send ]
sleep 200

start:
send q

count2 := 0

returnpoint:
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -500)
count++
count2++

PixelGetColor, color, 2530, 35
tooltip, %color%`n%count%`n%count2%/180
if (color = 0x646363 or color = 0x4D4D4D or color = 0x302927)
{
	sleep 500
	send {wheeldown}
	sleep 2000
	send {c down}
	sleep 500
	send {c up}
	sleep 1000
	send ]
	if (color = 0x302927)
	{
		MouseMove, 0, -10000, 100, R
		sleep 1000
		MouseMove, 0, 100, 100, R
		sleep 1000
	}
	else
	{
		sleep 2000
	}
	send {c down}
	sleep 500
	send {c up}
	sleep 1000
	send {wheelup}
	sleep 1000
	DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -500)
	sleep 100
	DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -500)
	sleep 100
	DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -500)
	sleep 500
	goto start
}
sleep 550
send {mbutton}
sleep 50
send {ctrl}
sleep 100
send {lbutton}
if (count2 >= 180)
{
	count2 := 0
	DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
}
sleep 400
send {mbutton}
sleep 50
send {ctrl}
sleep 60

send {w down}
send {shift down}
sleep 50
send q
sleep 100
send {w up}
send {shift up}



goto returnpoint
}
return