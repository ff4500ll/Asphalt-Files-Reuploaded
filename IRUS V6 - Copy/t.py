"""
Discord Integration Test Script - t.py
Testing Discord bot functionality for IRUS V5

This script sets up the basic structure for Discord integration.
Will be configured with webhook/bot details later.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiscordIntegration:
    """
    Discord Integration class for IRUS V5
    Handles webhooks, bot commands, and notifications
    """
    
    def __init__(self):
        self.webhook_url: Optional[str] = None
        self.bot_token: Optional[str] = None
        self.channel_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.enabled: bool = False
        
        # Message queue for batching
        self.message_queue: list = []
        self.last_send_time: float = 0
        self.send_cooldown: float = 5.0  # Seconds between messages
        
    def configure(self, webhook_url: str = None, bot_token: str = None, 
                  channel_id: str = None, user_id: str = None):
        """Configure Discord connection details"""
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.user_id = user_id
        
        if webhook_url or (bot_token and channel_id):
            self.enabled = True
            logger.info("Discord integration configured and enabled")
        else:
            self.enabled = False
            logger.warning("Discord integration not properly configured")
    
    async def send_webhook_message(self, content: str, embeds: list = None) -> bool:
        """Send message via Discord webhook"""
        if not self.webhook_url or not self.enabled:
            logger.warning("Webhook URL not configured or Discord disabled")
            return False
            
        payload = {
            "content": content,
            "username": "IRUS V5 Bot",
            "avatar_url": "https://cdn.discordapp.com/attachments/1234567890/avatar.png"  # Placeholder
        }
        
        if embeds:
            payload["embeds"] = embeds
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info(f"Webhook message sent successfully")
                        return True
                    else:
                        logger.error(f"Webhook failed with status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return False
    
    async def send_bot_message(self, content: str, embed: dict = None) -> bool:
        """Send message via Discord bot API"""
        if not self.bot_token or not self.channel_id or not self.enabled:
            logger.warning("Bot token/channel not configured or Discord disabled")
            return False
            
        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"content": content}
        if embed:
            payload["embed"] = embed
            
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info("Bot message sent successfully")
                        return True
                    else:
                        logger.error(f"Bot message failed with status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error sending bot message: {e}")
            return False
    
    def create_fishing_embed(self, title: str, description: str, color: int = 0x00ff00,
                           fields: list = None, thumbnail_url: str = None) -> dict:
        """Create a Discord embed for fishing notifications"""
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "IRUS V5 Fishing Bot",
                "icon_url": "https://cdn.discordapp.com/attachments/1234567890/bot_icon.png"
            }
        }
        
        if fields:
            embed["fields"] = fields
            
        if thumbnail_url:
            embed["thumbnail"] = {"url": thumbnail_url}
            
        return embed
    
    async def notify_fishing_start(self):
        """Send notification when fishing automation starts"""
        if not self.enabled:
            return
            
        embed = self.create_fishing_embed(
            title="🎣 Fishing Started",
            description="IRUS V5 fishing automation has been activated!",
            color=0x00ff00
        )
        
        await self.send_webhook_message("", [embed])
    
    async def notify_fishing_stop(self):
        """Send notification when fishing automation stops"""
        if not self.enabled:
            return
            
        embed = self.create_fishing_embed(
            title="🛑 Fishing Stopped",
            description="IRUS V5 fishing automation has been deactivated.",
            color=0xff0000
        )
        
        await self.send_webhook_message("", [embed])
    
    async def notify_fish_caught(self, fish_type: str = "Unknown", rarity: str = "Common"):
        """Send notification when a fish is caught"""
        if not self.enabled:
            return
            
        color_map = {
            "Common": 0x808080,
            "Uncommon": 0x00ff00,
            "Rare": 0x0099ff,
            "Epic": 0x9900ff,
            "Legendary": 0xffaa00,
            "Mythic": 0xff0000
        }
        
        embed = self.create_fishing_embed(
            title="🐟 Fish Caught!",
            description=f"Successfully caught a **{rarity} {fish_type}**!",
            color=color_map.get(rarity, 0x808080),
            fields=[
                {"name": "Fish Type", "value": fish_type, "inline": True},
                {"name": "Rarity", "value": rarity, "inline": True},
                {"name": "Time", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
            ]
        )
        
        await self.send_webhook_message("", [embed])
    
    async def notify_error(self, error_message: str):
        """Send error notification"""
        if not self.enabled:
            return
            
        embed = self.create_fishing_embed(
            title="⚠️ Error Detected",
            description=f"An error occurred in IRUS V5:\n```{error_message}```",
            color=0xff0000
        )
        
        await self.send_webhook_message("", [embed])
    
    async def notify_statistics(self, stats: Dict[str, Any]):
        """Send fishing statistics"""
        if not self.enabled:
            return
            
        fields = []
        for key, value in stats.items():
            fields.append({
                "name": key.replace("_", " ").title(),
                "value": str(value),
                "inline": True
            })
        
        embed = self.create_fishing_embed(
            title="📊 Fishing Statistics",
            description="Current session statistics",
            color=0x0099ff,
            fields=fields
        )
        
        await self.send_webhook_message("", [embed])

class DiscordTester:
    """Test class for Discord functionality"""
    
    def __init__(self):
        self.discord = DiscordIntegration()
    
    async def test_webhook(self, webhook_url: str):
        """Test webhook functionality"""
        logger.info("Testing Discord webhook...")
        
        self.discord.configure(webhook_url=webhook_url)
        
        # Test basic message
        await self.discord.send_webhook_message("🧪 Testing IRUS V5 Discord Integration!")
        await asyncio.sleep(2)
        
        # Test fishing notifications
        await self.discord.notify_fishing_start()
        await asyncio.sleep(2)
        
        await self.discord.notify_fish_caught("Bass", "Rare")
        await asyncio.sleep(2)
        
        await self.discord.notify_statistics({
            "fish_caught": 15,
            "session_time": "45 minutes",
            "success_rate": "92%",
            "total_casts": 67
        })
        await asyncio.sleep(2)
        
        await self.discord.notify_fishing_stop()
        
        logger.info("Webhook testing complete!")
    
    async def test_bot(self, bot_token: str, channel_id: str):
        """Test bot functionality"""
        logger.info("Testing Discord bot...")
        
        self.discord.configure(bot_token=bot_token, channel_id=channel_id)
        
        # Test bot message
        embed = self.discord.create_fishing_embed(
            title="🤖 Bot Test",
            description="Testing IRUS V5 Discord Bot integration!",
            color=0x00ff00
        )
        
        await self.discord.send_bot_message("Bot test message", embed)
        
        logger.info("Bot testing complete!")

import keyboard
import pyautogui
import io
import base64
import threading
import win32gui
import win32api
import win32ui
import win32con
from PIL import Image

class DiscordHotkeyManager:
    """Manages hotkeys for Discord integration"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.discord = DiscordIntegration()
        self.discord.configure(webhook_url=webhook_url)
        self.running = False
        self.loop = None
    
    def capture_screen_win32(self, x, y, width, height):
        """Capture screen using Windows API - more reliable for multi-monitor"""
        try:
            # Get desktop device context
            desktop_dc = win32gui.GetDC(0)
            
            # Create compatible device context and bitmap
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            # Create bitmap object
            screenshot_bmp = win32ui.CreateBitmap()
            screenshot_bmp.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot_bmp)
            
            # Copy screen area to bitmap
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)
            
            # Get bitmap info
            bmp_info = screenshot_bmp.GetInfo()
            bmp_str = screenshot_bmp.GetBitmapBits(True)
            
            # Convert to PIL Image
            screenshot = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_str, 'raw', 'BGRX', 0, 1
            )
            
            # Clean up
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot_bmp.GetHandle())
            win32gui.ReleaseDC(0, desktop_dc)
            
            return screenshot
            
        except Exception as e:
            print(f"Windows API capture error: {e}")
            return None
    
    def get_active_monitor(self):
        """Get the monitor where the currently focused window is located"""
        try:
            # Get the handle of the currently active window
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get the window rectangle
            window_rect = win32gui.GetWindowRect(hwnd)
            window_x, window_y, window_right, window_bottom = window_rect
            window_center_x = (window_x + window_right) // 2
            window_center_y = (window_y + window_bottom) // 2
            
            print(f"Active window: '{window_title}' at ({window_x}, {window_y}) to ({window_right}, {window_bottom})")
            print(f"Window center: ({window_center_x}, {window_center_y})")
            
            # Get all monitors
            monitors = win32api.EnumDisplayMonitors()
            print(f"Found {len(monitors)} monitors:")
            
            # Find which monitor contains the active window (use center point for better detection)
            for i, (hmon, hdc, monitor_rect) in enumerate(monitors):
                left, top, right, bottom = monitor_rect
                print(f"  Monitor {i + 1}: ({left}, {top}) to ({right}, {bottom})")
                
                # Check if the window's center is within this monitor
                if left <= window_center_x < right and top <= window_center_y < bottom:
                    print(f"✓ Active window center is on Monitor {i + 1}: {monitor_rect}")
                    return monitor_rect, i + 1
            
            # Alternative: Check if any part of the window overlaps with the monitor
            print("Center point method failed, trying overlap detection...")
            for i, (hmon, hdc, monitor_rect) in enumerate(monitors):
                left, top, right, bottom = monitor_rect
                
                # Check for any overlap between window and monitor
                overlap_x = max(0, min(window_right, right) - max(window_x, left))
                overlap_y = max(0, min(window_bottom, bottom) - max(window_y, top))
                overlap_area = overlap_x * overlap_y
                
                if overlap_area > 0:
                    print(f"✓ Active window overlaps with Monitor {i + 1} (area: {overlap_area})")
                    return monitor_rect, i + 1
            
            print("⚠ No monitor found for active window, using primary monitor")
            # If not found in any monitor, return the primary monitor
            return monitors[0][2], 1
            
        except Exception as e:
            print(f"Error detecting active monitor: {e}")
            # Fallback to full screen
            return None, 0
    
    async def send_screenshot(self):
        """Take screenshot of the active monitor and send to Discord"""
        try:
            # Get the monitor where the active window is located
            monitor_rect, monitor_num = self.get_active_monitor()
            
            if monitor_rect:
                left, top, right, bottom = monitor_rect
                width = right - left
                height = bottom - top
                print(f"Taking screenshot of Monitor {monitor_num}")
                print(f"  Position: ({left}, {top}) to ({right}, {bottom})")
                print(f"  Size: {width} x {height}")
                
                # Validate coordinates
                if width <= 0 or height <= 0:
                    print(f"⚠ Invalid monitor dimensions: {width}x{height}")
                    raise ValueError("Invalid monitor dimensions")
                
                # Try different screenshot methods for multi-monitor setups
                screenshot = None
                
                # Method 1: Windows API direct screen capture (best for multi-monitor)
                try:
                    print("Attempting Windows API screen capture...")
                    screenshot = self.capture_screen_win32(left, top, width, height)
                    if screenshot and screenshot.size[0] > 0:
                        print(f"✓ Windows API capture successful: {screenshot.size}")
                    else:
                        screenshot = None
                except Exception as e:
                    print(f"✗ Windows API capture failed: {e}")
                    screenshot = None
                
                # Method 2: Direct region capture
                if screenshot is None:
                    try:
                        print("Attempting pyautogui region capture...")
                        screenshot = pyautogui.screenshot(region=(left, top, width, height))
                        print(f"✓ Region capture successful: {screenshot.size}")
                    except Exception as e:
                        print(f"✗ Region capture failed: {e}")
                        screenshot = None
                
                # Method 3: Full screenshot then crop (more reliable for multi-monitor)
                if screenshot is None or screenshot.size[0] == 0 or screenshot.size[1] == 0:
                    try:
                        print("Attempting full screenshot with crop...")
                        full_screenshot = pyautogui.screenshot()
                        print(f"Full screenshot size: {full_screenshot.size}")
                        
                        # Adjust coordinates for cropping (handle negative coordinates)
                        crop_left = max(0, left)
                        crop_top = max(0, top) 
                        crop_right = min(full_screenshot.size[0], right)
                        crop_bottom = min(full_screenshot.size[1], bottom)
                        
                        print(f"Cropping to: ({crop_left}, {crop_top}, {crop_right}, {crop_bottom})")
                        screenshot = full_screenshot.crop((crop_left, crop_top, crop_right, crop_bottom))
                        print(f"✓ Crop successful: {screenshot.size}")
                    except Exception as e:
                        print(f"✗ Crop method failed: {e}")
                        screenshot = None
                
                # Method 4: Fallback to full screenshot
                if screenshot is None or screenshot.size[0] == 0:
                    print("⚠ Using full desktop fallback...")
                    screenshot = pyautogui.screenshot()
                    
            else:
                print("Taking screenshot of full desktop...")
                screenshot = pyautogui.screenshot()
                monitor_num = 0
            
            # Validate final screenshot
            if screenshot.size[0] == 0 or screenshot.size[1] == 0:
                raise ValueError(f"Screenshot has invalid size: {screenshot.size}")
            
            print(f"Final screenshot size: {screenshot.size}")
            
            # Convert PIL image to bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Send via webhook with file attachment
            await self.send_screenshot_to_discord(img_buffer.getvalue(), monitor_num)
            print(f"Screenshot of Monitor {monitor_num} sent to Discord!")
            
        except Exception as e:
            print(f"Error taking/sending screenshot: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_screenshot_to_discord(self, image_data: bytes, monitor_num: int = 0):
        """Send screenshot as file attachment to Discord"""
        try:
            # Create multipart form data
            from aiohttp import FormData
            
            data = FormData()
            data.add_field('file', image_data, filename=f'monitor_{monitor_num}_screenshot.png', content_type='image/png')
            data.add_field('payload_json', json.dumps({
                "content": f"📸 Screenshot captured from Monitor {monitor_num}!",
                "username": "IRUS V5 Bot"
            }))
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, data=data) as response:
                    if response.status == 200 or response.status == 204:
                        print("Screenshot uploaded successfully!")
                    else:
                        print(f"Failed to upload screenshot: {response.status}")
                        
        except Exception as e:
            print(f"Error uploading screenshot: {e}")
    
    async def send_test_text(self):
        """Send test text message"""
        try:
            await self.discord.send_webhook_message("Test Text")
            print("Test text sent to Discord!")
        except Exception as e:
            print(f"Error sending test text: {e}")
    
    def setup_hotkeys(self):
        """Set up F1 and F2 hotkeys"""
        print("Setting up hotkeys...")
        print("F1 = Take screenshot and send to Discord")
        print("F2 = Send test text to Discord") 
        print("ESC = Exit program")
        
        # F1 for screenshot
        keyboard.add_hotkey('f1', self._handle_screenshot)
        
        # F2 for test text
        keyboard.add_hotkey('f2', self._handle_test_text)
        
        # ESC to exit
        keyboard.add_hotkey('esc', self.stop)
        
        print("Hotkeys registered! Press F1 or F2 to test.")
    
    def _handle_screenshot(self):
        """Handle screenshot hotkey"""
        def run_async():
            asyncio.run(self.send_screenshot())
        threading.Thread(target=run_async, daemon=True).start()
    
    def _handle_test_text(self):
        """Handle test text hotkey"""
        def run_async():
            asyncio.run(self.send_test_text())
        threading.Thread(target=run_async, daemon=True).start()
    
    def stop(self):
        """Stop the hotkey manager"""
        self.running = False
        print("Stopping hotkey manager...")
    
    def run(self):
        """Run the hotkey manager"""
        self.running = True
        self.setup_hotkeys()
        
        print("Hotkey manager is running. Press ESC to exit.")
        try:
            while self.running:
                keyboard.wait('esc')
                break
        except KeyboardInterrupt:
            pass
        finally:
            keyboard.unhook_all_hotkeys()
            print("Hotkeys disabled.")

def main():
    """Main function with hotkey setup"""
    print("IRUS V6 Discord Hotkey Integration")
    print("=" * 40)
    
    # Your webhook URL
    webhook_url = "https://discord.com/api/webhooks/1426696956364853399/MAOX7cRbLjMC25Vg2_iUlCgCTtZaXKezlITtUfooR8CWS2IgNoBHl6U2flDNJA5PUYp7"
    
    # Create hotkey manager
    hotkey_manager = DiscordHotkeyManager(webhook_url)
    
    # Test connection first
    print("Testing Discord connection...")
    
    async def test_connection():
        await hotkey_manager.discord.send_webhook_message("🚀 IRUS V6 Discord integration activated!")
    
    asyncio.run(test_connection())
    
    # Run hotkey manager
    hotkey_manager.run()

if __name__ == "__main__":
    try:
        # Install required packages if not available
        import keyboard
        import pyautogui  
        import aiohttp
        from PIL import Image
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install: pip install keyboard pyautogui aiohttp pillow")
        exit(1)
    
    main()