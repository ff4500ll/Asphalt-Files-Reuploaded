#Requires AutoHotkey v2
SetWorkingDir(A_ScriptDir) ; Set working directory to the script's location

#include Gdip.ahk

DllCall("SetThreadDpiAwarenessContext", "ptr", -3)

global size := 50, minsize := 5, step := 3
CoordMode "Mouse", "Screen"
CoordMode "ToolTip", "Screen"
global isTracking := true

SetTimer(TrackMouse, 10)

p::CaptureArea() ; Bind the capture function to the "p" key

z::global size-=(size > minsize ? step : 0)
x::global size+=step

c::global isTracking := !isTracking

Highlight(x?, y?, w?, h?, color:="Red") {
    static guis := []
    if !IsSet(x) {
        for _, r in guis
            r.Destroy()
        guis := []
        return
    }
    if !guis.Length {
        Loop 4
            guis.Push(Gui("+AlwaysOnTop -Caption +ToolWindow -DPIScale +E0x08000000"))
    }
    Loop 4 {
        i := A_Index
        x1 := (i=2 ? x+w : x-2)
        y1 := (i=3 ? y+h : y-2)
        w1 := (i=1 or i=3 ? w+4 : 2)
        h1 := (i=2 or i=4 ? h+4 : 2)
        guis[i].BackColor := color
        guis[i].Show("NA x" . x1 . " y" . y1 . " w" . w1 . " h" . h1)
    }
}

TrackMouse() {
    global
    if (isTracking) {
        MouseGetPos(&x, &y)
        Highlight(x - size // 2, y + 10, size, size)
    } else {
        Highlight(x - size // 2, y + 10, size, size)
    }
}

CaptureArea() {
    ; Define the coordinates for the red box (x, y, width, height)
    boxX := 100
    boxY := 100
    boxWidth := 200
    boxHeight := 150

    ; Capture and save the image
    screenshotPath := A_ScriptDir . "\CapturedArea.png"
    CaptureScreenshot(boxX, boxY, boxWidth, boxHeight, screenshotPath)
    
    Tooltip "Captured screenshot saved to " screenshotPath
    SetTimer(Tooltip, -1000) ; Hide the tooltip after 1 second
}

CaptureScreenshot(x, y, w, h, filePath) {
    ; Initialize GDI+ to capture the screenshot
    pToken := Gdip_Startup()  ; Start GDI+
    
    ; Create a blank bitmap of the same size as the capture region
    pBitmap := Gdip_CreateBitmapFromScan0(w, h, w * 4, 0x26200A, 0)  ; Create a bitmap with correct format
    pGraphics := Gdip_GraphicsFromImage(pBitmap)  ; Create graphics object from the bitmap
    
    ; Capture the screen area into the bitmap
    Gdip_DrawImage(pGraphics, x, y, 0, 0, w, h)  ; Capture region into the bitmap
    
    ; Save the captured image as a PNG
    Gdip_SaveBitmapToFile(pBitmap, filePath)
    
    ; Clean up resources
    Gdip_DeleteGraphics(pGraphics)
    Gdip_FreeBitmap(pBitmap)
    Gdip_Shutdown(pToken)  ; Shut down GDI+
}
