#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

;===================================;===================================;

;;CHANGE THIS TO YOUR ROBLOX SENSITIVITY;;

SENSITIVITY := 0.3

;===================================;===================================;

fuckyoursensitivty := 0.3/SENSITIVITY
pause = off
trigger := 0
xcoords := A_ScreenWidth/20
ycoords := A_ScreenHeight/1.2
x1 := 1100/2560*A_ScreenWidth
x2 := 1450/2560*A_ScreenWidth
y1 := 1135/1440*A_ScreenHeight
y2 := 1145/1440*A_ScreenHeight
v21 := 1160/2560*A_ScreenWidth
v22 := 1165/2560*A_ScreenWidth
v31 := 1160/2560*A_ScreenWidth
v32 := 1165/2560*A_ScreenWidth
v41 := 1385/2560*A_ScreenWidth
v43 := -100/2560*A_ScreenWidth*fuckyoursensitivty
v51 := 1215/2560*A_ScreenWidth
v52 := 1220/2560*A_ScreenWidth
v53 := -170/2560*A_ScreenWidth*fuckyoursensitivty
v61 := 1385/2560*A_ScreenWidth
v71 := 1160/2560*A_ScreenWidth
v72 := 1165/2560*A_ScreenWidth
v73 := 150/2560*A_ScreenWidth*fuckyoursensitivty
JumpDelay1 := 500
JumpDelay2 := 520
JumpDelay3 := 540
JumpDelay4 := 600
JumpDelay := JumpDelay1
PurpleSpikeCoordinates := 1385/2560*A_ScreenWidth

JumpDelay := JumpDelay1
if (JumpDelay == JumpDelay1)
Server := "SG"
else if (JumpDelay == JumpDelay2)
Server := "JP"
else if (JumpDelay == JumpDelay3)
Server := "US"
else if (JumpDelay == JumpDelay4)
Server := "MOON"
else
Server := "UNKNOWN"

$up::
if (JumpDelay == JumpDelay1)
{
Server := "JP"
JumpDelay := JumpDelay2
}
else if (JumpDelay == JumpDelay2)
{
Server := "US"
JumpDelay := JumpDelay3
}
else if (JumpDelay == JumpDelay3)
{
Server := "MOON"
JumpDelay := JumpDelay4
}
else if (JumpDelay == JumpDelay4)
{
Server := "MOON"
JumpDelay := JumpDelay4
}
else
Server := "UNKNOWN"
return

$down::
if (JumpDelay == JumpDelay1)
{
Server := "SG"
JumpDelay := JumpDelay1
}
else if (JumpDelay == JumpDelay2)
{
Server := "SG"
JumpDelay := JumpDelay1
}
else if (JumpDelay == JumpDelay3)
{
Server := "JP"
JumpDelay := JumpDelay2
}
else if (JumpDelay == JumpDelay4)
{
Server := "US"
JumpDelay := JumpDelay3
}
else
Server := "UNKNOWN"
return

$xbutton1::
$xbutton2::
send {rbutton down}
return

$space::
send {shift}
sleep 30
send {space}
sleep 100
send {shift}
return

$/::
send {/ down}
keywait /
send {/ up}
if pause = off
{
pause = on
suspend, on
}
return

~$esc::
~$enter::
suspend, off
pause = off
return

$0:: exitapp
$9::
sleep 100
send {w up}
send {a up}
send {d up}
send {s up}
send {rbutton up}
if (trigger == 1)
{
send {shift}
}
send {esc}
sleep 50
send {esc}
reload
return

$1::
if (trigger == 0)
{
send {shift}
sleep 50
send {lbutton}
sleep 50
send {w down}
sleep 50
send {rbutton down}
trigger := 1
}
return

~$2::
if (trigger == 1)
	{
	trigger := 0
	ReloopHere2:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v31 and xxx < v32)
			{
			send {lbutton}
			goto endcycle2
			}
		}
	goto ReloopHere2
	endcycle2:
	send {w up}
	sleep 300
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {s down}
	send {a down}
	sleep 350
	send {lbutton}
	sleep 1000
	send {a up}
	send {s up}
	}
return

~$3::
if (trigger == 1)
	{
	trigger := 0
	ReloopHere3:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v21 and xxx < v22)
			{
			send {lbutton}
			goto endcycle3
			}
		}
	goto ReloopHere3
	endcycle3:
	send {w up}
	sleep 300
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {s down}
	sleep 350
	send {lbutton}
	sleep 1000
	send {s up}
	}
return

~$4::
if (trigger == 1)
	{
	trigger := 0
	DllCall("mouse_event", "UInt", 0x01, "UInt", v43, "UInt", 0)
	ReloopHere4:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v41)
			{
			send {lbutton}
			goto endcycle4
			}
		}
	goto ReloopHere4
	endcycle4:
	send {w up}
	sleep 350
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {a down}
	sleep 350
	send {lbutton}
	sleep 1000
	send {a up}
	}
return

~$5::
if (trigger == 1)
	{
	send {a down}
	sleep 1000
	trigger := 0
	ReloopHere5:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v51 and xxx < v52)
			{
			send {lbutton}
			goto endcycle5
			}
		}
	goto ReloopHere5
	endcycle5:
	DllCall("mouse_event", "UInt", 0x01, "UInt", v53, "UInt", 0)
	send {w up}
	send {a up}
	sleep 450
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {d down}
	sleep 400
	send {lbutton}
	sleep 1000
	send {d up}
	}
return

~$6::
if (trigger == 1)
	{
	trigger := 0
	ReloopHere8:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v61)
			{
			send {lbutton}
			goto endcycle8
			}
		}
	goto ReloopHere8
	endcycle8:
	send {w up}
	sleep 600
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {w down}
	sleep 650
	send {lbutton}
	sleep 1000
	send {w up}
	}
return

~$7::
if (trigger == 1)
	{
	send {d down}
	sleep 1000
	trigger := 0
	ReloopHere5a:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > v71 and xxx < v72)
			{
			send {lbutton}
			goto endcycle5a
			}
		}
	goto ReloopHere5a
	endcycle5a:
	DllCall("mouse_event", "UInt", 0x01, "UInt", v73, "UInt", 0)
	send {w up}
	send {d up}
	sleep 450
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 50
	send {w up}
	send {a down}
	sleep 400
	send {lbutton}
	sleep 1000
	send {a up}
	}
return

~$8::
if (trigger == 1)
	{
	trigger := 0
	ReloopHereb:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > PurpleSpikeCoordinates)
			{
			send {lbutton}
			goto endcycleb
			}
		}
	goto ReloopHereb
	endcycleb:
	send {w up}
	sleep %JumpDelay%
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 100
	send {w up}
	send {s down}
	send {lbutton}
	sleep 1000
	send {s up}
	}
return