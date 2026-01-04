import os
import json
import time
import numpy as np
import cv2
import keyboard
import mouse
import threading
from datetime import datetime
from PIL import ImageGrab
import pickle
from collections import deque
import logging

class GameplayRecorder:
    def __init__(self, screen_region=None, frame_rate=10):
        """
        Initialize the gameplay recorder
        
        Args:
            screen_region: Tuple (x1, y1, x2, y2) for screen capture region, None for full screen
            frame_rate: How many screenshots per second to capture
        """
        self.screen_region = screen_region
        self.frame_rate = frame_rate
        self.recording = False
        self.data_buffer = deque(maxlen=10000)  # Store last 10000 actions
        
        # Create directories
        self.data_dir = "gameplay_data"
        self.sessions_dir = os.path.join(self.data_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Session data
        self.session_id = None
        self.session_data = []
        self.start_time = None
        
        # Threading control
        self.recording_thread = None
        self.stop_recording_flag = threading.Event()
        
        # Action tracking
        self.last_mouse_pos = (0, 0)
        self.last_screenshot_time = 0
        
        # Setup logging
        logging.basicConfig(
            filename=os.path.join(self.data_dir, "recorder.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        print("Gameplay Recorder Initialized!")
        print("Controls:")
        print("F1 - Start Recording")
        print("F2 - Stop Recording") 
        print("F3 - Exit Program")
        print(f"Screenshots will be captured at {frame_rate} FPS")
        
    def setup_hotkeys(self):
        """Setup keyboard hotkeys for recording control"""
        keyboard.add_hotkey('f1', self.start_recording)
        keyboard.add_hotkey('f2', self.stop_recording)
        keyboard.add_hotkey('f3', self.exit_program)
        
    def start_recording(self):
        """Start recording gameplay actions"""
        if self.recording:
            print("Already recording!")
            return
            
        self.recording = True
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_data = []
        self.start_time = time.time()
        self.stop_recording_flag.clear()
        
        print(f"\n🔴 RECORDING STARTED - Session: {self.session_id}")
        print("Capturing your gameplay actions...")
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Setup input hooks
        self._setup_input_hooks()
        
        self.logger.info(f"Recording started - Session: {self.session_id}")
        
    def stop_recording(self):
        """Stop recording and save data"""
        if not self.recording:
            print("Not currently recording!")
            return
            
        self.recording = False
        self.stop_recording_flag.set()
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
            
        # Remove input hooks
        self._remove_input_hooks()
        
        # Save session data
        self._save_session_data()
        
        duration = time.time() - self.start_time
        print(f"\n⏹️ RECORDING STOPPED")
        print(f"Session Duration: {duration:.2f} seconds")
        print(f"Actions Recorded: {len(self.session_data)}")
        print(f"Data saved to: sessions/{self.session_id}.json")
        
        self.logger.info(f"Recording stopped - Duration: {duration:.2f}s, Actions: {len(self.session_data)}")
        
    def exit_program(self):
        """Exit the program gracefully"""
        if self.recording:
            self.stop_recording()
            
        print("\n👋 Exiting Gameplay Recorder...")
        self.logger.info("Program exited")
        os._exit(0)
        
    def _setup_input_hooks(self):
        """Setup hooks to capture keyboard and mouse input"""
        # Keyboard hook
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)
        
        # Mouse hooks - using general hook for all mouse events
        mouse.hook(self._on_mouse_event)
        
    def _remove_input_hooks(self):
        """Remove input hooks"""
        try:
            keyboard.unhook_all()
            mouse.unhook_all()
        except:
            pass
            
    def _on_key_press(self, event):
        """Handle keyboard press events"""
        if self.recording and hasattr(event, 'name'):
            action_data = {
                'timestamp': time.time() - self.start_time,
                'type': 'key_press',
                'key': event.name,
                'scan_code': getattr(event, 'scan_code', None)
            }
            self.session_data.append(action_data)
            
    def _on_key_release(self, event):
        """Handle keyboard release events"""
        if self.recording and hasattr(event, 'name'):
            action_data = {
                'timestamp': time.time() - self.start_time,
                'type': 'key_release', 
                'key': event.name,
                'scan_code': getattr(event, 'scan_code', None)
            }
            self.session_data.append(action_data)
            
    def _on_mouse_event(self, event):
        """Handle all mouse events (clicks and movements)"""
        if not self.recording:
            return
            
        if isinstance(event, mouse.ButtonEvent):
            # Handle mouse clicks
            action_data = {
                'timestamp': time.time() - self.start_time,
                'type': 'mouse_click',
                'x': event.x,
                'y': event.y,
                'button': str(event.button),
                'pressed': event.event_type == mouse.DOWN
            }
            self.session_data.append(action_data)
            
        elif isinstance(event, mouse.MoveEvent):
            # Handle mouse movements (throttled)
            x, y = event.x, event.y
            if abs(x - self.last_mouse_pos[0]) > 5 or abs(y - self.last_mouse_pos[1]) > 5:
                action_data = {
                    'timestamp': time.time() - self.start_time,
                    'type': 'mouse_move',
                    'x': x,
                    'y': y
                }
                self.session_data.append(action_data)
                self.last_mouse_pos = (x, y)
                
    def _recording_loop(self):
        """Main recording loop for screenshots"""
        screenshot_interval = 1.0 / self.frame_rate
        
        while self.recording and not self.stop_recording_flag.is_set():
            current_time = time.time()
            
            # Capture screenshot at specified frame rate
            if current_time - self.last_screenshot_time >= screenshot_interval:
                self._capture_screenshot()
                self.last_screenshot_time = current_time
                
            time.sleep(0.01)  # Small sleep to prevent excessive CPU usage
            
    def _capture_screenshot(self):
        """Capture and process screenshot"""
        try:
            # Capture screenshot
            if self.screen_region:
                screenshot = ImageGrab.grab(bbox=self.screen_region)
            else:
                screenshot = ImageGrab.grab()
                
            # Convert to numpy array and resize for efficiency
            screenshot_np = np.array(screenshot)
            screenshot_resized = cv2.resize(screenshot_np, (640, 480))  # Standardize size
            
            # Store screenshot data
            screenshot_data = {
                'timestamp': time.time() - self.start_time,
                'type': 'screenshot',
                'image_shape': screenshot_resized.shape,
                'image_hash': hash(screenshot_resized.tobytes())  # For deduplication
            }
            
            self.session_data.append(screenshot_data)
            
            # Save actual image (you might want to implement compression/deduplication)
            screenshot_path = os.path.join(
                self.sessions_dir, 
                f"{self.session_id}_screenshots"
            )
            os.makedirs(screenshot_path, exist_ok=True)
            
            # Save every Nth screenshot to disk (to save space)
            if len([x for x in self.session_data if x['type'] == 'screenshot']) % 5 == 0:
                img_filename = f"screenshot_{len(self.session_data):06d}.png"
                cv2.imwrite(
                    os.path.join(screenshot_path, img_filename),
                    cv2.cvtColor(screenshot_resized, cv2.COLOR_RGB2BGR)
                )
                
        except Exception as e:
            self.logger.error(f"Screenshot capture error: {e}")
            
    def _save_session_data(self):
        """Save recorded session data to file"""
        try:
            session_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")
            
            # Prepare metadata
            metadata = {
                'session_id': self.session_id,
                'start_time': self.start_time,
                'duration': time.time() - self.start_time,
                'total_actions': len(self.session_data),
                'action_types': {},
                'frame_rate': self.frame_rate,
                'screen_region': self.screen_region
            }
            
            # Count action types
            for action in self.session_data:
                action_type = action['type']
                metadata['action_types'][action_type] = metadata['action_types'].get(action_type, 0) + 1
                
            # Save data
            with open(session_file, 'w') as f:
                json.dump({
                    'metadata': metadata,
                    'actions': self.session_data
                }, f, indent=2)
                
            # Also save as pickle for faster loading
            pickle_file = os.path.join(self.sessions_dir, f"{self.session_id}.pkl")
            with open(pickle_file, 'wb') as f:
                pickle.dump({
                    'metadata': metadata,
                    'actions': self.session_data
                }, f)
                
            print(f"Session data saved successfully!")
            
        except Exception as e:
            self.logger.error(f"Error saving session data: {e}")
            print(f"Error saving data: {e}")
            
    def analyze_sessions(self):
        """Analyze all recorded sessions"""
        session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.json')]
        
        if not session_files:
            print("No recorded sessions found!")
            return
            
        print(f"\n📊 ANALYSIS OF {len(session_files)} SESSIONS")
        print("-" * 50)
        
        total_duration = 0
        total_actions = 0
        
        for session_file in session_files:
            try:
                with open(os.path.join(self.sessions_dir, session_file), 'r') as f:
                    data = json.load(f)
                    metadata = data['metadata']
                    
                    print(f"Session: {metadata['session_id']}")
                    print(f"  Duration: {metadata['duration']:.2f}s")
                    print(f"  Actions: {metadata['total_actions']}")
                    print(f"  Action types: {metadata['action_types']}")
                    print()
                    
                    total_duration += metadata['duration']
                    total_actions += metadata['total_actions']
                    
            except Exception as e:
                print(f"Error reading {session_file}: {e}")
                
        print(f"TOTAL RECORDING TIME: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
        print(f"TOTAL ACTIONS: {total_actions}")
        print(f"AVERAGE ACTIONS PER SECOND: {total_actions/total_duration:.2f}")

def main():
    """Main function to run the gameplay recorder"""
    print("🎮 Gameplay Recorder - ML Training Data Collection")
    print("=" * 60)
    
    # You can specify a screen region here if you want to focus on a specific area
    # For example: screen_region=(100, 100, 1100, 700)  # x1, y1, x2, y2
    screen_region = None  # Full screen
    
    recorder = GameplayRecorder(screen_region=screen_region, frame_rate=5)  # 5 FPS for efficiency
    recorder.setup_hotkeys()
    
    try:
        print("\nWaiting for hotkey commands...")
        print("Press F1 to start recording, F2 to stop, F3 to exit")
        
        # Keep the program running
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        recorder.exit_program()

if __name__ == "__main__":
    main()