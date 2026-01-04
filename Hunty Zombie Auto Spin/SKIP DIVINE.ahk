CoordMode, ToolTip, Screen 
CoordMode, Pixel, Screen 
CoordMode, Mouse, Screen 

TooltipXcoordinate := A_ScreenWidth/9
TooltipYcoordinate := A_ScreenHeight/2

NormalSpinXCoord := 1170*(A_ScreenWidth/2560)
NormalSpinYCoord := 1300*(A_ScreenHeight/1440)

SureXCoord := 1170*(A_ScreenWidth/2560)
SureYCoord := 870*(A_ScreenHeight/1440)

LeftRedBox := 1280*(A_ScreenWidth/2560)
RightRedBox := 1565*(A_ScreenWidth/2560)
TopRedBox := 810*(A_ScreenHeight/1440)
BottomRedBox := 920*(A_ScreenHeight/1440)

LeftTextBox := 930*(A_ScreenWidth/2560)
RightTextBox := 1630*(A_ScreenWidth/2560)
TopTextBox := 55*(A_ScreenHeight/1440)
BottomTextBox := 170*(A_ScreenHeight/1440)

SkipLegendary := True
SkipMythic := False

tooltip, Hotkeys`n`n1: Start Macro`n2: Stop`n`nSkip Legendary`nSkip Mythic`nSkip Divine`n`n5: Exit`n, TooltipXcoordinate, TooltipYcoordinate

$2:: reload
$5:: exitapp

$1::
istarthere:
click %NormalSpinXCoord% %NormalSpinYCoord%
PixelSearch, , , LeftRedBox, TopRedBox, RightRedBox, BottomRedBox, 0xFE0B0F, 5, Fast RGB
if ErrorLevel
    goto istarthere
else
    goto decide

decide:
sleep 500

PixelSearch, , , LeftTextBox, TopTextBox, RightTextBox, BottomTextBox, 0x4B4822, 5, Fast RGB
if (ErrorLevel == 0)
goto reroll

PixelSearch, , , LeftTextBox, TopTextBox, RightTextBox, BottomTextBox, 0x4B2122, 5, Fast RGB
if (ErrorLevel == 0)
goto reroll

PixelSearch, , , LeftTextBox, TopTextBox, RightTextBox, BottomTextBox, 0x4B2C20, 5, Fast RGB
if (ErrorLevel == 0)
goto reroll

msgbox, found that shit
return

reroll:
click %SureXCoord% %SureYCoord%
goto istarthere