loop,
{
MouseGetPos, MouseX, MouseY
PixelGetColor, color, %MouseX%, %MouseY%
ToolTip, %color% %MouseX% %MouseY%
}

$m:: exitapp