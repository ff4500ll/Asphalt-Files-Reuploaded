import customtkinter as ctk
import math
import random
import json
import os
import tkinter as tk
from collections import deque
from PIL import Image, ImageTk, ImageGrab
from pynput import keyboard


class CentralStorage:
    def __init__(self, config_file="irus_config.json"):
        self.config_file = config_file
        self.settings = {
            "hotkeys": {
                "start_stop": "f3",
                "change_area": "f1", 
                "exit": "f4"
            },
            "gui_settings": {
                "always_on_top": True,
                "auto_minimize": True,
                "auto_focus_roblox": True,
                "friend_color_tolerance": 0,
                "state_check_timeout": 5.0
            },
            "quad_boxes": {
                "friend_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300},
                "shake_box": {"x1": 400, "y1": 100, "x2": 600, "y2": 300},
                "detection_box": {"x1": 100, "y1": 400, "x2": 600, "y2": 600}
            },
            "cast_settings": {
                "delay_before_click": 0.0,
                "delay_hold_duration": 0.5,
                "delay_after_release": 0.5,
                "anti_nuke": True,
                "anti_nuke_delay_before": 0.0,
                "anti_nuke_rod_slot": 1,
                "anti_nuke_delay_after_rod": 0.5,
                "anti_nuke_bag_slot": 2,
                "anti_nuke_delay_after_bag": 0.5
            },
            "shake_settings": {
                "shake_method": "Pixel",
                "friend_color": [155, 255, 155],
                "shake_color": [255, 255, 255],
                "friend_color_tolerance": 5,
                "white_color_tolerance": 0,
                "duplicate_pixel_bypass": 2.0,
                "fail_shake_timeout": 5.0,
                "double_click": True,
                "double_click_delay": 25
            },
            "discord_settings": {
                "active": False,
                "webhook_url": "",
                "loops_per_screenshot": 10
            },
            "fish_settings": {
                "rod_model": "No Models Found",
                "tolerance_pixels": 10,
                "base_resolution_width": 2560,
                "accel_init": 50,
                "max_velocity_init": 1000,
                "smoothing": 5,
                "learning_rate": 0.95,
                "accel_learned": None,
                "max_velocity_learned": None
            }
        }
        
        self.runtime_states = {
            "is_running": False,
            "area_toggled": False
        }
        
        self.load()
    
    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self._merge_settings(loaded_settings)
                print(f"Settings loaded from {self.config_file}")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _merge_settings(self, loaded_settings):
        for key, value in loaded_settings.items():
            if isinstance(value, dict) and key in self.settings:
                self.settings[key].update(value)
            else:
                self.settings[key] = value
    
    def get_hotkey(self, key_name):
        return self.settings["hotkeys"].get(key_name, "")
    
    def set_hotkey(self, key_name, key_value):
        self.settings["hotkeys"][key_name] = key_value
        self.save()
    
    def get_state(self, state_name):
        return self.runtime_states.get(state_name, False)
    
    def set_state(self, state_name, value):
        self.runtime_states[state_name] = value
    
    def toggle_state(self, state_name):
        current = self.get_state(state_name)
        self.set_state(state_name, not current)
        return not current
    
    def get_gui_setting(self, setting_name):
        return self.settings["gui_settings"].get(setting_name, False)
    
    def set_gui_setting(self, setting_name, value):
        self.settings["gui_settings"][setting_name] = value
        self.save()
    
    def toggle_gui_setting(self, setting_name):
        current = self.get_gui_setting(setting_name)
        self.set_gui_setting(setting_name, not current)
        return not current
    
    def get_quad_box(self, box_name):
        return self.settings["quad_boxes"].get(box_name, {"x1": 0, "y1": 0, "x2": 100, "y2": 100})
    
    def set_quad_boxes(self, friend_box, shake_box, detection_box):
        self.settings["quad_boxes"]["friend_box"] = friend_box
        self.settings["quad_boxes"]["shake_box"] = shake_box
        self.settings["quad_boxes"]["detection_box"] = detection_box
        self.save()
    
    def get_shake_scan_area(self):
        shake_box = self.get_quad_box("shake_box")
        friend_box = self.get_quad_box("friend_box")
        
        x1 = min(shake_box["x1"], friend_box["x1"])
        y1 = min(shake_box["y1"], friend_box["y1"])
        x2 = max(shake_box["x2"], friend_box["x2"])
        y2 = max(shake_box["y2"], friend_box["y2"])
        
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    
    def get_fish_scan_area(self):
        shake_box = self.get_quad_box("shake_box")
        detection_box = self.get_quad_box("detection_box")
        
        x1 = min(shake_box["x1"], detection_box["x1"])
        y1 = min(shake_box["y1"], detection_box["y1"])
        x2 = max(shake_box["x2"], detection_box["x2"])
        y2 = max(shake_box["y2"], detection_box["y2"])
        
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    
    def get_cast_setting(self, setting_name):
        return self.settings["cast_settings"].get(setting_name, 0.0)
    
    def set_cast_setting(self, setting_name, value):
        self.settings["cast_settings"][setting_name] = value
        self.save()
    
    def toggle_cast_anti_nuke(self):
        current = self.get_cast_setting("anti_nuke")
        self.set_cast_setting("anti_nuke", not current)
        return not current
    
    def get_shake_setting(self, setting_name):
        return self.settings["shake_settings"].get(setting_name, "Pixel")
    
    def set_shake_setting(self, setting_name, value):
        self.settings["shake_settings"][setting_name] = value
        self.save()
    
    def get_discord_setting(self, setting_name):
        defaults = {"active": False, "webhook_url": "", "loops_per_screenshot": 10}
        return self.settings["discord_settings"].get(setting_name, defaults.get(setting_name))
    
    def set_discord_setting(self, setting_name, value):
        self.settings["discord_settings"][setting_name] = value
        self.save()
    
    def toggle_discord_active(self):
        current = self.get_discord_setting("active")
        self.set_discord_setting("active", not current)
        return not current
    
    def get_fish_setting(self, setting_name):
        defaults = {
            "rod_model": "No Models Found",
            "tolerance_pixels": 10,
            "base_resolution_width": 2560,
            "accel_init": 50,
            "max_velocity_init": 1000,
            "smoothing": 5,
            "learning_rate": 0.95,
            "accel_learned": None,
            "max_velocity_learned": None
        }
        return self.settings["fish_settings"].get(setting_name, defaults.get(setting_name))
    
    def set_fish_setting(self, setting_name, value):
        self.settings["fish_settings"][setting_name] = value
        self.save()
    
    def update_fish_learned_values(self, accel_right, max_velocity):
        self.settings["fish_settings"]["accel_learned"] = abs(accel_right)
        self.settings["fish_settings"]["max_velocity_learned"] = max_velocity
        self.save()


class AdaptiveBangBangController:
    VELOCITY_CAP_THRESHOLD = 0.98
    VELOCITY_LOW_SPEED_THRESHOLD = 15
    LEARNING_VELOCITY_THRESHOLD = 0.95
    MAX_VELOCITY_MULTIPLIER = 1.1
    
    def __init__(self, accel_init=50, max_velocity=1000, smoothing=5, learning_rate=0.95):
        self.position = None
        self.last_position = None
        self.velocity = 0
        self.last_velocity = 0
        self.last_time = None
        
        self.accel_right = accel_init
        self.accel_left = -accel_init
        self.max_velocity = max_velocity
        
        self.learning_rate = learning_rate
        self.last_action = None
        self.max_velocity_observed = 0
        
        self.velocity_buffer = deque(maxlen=smoothing)
        self.smoothing = smoothing
        
        self.initialized = False
    
    def estimate_velocity(self, current_position, current_time):
        if self.last_position is None or self.last_time is None:
            self.last_position = current_position
            self.last_time = current_time
            return 0
        
        dt = current_time - self.last_time
        if dt <= 0:
            return self.velocity
        
        raw_velocity = (current_position - self.last_position) / dt
        
        self.velocity_buffer.append(raw_velocity)
        
        smoothed_velocity = sum(self.velocity_buffer) / len(self.velocity_buffer)
        
        self.last_position = current_position
        self.last_time = current_time
        return smoothed_velocity
    
    def learn_parameters(self, velocity, action, dt):
        if self.last_velocity is None or self.last_action is None or dt <= 0:
            return
        
        abs_velocity = abs(velocity)
        if abs_velocity > self.max_velocity_observed:
            self.max_velocity_observed = abs_velocity
            self.max_velocity = abs_velocity * self.MAX_VELOCITY_MULTIPLIER
        
        velocity_change = velocity - self.last_velocity
        observed_accel = velocity_change / dt
        
        if abs(velocity) < self.max_velocity * self.LEARNING_VELOCITY_THRESHOLD:
            if self.last_action:
                if observed_accel > 0:
                    self.accel_right = self.learning_rate * self.accel_right + (1 - self.learning_rate) * observed_accel
            else:
                if observed_accel < 0:
                    self.accel_left = self.learning_rate * self.accel_left + (1 - self.learning_rate) * observed_accel
        
        if len(self.velocity_buffer) >= self.smoothing:
            self.initialized = True
    
    def calculate_stopping_distance(self, velocity):
        if abs(velocity) < 1:
            return 0
        
        if velocity > 0:
            stopping_accel = self.accel_left
        else:
            stopping_accel = self.accel_right
        
        stopping_distance = (velocity ** 2) / (2 * abs(stopping_accel))
        return stopping_distance if velocity > 0 else -stopping_distance
    
    def update(self, bar_position, target_position, currently_holding, current_time, tolerance=10):
        velocity = self.estimate_velocity(bar_position, current_time)
        
        if self.last_time is not None:
            dt = current_time - self.last_time
            self.learn_parameters(velocity, currently_holding, dt)
        
        self.velocity = velocity
        
        error = target_position - bar_position
        stopping_distance = self.calculate_stopping_distance(velocity)
        predicted_stop = bar_position + stopping_distance
        predicted_error = target_position - predicted_stop
        
        if not self.initialized:
            action = error > 0
        elif abs(error) < tolerance:
            if abs(velocity) < self.VELOCITY_LOW_SPEED_THRESHOLD:
                action = not currently_holding
            else:
                action = velocity < 0
        elif abs(predicted_error) < abs(error):
            action = error < 0
        else:
            action = error > 0
        
        if abs(velocity) >= self.max_velocity * self.VELOCITY_CAP_THRESHOLD:
            action = velocity <= 0
        
        self.last_action = action
        self.last_velocity = velocity
        
        return action
    
    def get_debug_info(self):
        return {
            'velocity': self.velocity,
            'accel_right': self.accel_right,
            'accel_left': self.accel_left,
            'max_velocity': self.max_velocity,
            'initialized': self.initialized
        }


