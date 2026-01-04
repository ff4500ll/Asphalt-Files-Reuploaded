# Gameplay Machine Learning System

A Python-based system that records your gameplay actions and uses machine learning to learn your playing patterns. The system can capture keyboard inputs, mouse movements, clicks, and screen states to build a comprehensive dataset of your gameplay behavior.

## Features

- **Real-time Action Recording**: Captures keyboard, mouse, and screen data while you play
- **Hotkey Controls**: F1 to start recording, F2 to stop, F3 to exit
- **Machine Learning Models**: Trains both traditional ML (Random Forest) and deep learning (LSTM) models
- **Pattern Analysis**: Analyzes your gameplay patterns and provides insights
- **Multiple Session Support**: Record multiple gameplay sessions for better learning

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Main Program**:
   ```bash
   python main.py
   ```

3. **Record Gameplay**:
   - Choose option 1 from the menu
   - Start your game
   - Press F1 to begin recording
   - Play normally
   - Press F2 to stop recording
   - Press F3 to exit

4. **Train ML Models**:
   - Choose option 2 from the menu
   - The system will analyze your recorded data and train models

## How Much Gameplay Data Do You Need?

### Minimum Viable Training:
- **15-30 minutes**: Basic pattern recognition
- **1000-5000 actions**: Simple behavior modeling

### Recommended for Good Results:
- **1-2 hours**: Across multiple sessions
- **5000-20000 actions**: Reliable pattern learning
- **Different scenarios**: Combat, exploration, menus, etc.

### Optimal Performance:
- **3+ hours**: Comprehensive gameplay coverage
- **20000+ actions**: Advanced behavior prediction
- **Diverse sessions**: Various game situations and strategies

## File Structure

```
gameplay_data/
├── sessions/           # Recorded gameplay sessions
│   ├── 20241011_143022.json
│   ├── 20241011_143022.pkl
│   └── screenshots/
└── models/            # Trained ML models
    ├── action_predictor.pkl
    ├── sequence_model.h5
    └── training_history.png
```

## Controls During Recording

- **F1**: Start recording session
- **F2**: Stop current recording session
- **F3**: Exit the recording program

## What Gets Recorded

### Input Actions:
- Keyboard key presses and releases
- Mouse clicks and movements
- Timestamps for all actions

### Visual Data:
- Screenshots at configurable intervals (default: 5 FPS)
- Screen region can be customized

### Metadata:
- Session duration
- Action counts and types
- Performance statistics

## Machine Learning Models

### 1. Action Predictor (Random Forest)
- Predicts next action type based on recent inputs
- Fast training and inference
- Good for real-time prediction

### 2. Sequence Model (LSTM Neural Network)
- Learns complex temporal patterns
- Better for long-term behavior modeling
- More accurate but requires more data

## Tips for Better Results

1. **Consistent Gameplay**: Play naturally, avoid random clicking
2. **Multiple Sessions**: Record several shorter sessions vs one long session
3. **Diverse Scenarios**: Record different parts of the game
4. **Stable Environment**: Keep game window visible and consistent
5. **Regular Patterns**: The more consistent your playstyle, the better the learning

## Troubleshooting

### Common Issues:
- **Hotkeys not working**: Run as administrator
- **Mouse/keyboard not captured**: Check antivirus settings
- **High memory usage**: Reduce screenshot frame rate
- **Training fails**: Need more recorded data

### Performance Optimization:
- Adjust screenshot frame rate in `gameplay_recorder.py`
- Modify sequence length in `gameplay_learner.py`
- Use screen region instead of full screen capture

## Technical Details

### Dependencies:
- `numpy`: Numerical computing
- `opencv-python`: Image processing
- `keyboard`: Keyboard input capture
- `mouse`: Mouse input capture
- `pillow`: Screenshot capture
- `scikit-learn`: Traditional ML models
- `tensorflow`: Deep learning models

### Data Format:
Sessions are saved in JSON format with the following structure:
```json
{
  "metadata": {
    "session_id": "20241011_143022",
    "duration": 156.78,
    "total_actions": 1247
  },
  "actions": [
    {
      "timestamp": 0.123,
      "type": "key_press",
      "key": "w"
    }
  ]
}
```

## Future Enhancements

- Real-time gameplay replay functionality
- Advanced computer vision for game state recognition
- Multi-game support and transfer learning
- Web interface for easier interaction
- Cloud storage for session data

## Requirements

- Python 3.7+
- Windows (for keyboard/mouse capture)
- At least 2GB RAM
- 1GB free disk space (for recordings)

## License

This project is for educational and research purposes. Make sure you comply with game terms of service when recording gameplay.