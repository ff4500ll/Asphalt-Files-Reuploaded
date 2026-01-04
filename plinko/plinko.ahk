#SingleInstance Force
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

middlescreen := A_ScreenWidth/2

$m:: exitapp
$p::
loop,
{
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\rebirth.png
if (ErrorLevel == 0)
	{
	click, %xxx%, %yyy%
	sleep 100
	mousemove, %middlescreen%, 1280
	}
sleep 1000
mousemove, %middlescreen%, 1280
}
return