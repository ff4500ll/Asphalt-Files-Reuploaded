#ifWinActive, Roblox
CoordMode Pixel
setkeydelay, 0
setmousedelay, 0

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Sensitivity
tolerance := 5

;Scan Range
left := 0
right := 1919
top := 0
bottom :=  1079

;Box Range
lleft := 880
rright := 920
ttop := 330
bbottom := 370
ShowBox := false

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

tooltip, Reloaded, 300, 500, 1
$m::
suspend, off
send {w up}
send {s up}
reload
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::

;Box Tooltip
if (ShowBox = true)
{
tooltip, tleft, %lleft%, %ttop%, 2
tooltip, tright, %rright%, %ttop%, 3
tooltip, bleft, %lleft%, %bbottom%, 4
tooltip, bright, %rright%, %bbottom%, 5
}
tooltip, %lleft%-%rright%, 300, 580, 9
tooltip, %ttop%-%bbottom%, 300, 600, 10
tooltip, X: Waiting, 300, 520, 6
tooltip, Y: Waiting, 300, 540, 7

;Math
xabsolute := (lleft + rright) / 2
xabsolute := round(xabsolute)
yabsolute := (ttop + bbottom) / 2
yabsolute := round(yabsolute)

;Camera Orientation
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -2000)
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 500)
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -2000)
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 500)

;Main Loop
loop,
{

ImageSearch, xxx, yyy, %left%, %top%, %right%, %bottom%, *%tolerance% %A_ScriptDir%\Sharko\Forehead.png
tooltip, x:%xxx% y:%yyy%, 300, 560, 8
 if (ErrorLevel = 0)
  {
  yyyy := yyy - 20
  tooltip, Found, %xxx%, %yyyy%, 1
  gosub, autolockX
  gosub, autolockY
  }
  else if (ErrorLevel = 1)
  {
  send {w up}
  send {s up}
  tooltip, Scanning, 300, 500, 1
  } 

}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

autolockX:
;X-axis Positioning
if (xxx > lleft) and (xxx < rright)
 {
 tooltip, X: Perfect, 300, 520, 6
 return
 }
else if (xxx < lleft)
 {
 tooltip, X: Turn Left, 300, 520, 6
 XMoveDist := (xabsolute - xxx) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", -XMoveDist, "UInt", 0)
 return
 }
else if (xxx > rright)
 {
 tooltip, X: Turn Right, 300, 520, 6
 XMoveDist := (xabsolute - xxx) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", -XMoveDist, "UInt", 0)
 return
 }
else
 {
 tooltip, X: ERROR, 300, 520, 6
 }

autolockY:
;Y-axis Positioning
if (yyy > ttop) and (yyy < bbottom)
 {
 tooltip, Y: Perfect, 300, 540, 7
 send {w up}
 send {s up}
 return
 }
else if (yyy < ttop)
 {
 tooltip, Y: Walk Backwards, 300, 540, 7
 send {w up}
 send {s down}
 return
 }
else if (yyy > bbottom)
 {
 tooltip, Y: Walk Forward, 300, 540, 7
 send {s up}
 send {w down}
 return
 }
else
 {
 tooltip, X: ERROR, 300, 540, 7
 }

return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;




