class QuadAreaSelector:
    def __init__(self, parent, screenshot, friend_box, shake_box, detection_box, callback):
        self.callback = callback
        self.screenshot = screenshot
        
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.configure(cursor='cross')
        
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        self.photo = ImageTk.PhotoImage(screenshot)
        
        self.canvas = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        
        self.boxes = {
            'friend': {'coords': friend_box.copy(), 'color': '#00ff00', 'name': 'FriendBox'},
            'shake': {'coords': shake_box.copy(), 'color': '#ff0000', 'name': 'ShakeBox'},
            'detection': {'coords': detection_box.copy(), 'color': '#0000ff', 'name': 'DetectionBox'}
        }
        
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
        self.resize_threshold = 10
        
        self.rects = {}
        self.labels = {}
        self.handles = {}
        
        for box_id, box_data in self.boxes.items():
            self.create_box(box_id)
        
        self.zoom_window_size = 150
        self.zoom_factor = 4
        self.zoom_rect = None
        self.zoom_image_id = None
        self.zoom_photo = None
        
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
    
    def create_box(self, box_id):
        box_data = self.boxes[box_id]
        coords = box_data['coords']
        color = box_data['color']
        name = box_data['name']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=3,
            fill=color,
            stipple='gray50',
            tags=f'{box_id}_box'
        )
        self.rects[box_id] = rect
        
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        label = self.canvas.create_text(
            label_x, label_y,
            text=name,
            font=("Arial", 14, "bold"),
            fill=color,
            tags=f'{box_id}_label'
        )
        self.labels[box_id] = label
        
        self.create_handles_for_box(box_id)
    
    def create_handles_for_box(self, box_id):
        handle_size = 12
        corner_marker_size = 3
        
        box_data = self.boxes[box_id]
        coords = box_data['coords']
        color = box_data['color']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        corners = [
            (x1, y1, 'nw'),
            (x2, y1, 'ne'),
            (x1, y2, 'sw'),
            (x2, y2, 'se')
        ]
        
        if box_id in self.handles:
            for handle in self.handles[box_id]:
                self.canvas.delete(handle)
        
        self.handles[box_id] = []
        
        for x, y, corner in corners:
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline=color,
                width=2,
                tags=f'{box_id}_handle_{corner}'
            )
            self.handles[box_id].append(handle)
            
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='white',
                outline=color,
                width=1,
                tags=f'{box_id}_corner_{corner}'
            )
            self.handles[box_id].append(corner_marker)
            
            line1 = self.canvas.create_line(
                x - handle_size, y, x + handle_size, y,
                fill='white',
                width=1,
                tags=f'{box_id}_cross_{corner}'
            )
            line2 = self.canvas.create_line(
                x, y - handle_size, x, y + handle_size,
                fill='white',
                width=1,
                tags=f'{box_id}_cross_{corner}'
            )
            self.handles[box_id].append(line1)
            self.handles[box_id].append(line2)
    
    def get_corner_at_position(self, x, y, box_id):
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        corners = {
            'nw': (x1, y1),
            'ne': (x2, y1),
            'sw': (x1, y2),
            'se': (x2, y2)
        }
        
        for corner, (cx, cy) in corners.items():
            if abs(x - cx) < self.resize_threshold and abs(y - cy) < self.resize_threshold:
                return corner
        
        return None
    
    def is_inside_box(self, x, y, box_id):
        coords = self.boxes[box_id]['coords']
        return coords['x1'] < x < coords['x2'] and coords['y1'] < y < coords['y2']
    
    def on_mouse_down(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = corner
                return
            
            if self.is_inside_box(event.x, event.y, box_id):
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = 'move'
                return
    
    def on_mouse_drag(self, event):
        if not self.dragging or not self.active_box:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        coords = self.boxes[self.active_box]['coords']
        
        if self.drag_corner == 'move':
            coords['x1'] += dx
            coords['y1'] += dy
            coords['x2'] += dx
            coords['y2'] += dy
        else:
            if self.drag_corner == 'nw':
                coords['x1'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'ne':
                coords['x2'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'sw':
                coords['x1'] = event.x
                coords['y2'] = event.y
            elif self.drag_corner == 'se':
                coords['x2'] = event.x
                coords['y2'] = event.y
            
            if coords['x1'] > coords['x2']:
                coords['x1'], coords['x2'] = coords['x2'], coords['x1']
            if coords['y1'] > coords['y2']:
                coords['y1'], coords['y2'] = coords['y2'], coords['y1']
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.update_box(self.active_box)
        self.show_zoom(event.x, event.y)
    
    def on_mouse_up(self, event):
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
    
    def on_mouse_move(self, event):
        cursor = 'cross'
        
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                cursor_map = {
                    'nw': 'size_nw_se',
                    'ne': 'size_ne_sw',
                    'sw': 'size_ne_sw',
                    'se': 'size_nw_se'
                }
                cursor = cursor_map[corner]
                break
            elif self.is_inside_box(event.x, event.y, box_id):
                cursor = 'fleur'
                break
        
        self.window.configure(cursor=cursor)
        self.show_zoom(event.x, event.y)
    
    def update_box(self, box_id):
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        self.canvas.coords(self.rects[box_id], x1, y1, x2, y2)
        
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        self.canvas.coords(self.labels[box_id], label_x, label_y)
        
        self.create_handles_for_box(box_id)
    
    def show_zoom(self, x, y):
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
        if self.zoom_image_id:
            self.canvas.delete(self.zoom_image_id)
        
        zoom_src_size = self.zoom_window_size // self.zoom_factor
        x1_src = max(0, x - zoom_src_size // 2)
        y1_src = max(0, y - zoom_src_size // 2)
        x2_src = min(self.screen_width, x1_src + zoom_src_size)
        y2_src = min(self.screen_height, y1_src + zoom_src_size)
        
        cropped = self.screenshot.crop((x1_src, y1_src, x2_src, y2_src))
        zoomed = cropped.resize((self.zoom_window_size, self.zoom_window_size), Image.NEAREST)
        
        from PIL import ImageDraw
        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_window_size // 2
        crosshair_size = 10
        draw.line([(center - crosshair_size, center), (center + crosshair_size, center)], fill='red', width=2)
        draw.line([(center, center - crosshair_size), (center, center + crosshair_size)], fill='red', width=2)
        
        self.zoom_photo = ImageTk.PhotoImage(zoomed)
        
        zoom_x = x + 30
        zoom_y = y + 30
        
        if zoom_x + self.zoom_window_size > self.screen_width:
            zoom_x = x - self.zoom_window_size - 30
        if zoom_y + self.zoom_window_size > self.screen_height:
            zoom_y = y - self.zoom_window_size - 30
        
        self.zoom_rect = self.canvas.create_rectangle(
            zoom_x, zoom_y,
            zoom_x + self.zoom_window_size, zoom_y + self.zoom_window_size,
            fill='black',
            outline='white',
            width=2
        )
        
        self.zoom_image_id = self.canvas.create_image(
            zoom_x, zoom_y,
            image=self.zoom_photo,
            anchor='nw'
        )
    
    def finish_selection(self):
        friend_box = self.boxes['friend']['coords']
        shake_box = self.boxes['shake']['coords']
        detection_box = self.boxes['detection']['coords']
        
        self.window.destroy()
        self.callback(friend_box, shake_box, detection_box)


class Particle:
    def __init__(self, current_node, color):
        self.current_node = current_node
        self.target_node = None
        self.progress = 0
        self.color = color
        self.base_travel_speed = 0.03
        self.waiting = False
        self.last_distance = None
        self.previous_node = None
        
    def update(self, all_nodes, connection_threshold):

        if self.waiting or self.target_node is None:
            available_connections = []
            for node in all_nodes:
                if node != self.current_node:
                    distance = self.current_node.distance_to(node)
                    if distance < connection_threshold:
                        available_connections.append(node)
            
            if available_connections:
                forward_connections = [n for n in available_connections if n != self.previous_node]
                
                if forward_connections:
                    self.target_node = random.choice(forward_connections)
                else:
                    self.target_node = random.choice(available_connections)
                
                self.progress = 0
                self.waiting = False
                self.last_distance = None
            else:
                self.waiting = True
                self.target_node = None

        else:
            distance = self.current_node.distance_to(self.target_node)
            
            if distance >= connection_threshold:
                self._arrive_at_node(self.target_node)
                self.waiting = True
                
            else:
                travel_speed = self._calculate_travel_speed(distance, connection_threshold)
                self.progress += travel_speed
                
                if self.progress >= 1.0:
                    self._arrive_at_node(self.target_node)
    
    def _calculate_travel_speed(self, distance, connection_threshold):
        if self.last_distance is not None:
            distance_change = distance - self.last_distance
        else:
            distance_change = 0
        
        self.last_distance = distance
        
        if distance_change > 0:
            distance_to_threshold = connection_threshold - distance
            
            if distance_change > 0.01:
                frames_until_disconnect = distance_to_threshold / distance_change
                remaining_progress = 1.0 - self.progress
                
                if frames_until_disconnect > 0:
                    required_speed = (remaining_progress / frames_until_disconnect) * 0.9
                    return max(self.base_travel_speed, required_speed)
                else:
                    return self.base_travel_speed * 3
            else:
                return self.base_travel_speed * 1.5
        else:
            return self.base_travel_speed
    
    def _arrive_at_node(self, node):
        self.previous_node = self.current_node
        self.current_node = node
        
        if not self.current_node.is_main:
            self.current_node.activation_color = self.color
            self.current_node.activation_strength = 1.0
        
        self.target_node = None
        self.progress = 0
        self.last_distance = None
    
    def get_position(self):
        if self.target_node and not self.waiting:
            x = self.current_node.x + (self.target_node.x - self.current_node.x) * self.progress
            y = self.current_node.y + (self.target_node.y - self.current_node.y) * self.progress
            return x, y
        else:
            return self.current_node.x, self.current_node.y


class NeuralNode:
    def __init__(self, x, y, label="", radius=30, is_main=False, colors=None):
        self.x = x
        self.y = y
        self.label = label
        self.radius = radius
        self.is_main = is_main
        self.colors = colors if colors else ["#4d4d4d", "#666666", "#808080"]
        
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.is_frozen = False
        
        self.activation_color = None
        self.activation_strength = 0
        
    def update(self, width, height):
        if self.is_frozen:
            return
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.vx *= -1
            if not self.is_main:
                self.vy += random.uniform(-0.3, 0.3)
            self.x = max(self.radius, min(width - self.radius, self.x))
            
            if self.is_main:
                speed = math.sqrt(self.vx**2 + self.vy**2)
                if speed > 0:
                    self.vx = (self.vx / speed) * 1.0
                    self.vy = (self.vy / speed) * 1.0
            
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.vy *= -1
            if not self.is_main:
                self.vx += random.uniform(-0.3, 0.3)
            self.y = max(self.radius, min(height - self.radius, self.y))
            
            if self.is_main:
                speed = math.sqrt(self.vx**2 + self.vy**2)
                if speed > 0:
                    self.vx = (self.vx / speed) * 1.0
                    self.vy = (self.vy / speed) * 1.0
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def is_point_inside(self, px, py):
        distance = math.sqrt((px - self.x)**2 + (py - self.y)**2)
        return distance <= self.radius


class NeuralNetworkGUI(ctk.CTk):
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    CONNECTION_THRESHOLD = 180
    NODE_ACTIVATION_FADE_SPEED = 0.01
    ANIMATION_FPS = 60
    
    MAIN_NODE_SPEED = 1.0
    SMALL_NODE_RADIUS = 10
    MAIN_NODE_RADIUS = 35
    PARTICLE_GLOW_SIZE = 6
    HANDLE_SIZE = 12
    CORNER_MARKER_SIZE = 3
    
    def __init__(self):
        super().__init__()
        
        self.storage = CentralStorage()
        
        self.title("IRUS Neural - Made by AsphaltCake")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.canvas = ctk.CTkCanvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.nodes = []
        self.particles = []
        self.connection_animations = {}
        self.animation_frame = 0
        
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.last_frame_time = None
        self.target_frame_time = 1000 / self.ANIMATION_FPS
        
        self.current_menu = "main"
        self.transition_progress = 0
        self.transition_target = None
        self.transition_duration = 600
        self.transition_origin = None
        
        self.hotkeys = self._load_hotkeys_from_storage()
        self.rebinding_key = None
        
        self.quad_selector = None
        
        self.bot_running = False
        self.bot_thread = None
        self.bot_stop_event = None
        self.bot_minimized_gui = False
        self.bot_focused_roblox = False
        self.discord_loop_counter = 0
        
        self.dragging_slider = None
        
        self.dropdown_open = None
        
        self.cast_rod_dropdown_open = False
        self.cast_bag_dropdown_open = False
        
        self.fish_rod_model_dropdown_open = False
        
        self.fish_controller = None
        
        self.active_text_input = None
        self.text_input_cursor_visible = True
        self.text_input_cursor_blink_id = None
        
        self.menu_scroll_offset = 0
        self.menu_content_height = 700
        
        self._apply_gui_settings()
        
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_mouse_click)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        
        self.keyboard_listener = keyboard.Listener(on_press=self._on_global_key_press)
        self.keyboard_listener.start()
        
        self.bind("<KeyPress>", self._on_key_press)
        
        self.after(100, self.initialize_nodes)
    
    def _apply_gui_settings(self):
        always_on_top = self.storage.get_gui_setting("always_on_top")
        self.attributes("-topmost", always_on_top)
    
    def _load_hotkeys_from_storage(self):
        hotkeys = {}
        for key_name in ["start_stop", "change_area", "exit"]:
            key_str = self.storage.get_hotkey(key_name)
            hotkeys[key_name] = self._string_to_key(key_str)
        return hotkeys
    
    def _string_to_key(self, key_str):
        key_str = key_str.lower()
        
        if key_str.startswith('f') and key_str[1:].isdigit():
            f_num = int(key_str[1:])
            if 1 <= f_num <= 20:
                return getattr(keyboard.Key, key_str)
        
        special_keys = ['alt', 'alt_l', 'alt_r', 'ctrl', 'ctrl_l', 'ctrl_r', 
                       'shift', 'shift_l', 'shift_r', 'cmd', 'cmd_l', 'cmd_r',
                       'esc', 'tab', 'caps_lock', 'space', 'enter', 'backspace',
                       'delete', 'home', 'end', 'page_up', 'page_down',
                       'up', 'down', 'left', 'right', 'insert']
        
        if key_str in special_keys:
            return getattr(keyboard.Key, key_str)
        
        if len(key_str) == 1:
            return keyboard.KeyCode.from_char(key_str)
        
        return keyboard.Key.f3
    
    def _key_to_string(self, key):
        if hasattr(key, 'name'):
            return key.name.lower()
        elif hasattr(key, 'char') and key.char:
            return key.char.lower()
        else:
            return str(key).lower()

    def _on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
        
        if self.current_menu == "main":
            for node in self.nodes:
                if node.is_main:
                    if node.is_point_inside(self.mouse_x, self.mouse_y):
                        node.is_frozen = True
                    else:
                        node.is_frozen = False
    
    def _on_mouse_click(self, event):
        click_x = event.x
        click_y = event.y
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if self.current_menu == "transitioning":
            return
        
        if self.current_menu == "main":
            for node in self.nodes:
                if node.is_main:
                    if node.is_point_inside(click_x, click_y):
                        self.current_menu = "transitioning"
                        self.transition_target = node.label.lower()
                        self.transition_progress = 0
                        self.transition_origin = (node.x, node.y)
                        self.menu_scroll_offset = 0
                        return
        elif self.current_menu in ["basic", "cast", "shake", "fish", "discord"]:
            if self._is_click_on_back_button(click_x, click_y):
                self.current_menu = "main"
                self.menu_scroll_offset = 0
                return
            
            nav_target = self._check_nav_buttons(click_x, click_y, self.current_menu)
            if nav_target:
                self.current_menu = nav_target
                self.menu_scroll_offset = 0
                return
            
            if self.current_menu == "basic":
                rebind_key = self._check_rebind_buttons(click_x, click_y)
                if rebind_key:
                    self.rebinding_key = rebind_key
                    return
                
                checkbox = self._check_checkboxes(click_x, click_y)
                if checkbox:
                    self._toggle_checkbox(checkbox)
                    return
                
                self._check_slider_click(click_x, click_y)
            
            if self.current_menu == "cast":
                self._check_cast_buttons(click_x, click_y)
                self._check_cast_anti_nuke_elements(click_x, click_y)
            
            if self.current_menu == "shake":
                self._check_shake_dropdown(click_x, click_y)
                self._check_shake_pixel_controls(click_x, click_y)
            
            if self.current_menu == "fish":
                self._check_fish_elements(click_x, click_y)
            
            if self.current_menu == "discord":
                self._check_discord_elements(click_x, click_y)
    
    def _is_click_on_back_button(self, x, y):
        button_x = 20
        button_y = 20
        button_width = 80
        button_height = 30
        
        return (button_x <= x <= button_x + button_width and 
                button_y <= y <= button_y + button_height)
    
    def _check_nav_buttons(self, x, y, current_menu):
        button_y = 20
        button_height = 30
        
        back_button_width = 80
        nav_button_x = 20 + back_button_width + 20
        nav_button_width = 70
        nav_button_spacing = 10
        
        all_menus = ["basic", "cast", "shake", "fish", "discord"]
        other_menus = [m for m in all_menus if m != current_menu]
        
        for i, menu in enumerate(other_menus):
            current_x = nav_button_x + i * (nav_button_width + nav_button_spacing)
            
            if (current_x <= x <= current_x + nav_button_width and
                button_y <= y <= button_y + button_height):
                return menu
        
        return None
    
    def _check_rebind_buttons(self, x, y):
        margin_left = 50
        base_x = margin_left + 400
        rebind_width = 80
        rebind_height = 30
        
        adjusted_y = y + self.menu_scroll_offset
        
        options = [
            ("start_stop", 200),
            ("change_area", 250),
            ("exit", 300)
        ]
        
        for key_name, y_pos in options:
            if (base_x <= x <= base_x + rebind_width and
                y_pos <= adjusted_y <= y_pos + rebind_height):
                return key_name
        
        return None
    
    def _check_checkboxes(self, x, y):
        margin_left = 50
        checkbox_x = margin_left
        checkbox_size = 20
        
        adjusted_y = y + self.menu_scroll_offset
        
        checkboxes = [
            ("always_on_top", 380),
            ("auto_minimize", 430),
            ("auto_focus_roblox", 480)
        ]
        
        for setting_name, y_pos in checkboxes:
            if (checkbox_x <= x <= checkbox_x + checkbox_size and
                y_pos <= adjusted_y <= y_pos + checkbox_size):
                return setting_name
        
        return None
    
    def _toggle_checkbox(self, setting_name):
        new_value = self.storage.toggle_gui_setting(setting_name)
        
        if setting_name == "always_on_top":
            self.attributes("-topmost", new_value)
            print(f"Always On Top: {'Enabled' if new_value else 'Disabled'}")
        elif setting_name == "auto_minimize":
            print(f"Auto Minimize: {'Enabled' if new_value else 'Disabled'}")
        elif setting_name == "auto_focus_roblox":
            print(f"Auto Focus Roblox: {'Enabled' if new_value else 'Disabled'}")
    
    def _check_slider_click(self, x, y):
        margin_left = 50
        slider_x = margin_left
        slider_width = 300
        slider_y_start = 550
        slider_height = 10
        
        adjusted_y = y + self.menu_scroll_offset
        
        tolerance_y = slider_y_start + 25
        if (slider_x <= x <= slider_x + slider_width and
            tolerance_y - 8 <= adjusted_y <= tolerance_y + slider_height + 8):
            self.dragging_slider = "friend_color_tolerance"
            self._update_slider_value(x, "friend_color_tolerance")
            return
        
        timeout_y = slider_y_start + 60 + 25
        if (slider_x <= x <= slider_x + slider_width and
            timeout_y - 8 <= adjusted_y <= timeout_y + slider_height + 8):
            self.dragging_slider = "state_check_timeout"
            self._update_slider_value(x, "state_check_timeout")
            return
    
    def _on_mouse_drag(self, event):
        if self.dragging_slider and self.current_menu == "basic":
            self._update_slider_value(event.x, self.dragging_slider)
    
    def _on_mouse_release(self, event):
        self.dragging_slider = None
    
    def _update_slider_value(self, x, slider_name):
        margin_left = 50
        slider_x = margin_left
        slider_width = 300
        
        progress = (x - slider_x) / slider_width
        progress = max(0.0, min(1.0, progress))
        
        if slider_name == "friend_color_tolerance":
            new_value = int(progress * 20)
            self.storage.set_gui_setting("friend_color_tolerance", new_value)
            print(f"Friend Color Tolerance: {new_value}")
        elif slider_name == "state_check_timeout":
            new_value = round(progress * 10.0, 1)
            self.storage.set_gui_setting("state_check_timeout", new_value)
            print(f"State Check Timeout: {new_value:.1f}s")
    
    def _check_shake_dropdown(self, x, y):
        margin_left = 50
        dropdown_x = margin_left + 180
        dropdown_width = 150
        dropdown_height = 35
        dropdown_y = 180
        
        adjusted_y = y + self.menu_scroll_offset
        
        if (dropdown_x <= x <= dropdown_x + dropdown_width and
            dropdown_y <= adjusted_y <= dropdown_y + dropdown_height):
            if self.dropdown_open == "shake_method":
                self.dropdown_open = None
            else:
                self.dropdown_open = "shake_method"
            return
        
        if self.dropdown_open == "shake_method":
            options = ["Pixel", "Navigation"]
            option_height = 30
            
            for i, option in enumerate(options):
                option_y = dropdown_y + dropdown_height + i * option_height
                
                if (dropdown_x <= x <= dropdown_x + dropdown_width and
                    option_y <= adjusted_y <= option_y + option_height):
                    self.storage.set_shake_setting("shake_method", option)
                    self.dropdown_open = None
                    print(f"Shake Method: {option}")
                    return
            
            self.dropdown_open = None
    
    def _check_shake_pixel_controls(self, x, y):
        if self.storage.get_shake_setting("shake_method") != "Pixel":
            return
        
        margin_left = 50
        adjusted_y = y + self.menu_scroll_offset
        
        content_y = 280
        current_y = content_y + 50
        line_height = 60
        control_x = margin_left + 350
        button_width = 30
        button_height = 25
        box_width = 80
        
        controls = [
            ("friend_color_tolerance", 1, 0, 255),
            ("white_color_tolerance", 1, 0, 255),
            ("duplicate_pixel_bypass", 0.1, 0.0, 60.0),
            ("fail_shake_timeout", 0.5, 0.0, 60.0),
            None,
            ("double_click_delay", 5, 1, 1000)
        ]
        
        for control in controls:
            if control is None:
                current_y += line_height
                continue
            
            setting_name, increment, min_val, max_val = control
            
            minus_x = control_x - button_width - 10
            plus_x = control_x + box_width + 10
            button_y_top = current_y - button_height / 2
            button_y_bottom = current_y + button_height / 2
            
            if (minus_x <= x <= minus_x + button_width and
                button_y_top <= adjusted_y <= button_y_bottom):
                current_value = self.storage.get_shake_setting(setting_name)
                new_value = max(min_val, current_value - increment)
                self.storage.set_shake_setting(setting_name, new_value)
                print(f"{setting_name}: {new_value}")
                return
            
            if (plus_x <= x <= plus_x + button_width and
                button_y_top <= adjusted_y <= button_y_bottom):
                current_value = self.storage.get_shake_setting(setting_name)
                new_value = min(max_val, current_value + increment)
                self.storage.set_shake_setting(setting_name, new_value)
                print(f"{setting_name}: {new_value}")
                return
            
            current_y += line_height
        
        checkbox_y = content_y + 50 + line_height * 4
        checkbox_size = 20
        checkbox_x = margin_left
        
        if (checkbox_x <= x <= checkbox_x + checkbox_size and
            checkbox_y <= adjusted_y <= checkbox_y + checkbox_size):
            current = self.storage.get_shake_setting("double_click")
            self.storage.set_shake_setting("double_click", not current)
            print(f"Double Click: {'Enabled' if not current else 'Disabled'}")
            return
    
    
    def _check_fish_elements(self, x, y):
        margin_left = 50
        control_x = margin_left + 440
        button_width = 30
        button_height = 25
        adjusted_y = y + self.menu_scroll_offset
        
        dropdown_x = margin_left + 150
        dropdown_width = 200
        dropdown_height = 35
        
        current_y = 180
        if (dropdown_x <= x <= dropdown_x + dropdown_width and
            current_y <= adjusted_y <= current_y + dropdown_height):
            self.fish_rod_model_dropdown_open = not self.fish_rod_model_dropdown_open
            return
        
        if self.fish_rod_model_dropdown_open:
            import os
            import sys
            
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
            
            model_files = [f for f in os.listdir(current_dir) if f.endswith('.pt')]
            if not model_files:
                model_files = ["No Models Found"]
            
            option_height = 30
            for i, model in enumerate(model_files):
                option_y = current_y + dropdown_height + 5 + (i * option_height)
                if (dropdown_x <= x <= dropdown_x + dropdown_width and
                    option_y <= adjusted_y <= option_y + option_height):
                    self.storage.set_fish_setting("rod_model", model)
                    self.fish_rod_model_dropdown_open = False
                    print(f"[Fish] Selected model: {model}")
                    return
        
        current_y = 180 + 70 + 10
        
        def check_plus_minus_buttons(y_pos, setting_name, increment, min_val=None, max_val=None, is_decimal=False):
            box_width = 80
            minus_x = control_x - button_width - 10
            plus_x = control_x + box_width + 10
            
            if (minus_x <= x <= minus_x + button_width and
                y_pos - button_height/2 <= adjusted_y <= y_pos + button_height/2):
                current_val = self.storage.get_fish_setting(setting_name)
                new_val = current_val - increment
                if is_decimal:
                    new_val = round(new_val * 20) / 20
                if min_val is not None:
                    new_val = max(min_val, new_val)
                if max_val is not None:
                    new_val = min(max_val, new_val)
                self.storage.set_fish_setting(setting_name, new_val)
                print(f"[Fish] {setting_name}: {new_val}")
                return True
            
            if (plus_x <= x <= plus_x + button_width and
                y_pos - button_height/2 <= adjusted_y <= y_pos + button_height/2):
                current_val = self.storage.get_fish_setting(setting_name)
                new_val = current_val + increment
                if is_decimal:
                    new_val = round(new_val * 20) / 20
                if min_val is not None:
                    new_val = max(min_val, new_val)
                if max_val is not None:
                    new_val = min(max_val, new_val)
                self.storage.set_fish_setting(setting_name, new_val)
                print(f"[Fish] {setting_name}: {new_val}")
                return True
            
            return False
        
        if check_plus_minus_buttons(current_y + 10, "tolerance_pixels", 1, min_val=0, max_val=50):
            return
        current_y += 70
        
        if check_plus_minus_buttons(current_y + 10, "accel_init", 10, min_val=10, max_val=500):
            return
        current_y += 70
        
        if check_plus_minus_buttons(current_y + 10, "max_velocity_init", 50, min_val=100, max_val=5000):
            return
        current_y += 70
        
        if check_plus_minus_buttons(current_y + 10, "smoothing", 1, min_val=1, max_val=10):
            return
        current_y += 70
        
        if check_plus_minus_buttons(current_y + 10, "learning_rate", 0.05, min_val=0.50, max_val=0.99, is_decimal=True):
            return
        
        self.fish_rod_model_dropdown_open = False
    
    def _check_discord_elements(self, x, y):
        margin_left = 50
        adjusted_y = y + self.menu_scroll_offset
        
        checkbox_y = 180
        checkbox_size = 20
        if (margin_left <= x <= margin_left + checkbox_size and
            checkbox_y <= adjusted_y <= checkbox_y + checkbox_size):
            is_active = self.storage.toggle_discord_active()
            print(f"Discord Active: {'Enabled' if is_active else 'Disabled'}")
            return
        
        input_x = margin_left
        input_y = 270
        input_width = 400
        input_height = 30
        if (input_x <= x <= input_x + input_width and
            input_y <= adjusted_y <= input_y + input_height):
            self.active_text_input = "webhook_url"
            self._start_cursor_blink()
            return
        
        test_button_x = input_x + input_width + 20
        test_button_width = 80
        test_button_height = 30
        if (test_button_x <= x <= test_button_x + test_button_width and
            input_y <= adjusted_y <= input_y + test_button_height):
            self._test_discord_webhook()
            return
        
        loops_input_x = margin_left + 220
        loops_input_y = 335
        loops_input_width = 80
        loops_input_height = 30
        if (loops_input_x <= x <= loops_input_x + loops_input_width and
            loops_input_y <= adjusted_y <= loops_input_y + loops_input_height):
            self.active_text_input = "loops_per_screenshot"
            self._start_cursor_blink()
            return
        
        if self.active_text_input:
            self.active_text_input = None
            self._stop_cursor_blink()
    
    def _on_key_press(self, event):
        if not self.active_text_input or self.current_menu != "discord":
            return
        
        if self.active_text_input == "webhook_url":
            current_url = self.storage.get_discord_setting("webhook_url")
            
            if event.keysym == "BackSpace":
                new_url = current_url[:-1] if current_url else ""
                self.storage.set_discord_setting("webhook_url", new_url)
            elif event.keysym == "Return":
                self.active_text_input = None
                self._stop_cursor_blink()
            elif len(event.char) == 1 and event.char.isprintable():
                new_url = current_url + event.char
                self.storage.set_discord_setting("webhook_url", new_url)
        
        elif self.active_text_input == "loops_per_screenshot":
            current_loops = str(self.storage.get_discord_setting("loops_per_screenshot"))
            
            if event.keysym == "BackSpace":
                new_loops = current_loops[:-1] if len(current_loops) > 1 else "0"
                self.storage.set_discord_setting("loops_per_screenshot", int(new_loops))
            elif event.keysym == "Return":
                self.active_text_input = None
                self._stop_cursor_blink()
            elif event.char.isdigit():
                new_loops = current_loops + event.char
                if int(new_loops) <= 9999:
                    self.storage.set_discord_setting("loops_per_screenshot", int(new_loops))
    
    def _start_cursor_blink(self):
        self._stop_cursor_blink()
        self.text_input_cursor_visible = True
        self._cursor_blink()
    
    def _stop_cursor_blink(self):
        if self.text_input_cursor_blink_id:
            self.after_cancel(self.text_input_cursor_blink_id)
            self.text_input_cursor_blink_id = None
    
    def _cursor_blink(self):
        self.text_input_cursor_visible = not self.text_input_cursor_visible
        self.text_input_cursor_blink_id = self.after(500, self._cursor_blink)
    
    def _test_discord_webhook(self):
        webhook_url = self.storage.get_discord_setting("webhook_url")
        if not webhook_url:
            print("Discord Test: No webhook URL provided")
            return
        
        print(f"Testing Discord webhook: {webhook_url[:50]}...")
        
        try:
            import requests
            import mss
            from PIL import Image
            import io
            
            print("Discord Test: Taking screenshot...")
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {
                'file': ('test_screenshot.png', img_bytes, 'image/png')
            }
            
            data = {
                'content': 'Test screenshot from IRUS Neural'
            }
            
            print("Discord Test: Sending screenshot to webhook...")
            response = requests.post(webhook_url, files=files, data=data)
            
            if response.status_code == 204 or response.status_code == 200:
                print("Discord Test: Screenshot sent successfully ✓")
            else:
                print(f"Discord Test: Failed to send - Status code {response.status_code}")
                
        except ImportError as e:
            print(f"Discord Test: ERROR - Missing library: {e}")
            print("Install with: pip install requests mss pillow")
        except Exception as e:
            print(f"Discord Test: ERROR - {e}")
    
    def _check_cast_buttons(self, x, y):
        margin_left = 50
        box_x = margin_left + 100
        box_width = 200
        box_height = 50
        box_spacing = 30
        box_y_start = 180
        
        control_x = box_x + box_width + 80
        button_width = 30
        button_height = 25
        
        adjusted_y = y + self.menu_scroll_offset
        
        y1 = box_y_start
        y3 = y1 + (box_height + box_spacing) * 2
        y5 = y3 + (box_height + box_spacing) * 2
        
        delay_controls = [
            (y1 + 30, "delay_before_click", 0.1),
            (y3 + 30, "delay_hold_duration", 0.1),
            (y5 + 30, "delay_after_release", 0.1)
        ]
        
        for control_y, setting_name, increment in delay_controls:
            if (control_x <= x <= control_x + button_width and
                control_y <= adjusted_y <= control_y + button_height):
                current = self.storage.get_cast_setting(setting_name)
                new_value = max(0.0, round(current - increment, 1))
                self.storage.set_cast_setting(setting_name, new_value)
                print(f"{setting_name}: {new_value:.1f}s")
                return
            
            plus_x = control_x + button_width + 90
            if (plus_x <= x <= plus_x + button_width and
                control_y <= adjusted_y <= control_y + button_height):
                current = self.storage.get_cast_setting(setting_name)
                new_value = min(10.0, round(current + increment, 1))
                self.storage.set_cast_setting(setting_name, new_value)
                print(f"{setting_name}: {new_value:.1f}s")
                return
    
    def _check_cast_anti_nuke_elements(self, x, y):
        margin_left = 50
        adjusted_y = y + self.menu_scroll_offset
        
        box_x = margin_left + 100
        box_height = 50
        box_spacing = 30
        box_y_start = 180
        anti_nuke_y = box_y_start + (box_height + box_spacing) * 5 + 80
        checkbox_size = 20
        
        if (margin_left <= x <= margin_left + checkbox_size and
            anti_nuke_y <= adjusted_y <= anti_nuke_y + checkbox_size):
            is_active = self.storage.toggle_cast_anti_nuke()
            print(f"Anti Nuke: {'Enabled' if is_active else 'Disabled'}")
            self.cast_rod_dropdown_open = False
            self.cast_bag_dropdown_open = False
            return
        
        if self.storage.get_cast_setting("anti_nuke"):
            flow_y = anti_nuke_y + 60
            box_x_flow = box_x
            box_width = 200
            box_height_flow = 50
            control_x = box_x_flow + box_width + 80
            
            rod_y = flow_y + box_height_flow + box_spacing
            if (box_x_flow <= x <= box_x_flow + box_width and
                rod_y <= adjusted_y <= rod_y + box_height_flow):
                self.cast_rod_dropdown_open = not self.cast_rod_dropdown_open
                self.cast_bag_dropdown_open = False
                return
            
            if self.cast_rod_dropdown_open:
                option_height = 30
                dropdown_x = control_x + 200
                dropdown_width = 60
                for i in range(1, 10):
                    option_y = rod_y + (i - 1) * option_height
                    if (dropdown_x <= x <= dropdown_x + dropdown_width and
                        option_y <= adjusted_y <= option_y + option_height):
                        self.storage.set_cast_setting("anti_nuke_rod_slot", i)
                        self.cast_rod_dropdown_open = False
                        print(f"Anti Nuke Rod Slot: {i}")
                        return
            
            bag_y = flow_y + (box_height_flow + box_spacing) * 3
            if (box_x_flow <= x <= box_x_flow + box_width and
                bag_y <= adjusted_y <= bag_y + box_height_flow):
                self.cast_bag_dropdown_open = not self.cast_bag_dropdown_open
                self.cast_rod_dropdown_open = False
                return
            
            if self.cast_bag_dropdown_open:
                option_height = 30
                dropdown_x = control_x + 200
                dropdown_width = 60
                for i in range(1, 10):
                    option_y = bag_y + (i - 1) * option_height
                    if (dropdown_x <= x <= dropdown_x + dropdown_width and
                        option_y <= adjusted_y <= option_y + option_height):
                        self.storage.set_cast_setting("anti_nuke_bag_slot", i)
                        self.cast_bag_dropdown_open = False
                        print(f"Anti Nuke Bag Slot: {i}")
                        return
            
            button_width = 30
            button_height = 25
            
            delay_controls = [
                (flow_y + 30, "anti_nuke_delay_before", 0.1),
                (flow_y + (box_height_flow + box_spacing) * 2 + 30, "anti_nuke_delay_after_rod", 0.1),
                (flow_y + (box_height_flow + box_spacing) * 4 + 30, "anti_nuke_delay_after_bag", 0.1)
            ]
            
            for control_y, setting_name, increment in delay_controls:
                if (control_x <= x <= control_x + button_width and
                    control_y <= adjusted_y <= control_y + button_height):
                    current = self.storage.get_cast_setting(setting_name)
                    new_value = max(0.0, round(current - increment, 1))
                    self.storage.set_cast_setting(setting_name, new_value)
                    print(f"{setting_name}: {new_value:.1f}s")
                    return
                
                plus_x = control_x + button_width + 90
                if (plus_x <= x <= plus_x + button_width and
                    control_y <= adjusted_y <= control_y + button_height):
                    current = self.storage.get_cast_setting(setting_name)
                    new_value = min(10.0, round(current + increment, 1))
                    self.storage.set_cast_setting(setting_name, new_value)
                    print(f"{setting_name}: {new_value:.1f}s")
                    return
        
        self.cast_rod_dropdown_open = False
        self.cast_bag_dropdown_open = False
    
    def _on_mouse_wheel(self, event):
        if self.current_menu in ["basic", "cast", "shake", "fish", "discord"]:
            scroll_amount = -30 if event.delta > 0 else 30
            
            self.menu_scroll_offset += scroll_amount
            
            content_height = 700
            if self.current_menu == "cast":
                content_height = 700
                if self.storage.get_cast_setting("anti_nuke"):
                    content_height = 1400
            
            max_scroll = max(0, content_height - self.WINDOW_HEIGHT + 100)
            self.menu_scroll_offset = max(0, min(max_scroll, self.menu_scroll_offset))
    
    def _on_global_key_press(self, key):
        if self.rebinding_key:
            self.hotkeys[self.rebinding_key] = key
            key_str = self._key_to_string(key)
            self.storage.set_hotkey(self.rebinding_key, key_str)
            self.rebinding_key = None
            return
        
        if key == self.hotkeys["start_stop"]:
            self.after(0, self._toggle_bot_loop)
        elif key == self.hotkeys["change_area"]:
            self.after(0, self._toggle_quad_selector)
        elif key == self.hotkeys["exit"]:
            self._exit_application()
    
    def _toggle_quad_selector(self):
        if self.quad_selector is not None:
            self._save_and_close_quad_selector()
        else:
            if self.storage.get_gui_setting("auto_minimize"):
                self.iconify()
                self.after(200, self._open_quad_selector_after_minimize)
            else:
                self._open_quad_selector()
    
    def _open_quad_selector_after_minimize(self):
        self._open_quad_selector()
    
    def _open_quad_selector(self):
        try:
            screenshot = ImageGrab.grab()
            
            friend_box = self.storage.get_quad_box('friend_box')
            shake_box = self.storage.get_quad_box('shake_box')
            detection_box = self.storage.get_quad_box('detection_box')
            
            self.quad_selector = QuadAreaSelector(
                self,
                screenshot,
                friend_box,
                shake_box,
                detection_box,
                self._on_quad_selection_complete
            )
            
            print("QuadAreaSelector opened - Use mouse to adjust boxes, press hotkey again to save and close")
        except Exception as e:
            print(f"Error opening QuadAreaSelector: {e}")
    
    def _save_and_close_quad_selector(self):
        if self.quad_selector is not None:
            try:
                friend_box = self.quad_selector.boxes['friend']['coords']
                shake_box = self.quad_selector.boxes['shake']['coords']
                detection_box = self.quad_selector.boxes['detection']['coords']
                
                self.quad_selector.window.destroy()
                self.quad_selector = None
                
                self.storage.set_quad_boxes(friend_box, shake_box, detection_box)
                print("Quad areas saved and closed!")
                print(f"FriendBox: {friend_box}")
                print(f"ShakeBox: {shake_box}")
                print(f"DetectionBox: {detection_box}")
                
                if self.storage.get_gui_setting("auto_minimize"):
                    self.deiconify()
                    self.lift()
                    print("GUI restored")
            except Exception as e:
                print(f"Error saving quad selector: {e}")
                self.quad_selector = None
                if self.storage.get_gui_setting("auto_minimize"):
                    self.deiconify()
    
    def _on_quad_selection_complete(self, friend_box, shake_box, detection_box):
        self.quad_selector = None
    
    def _toggle_bot_loop(self):
        if self.bot_running:
            self._stop_bot_loop()
        else:
            self._start_bot_loop()
    
    def _start_bot_loop(self):
        if not self.bot_running:
            self.bot_running = True
            self.storage.set_state("is_running", True)
            self.bot_minimized_gui = False
            self.bot_focused_roblox = False
            self.discord_loop_counter = 0
            print("Bot started - Running loop: on_start > cast > shake > fish > discord")
            
            import threading
            self.bot_stop_event = threading.Event()
            
            self.bot_thread = threading.Thread(target=self._bot_loop_worker, daemon=True)
            self.bot_thread.start()
    
    def _stop_bot_loop(self):
        if self.bot_running:
            self.bot_running = False
            self.storage.set_state("is_running", False)
            
            if self.bot_stop_event:
                self.bot_stop_event.set()
            
            if self.bot_minimized_gui:
                self.after(100, self._restore_gui_after_bot)
            
            print("Bot stopped")
    
    def _restore_gui_after_bot(self):
        self.deiconify()
        self.lift()
        self.bot_minimized_gui = False
        print("GUI restored")
    
    def _bot_loop_worker(self):
        import time
        
        while self.bot_running:
            try:
                if self.bot_stop_event.is_set():
                    break
                print("[Bot] Executing: on_start")
                self._execute_on_start()
                
                if self.bot_stop_event.is_set():
                    break
                print("[Bot] Executing: cast")
                self._execute_cast()
                
                if self.bot_stop_event.is_set():
                    break
                print("[Bot] Executing: shake")
                self._execute_shake()
                
                if self.bot_stop_event.is_set():
                    break
                print("[Bot] Executing: fish")
                self._execute_fish()
                
                if self.bot_stop_event.is_set():
                    break
                print("[Bot] Executing: discord")
                self._execute_discord()
                
                if self.bot_running and not self.bot_stop_event.is_set():
                    print("[Bot] Loop cycle completed, restarting...")
                
            except Exception as e:
                print(f"[Bot] Error in loop: {e}")
                self.bot_running = False
                self.storage.set_state("is_running", False)
                break
    
    def _should_stop(self):
        return self.bot_stop_event and self.bot_stop_event.is_set()
    
    def _interruptible_sleep(self, duration):
        if self.bot_stop_event:
            self.bot_stop_event.wait(duration)
    
    def _execute_on_start(self):
        if not self.bot_minimized_gui and self.storage.get_gui_setting("auto_minimize"):
            self.after(0, self._minimize_gui_for_bot)
            self.bot_minimized_gui = True
            self._interruptible_sleep(0.2)
        
        if not self.bot_focused_roblox and self.storage.get_gui_setting("auto_focus_roblox"):
            self._focus_roblox_window()
            self.bot_focused_roblox = True
    
    def _minimize_gui_for_bot(self):
        self.iconify()
        print("GUI minimized for bot operation")
    
    def _focus_roblox_window(self):
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd).lower()
                    if 'roblox' in window_title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                roblox_hwnd = windows[0]
                
                if win32gui.IsIconic(roblox_hwnd):
                    win32gui.ShowWindow(roblox_hwnd, win32con.SW_RESTORE)
                
                win32gui.SetForegroundWindow(roblox_hwnd)
                print("Roblox window focused")
            else:
                print("Roblox window not found")
        except Exception as e:
            print(f"Error focusing Roblox: {e}")
    
    def _execute_cast(self):
        self._wait_for_friend_color()
        
        if self.storage.get_cast_setting("anti_nuke"):
            self._execute_cast_anti_nuke()
        
        self._execute_cast_regular()
    
    def _wait_for_friend_color(self):
        print("[Cast] Checking for friend color before casting...")
        
        friend_box_dict = self.storage.get_quad_box('friend_box')
        
        friend_box = (friend_box_dict["x1"], friend_box_dict["y1"], friend_box_dict["x2"], friend_box_dict["y2"])
        
        try:
            import dxcam
            import numpy as np
            
            camera = dxcam.create(region=friend_box)
            camera.start(target_fps=60)
            
            friend_color = np.array(self.storage.get_shake_setting("friend_color"), dtype=np.uint8)
            friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
            
            print(f"[Cast] Waiting for friend color RGB{tuple(friend_color)} with tolerance {friend_tolerance}...")
            
            while self.bot_running and not self._should_stop():
                frame = camera.get_latest_frame()
                
                if frame is not None:
                    friend_color_found = np.any(
                        np.all(np.abs(frame - friend_color) <= friend_tolerance, axis=-1)
                    )
                    
                    if friend_color_found:
                        print("[Cast] Friend color detected - proceeding with cast")
                        break
                
                self._interruptible_sleep(0.1)
            
            camera.stop()
            camera.release()
            
        except ImportError:
            print("[Cast] WARNING: dxcam not installed - skipping friend color check")
        except Exception as e:
            print(f"[Cast] ERROR during friend color check: {e}")
    
    def _execute_cast_anti_nuke(self):
        print("[Cast] Anti Nuke is enabled - Executing Anti Nuke sequence")
        
        delay_before = self.storage.get_cast_setting("anti_nuke_delay_before")
        rod_slot = self.storage.get_cast_setting("anti_nuke_rod_slot")
        delay_after_rod = self.storage.get_cast_setting("anti_nuke_delay_after_rod")
        bag_slot = self.storage.get_cast_setting("anti_nuke_bag_slot")
        delay_after_bag = self.storage.get_cast_setting("anti_nuke_delay_after_bag")
        
        if self._should_stop():
            return
        print(f"[Cast] Anti Nuke: Waiting {delay_before:.1f}s before selecting rod")
        self._interruptible_sleep(delay_before)
        
        if self._should_stop():
            return
        print(f"[Cast] Anti Nuke: Pressing key '{rod_slot}' (Rod slot)")
        self._press_key(str(rod_slot))
        
        if self._should_stop():
            return
        print(f"[Cast] Anti Nuke: Waiting {delay_after_rod:.1f}s after rod selection")
        self._interruptible_sleep(delay_after_rod)
        
        if self._should_stop():
            return
        print(f"[Cast] Anti Nuke: Pressing key '{bag_slot}' (Bag slot)")
        self._press_key(str(bag_slot))
        
        if self._should_stop():
            return
        print(f"[Cast] Anti Nuke: Waiting {delay_after_bag:.1f}s after bag selection")
        self._interruptible_sleep(delay_after_bag)
        
        print("[Cast] Anti Nuke sequence completed")
    
    def _execute_cast_regular(self):
        print("[Cast] Executing regular cast sequence")
        
        delay_before = self.storage.get_cast_setting("delay_before_click")
        delay_hold = self.storage.get_cast_setting("delay_hold_duration")
        delay_after = self.storage.get_cast_setting("delay_after_release")
        
        if self._should_stop():
            return
        print(f"[Cast] Waiting {delay_before:.1f}s before clicking")
        self._interruptible_sleep(delay_before)
        
        if self._should_stop():
            return
        print("[Cast] Holding left mouse button")
        self._mouse_down()
        
        if self._should_stop():
            self._mouse_up()
            return
        print(f"[Cast] Holding for {delay_hold:.1f}s")
        self._interruptible_sleep(delay_hold)
        
        if self._should_stop():
            return
        print("[Cast] Releasing left mouse button")
        self._mouse_up()
        
        if self._should_stop():
            return
        print(f"[Cast] Waiting {delay_after:.1f}s after release")
        self._interruptible_sleep(delay_after)
        
        print("[Cast] Cast sequence completed")
    
    def _execute_shake(self):
        shake_method = self.storage.get_shake_setting("shake_method")
        
        if shake_method == "Pixel":
            self._execute_shake_pixel()
        elif shake_method == "Navigation":
            self._execute_shake_navigation()
        else:
            print(f"[Shake] Unknown method: {shake_method}")
    
    def _execute_shake_pixel(self):
        print("[Shake] Starting shake detection (Pixel mode)")
        
        friend_box_dict = self.storage.get_quad_box('friend_box')
        shake_box_dict = self.storage.get_quad_box('shake_box')
        
        friend_box = (friend_box_dict["x1"], friend_box_dict["y1"], friend_box_dict["x2"], friend_box_dict["y2"])
        shake_box = (shake_box_dict["x1"], shake_box_dict["y1"], shake_box_dict["x2"], shake_box_dict["y2"])
        
        shake_area_x1 = min(friend_box[0], shake_box[0])
        shake_area_y1 = min(friend_box[1], shake_box[1])
        shake_area_x2 = max(friend_box[2], shake_box[2])
        shake_area_y2 = max(friend_box[3], shake_box[3])
        
        shake_area = (shake_area_x1, shake_area_y1, shake_area_x2, shake_area_y2)
        
        print(f"[Shake] Shake area: {shake_area}")
        print(f"[Shake]   Friend box: {friend_box}")
        print(f"[Shake]   Shake box: {shake_box}")
        
        try:
            import dxcam
            camera = dxcam.create(region=shake_area)
            print("[Shake] dxcam camera created successfully")
            
            camera.start(target_fps=60)
            print("[Shake] Video capture started (60 FPS)")
            
            friend_box_relative = (
                friend_box[0] - shake_area_x1,
                friend_box[1] - shake_area_y1,
                friend_box[2] - shake_area_x1,
                friend_box[3] - shake_area_y1
            )
            
            shake_box_relative = (
                shake_box[0] - shake_area_x1,
                shake_box[1] - shake_area_y1,
                shake_box[2] - shake_area_x1,
                shake_box[3] - shake_area_y1
            )
            
            print(f"[Shake] Relative friend box: {friend_box_relative}")
            print(f"[Shake] Relative shake box: {shake_box_relative}")
            
            import numpy as np
            friend_color = np.array(self.storage.get_shake_setting("friend_color"), dtype=np.uint8)
            friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
            shake_color = np.array(self.storage.get_shake_setting("shake_color"), dtype=np.uint8)
            white_tolerance = self.storage.get_shake_setting("white_color_tolerance")
            
            print(f"[Shake] Friend color: RGB{tuple(friend_color)}")
            print(f"[Shake] Friend color tolerance: {friend_tolerance}")
            print(f"[Shake] Shake color: RGB{tuple(shake_color)}")
            print(f"[Shake] White color tolerance: {white_tolerance}")
            
            fail_shake_timeout = self.storage.get_shake_setting("fail_shake_timeout")
            duplicate_pixel_bypass = self.storage.get_shake_setting("duplicate_pixel_bypass")
            double_click = self.storage.get_shake_setting("double_click")
            double_click_delay = self.storage.get_shake_setting("double_click_delay")
            print(f"[Shake] Fail shake timeout: {fail_shake_timeout:.1f}s")
            print(f"[Shake] Duplicate pixel bypass: {duplicate_pixel_bypass:.1f}s")
            print(f"[Shake] Double click: {'Enabled' if double_click else 'Disabled'}")
            if double_click:
                print(f"[Shake] Double click delay: {double_click_delay}ms")
            
            import time
            import win32api
            import win32con
            timeout_start = None
            timeout_duration = fail_shake_timeout
            
            last_white_pixel = None
            duplicate_start = None
            duplicate_duration = duplicate_pixel_bypass
            
            while self.bot_running and not self._should_stop():
                frame = camera.get_latest_frame()
                
                if frame is not None:
                    friend_area = frame[
                        friend_box_relative[1]:friend_box_relative[3],
                        friend_box_relative[0]:friend_box_relative[2]
                    ]
                    
                    shake_area_crop = frame[
                        shake_box_relative[1]:shake_box_relative[3],
                        shake_box_relative[0]:shake_box_relative[2]
                    ]
                    
                    friend_color_found = np.any(
                        np.all(np.abs(friend_area - friend_color) <= friend_tolerance, axis=-1)
                    )
                    
                    if not friend_color_found:
                        print("[Shake] Friend color disappeared - PASS: Continuing to fish")
                        break
                    
                    print("[Shake] Friend color detected - searching for shake pixel")
                    
                    white_matches = np.all(np.abs(shake_area_crop - shake_color) <= white_tolerance, axis=-1)
                    
                    white_coords = np.argwhere(white_matches)
                    
                    if len(white_coords) > 0:
                        first_white = white_coords[0]
                        white_y, white_x = first_white[0], first_white[1]
                        
                        absolute_x = shake_area_x1 + shake_box_relative[0] + white_x
                        absolute_y = shake_area_y1 + shake_box_relative[1] + white_y
                        
                        current_white_pixel = (absolute_x, absolute_y)
                        
                        print(f"[Shake] White pixel found at relative position: ({white_x}, {white_y})")
                        print(f"[Shake] Absolute screen position: ({absolute_x}, {absolute_y})")
                        
                        if last_white_pixel != current_white_pixel:
                            print(f"[Shake] New white pixel detected - moving mouse and clicking")
                            
                            win32api.SetCursorPos((absolute_x, absolute_y))
                            print(f"[Shake] Mouse moved to ({absolute_x}, {absolute_y})")
                            
                            current_pos = win32api.GetCursorPos()
                            win32api.SetCursorPos((current_pos[0], current_pos[1] + 1))
                            print(f"[Shake] Mouse moved down 1px relative")
                            
                            if double_click:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                print(f"[Shake] First click")
                                
                                self._interruptible_sleep(double_click_delay / 1000.0)
                                
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                print(f"[Shake] Second click (double click)")
                            else:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                print(f"[Shake] Single click")
                            
                            last_white_pixel = current_white_pixel
                            duplicate_start = None
                            
                        else:
                            if duplicate_start is None:
                                duplicate_start = time.time()
                                print(f"[Shake] Same pixel detected - starting duplicate bypass timer ({duplicate_duration:.1f}s)")
                            else:
                                elapsed = time.time() - duplicate_start
                                remaining = duplicate_duration - elapsed
                                
                                if elapsed >= duplicate_duration:
                                    print(f"[Shake] Duplicate bypass timer expired - moving mouse and clicking again")
                                    
                                    win32api.SetCursorPos((absolute_x, absolute_y))
                                    print(f"[Shake] Mouse moved to ({absolute_x}, {absolute_y})")
                                    
                                    current_pos = win32api.GetCursorPos()
                                    win32api.SetCursorPos((current_pos[0], current_pos[1] + 1))
                                    print(f"[Shake] Mouse moved down 1px relative")
                                    
                                    if double_click:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        print(f"[Shake] First click")
                                        
                                        self._interruptible_sleep(double_click_delay / 1000.0)
                                        
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        print(f"[Shake] Second click (double click)")
                                    else:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        print(f"[Shake] Single click")
                                    
                                    duplicate_start = time.time()
                                    print(f"[Shake] Duplicate bypass timer reset")
                                else:
                                    if int(remaining) != int(remaining + 0.001):
                                        print(f"[Shake] Same pixel - bypass in {remaining:.1f}s")
                        
                        if timeout_start is not None:
                            print("[Shake] White pixel found - resetting fail timeout")
                        timeout_start = None
                    else:
                        if timeout_start is None:
                            timeout_start = time.time()
                            print(f"[Shake] White pixel not found - starting fail timeout ({timeout_duration:.1f}s)")
                        else:
                            elapsed = time.time() - timeout_start
                            remaining = timeout_duration - elapsed
                            
                            if elapsed >= timeout_duration:
                                print(f"[Shake] FAIL: Timeout expired ({timeout_duration:.1f}s) - returning to start of bot loop")
                                return
                            else:
                                if int(remaining) != int(remaining + 0.001):
                                    print(f"[Shake] White pixel not found - timeout in {remaining:.1f}s")
                
                self._interruptible_sleep(0.001)
                
        except ImportError:
            print("[Shake] ERROR: dxcam not installed. Install with: pip install dxcam")
            return
        except Exception as e:
            print(f"[Shake] ERROR: {e}")
        finally:
            if 'camera' in locals():
                try:
                    camera.stop()
                    camera.release()
                    print("[Shake] Camera stopped and released")
                except:
                    pass
        
        print("[Shake] Shake detection completed")
    
    def _execute_shake_navigation(self):
        print("[Shake] Starting shake detection (Navigation mode)")
        
        friend_box_dict = self.storage.get_quad_box('friend_box')
        
        friend_box = (friend_box_dict["x1"], friend_box_dict["y1"], friend_box_dict["x2"], friend_box_dict["y2"])
        
        print(f"[Shake] Friend box: {friend_box}")
        
        try:
            import dxcam
            import numpy as np
            import time
            import win32api
            import win32con
            from pynput.keyboard import Controller, Key
            
            camera = dxcam.create(region=friend_box)
            print("[Shake] dxcam camera created successfully")
            
            camera.start(target_fps=60)
            print("[Shake] Video capture started (60 FPS)")
            
            friend_color = np.array(self.storage.get_shake_setting("friend_color"), dtype=np.uint8)
            friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
            fail_shake_timeout = self.storage.get_shake_setting("fail_shake_timeout")
            
            print(f"[Shake] Friend color: RGB{tuple(friend_color)}")
            print(f"[Shake] Friend color tolerance: {friend_tolerance}")
            print(f"[Shake] Fail shake timeout: {fail_shake_timeout:.1f}s")
            
            keyboard_controller = Controller()
            
            timeout_start = None
            timeout_duration = fail_shake_timeout
            
            while self.bot_running and not self._should_stop():
                frame = camera.get_latest_frame()
                
                if frame is not None:
                    friend_area = frame
                    
                    friend_color_found = np.any(
                        np.all(np.abs(friend_area - friend_color) <= friend_tolerance, axis=-1)
                    )
                    
                    if not friend_color_found:
                        print("[Shake] Friend color disappeared - PASS: Continuing to fish")
                        break
                    
                    if timeout_start is None:
                        timeout_start = time.time()
                        print(f"[Shake] Friend color detected - starting fail timeout ({timeout_duration:.1f}s)")
                    
                    elapsed = time.time() - timeout_start
                    remaining = timeout_duration - elapsed
                    
                    if elapsed >= timeout_duration:
                        print(f"[Shake] FAIL: Timeout expired ({timeout_duration:.1f}s) - returning to start of bot loop")
                        return
                    
                    if int(remaining) != int(remaining + 0.001):
                        print(f"[Shake] Friend color present - timeout in {remaining:.1f}s")
                    
                    keyboard_controller.press(Key.enter)
                    keyboard_controller.release(Key.enter)
                
                self._interruptible_sleep(0.001)
                
        except ImportError:
            print("[Shake] ERROR: dxcam not installed. Install with: pip install dxcam")
            return
        except Exception as e:
            print(f"[Shake] ERROR: {e}")
        finally:
            if 'camera' in locals():
                try:
                    camera.stop()
                    camera.release()
                    print("[Shake] Camera stopped and released")
                except:
                    pass
        
        print("[Shake] Shake detection completed")
    
    def _execute_fish(self):
        print("[Fish] Starting AI-controlled fishing minigame")
        
        model_path = self.storage.get_fish_setting("rod_model")
        tolerance_base = self.storage.get_fish_setting("tolerance_pixels")
        base_resolution = self.storage.get_fish_setting("base_resolution_width")
        accel_init = self.storage.get_fish_setting("accel_init")
        max_velocity_init = self.storage.get_fish_setting("max_velocity_init")
        smoothing = self.storage.get_fish_setting("smoothing")
        learning_rate = self.storage.get_fish_setting("learning_rate")
        
        if model_path == "No Models Found":
            print("[Fish] ERROR: No YOLO model selected. Please select a model in Fish menu.")
            return
        
        import os
        import sys
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        full_model_path = os.path.join(current_dir, model_path)
        if not os.path.exists(full_model_path):
            print(f"[Fish] ERROR: Model file not found: {full_model_path}")
            return
        
        print(f"[Fish] Using model: {model_path}")
        
        detection_box_dict = self.storage.get_quad_box('detection_box')
        detection_box = (detection_box_dict["x1"], detection_box_dict["y1"], 
                        detection_box_dict["x2"], detection_box_dict["y2"])
        
        friend_box_dict = self.storage.get_quad_box('friend_box')
        friend_box = (friend_box_dict["x1"], friend_box_dict["y1"],
                     friend_box_dict["x2"], friend_box_dict["y2"])
        
        fish_area_x1 = min(detection_box[0], friend_box[0])
        fish_area_y1 = min(detection_box[1], friend_box[1])
        fish_area_x2 = max(detection_box[2], friend_box[2])
        fish_area_y2 = max(detection_box[3], friend_box[3])
        fish_area = (fish_area_x1, fish_area_y1, fish_area_x2, fish_area_y2)
        
        print(f"[Fish] Fish area (combined): {fish_area}")
        print(f"[Fish] Detection box: {detection_box}")
        print(f"[Fish] Friend box (for exit): {friend_box}")
        
        controller = AdaptiveBangBangController(
            accel_init=accel_init,
            max_velocity=max_velocity_init,
            smoothing=smoothing,
            learning_rate=learning_rate
        )
        print(f"[Fish] Controller initialized: accel={accel_init}, max_vel={max_velocity_init}, smooth={smoothing}, learn={learning_rate}")
        
        try:
            import dxcam
            import numpy as np
            import time
            from ultralytics import YOLO
            import win32api
            import win32con
            import traceback
            
            screen_width = win32api.GetSystemMetrics(0)
            scale_factor = screen_width / base_resolution
            tolerance = int(tolerance_base * scale_factor)
            print(f"[Fish] Screen: {screen_width}px, Base: {base_resolution}px, Scale: {scale_factor:.2f}x")
            print(f"[Fish] Tolerance: {tolerance_base}px -> {tolerance}px (scaled)")
            
            model = YOLO(full_model_path)
            print("[Fish] YOLO model loaded successfully")
            
            camera = dxcam.create(region=fish_area)
            camera.start(target_fps=60)
            print("[Fish] Camera started (60 FPS)")
            
            detection_box_relative = (
                detection_box[0] - fish_area_x1,
                detection_box[1] - fish_area_y1,
                detection_box[2] - fish_area_x1,
                detection_box[3] - fish_area_y1
            )
            
            friend_box_relative = (
                friend_box[0] - fish_area_x1,
                friend_box[1] - fish_area_y1,
                friend_box[2] - fish_area_x1,
                friend_box[3] - fish_area_y1
            )
            
            print(f"[Fish] Relative detection box: {detection_box_relative}")
            print(f"[Fish] Relative friend box: {friend_box_relative}")
            
            friend_color = np.array(self.storage.get_shake_setting("friend_color"), dtype=np.uint8)
            friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
            
            currently_holding = False
            last_frame_time = time.time()
            frames_processed = 0
            
            print("[Fish] Starting minigame loop...")
            
            while self.bot_running and not self._should_stop():
                current_time = time.time()
                frames_processed += 1
                
                frame = camera.get_latest_frame()
                if frame is None:
                    self._interruptible_sleep(0.001)
                    continue
                
                friend_frame = frame[
                    friend_box_relative[1]:friend_box_relative[3],
                    friend_box_relative[0]:friend_box_relative[2]
                ]
                
                friend_color_found = np.any(
                    np.all(np.abs(friend_frame - friend_color) <= friend_tolerance, axis=-1)
                )
                if friend_color_found:
                    print(f"[Fish] Fish caught! Frames: {frames_processed}, Time: {current_time - last_frame_time:.1f}s")
                    break
                
                detection_frame = frame[
                    detection_box_relative[1]:detection_box_relative[3],
                    detection_box_relative[0]:detection_box_relative[2]
                ]
                
                results = model.predict(detection_frame, conf=0.01, verbose=False)
                
                bar_position = None
                icon_position = None
                best_bar_conf = -1
                best_icon_conf = -1
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        if cls == 0 and conf > best_bar_conf:
                            bar_position = center_y
                            best_bar_conf = conf
                        elif cls == 1 and conf > best_icon_conf:
                            icon_position = center_y
                            best_icon_conf = conf
                
                if bar_position is not None and icon_position is not None:
                    should_hold = controller.update(
                        bar_position=bar_position,
                        target_position=icon_position,
                        currently_holding=currently_holding,
                        current_time=current_time,
                        tolerance=tolerance
                    )
                    
                    if should_hold and not currently_holding:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        currently_holding = True
                    elif not should_hold and currently_holding:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                        currently_holding = False
                
                self._interruptible_sleep(0.001)
            
            if currently_holding:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                print("[Fish] Released mouse button")
            
            debug_info = controller.get_debug_info()
            if debug_info['initialized']:
                self.storage.update_fish_learned_values(
                    controller.accel_right,
                    controller.max_velocity
                )
                print(f"[Fish] Learned values saved: accel={controller.accel_right:.1f}, max_vel={controller.max_velocity:.1f}")
            
            print(f"[Fish] Session complete: {frames_processed} frames processed")
            
        except ImportError as e:
            print(f"[Fish] ERROR: Missing dependency - {e}")
            print("[Fish] Required: pip install dxcam ultralytics pywin32")
        except Exception as e:
            print(f"[Fish] ERROR: {e}")
            traceback.print_exc()
        finally:
            if 'camera' in locals():
                try:
                    camera.stop()
                    camera.release()
                except:
                    pass
            try:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            except:
                pass
            print("[Fish] Cleanup complete")
    
    def _execute_discord(self):
        if not self.storage.get_discord_setting("active"):
            print("[Discord] Discord notifications disabled - skipping")
            return
        
        print("[Discord] Discord notifications enabled - checking loop counter")
        
        self.discord_loop_counter += 1
        
        loops_per_screenshot = self.storage.get_discord_setting("loops_per_screenshot")
        
        if self.discord_loop_counter == 1 or self.discord_loop_counter % loops_per_screenshot == 0:
            print(f"[Discord] Loop {self.discord_loop_counter} - Sending screenshot")
            self._send_discord_screenshot()
        else:
            print(f"[Discord] Loop {self.discord_loop_counter}/{loops_per_screenshot} - Skipping screenshot")
    
    def _send_discord_screenshot(self):
        try:
            import requests
            import mss
            from PIL import Image
            import io
            
            webhook_url = self.storage.get_discord_setting("webhook_url")
            if not webhook_url:
                print("[Discord] No webhook URL configured - skipping")
                return
            
            print("[Discord] Taking screenshot...")
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {
                'file': ('screenshot.png', img_bytes, 'image/png')
            }
            
            data = {
                'content': f'Screenshot from loop #{self.discord_loop_counter}'
            }
            
            print(f"[Discord] Sending to webhook: {webhook_url[:50]}...")
            response = requests.post(webhook_url, files=files, data=data)
            
            if response.status_code == 204 or response.status_code == 200:
                print(f"[Discord] Screenshot sent successfully (Loop {self.discord_loop_counter})")
            else:
                print(f"[Discord] Failed to send screenshot: {response.status_code}")
                
        except ImportError as e:
            print(f"[Discord] ERROR: Missing library: {e}")
            print("Install with: pip install requests mss pillow")
        except Exception as e:
            print(f"[Discord] ERROR: {e}")

    def _press_key(self, key_char):
        from pynput.keyboard import Controller
        keyboard_controller = Controller()
        
        try:
            keyboard_controller.press(key_char)
            keyboard_controller.release(key_char)
            print(f"[Input] Key '{key_char}' pressed and released")
        except Exception as e:
            print(f"[Input] Error pressing key '{key_char}': {e}")
    
    def _mouse_down(self):
        from pynput.mouse import Controller, Button
        mouse_controller = Controller()
        
        try:
            mouse_controller.press(Button.left)
            print("[Input] Left mouse button pressed")
        except Exception as e:
            print(f"[Input] Error pressing mouse button: {e}")
    
    def _mouse_up(self):
        from pynput.mouse import Controller, Button
        mouse_controller = Controller()
        
        try:
            mouse_controller.release(Button.left)
            print("[Input] Left mouse button released")
        except Exception as e:
            print(f"[Input] Error releasing mouse button: {e}")
    
    def _exit_application(self):
        if self.bot_running:
            self._stop_bot_loop()
        
        self.keyboard_listener.stop()
        self.quit()
        self.destroy()

    def initialize_nodes(self):
        self.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        self._create_main_nodes(width, height)
        self._create_small_nodes(width, height)
        self._create_particles()
        
        self.animate()
    
    def _create_main_nodes(self, width, height):
        main_labels = ["Basic", "Cast", "Shake", "Fish", "Discord"]
        main_colors = [
            ["#cc0066", "#ff0080", "#ff3399"],
            ["#0066cc", "#0080ff", "#3399ff"],
            ["#cc6600", "#ff8000", "#ff9933"],
            ["#00cc66", "#00ff80", "#33ff99"],
            ["#6600cc", "#8000ff", "#9933ff"]
        ]
        main_radius = 35
        
        center_x = width / 2
        center_y = height / 2
        radius_from_center = 180
        
        main_node_speed = 1.0
        
        for i, label in enumerate(main_labels):
            angle = (i * 2 * math.pi / 5) - math.pi / 2
            x = center_x + radius_from_center * math.cos(angle)
            y = center_y + radius_from_center * math.sin(angle)
            
            node = NeuralNode(x, y, label, main_radius, is_main=True, colors=main_colors[i])
            velocity_angle = random.uniform(0, 2 * math.pi)
            node.vx = main_node_speed * math.cos(velocity_angle)
            node.vy = main_node_speed * math.sin(velocity_angle)
            self.nodes.append(node)
    
    def _create_small_nodes(self, width, height):
        small_radius = 10
        num_random_nodes = 15
        
        for _ in range(num_random_nodes):
            x = random.randint(small_radius + 50, width - small_radius - 50)
            y = random.randint(small_radius + 50, height - small_radius - 50)
            node = NeuralNode(x, y, "", small_radius, is_main=False)
            self.nodes.append(node)
    
    def _create_particles(self):
        particle_colors = ["#ff0099", "#0099ff", "#ff9900", "#00ff99", "#9900ff"]
        for i in range(5):
            particle = Particle(self.nodes[i], particle_colors[i])
            self.particles.append(particle)

    def draw_connection(self, node1, node2, distance):
        opacity_factor = 1 - (distance / self.CONNECTION_THRESHOLD)
        opacity = max(0, min(1, opacity_factor))
        
        conn_id = (id(node1), id(node2)) if id(node1) < id(node2) else (id(node2), id(node1))
        
        if conn_id not in self.connection_animations:
            self.connection_animations[conn_id] = 0
        
        if self.connection_animations[conn_id] < 30:
            self.connection_animations[conn_id] += 1
        
        anim_progress = min(1.0, self.connection_animations[conn_id] / 30)
        pulse = math.sin(self.animation_frame * 0.1 + conn_id[0] * 0.01) * 0.3 + 0.7
        
        blue_value = int(80 + 175 * opacity * pulse)
        color = f"#{blue_value//3:02x}{blue_value//2:02x}{blue_value:02x}"
        
        base_width = max(3, int(10 * opacity))
        line_width = base_width * anim_progress
        
        self.canvas.create_line(
            node1.x, node1.y, node2.x, node2.y,
            fill=color, width=line_width, smooth=True
        )
    
    def draw_node(self, node):
        x, y, r = node.x, node.y, node.radius
        
        if node.is_main:
            self._draw_main_node(x, y, r, node)
        else:
            self._draw_small_node(x, y, r, node)
    
    def _draw_main_node(self, x, y, r, node):
        if node.is_frozen:
            pulse = math.sin(self.animation_frame * 0.15) * 0.3 + 0.7
            glow_size = 8 * pulse
            
            self.canvas.create_oval(
                x - r - glow_size, y - r - glow_size,
                x + r + glow_size, y + r + glow_size,
                outline="#ffffff", width=int(3 * pulse)
            )
            
            self.canvas.create_oval(
                x - r - glow_size/2, y - r - glow_size/2,
                x + r + glow_size/2, y + r + glow_size/2,
                outline=node.colors[-1], width=int(2 * pulse)
            )
        
        for i, color in enumerate(node.colors):
            offset = i * 3
            self.canvas.create_oval(
                x - r + offset, y - r + offset,
                x + r - offset, y + r - offset,
                fill=color, outline=""
            )
        
        font_size = 12 if node.is_frozen else 11
        self.canvas.create_text(
            x, y, text=node.label,
            fill="white", font=("Arial", font_size, "bold")
        )
        
        ring_color = node.colors[-1]
        ring_width = 4 if node.is_frozen else 3
        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline=ring_color, width=ring_width
        )
    
    def _draw_small_node(self, x, y, r, node):
        if node.activation_strength > 0:
            fill_color, outline_color, glow_color = self._calculate_activation_colors(node)
            
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill_color, outline=outline_color, width=2
            )
            
            self.canvas.create_oval(
                x - r - 3, y - r - 3, x + r + 3, y + r + 3,
                outline=glow_color, width=int(1 + node.activation_strength * 2)
            )
        else:
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="#4d4d4d", outline="#808080", width=1
            )
            
            self.canvas.create_oval(
                x - r - 3, y - r - 3, x + r + 3, y + r + 3,
                outline="#666666", width=1
            )
    
    def _calculate_activation_colors(self, node):
        act_color = node.activation_color
        r_val = int(act_color[1:3], 16)
        g_val = int(act_color[3:5], 16)
        b_val = int(act_color[5:7], 16)
        
        strength = node.activation_strength
        
        final_r = int(77 + (r_val - 77) * strength)
        final_g = int(77 + (g_val - 77) * strength)
        final_b = int(77 + (b_val - 77) * strength)
        fill_color = f"#{final_r:02x}{final_g:02x}{final_b:02x}"
        
        outline_r = int(128 + (r_val - 128) * strength)
        outline_g = int(128 + (g_val - 128) * strength)
        outline_b = int(128 + (b_val - 128) * strength)
        outline_color = f"#{outline_r:02x}{outline_g:02x}{outline_b:02x}"
        
        glow_r = int(102 + (r_val - 102) * strength)
        glow_g = int(102 + (g_val - 102) * strength)
        glow_b = int(102 + (b_val - 102) * strength)
        glow_color = f"#{glow_r:02x}{glow_g:02x}{glow_b:02x}"
        
        return fill_color, outline_color, glow_color
    
    def draw_particle(self, particle):
        x, y = particle.get_position()
        pulse_size = 6
        
        self.canvas.create_oval(
            x - pulse_size - 2, y - pulse_size - 2,
            x + pulse_size + 2, y + pulse_size + 2,
            fill=particle.color, outline=""
        )
        
        self.canvas.create_oval(
            x - pulse_size, y - pulse_size,
            x + pulse_size, y + pulse_size,
            fill="#ffffff", outline=particle.color, width=2
        )

    def animate(self):
        import time
        
        current_time = time.time() * 1000
        if self.last_frame_time is not None:
            actual_frame_time = current_time - self.last_frame_time
        else:
            actual_frame_time = self.target_frame_time
        
        self.last_frame_time = current_time
        
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if self.current_menu == "transitioning":
            self._update_transition(actual_frame_time)
            
            if self.current_menu == "transitioning":
                self._render_transition(width, height)
            elif self.current_menu == "main":
                self._render_main_menu(width, height)
            else:
                self._render_submenu(width, height, self.current_menu)
        elif self.current_menu == "main":
            self._render_main_menu(width, height)
        else:
            self._render_submenu(width, height, self.current_menu)
        
        self.animation_frame += 1
        
        processing_time = (time.time() * 1000) - current_time
        delay = max(1, int(self.target_frame_time - processing_time))
        
        self.after(delay, self.animate)
    
    def _render_main_menu(self, width, height):

        self._update_nodes(width, height)
        self._update_particles()

        current_connections = self._draw_connections()
        self._cleanup_connection_animations(current_connections)
        self._draw_small_nodes()
        self._draw_particles()
        self._draw_main_nodes()
    
    def _update_transition(self, delta_time):
        progress_increment = delta_time / self.transition_duration
        self.transition_progress += progress_increment
        
        if self.transition_progress >= 1.0:
            self.transition_progress = 0
            self.current_menu = self.transition_target
            self.transition_target = None
            self.transition_origin = None
            self.menu_scroll_offset = 0
    
    def _render_transition(self, width, height):
        t = self.transition_progress
        eased = t * t * (3 - 2 * t)
        
        if self.transition_target in ["basic", "cast", "shake", "fish", "discord"]:
            self._render_main_menu(width, height)
            
            origin_x, origin_y = self.transition_origin
            
            max_distance = max(
                math.sqrt(origin_x**2 + origin_y**2),
                math.sqrt((width - origin_x)**2 + origin_y**2),
                math.sqrt(origin_x**2 + (height - origin_y)**2),
                math.sqrt((width - origin_x)**2 + (height - origin_y)**2)
            )
            
            wave_distance = max_distance * eased
            ring_width = 40
            
            num_rings = 3
            for ring_idx in range(num_rings):
                ring_offset = ring_idx * 20
                current_ring_distance = wave_distance - ring_offset
                
                if current_ring_distance > 0:
                    ring_opacity = (1 - eased) * (1 - ring_idx * 0.3)
                    if ring_opacity > 0:
                        opacity_val = int(255 * ring_opacity)
                        ring_color = f"#{opacity_val//4:02x}{opacity_val//2:02x}{opacity_val:02x}"
                        
                        self.canvas.create_oval(
                            origin_x - current_ring_distance, origin_y - current_ring_distance,
                            origin_x + current_ring_distance, origin_y + current_ring_distance,
                            outline=ring_color, width=int(6 * ring_opacity)
                        )
            
            connection_reach = wave_distance + 50
            for node in self.nodes:
                dx = node.x - origin_x
                dy = node.y - origin_y
                node_distance = math.sqrt(dx**2 + dy**2)
                
                if abs(node_distance - wave_distance) < 80 and node_distance > 20:
                    num_segments = 8
                    points = [origin_x, origin_y]
                    
                    for seg in range(1, num_segments):
                        t = seg / num_segments
                        base_x = origin_x + dx * t
                        base_y = origin_y + dy * t
                        
                        offset = random.uniform(-15, 15)
                        perp_x = -dy / node_distance * offset
                        perp_y = dx / node_distance * offset
                        
                        points.extend([base_x + perp_x, base_y + perp_y])
                    
                    points.extend([node.x, node.y])
                    
                    brightness = int(255 * (1 - eased) * random.uniform(0.7, 1.0))
                    lightning_color = f"#{brightness//3:02x}{brightness//2:02x}{brightness:02x}"
                    
                    self.canvas.create_line(
                        points,
                        fill=lightning_color,
                        width=2,
                        smooth=False
                    )
                    
                    glow_size = 8
                    self.canvas.create_oval(
                        node.x - glow_size, node.y - glow_size,
                        node.x + glow_size, node.y + glow_size,
                        fill="#00ffff", outline="#ffffff", width=1
                    )
            
            for node in self.nodes:
                dx = node.x - origin_x
                dy = node.y - origin_y
                target_distance = math.sqrt(dx**2 + dy**2)
                
                if wave_distance >= target_distance - ring_width:
                    node_progress = min(1.0, (wave_distance - target_distance + ring_width) / 60)
                    
                    if node_progress < 1.0:
                        num_explosion_particles = 6
                        explosion_radius = 30 * node_progress
                        for i in range(num_explosion_particles):
                            angle = (i / num_explosion_particles) * 2 * math.pi
                            px = node.x + math.cos(angle) * explosion_radius
                            py = node.y + math.sin(angle) * explosion_radius
                            
                            particle_size = 4 * (1 - node_progress)
                            color = "#ff3399" if node.is_main else "#0099ff"
                            
                            self.canvas.create_oval(
                                px - particle_size, py - particle_size,
                                px + particle_size, py + particle_size,
                                fill=color, outline=""
                            )
            

    
    def _render_submenu(self, width, height, menu_name):
        menu_colors = {
            "basic": ("#cc0066", "#ff3399"),
            "cast": ("#0066cc", "#3399ff"),
            "shake": ("#cc6600", "#ff9933"),
            "fish": ("#00cc66", "#33ff99"),
            "discord": ("#6600cc", "#9933ff")
        }
        
        primary_color, accent_color = menu_colors.get(menu_name, ("#0066cc", "#3399ff"))
        
        if menu_name == "basic":
            self._render_basic_menu_content(width, height, accent_color)
        elif menu_name == "cast":
            self._render_cast_menu_content(width, height, accent_color)
        elif menu_name == "shake":
            self._render_shake_menu_content(width, height, accent_color)
        elif menu_name == "fish":
            self._render_fish_menu_content(width, height, accent_color)
        elif menu_name == "discord":
            self._render_discord_menu_content(width, height, accent_color)
        
        self.canvas.create_rectangle(
            0, 0, width, 70,
            fill="#1a1a1a", outline=""
        )
        
        button_margin = 20
        button_x = button_margin
        button_y = button_margin
        button_width = min(80, width * 0.1)
        button_height = 30
        
        self.canvas.create_rectangle(
            button_x, button_y,
            button_x + button_width, button_y + button_height,
            fill=primary_color, outline=accent_color, width=2
        )
        
        self.canvas.create_text(
            button_x + button_width / 2, button_y + button_height / 2,
            text="Back", fill="white", font=("Arial", 12, "bold")
        )
        
        all_menus = ["basic", "cast", "shake", "fish", "discord"]
        other_menus = [m for m in all_menus if m != menu_name]
        
        nav_button_x = button_x + button_width + 20
        nav_button_width = 70
        nav_button_spacing = 10
        
        for i, other_menu in enumerate(other_menus):
            other_primary, other_accent = menu_colors[other_menu]
            current_x = nav_button_x + i * (nav_button_width + nav_button_spacing)
            
            self.canvas.create_rectangle(
                current_x, button_y,
                current_x + nav_button_width, button_y + button_height,
                fill=other_primary, outline=other_accent, width=2
            )
            
            self.canvas.create_text(
                current_x + nav_button_width / 2, button_y + button_height / 2,
                text=other_menu.capitalize(), fill="white", font=("Arial", 10, "bold")
            )
    
    def _render_basic_menu_content(self, width, height, accent_color):
        scroll_y = -self.menu_scroll_offset
        
        margin_left = 50
        content_start_y = 100
        
        self.canvas.create_text(
            margin_left, content_start_y + scroll_y,
            text="Basic Menu",
            fill=accent_color, font=("Arial", 32, "bold"),
            anchor="w"
        )
        
        options = [
            ("start_stop", "Start/Stop", 200, self.storage.get_state("is_running")),
            ("change_area", "Change Area", 250, self.storage.get_state("area_toggled")),
            ("exit", "Exit", 300, None)
        ]
        
        for key_name, label, y_pos, state in options:
            current_key = self.hotkeys[key_name]
            key_str = self._format_key(current_key)
            
            label_x = margin_left
            hotkey_x = margin_left + 200
            rebind_x = margin_left + 400
            rebind_width = 80
            rebind_height = 30
            state_x = margin_left + 500
            
            self.canvas.create_text(
                label_x, y_pos + 15 + scroll_y,
                text=f"{label}:",
                fill="white", font=("Arial", 16, "bold"),
                anchor="w"
            )
            
            hotkey_text = f"Press '{key_str}' to rebind" if self.rebinding_key == key_name else key_str
            self.canvas.create_text(
                hotkey_x, y_pos + 15 + scroll_y,
                text=hotkey_text,
                fill="#ffff00" if self.rebinding_key == key_name else accent_color,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            
            self.canvas.create_rectangle(
                rebind_x, y_pos + scroll_y,
                rebind_x + rebind_width, y_pos + rebind_height + scroll_y,
                fill="#333333", outline=accent_color, width=2
            )
            
            self.canvas.create_text(
                rebind_x + rebind_width / 2, y_pos + rebind_height / 2 + scroll_y,
                text="Rebind", fill="white", font=("Arial", 11, "bold")
            )
            
            if state is not None:
                state_text = "ON" if state else "OFF"
                state_color = "#00ff00" if state else "#ff0000"
                self.canvas.create_text(
                    state_x, y_pos + 15 + scroll_y,
                    text=f"[{state_text}]",
                    fill=state_color, font=("Arial", 14, "bold"),
                    anchor="w"
                )
        
        checkbox_y_start = 380
        checkboxes = [
            ("always_on_top", "Always On Top"),
            ("auto_minimize", "Auto Minimize GUI"),
            ("auto_focus_roblox", "Auto Focus Roblox")
        ]
        
        for i, (setting_name, label) in enumerate(checkboxes):
            y_pos = checkbox_y_start + i * 50
            checkbox_x = margin_left
            checkbox_size = 20
            
            is_checked = self.storage.get_gui_setting(setting_name)
            
            self.canvas.create_rectangle(
                checkbox_x, y_pos + scroll_y,
                checkbox_x + checkbox_size, y_pos + checkbox_size + scroll_y,
                fill="#333333", outline=accent_color, width=2
            )
            
            if is_checked:
                self.canvas.create_line(
                    checkbox_x + 4, y_pos + 4 + scroll_y,
                    checkbox_x + checkbox_size - 4, y_pos + checkbox_size - 4 + scroll_y,
                    fill="#00ff00", width=3
                )
                self.canvas.create_line(
                    checkbox_x + checkbox_size - 4, y_pos + 4 + scroll_y,
                    checkbox_x + 4, y_pos + checkbox_size - 4 + scroll_y,
                    fill="#00ff00", width=3
                )
            
            self.canvas.create_text(
                checkbox_x + checkbox_size + 15, y_pos + checkbox_size / 2 + scroll_y,
                text=label,
                fill="white", font=("Arial", 14, "bold"),
                anchor="w"
            )
        
        slider_y_start = 550
        
        slider_x = margin_left
        slider_width = 300
        slider_height = 10
        
        tolerance_y = slider_y_start
        tolerance_value = self.storage.get_gui_setting("friend_color_tolerance")
        self.canvas.create_text(
            slider_x, tolerance_y + scroll_y,
            text=f"Friend Color Tolerance: {tolerance_value}",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self.canvas.create_rectangle(
            slider_x, tolerance_y + 25 + scroll_y,
            slider_x + slider_width, tolerance_y + 25 + slider_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        tolerance_progress = tolerance_value / 20.0
        self.canvas.create_rectangle(
            slider_x, tolerance_y + 25 + scroll_y,
            slider_x + slider_width * tolerance_progress, tolerance_y + 25 + slider_height + scroll_y,
            fill=accent_color, outline=""
        )
        
        handle_x = slider_x + slider_width * tolerance_progress
        self.canvas.create_oval(
            handle_x - 8, tolerance_y + 25 + slider_height / 2 - 8 + scroll_y,
            handle_x + 8, tolerance_y + 25 + slider_height / 2 + 8 + scroll_y,
            fill="white", outline=accent_color, width=2
        )
        
        timeout_y = slider_y_start + 60
        timeout_value = self.storage.get_gui_setting("state_check_timeout")
        self.canvas.create_text(
            slider_x, timeout_y + scroll_y,
            text=f"State Check Timeout: {timeout_value:.1f}s",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        self.canvas.create_rectangle(
            slider_x, timeout_y + 25 + scroll_y,
            slider_x + slider_width, timeout_y + 25 + slider_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        timeout_progress = timeout_value / 10.0
        self.canvas.create_rectangle(
            slider_x, timeout_y + 25 + scroll_y,
            slider_x + slider_width * timeout_progress, timeout_y + 25 + slider_height + scroll_y,
            fill=accent_color, outline=""
        )
        
        handle_x = slider_x + slider_width * timeout_progress
        self.canvas.create_oval(
            handle_x - 8, timeout_y + 25 + slider_height / 2 - 8 + scroll_y,
            handle_x + 8, timeout_y + 25 + slider_height / 2 + 8 + scroll_y,
            fill="white", outline=accent_color, width=2
        )
    
    def _format_key(self, key):
        if hasattr(key, 'name'):
            return key.name.upper()
        elif hasattr(key, 'char'):
            return key.char.upper() if key.char else str(key)
        else:
            return str(key)
    
    def _render_cast_menu_content(self, width, height, accent_color):
        scroll_y = -self.menu_scroll_offset
        margin_left = 50
        
        self.canvas.create_text(
            margin_left, 100 + scroll_y,
            text="Cast Menu",
            fill=accent_color, font=("Arial", 32, "bold"),
            anchor="w"
        )
        
        box_x = margin_left + 100
        box_y_start = 180
        box_width = 200
        box_height = 50
        box_spacing = 30
        arrow_length = 20
        
        delay1 = self.storage.get_cast_setting("delay_before_click")
        delay2 = self.storage.get_cast_setting("delay_hold_duration")
        delay3 = self.storage.get_cast_setting("delay_after_release")
        
        y1 = box_y_start + scroll_y
        self.canvas.create_rectangle(
            box_x, y1,
            box_x + box_width, y1 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y1 + box_height / 2,
            text=f"Delay {delay1:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y1 = y1 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y1,
            box_x + box_width / 2, arrow_y1 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y2 = box_y_start + box_height + box_spacing + scroll_y
        self.canvas.create_rectangle(
            box_x, y2,
            box_x + box_width, y2 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y2 + box_height / 2,
            text="Hold Left Click",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y2 = y2 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y2,
            box_x + box_width / 2, arrow_y2 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y3 = box_y_start + (box_height + box_spacing) * 2 + scroll_y
        self.canvas.create_rectangle(
            box_x, y3,
            box_x + box_width, y3 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y3 + box_height / 2,
            text=f"Delay {delay2:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y3 = y3 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y3,
            box_x + box_width / 2, arrow_y3 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y4 = box_y_start + (box_height + box_spacing) * 3 + scroll_y
        self.canvas.create_rectangle(
            box_x, y4,
            box_x + box_width, y4 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y4 + box_height / 2,
            text="Release Left Click",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y4 = y4 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y4,
            box_x + box_width / 2, arrow_y4 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y5 = box_y_start + (box_height + box_spacing) * 4 + scroll_y
        self.canvas.create_rectangle(
            box_x, y5,
            box_x + box_width, y5 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y5 + box_height / 2,
            text=f"Delay {delay3:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        control_x = box_x + box_width + 80
        
        self.canvas.create_text(
            control_x, y1 + 10,
            text="Before Click:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, box_y_start + 30, delay1, "delay_before_click", accent_color, scroll_y)
        
        self.canvas.create_text(
            control_x, y3 + 10,
            text="Hold Duration:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, box_y_start + (box_height + box_spacing) * 2 + 30, delay2, "delay_hold_duration", accent_color, scroll_y)
        
        self.canvas.create_text(
            control_x, y5 + 10,
            text="After Release:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, box_y_start + (box_height + box_spacing) * 4 + 30, delay3, "delay_after_release", accent_color, scroll_y)
        
        anti_nuke_y = box_y_start + (box_height + box_spacing) * 5 + 80
        
        checkbox_size = 20
        is_anti_nuke = self.storage.get_cast_setting("anti_nuke")
        
        self.canvas.create_rectangle(
            margin_left, anti_nuke_y + scroll_y,
            margin_left + checkbox_size, anti_nuke_y + checkbox_size + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        if is_anti_nuke:
            self.canvas.create_line(
                margin_left + 4, anti_nuke_y + 4 + scroll_y,
                margin_left + checkbox_size - 4, anti_nuke_y + checkbox_size - 4 + scroll_y,
                fill="#00ff00", width=3
            )
            self.canvas.create_line(
                margin_left + checkbox_size - 4, anti_nuke_y + 4 + scroll_y,
                margin_left + 4, anti_nuke_y + checkbox_size - 4 + scroll_y,
                fill="#00ff00", width=3
            )
        
        self.canvas.create_text(
            margin_left + checkbox_size + 15, anti_nuke_y + checkbox_size / 2 + scroll_y,
            text="Anti Nuke",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        if is_anti_nuke:
            self._render_anti_nuke_flow(margin_left, anti_nuke_y + 60, accent_color, scroll_y)
    
    def _render_delay_input(self, x, y, value, setting_name, accent_color, scroll_y):
        button_width = 30
        button_height = 25
        
        self.canvas.create_rectangle(
            x, y + scroll_y,
            x + button_width, y + button_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            x + button_width / 2, y + button_height / 2 + scroll_y,
            text="-", fill="white", font=("Arial", 16, "bold")
        )
        
        value_x = x + button_width + 10
        self.canvas.create_text(
            value_x + 40, y + button_height / 2 + scroll_y,
            text=f"{value:.1f}s",
            fill=accent_color, font=("Arial", 14, "bold")
        )
        
        plus_x = value_x + 80
        self.canvas.create_rectangle(
            plus_x, y + scroll_y,
            plus_x + button_width, y + button_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            plus_x + button_width / 2, y + button_height / 2 + scroll_y,
            text="+", fill="white", font=("Arial", 16, "bold")
        )
    
    def _render_anti_nuke_flow(self, x, y, accent_color, scroll_y):
        box_width = 200
        box_height = 50
        box_spacing = 30
        arrow_length = 20
        
        delay_before = self.storage.get_cast_setting("anti_nuke_delay_before")
        rod_slot = self.storage.get_cast_setting("anti_nuke_rod_slot")
        delay_after_rod = self.storage.get_cast_setting("anti_nuke_delay_after_rod")
        bag_slot = self.storage.get_cast_setting("anti_nuke_bag_slot")
        delay_after_bag = self.storage.get_cast_setting("anti_nuke_delay_after_bag")
        
        box_x = x + 100
        
        y1 = y + scroll_y
        self.canvas.create_rectangle(
            box_x, y1,
            box_x + box_width, y1 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y1 + box_height / 2,
            text=f"Delay {delay_before:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y1 = y1 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y1,
            box_x + box_width / 2, arrow_y1 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y2 = y + box_height + box_spacing + scroll_y
        self.canvas.create_rectangle(
            box_x, y2,
            box_x + box_width, y2 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + 10, y2 + box_height / 2,
            text=f"Select Rod: {rod_slot}",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        arrow_x = box_x + box_width - 20
        self.canvas.create_text(
            arrow_x, y2 + box_height / 2,
            text="▼",
            fill=accent_color, font=("Arial", 10)
        )
        
        arrow_y2 = y2 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y2,
            box_x + box_width / 2, arrow_y2 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y3 = y + (box_height + box_spacing) * 2 + scroll_y
        self.canvas.create_rectangle(
            box_x, y3,
            box_x + box_width, y3 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y3 + box_height / 2,
            text=f"Delay {delay_after_rod:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        arrow_y3 = y3 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y3,
            box_x + box_width / 2, arrow_y3 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y4 = y + (box_height + box_spacing) * 3 + scroll_y
        self.canvas.create_rectangle(
            box_x, y4,
            box_x + box_width, y4 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + 10, y4 + box_height / 2,
            text=f"Select Bag: {bag_slot}",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        arrow_x = box_x + box_width - 20
        self.canvas.create_text(
            arrow_x, y4 + box_height / 2,
            text="▼",
            fill=accent_color, font=("Arial", 10)
        )
        
        arrow_y4 = y4 + box_height + 5
        self.canvas.create_line(
            box_x + box_width / 2, arrow_y4,
            box_x + box_width / 2, arrow_y4 + arrow_length,
            fill=accent_color, width=3, arrow="last"
        )
        
        y5 = y + (box_height + box_spacing) * 4 + scroll_y
        self.canvas.create_rectangle(
            box_x, y5,
            box_x + box_width, y5 + box_height,
            fill="#333333", outline=accent_color, width=2
        )
        self.canvas.create_text(
            box_x + box_width / 2, y5 + box_height / 2,
            text=f"Delay {delay_after_bag:.1f}s",
            fill="white", font=("Arial", 14, "bold")
        )
        
        control_x = box_x + box_width + 80
        
        self.canvas.create_text(
            control_x, y1 + 10,
            text="Before Rod:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, y + 30, delay_before, "anti_nuke_delay_before", accent_color, scroll_y)
        
        self.canvas.create_text(
            control_x, y3 + 10,
            text="After Rod:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, y + (box_height + box_spacing) * 2 + 30, delay_after_rod, "anti_nuke_delay_after_rod", accent_color, scroll_y)
        
        self.canvas.create_text(
            control_x, y5 + 10,
            text="After Bag:",
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        self._render_delay_input(control_x, y + (box_height + box_spacing) * 4 + 30, delay_after_bag, "anti_nuke_delay_after_bag", accent_color, scroll_y)
        
        dropdown_x = control_x + 200
        dropdown_width = 60
        
        if self.cast_rod_dropdown_open:
            option_height = 30
            dropdown_y = y2
            
            self.canvas.create_rectangle(
                dropdown_x, dropdown_y,
                dropdown_x + dropdown_width, dropdown_y + option_height * 9,
                fill="#2a2a2a", outline=accent_color, width=2
            )
            
            for i in range(1, 10):
                option_y = dropdown_y + (i - 1) * option_height
                
                self.canvas.create_rectangle(
                    dropdown_x, option_y,
                    dropdown_x + dropdown_width, option_y + option_height,
                    fill="#444444", outline=accent_color, width=1
                )
                
                self.canvas.create_text(
                    dropdown_x + dropdown_width / 2, option_y + option_height / 2,
                    text=str(i),
                    fill="white", font=("Arial", 14, "bold")
                )
        
        if self.cast_bag_dropdown_open:
            option_height = 30
            dropdown_y = y4
            
            self.canvas.create_rectangle(
                dropdown_x, dropdown_y,
                dropdown_x + dropdown_width, dropdown_y + option_height * 9,
                fill="#2a2a2a", outline=accent_color, width=2
            )
            
            for i in range(1, 10):
                option_y = dropdown_y + (i - 1) * option_height
                
                self.canvas.create_rectangle(
                    dropdown_x, option_y,
                    dropdown_x + dropdown_width, option_y + option_height,
                    fill="#444444", outline=accent_color, width=1
                )
                
                self.canvas.create_text(
                    dropdown_x + dropdown_width / 2, option_y + option_height / 2,
                    text=str(i),
                    fill="white", font=("Arial", 14, "bold")
                )
    
    def _render_anti_nuke_dropdown(self, x, y, width, height, text, dropdown_type, accent_color):
        self.canvas.create_rectangle(
            x, y,
            x + width, y + height,
            fill="#333333", outline=accent_color, width=2
        )
        
        self.canvas.create_text(
            x + 10, y + height / 2,
            text=text,
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        arrow_x = x + width - 20
        arrow_y = y + height / 2
        self.canvas.create_text(
            arrow_x, arrow_y,
            text="▼",
            fill=accent_color, font=("Arial", 10)
        )
        
        is_open = (dropdown_type == "rod" and self.cast_rod_dropdown_open) or \
                  (dropdown_type == "bag" and self.cast_bag_dropdown_open)
        
        if is_open:
            option_height = 30
            for i in range(1, 10):
                option_y = y + height + (i - 1) * option_height
                
                self.canvas.create_rectangle(
                    x, option_y,
                    x + width, option_y + option_height,
                    fill="#444444", outline=accent_color, width=1
                )
                
                self.canvas.create_text(
                    x + 10, option_y + option_height / 2,
                    text=str(i),
                    fill="white", font=("Arial", 12),
                    anchor="w"
                )
    
    def _render_shake_menu_content(self, width, height, accent_color):
        scroll_y = -self.menu_scroll_offset
        margin_left = 50
        
        self.canvas.create_text(
            margin_left, 100 + scroll_y,
            text="Shake Menu",
            fill=accent_color, font=("Arial", 32, "bold"),
            anchor="w"
        )
        
        dropdown_y = 180
        
        self.canvas.create_text(
            margin_left, dropdown_y + scroll_y,
            text="Shake Method:",
            fill="white", font=("Arial", 16, "bold"),
            anchor="w"
        )
        
        dropdown_x = margin_left + 180
        dropdown_width = 150
        dropdown_height = 35
        current_method = self.storage.get_shake_setting("shake_method")
        
        self.canvas.create_rectangle(
            dropdown_x, dropdown_y + scroll_y,
            dropdown_x + dropdown_width, dropdown_y + dropdown_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        self.canvas.create_text(
            dropdown_x + 10, dropdown_y + dropdown_height / 2 + scroll_y,
            text=current_method,
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        arrow_x = dropdown_x + dropdown_width - 20
        arrow_y = dropdown_y + dropdown_height / 2 + scroll_y
        self.canvas.create_text(
            arrow_x, arrow_y,
            text="▼",
            fill=accent_color, font=("Arial", 10)
        )
        
        if self.dropdown_open == "shake_method":
            options = ["Pixel", "Navigation"]
            option_height = 30
            
            for i, option in enumerate(options):
                option_y = dropdown_y + dropdown_height + i * option_height + scroll_y
                
                self.canvas.create_rectangle(
                    dropdown_x, option_y,
                    dropdown_x + dropdown_width, option_y + option_height,
                    fill="#444444", outline=accent_color, width=1
                )
                
                self.canvas.create_text(
                    dropdown_x + 10, option_y + option_height / 2,
                    text=option,
                    fill="white", font=("Arial", 12),
                    anchor="w"
                )
        
        content_y = 280
        
        if current_method == "Pixel":
            self._render_pixel_shake_content(margin_left, content_y, accent_color, scroll_y)
        elif current_method == "Navigation":
            self._render_navigation_shake_content(margin_left, content_y, accent_color, scroll_y)
    
    def _render_pixel_shake_content(self, x, y, accent_color, scroll_y):
        self.canvas.create_text(
            x, y + scroll_y,
            text="Pixel Shake Method",
            fill=accent_color, font=("Arial", 18, "bold"),
            anchor="w"
        )
        
        friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
        white_tolerance = self.storage.get_shake_setting("white_color_tolerance")
        duplicate_bypass = self.storage.get_shake_setting("duplicate_pixel_bypass")
        fail_timeout = self.storage.get_shake_setting("fail_shake_timeout")
        double_click = self.storage.get_shake_setting("double_click")
        double_click_delay = self.storage.get_shake_setting("double_click_delay")
        
        current_y = y + 50
        line_height = 60
        control_x = x + 350
        button_width = 30
        button_height = 25
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Friend Color Tolerance:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_numeric_control(control_x, current_y + scroll_y, friend_tolerance, 
                                     button_width, button_height, accent_color)
        current_y += line_height
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"White Color Tolerance:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_numeric_control(control_x, current_y + scroll_y, white_tolerance, 
                                     button_width, button_height, accent_color)
        current_y += line_height
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Duplicate Pixel Bypass:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_delay_control(control_x, current_y + scroll_y, duplicate_bypass, 
                                   button_width, button_height, accent_color, suffix="s")
        current_y += line_height
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Fail Shake Timeout:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_delay_control(control_x, current_y + scroll_y, fail_timeout, 
                                   button_width, button_height, accent_color, suffix="s")
        current_y += line_height
        
        checkbox_size = 20
        checkbox_x = x
        checkbox_y = current_y + scroll_y
        
        self.canvas.create_rectangle(
            checkbox_x, checkbox_y,
            checkbox_x + checkbox_size, checkbox_y + checkbox_size,
            fill="#333333", outline=accent_color, width=2
        )
        
        if double_click:
            self.canvas.create_text(
                checkbox_x + checkbox_size / 2, checkbox_y + checkbox_size / 2,
                text="✓",
                fill=accent_color, font=("Arial", 14, "bold")
            )
        
        self.canvas.create_text(
            checkbox_x + checkbox_size + 10, checkbox_y + checkbox_size / 2,
            text="Double Click",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        current_y += line_height
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Double Click Delay:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_numeric_control(control_x, current_y + scroll_y, double_click_delay, 
                                     button_width, button_height, accent_color, suffix="ms")
    
    def _render_numeric_control(self, x, y, value, button_width, button_height, accent_color, suffix=""):
        box_width = 80
        self.canvas.create_rectangle(
            x, y - button_height / 2,
            x + box_width, y + button_height / 2,
            fill="#333333", outline=accent_color, width=2
        )
        
        display_text = f"{value}{suffix}" if suffix else str(value)
        self.canvas.create_text(
            x + box_width / 2, y,
            text=display_text,
            fill="white", font=("Arial", 12, "bold")
        )
        
        minus_x = x - button_width - 10
        self.canvas.create_rectangle(
            minus_x, y - button_height / 2,
            minus_x + button_width, y + button_height / 2,
            fill="#444444", outline=accent_color, width=2
        )
        self.canvas.create_text(
            minus_x + button_width / 2, y,
            text="-",
            fill="white", font=("Arial", 16, "bold")
        )
        
        plus_x = x + box_width + 10
        self.canvas.create_rectangle(
            plus_x, y - button_height / 2,
            plus_x + button_width, y + button_height / 2,
            fill="#444444", outline=accent_color, width=2
        )
        self.canvas.create_text(
            plus_x + button_width / 2, y,
            text="+",
            fill="white", font=("Arial", 16, "bold")
        )
    
    def _render_delay_control(self, x, y, value, button_width, button_height, accent_color, suffix="s", decimals=1):
        box_width = 80
        self.canvas.create_rectangle(
            x, y - button_height / 2,
            x + box_width, y + button_height / 2,
            fill="#333333", outline=accent_color, width=2
        )
        
        if decimals == 2:
            display_text = f"{value:.2f}{suffix}"
        else:
            display_text = f"{value:.1f}{suffix}"
        
        self.canvas.create_text(
            x + box_width / 2, y,
            text=display_text,
            fill="white", font=("Arial", 12, "bold")
        )
        
        minus_x = x - button_width - 10
        self.canvas.create_rectangle(
            minus_x, y - button_height / 2,
            minus_x + button_width, y + button_height / 2,
            fill="#444444", outline=accent_color, width=2
        )
        self.canvas.create_text(
            minus_x + button_width / 2, y,
            text="-",
            fill="white", font=("Arial", 16, "bold")
        )
        
        plus_x = x + box_width + 10
        self.canvas.create_rectangle(
            plus_x, y - button_height / 2,
            plus_x + button_width, y + button_height / 2,
            fill="#444444", outline=accent_color, width=2
        )
        self.canvas.create_text(
            plus_x + button_width / 2, y,
            text="+",
            fill="white", font=("Arial", 16, "bold")
        )
    
    def _render_navigation_shake_content(self, x, y, accent_color, scroll_y):
        self.canvas.create_text(
            x, y + scroll_y,
            text="Navigation Shake Method",
            fill=accent_color, font=("Arial", 18, "bold"),
            anchor="w"
        )
        
        friend_tolerance = self.storage.get_shake_setting("friend_color_tolerance")
        fail_timeout = self.storage.get_shake_setting("fail_shake_timeout")
        
        current_y = y + 50
        line_height = 60
        control_x = x + 350
        button_width = 30
        button_height = 25
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Friend Color Tolerance:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_numeric_control(control_x, current_y + scroll_y, friend_tolerance, 
                                     button_width, button_height, accent_color)
        current_y += line_height
        
        self.canvas.create_text(
            x, current_y + scroll_y,
            text=f"Fail Shake Timeout:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        self._render_delay_control(control_x, current_y + scroll_y, fail_timeout, 
                                   button_width, button_height, accent_color, suffix="s")
    
    def _render_fish_menu_content(self, width, height, accent_color):
        scroll_y = -self.menu_scroll_offset
        margin_left = 50
        
        self.canvas.create_text(
            margin_left, 100 + scroll_y,
            text="Fish Menu - Bang-Bang Controller",
            fill=accent_color, font=("Arial", 28, "bold"),
            anchor="w"
        )
        
        self.canvas.create_text(
            margin_left, 140 + scroll_y,
            text="AI-powered bar control system that learns your game physics automatically",
            fill="#888888", font=("Arial", 11, "italic"),
            anchor="w"
        )
        
        current_y = 180
        line_height = 70
        control_x = margin_left + 440
        button_width = 30
        button_height = 25
        desc_max_width = 420
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="YOLO Model:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        dropdown_x = margin_left + 150
        dropdown_width = 200
        dropdown_height = 35
        current_model = self.storage.get_fish_setting("rod_model")
        
        self.canvas.create_rectangle(
            dropdown_x, current_y + scroll_y,
            dropdown_x + dropdown_width, current_y + dropdown_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        display_model = current_model if len(current_model) <= 25 else current_model[:22] + "..."
        self.canvas.create_text(
            dropdown_x + 10, current_y + dropdown_height / 2 + scroll_y,
            text=display_model,
            fill="white", font=("Arial", 12, "bold"),
            anchor="w"
        )
        
        arrow_x = dropdown_x + dropdown_width - 20
        self.canvas.create_text(
            arrow_x, current_y + dropdown_height / 2 + scroll_y,
            text="▼",
            fill=accent_color, font=("Arial", 10)
        )
        
        if self.fish_rod_model_dropdown_open:
            import os
            import sys
            
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
            
            model_files = [f for f in os.listdir(current_dir) if f.endswith('.pt')]
            
            if not model_files:
                model_files = ["No Models Found"]
            
            option_height = 30
            for i, model in enumerate(model_files):
                option_y = current_y + dropdown_height + 5 + (i * option_height) + scroll_y
                
                is_hovered = (dropdown_x < self.mouse_x < dropdown_x + dropdown_width and
                             option_y < self.mouse_y < option_y + option_height)
                
                bg_color = "#555555" if is_hovered else "#333333"
                
                self.canvas.create_rectangle(
                    dropdown_x, option_y,
                    dropdown_x + dropdown_width, option_y + option_height,
                    fill=bg_color, outline=accent_color, width=1
                )
                
                display_name = model if len(model) <= 25 else model[:22] + "..."
                self.canvas.create_text(
                    dropdown_x + 10, option_y + option_height / 2,
                    text=display_name,
                    fill="white", font=("Arial", 11),
                    anchor="w"
                )
        
        current_y += line_height + 10
        
        tolerance = self.storage.get_fish_setting("tolerance_pixels")
        base_res = self.storage.get_fish_setting("base_resolution_width")
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="Target Tolerance:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        self.canvas.create_text(
            margin_left, current_y + 22 + scroll_y,
            text=f"How close is 'close enough' (±{tolerance}px at {base_res}p, auto-scales)",
            fill="#888888", font=("Arial", 10),
            anchor="w", width=desc_max_width
        )
        
        self._render_numeric_control(control_x, current_y + 10 + scroll_y, tolerance, 
                                     button_width, button_height, accent_color, suffix="px")
        current_y += line_height
        
        accel = self.storage.get_fish_setting("accel_init")
        accel_learned = self.storage.get_fish_setting("accel_learned")
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="Acceleration (Learning):",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        if accel_learned is not None:
            desc_text = f"Initial: {int(accel)} px/s² | Learned: {int(accel_learned)} px/s² ✓"
            desc_color = "#00ff88"
        else:
            desc_text = "Starting guess for bar acceleration (AI learns actual value)"
            desc_color = "#888888"
        
        self.canvas.create_text(
            margin_left, current_y + 22 + scroll_y,
            text=desc_text,
            fill=desc_color, font=("Arial", 10),
            anchor="w", width=desc_max_width
        )
        
        self._render_numeric_control(control_x, current_y + 10 + scroll_y, int(accel), 
                                     button_width, button_height, accent_color, suffix=" px/s²")
        current_y += line_height
        
        max_vel = self.storage.get_fish_setting("max_velocity_init")
        max_vel_learned = self.storage.get_fish_setting("max_velocity_learned")
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="Max Velocity (Learning):",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        if max_vel_learned is not None:
            desc_text = f"Initial: {int(max_vel)} px/s | Learned: {int(max_vel_learned)} px/s ✓"
            desc_color = "#00ff88"
        else:
            desc_text = "Starting guess for max speed (AI finds actual speed cap)"
            desc_color = "#888888"
        
        self.canvas.create_text(
            margin_left, current_y + 22 + scroll_y,
            text=desc_text,
            fill=desc_color, font=("Arial", 10),
            anchor="w", width=desc_max_width
        )
        
        self._render_numeric_control(control_x, current_y + 10 + scroll_y, int(max_vel), 
                                     button_width, button_height, accent_color, suffix=" px/s")
        current_y += line_height
        
        smoothing = self.storage.get_fish_setting("smoothing")
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="Velocity Smoothing:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        self.canvas.create_text(
            margin_left, current_y + 22 + scroll_y,
            text=f"Averages last {smoothing} readings (higher = smoother, slower response)",
            fill="#888888", font=("Arial", 10),
            anchor="w", width=desc_max_width
        )
        
        self._render_numeric_control(control_x, current_y + 10 + scroll_y, int(smoothing), 
                                     button_width, button_height, accent_color, suffix=" frames")
        current_y += line_height
        
        learning_rate = self.storage.get_fish_setting("learning_rate")
        
        self.canvas.create_text(
            margin_left, current_y + scroll_y,
            text="Learning Speed:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        self.canvas.create_text(
            margin_left, current_y + 22 + scroll_y,
            text="How fast AI adapts (0.95 = slow/stable, 0.50 = fast/reactive)",
            fill="#888888", font=("Arial", 10),
            anchor="w", width=desc_max_width
        )
        
        self._render_delay_control(control_x, current_y + 10 + scroll_y, learning_rate, 
                                   button_width, button_height, accent_color, suffix="", decimals=2)
        
        self.menu_content_height = current_y + 150
    
    def _render_discord_menu_content(self, width, height, accent_color):
        scroll_y = -self.menu_scroll_offset
        margin_left = 50
        
        self.canvas.create_text(
            margin_left, 100 + scroll_y,
            text="Discord Menu",
            fill=accent_color, font=("Arial", 32, "bold"),
            anchor="w"
        )
        
        checkbox_y = 180
        checkbox_size = 20
        is_active = self.storage.get_discord_setting("active")
        
        self.canvas.create_rectangle(
            margin_left, checkbox_y + scroll_y,
            margin_left + checkbox_size, checkbox_y + checkbox_size + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        if is_active:
            self.canvas.create_line(
                margin_left + 4, checkbox_y + 4 + scroll_y,
                margin_left + checkbox_size - 4, checkbox_y + checkbox_size - 4 + scroll_y,
                fill="#00ff00", width=3
            )
            self.canvas.create_line(
                margin_left + checkbox_size - 4, checkbox_y + 4 + scroll_y,
                margin_left + 4, checkbox_y + checkbox_size - 4 + scroll_y,
                fill="#00ff00", width=3
            )
        
        self.canvas.create_text(
            margin_left + checkbox_size + 15, checkbox_y + checkbox_size / 2 + scroll_y,
            text="Active",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        webhook_y = 240
        webhook_url = self.storage.get_discord_setting("webhook_url")
        
        self.canvas.create_text(
            margin_left, webhook_y + scroll_y,
            text="Webhook URL:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        input_x = margin_left
        input_y = webhook_y + 30
        input_width = 400
        input_height = 30
        
        self.canvas.create_rectangle(
            input_x, input_y + scroll_y,
            input_x + input_width, input_y + input_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        display_text = webhook_url if len(webhook_url) <= 50 else webhook_url[:47] + "..."
        if self.active_text_input == "webhook_url" and not display_text:
            display_text = "|"
        elif self.active_text_input == "webhook_url" and self.text_input_cursor_visible:
            display_text += "|"
        
        self.canvas.create_text(
            input_x + 10, input_y + input_height / 2 + scroll_y,
            text=display_text if display_text else "Enter webhook URL...",
            fill="white" if display_text else "#888888",
            font=("Arial", 11),
            anchor="w"
        )
        
        test_button_x = input_x + input_width + 20
        test_button_width = 80
        test_button_height = 30
        
        self.canvas.create_rectangle(
            test_button_x, input_y + scroll_y,
            test_button_x + test_button_width, input_y + test_button_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        self.canvas.create_text(
            test_button_x + test_button_width / 2, input_y + test_button_height / 2 + scroll_y,
            text="Test",
            fill="white", font=("Arial", 12, "bold")
        )
        
        loops_y = 340
        loops_value = self.storage.get_discord_setting("loops_per_screenshot")
        
        self.canvas.create_text(
            margin_left, loops_y + scroll_y,
            text="Loops per screenshot:",
            fill="white", font=("Arial", 14, "bold"),
            anchor="w"
        )
        
        loops_input_x = margin_left + 220
        loops_input_y = loops_y - 5
        loops_input_width = 80
        loops_input_height = 30
        
        self.canvas.create_rectangle(
            loops_input_x, loops_input_y + scroll_y,
            loops_input_x + loops_input_width, loops_input_y + loops_input_height + scroll_y,
            fill="#333333", outline=accent_color, width=2
        )
        
        loops_display = str(loops_value)
        if self.active_text_input == "loops_per_screenshot" and self.text_input_cursor_visible:
            loops_display += "|"
        
        self.canvas.create_text(
            loops_input_x + loops_input_width / 2, loops_input_y + loops_input_height / 2 + scroll_y,
            text=loops_display,
            fill="white", font=("Arial", 14, "bold")
        )
    
    def _update_nodes(self, width, height):
        for node in self.nodes:
            node.update(width, height)
            
            if not node.is_main and node.activation_strength > 0:
                node.activation_strength -= self.NODE_ACTIVATION_FADE_SPEED
                if node.activation_strength < 0:
                    node.activation_strength = 0
                    node.activation_color = None
    
    def _update_particles(self):
        for particle in self.particles:
            particle.update(self.nodes, self.CONNECTION_THRESHOLD)
    
    def _draw_connections(self):
        current_connections = set()
        
        for i, node1 in enumerate(self.nodes):
            for node2 in self.nodes[i+1:]:
                distance = node1.distance_to(node2)
                if distance < self.CONNECTION_THRESHOLD:
                    conn_id = (id(node1), id(node2)) if id(node1) < id(node2) else (id(node2), id(node1))
                    current_connections.add(conn_id)
                    self.draw_connection(node1, node2, distance)
        
        return current_connections
    
    def _cleanup_connection_animations(self, current_connections):
        disconnected = set(self.connection_animations.keys()) - current_connections
        for conn_id in disconnected:
            del self.connection_animations[conn_id]
    
    def _draw_small_nodes(self):
        for node in self.nodes:
            if not node.is_main:
                self.draw_node(node)
    
    def _draw_particles(self):
        for particle in self.particles:
            self.draw_particle(particle)
    
    def _draw_main_nodes(self):
        for node in self.nodes:
            if node.is_main:
                self.draw_node(node)


if __name__ == "__main__":
    app = NeuralNetworkGUI()
    app.mainloop()
