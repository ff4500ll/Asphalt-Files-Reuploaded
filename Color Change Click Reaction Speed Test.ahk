setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

$p::
MouseGetPos, MouseX, MouseY
PixelGetColor, saved, %MouseX%, %MouseY%
back:
PixelGetColor, color, %MouseX%, %MouseY%
if (color == saved)
goto back
send {click}
tooltip, %saved% %color%
return

$m:: exitapp