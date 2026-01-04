#ifWinActive, Roblox
setkeydelay, 0
setmousedelay, 0

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$m::
suspend, off
reload
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

WaterLineX := 0
WaterLineY := 0
LeftX := 0
LeftY := 0
RightX := 0
RightY := 0

MouseGetPos, LeftX, LeftY
MouseGetPos, RightX, RightY

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::
tooltip, Click On >LEFT< Of Character, 300, 500
keywait, lbutton, D
MouseGetPos, LeftX, LeftY
keywait lbutton
sleep 500

tooltip, Click On >RIGHT< Of Character, 300, 500
keywait, lbutton, D
MouseGetPos, RightX, RightY
keywait lbutton
sleep 500

tooltip, Click On >CENTER< Of Character, 300, 500
keywait, lbutton, D
MouseGetPos, CenterX, CenterY
keywait lbutton
sleep 500

send {shift down}
sleep 100
send {shift up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 2000)
send {shift down}
sleep 100
send {shift up}
sleep 100

tooltip, Click On Water, 300, 500, 1
keywait, lbutton, D
MouseGetPos, WaterLineX, WaterLineY
keywait lbutton
sleep 500

tooltip, X-WaterLine: %WaterLineX%, 300, 600, 1
tooltip, Y-WaterLine: %WaterLineY%, 300, 580, 2
tooltip, X-Left: %LeftX%, 300, 560, 3
tooltip, Y-Left: %LeftY%, 300, 540, 4
tooltip, X-Right: %RightX%, 300, 520, 5
tooltip, Y-Right: %RightY%, 300, 500, 6

;Math
ScanLeft := (WaterLineX - 10)
ScanRight := (WaterLineX + 10)
ScanTop := (WaterLineY - 10)
ScanBottom := (WaterLineY + 10)

LeftLeft := (LeftX - 10)
LeftRight := (LeftX + 10)
LeftTop := (LeftY - 10)
LeftBottom := (LeftY + 10)

RightLeft := (RightX - 10)
RightRight := (RightX + 10)
RightTop := (RightY - 10)
RightBottom := (RightY + 10)

CenterLeft := (CenterX - 10)
CenterRight := (CenterX + 10)
CenterTop := (CenterY - 10)
CenterBottom := (CenterY + 10)

send {1 down}
sleep 100
send {1 up}
sleep 100

loop,
{
send {shift down}
sleep 100
send {shift up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 2000)
send {shift down}
sleep 100
send {shift up}
sleep 100

send {lbutton down}
sleep 100
send {lbutton up}
sleep 100

Tolerance := 30

loopscan := true
colorcheck := true
while (loopscan = true)
{
returncolorcheck:
ImageSearch, xxx, yyy, ScanLeft, ScanTop, ScanRight, ScanBottom, *%Tolerance% %A_ScriptDir%\Fishing\Water.png
If (ErrorLevel = 1)
 {
  if (colorcheck = true)
   {
   Tolerance := (Tolerance + 1)
   tooltip, Tolerance: %Tolerance%, 300, 440, 8
   }
  if (colorcheck = false)
   {
   loopscan := false
   tooltip, Fish Caught, 300, 460, 7
   goto, exitloopscan
   }
 }
Else If (ErrorLevel = 0)
 {
 if (colorcheck = true)
  {
  colorcheck := false
  Tolerance := (Tolerance + 10)
  tooltip, Tolerance: %Tolerance%, 300, 440, 8
  goto, returncolorcheck
  }
 if (colorcheck = false)
  {
   tooltip, Waiting For Fish, 300, 460, 7
  }
 }
}

exitloopscan:

Tolerance := (Tolerance + 10)
tooltip, Tolerance: %Tolerance%, 300, 440, 8

catchingfish := true
settimer, loopclick, 100
while (catchingfish = true)
{

catchingfish:
ImageSearch, xxx, yyy, CenterLeft, CenterTop, CenterRight, CenterBottom, *%Tolerance% %A_ScriptDir%\Fishing\Water.png
If (ErrorLevel = 0)
 {
 catchingfish := false
 settimer, loopclick, off
 goto, skipitall
 }

ImageSearch, xxx, yyy, LeftLeft, LeftTop, LeftRight, LeftBottom, *%Tolerance% %A_ScriptDir%\Fishing\Water.png
If (ErrorLevel = 0)
 {
 ImageSearch, xxx, yyy, RightLeft, RightTop, RightRight, RightBottom, *%Tolerance% %A_ScriptDir%\Fishing\Water.png
 If (ErrorLevel = 0)
  {
  direction := back
  }
 Else If (ErrorLevel = 1)
  {
  direction := right
  }
 }
Else If (ErrorLevel = 1)
{
direction := left
}

if (direction = back)
{
tooltip, Back, 300, 400, 9
}
else if (direction = left)
{
tooltip, Left, 300, 400, 9
}
else if (direction = right)
{
tooltip, Right, 300, 400, 9
}

skipitall:
}

send {a up}
send {s up}
send {d up}
sleep 5000
}

return

loopclick:
send {lbutton down}
sleep 50
send {lbutton up}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;