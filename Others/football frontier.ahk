#SingleInstance Force
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

height := A_ScreenHeight/2

$m:: exitapp
$p::
settimer, scan, 50
keywait p
settimer, scan, off
return

scan:
ImageSearch, , , 0, height, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Image.png
if (ErrorLevel == 0)
	{
	click, %xxx%, %yyy%
	}
return