#ifWinActive, Roblox
CoordMode Pixel
setkeydelay, 0
setmousedelay, 0

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Sensitivity
tolerance := 10

;Scan Range
left := 250
right := 1670
top := 150
bottom :=  930

;Box Range
lleft := 910
rright := 1010
ttop := 640
bbottom := 740

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

tooltip, Reloaded, 300, 500, 1
$m::
suspend, off
reload
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

$p::

;Box Tooltip
tooltip, tleft, %lleft%, %ttop%, 2
tooltip, tright, %rright%, %ttop%, 3
tooltip, bleft, %lleft%, %bbottom%, 4
tooltip, bright, %rright%, %bbottom%, 5

;Math
xabsolute := (lleft + rright) / 2
xabsolute := round(xabsolute)
yabsolute := (ttop + bbottom) / 2
yabsolute := round(yabsolute)

;Main Loop
loop,
{

 ImageSearch, xxx, yyy, %left%, %top%, %right%, %bottom%, *%tolerance% %A_ScriptDir%\Ferryman\1Shade.png
 if (ErrorLevel = 0)
  {
  yyyy := yyy - 20
  tooltip, Found, %xxx%, %yyyy%, 1
  gosub, autolock
  }
  else if (ErrorLevel = 1)
  {
   ImageSearch, xxx, yyy, %left%, %top%, %right%, %bottom%, *%tolerance% %A_ScriptDir%\Ferryman\2Shade.png
   if (ErrorLevel = 0)
    {
    yyyy := yyy - 20
    tooltip, Found, %xxx%, %yyyy%, 1
    gosub, autolock
    }
    else if (ErrorLevel = 1)
    {
     ImageSearch, xxx, yyy, %left%, %top%, %right%, %bottom%, *%tolerance% %A_ScriptDir%\Ferryman\3Shade.png
     if (ErrorLevel = 0)
      {
      yyyy := yyy - 20
      tooltip, Found, %xxx%, %yyyy%, 1
      gosub, autolock
      }
      else if (ErrorLevel = 1)
      {
       ImageSearch, xxx, yyy, %left%, %top%, %right%, %bottom%, *%tolerance% %A_ScriptDir%\Ferryman\4Shade.png
       if (ErrorLevel = 0)
        {
        yyyy := yyy - 20
        tooltip, Found, %xxx%, %yyyy%, 1
        gosub, autolock
        }
        else if (ErrorLevel = 1)
        {
        tooltip, Scanning, 300, 500, 1
        } 
      } 
    } 
  }

}
return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

autolock:
;X-axis Positioning
if xxx < lleft
 {
 tooltip, X: Locking, 300, 520, 6
 XMoveDist := (xabsolute - xxx) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", -XMoveDist, "UInt", 0)
 }
else if xxx > rright
 {
 tooltip, X: Locking, 300, 520, 6
 XMoveDist := (xabsolute - xxx) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", -XMoveDist, "UInt", 0)
 }
else
 {
 tooltip, X: Locked On, 300, 520, 6
 }

;Y-axis Positioning
if yyy < ttop
 {
 tooltip, Y: Locking, 300, 540, 7
 YMoveDist := (yabsolute - yyy) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -YMoveDist)
 }
else if yyy > bbottom
 {
 tooltip, Y: Locking, 300, 540, 7
 YMoveDist := (yabsolute - yyy) / 2
 DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -YMoveDist)
 }
else
 {
 tooltip, Y: Locked On, 300, 540, 7
 }

return