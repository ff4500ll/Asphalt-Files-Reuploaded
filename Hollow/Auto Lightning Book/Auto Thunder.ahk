#SingleInstance Force
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

CoordMode, Tooltip, Relative
CoordMode, Pixel, Relative
CoordMode, Mouse, Relative

$m:: exitapp
$p::
restart:

ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Static.png
if (ErrorLevel == 0)
	{
	click, %xxx%, %yyy%
	}
else
	{
	ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Volt.png
	if (ErrorLevel == 0)
		{
		click, %xxx%, %yyy%
		}
	else
		{
		ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Zap.png
		if (ErrorLevel == 0)
			{
			click, %xxx%, %yyy%
			}
		else
			{
			ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Thund.png
			if (ErrorLevel == 0)
				{
				click, %xxx%, %yyy%
				}
			else
				{
				ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Elect.png
				if (ErrorLevel == 0)
					{
					click, %xxx%, %yyy%
					}
				else
					{
					ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Shock.png
					if (ErrorLevel == 0)
						{
						click, %xxx%, %yyy%
						}
					else
						{
						ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Light.png
						if (ErrorLevel == 0)
							{
							click, %xxx%, %yyy%
							}
						else
							{
							ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Storm.png
							if (ErrorLevel == 0)
								{
								click, %xxx%, %yyy%
								}
							else
								{
								
								}
							}
						}
					}
				}
			}
		}
	}
sleep 50
goto restart