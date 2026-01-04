#SingleInstance Force
#include Gdip_All.ahk

TesseractPath := "C:\Program Files\Tesseract-OCR\tesseract.exe"

F1::
MouseGetPos, x, y
mouseareax := 150
mouseareay := 250 

picx := x-mouseareax
picy := y-mouseareax
picx2 := x+mouseareax
picy2 := y+mouseareay

if (picx < 0) {
    picx2 := picx2 - picx
    picx := 0
} else if (picx2 > A_ScreenWidth ){
    picx := picx - (picx2 - A_ScreenWidth)
    picx2 := 0   
}
if (picy < 0) {
    picy2 := picy2 - picy
    picy := 0
} else if (picy2 > A_ScreenHeight ){
    picy := picy - (picy2 - A_ScreenHeight)
    picy2 := 0   
}
capturecoords := """" picx ", " picy ", " picx2 ", " picy2 """"

pToken := Gdip_Startup()
snap := Gdip_BitmapFromScreen(picx "|" picy "|" picx2 "|" picy2)

; Convert to grayscale by manipulating the image
width := Gdip_GetImageWidth(snap)
height := Gdip_GetImageHeight(snap)

Loop, % height {
    yPos := A_Index - 1
    Loop, % width {
        xPos := A_Index - 1
        color := Gdip_GetPixel(snap, xPos, yPos)
        
        ; Extract RGB values
        r := (color >> 16) & 0xFF
        g := (color >> 8) & 0xFF
        b := color & 0xFF
        
        ; Convert to grayscale using the average of R, G, and B
        gray := (r + g + b) // 3
        
        ; Set the pixel to grayscale value
        grayColor := (gray << 16) | (gray << 8) | gray
        Gdip_SetPixel(snap, xPos, yPos, grayColor)
    }
}

Gdip_SaveBitmapToFile(snap, "Shot_grayscale.png")
Gdip_DisposeImage(snap)

sleep 1000

Run, %TesseractPath% "Shot.png" "output" ; This will save the text to "output.txt"
return