import json
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Neural network features will be disabled.")
import cv2
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd

class GameplayLearner:
    def __init__(self, data_dir="gameplay_data"):
        """
        Initialize the gameplay learning system
        
        Args:
            data_dir: Directory containing recorded gameplay sessions
        """
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.model_dir = os.path.join(data_dir, "models")
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Data storage
        self.session_data = []
        self.sequences = []
        self.labels = []
        
        # Models
        self.action_predictor = None
        self.sequence_model = None
        
        print("🤖 Gameplay Learner Initialized!")
        
    def load_all_sessions(self):
        """Load all recorded gameplay sessions"""
        if not os.path.exists(self.sessions_dir):
            print("No sessions directory found. Record some gameplay first!")
            return False
            
        session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.json')]
        
        if not session_files:
            print("No recorded sessions found!")
            return False
            
        print(f"Loading {len(session_files)} sessions...")
        
        for session_file in session_files:
            try:
                session_path = os.path.join(self.sessions_dir, session_file)
                with open(session_path, 'r') as f:
                    session = json.load(f)
                    self.session_data.append(session)
                    print(f"✓ Loaded {session_file}")
                    
            except Exception as e:
                print(f"✗ Error loading {session_file}: {e}")
                
        print(f"Successfully loaded {len(self.session_data)} sessions")
        return True
        
    def preprocess_data(self):
        """Convert recorded sessions into ML-ready features"""
        print("\n🔄 Preprocessing gameplay data...")
        
        all_sequences = []
        all_labels = []
        
        for session in self.session_data:
            actions = session['actions']
            sequence = self._extract_features_from_session(actions)
            
            if len(sequence) > 0:
                all_sequences.extend(sequence)
                
        self.sequences = np.array(all_sequences)
        print(f"Created {len(self.sequences)} feature sequences")
        
        return len(self.sequences) > 0
        
    def _extract_features_from_session(self, actions):
        """Extract features from a single session"""
        sequences = []
        current_sequence = []
        sequence_length = 10  # Look at last 10 actions to predict next
        
        # Define feature mapping
        key_to_id = {}
        button_to_id = {}
        action_type_to_id = {
            'key_press': 0,
            'key_release': 1, 
            'mouse_click': 2,
            'mouse_move': 3,
            'screenshot': 4
        }
        
        for i, action in enumerate(actions):
            if action['type'] == 'screenshot':
                continue  # Skip screenshots for now
                
            # Create feature vector for this action
            features = [
                action['timestamp'],
                action_type_to_id.get(action['type'], -1)
            ]
            
            # Add action-specific features
            if action['type'] in ['key_press', 'key_release']:
                key = action.get('key', 'unknown')
                if key not in key_to_id:
                    key_to_id[key] = len(key_to_id)
                features.extend([key_to_id[key], 0, 0])  # key_id, x, y
                
            elif action['type'] in ['mouse_click', 'mouse_move']:
                features.extend([
                    -1,  # no key
                    action.get('x', 0),
                    action.get('y', 0)
                ])
                
                if action['type'] == 'mouse_click':
                    button = action.get('button', 'unknown')
                    if button not in button_to_id:
                        button_to_id[button] = len(button_to_id)
                    features.append(button_to_id[button])
                else:
                    features.append(-1)  # no button for mouse move
            else:
                features.extend([-1, 0, 0, -1])
                
            current_sequence.append(features)
            
            # Create training sequences
            if len(current_sequence) >= sequence_length:
                # Use last sequence_length-1 actions to predict the current action
                input_seq = current_sequence[-(sequence_length):-1]
                target_action = current_sequence[-1]
                
                sequences.append({
                    'input': input_seq,
                    'target': target_action
                })
                
        return sequences
        
    def train_action_predictor(self):
        """Train a model to predict next actions"""
        if len(self.sequences) == 0:
            print("No sequences available for training!")
            return False
            
        print("\n🧠 Training action prediction model...")
        
        # Prepare training data
        X = []
        y = []
        
        for seq in self.sequences:
            # Flatten input sequence
            input_features = np.array(seq['input']).flatten()
            target_features = seq['target']
            
            X.append(input_features)
            y.append(target_features[1])  # Predict action type
            
        X = np.array(X)
        y = np.array(y)
        
        print(f"Training data shape: X={X.shape}, y={y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest model
        self.action_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        self.action_predictor.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.action_predictor.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Action Predictor Accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        model_path = os.path.join(self.model_dir, "action_predictor.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(self.action_predictor, f)
            
        print(f"Model saved to {model_path}")
        return True
        
    def train_neural_network(self):
        """Train a neural network for sequence prediction"""
        if not TENSORFLOW_AVAILABLE:
            print("❌ TensorFlow not available. Skipping neural network training.")
            print("To enable neural networks, install TensorFlow: pip install tensorflow")
            return False
            
        if len(self.sequences) == 0:
            print("No sequences available for training!")
            return False
            
        print("\n🧠 Training neural network model...")
        
        # Prepare data for neural network
        sequence_length = 9  # Input sequence length
        feature_dim = 6  # Number of features per action
        
        X = []
        y = []
        
        for seq in self.sequences:
            if len(seq['input']) == sequence_length:
                # Pad or truncate sequences to fixed length
                input_seq = np.array(seq['input'])
                if input_seq.shape[0] == sequence_length and input_seq.shape[1] == feature_dim:
                    X.append(input_seq)
                    y.append(seq['target'])
                    
        if len(X) == 0:
            print("No valid sequences for neural network training!")
            return False
            
        X = np.array(X)
        y = np.array(y)
        
        print(f"Neural network data shape: X={X.shape}, y={y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Build neural network
        model = keras.Sequential([
            keras.layers.LSTM(64, return_sequences=True, input_shape=(sequence_length, feature_dim)),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(feature_dim, activation='linear')  # Predict next action features
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            verbose=1
        )
        
        # Save model
        model_path = os.path.join(self.model_dir, "sequence_model.h5")
        model.save(model_path)
        self.sequence_model = model
        
        print(f"Neural network model saved to {model_path}")
        
        # Plot training history
        self._plot_training_history(history)
        
        return True
        
    def _plot_training_history(self, history):
        """Plot training history"""
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.title('Model Mean Absolute Error')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        
        plt.tight_layout()
        plot_path = os.path.join(self.model_dir, "training_history.png")
        plt.savefig(plot_path)
        plt.show()
        
        print(f"Training history plot saved to {plot_path}")
        
    def analyze_gameplay_patterns(self):
        """Analyze patterns in recorded gameplay"""
        print("\n📊 Analyzing gameplay patterns...")
        
        all_actions = []
        for session in self.session_data:
            all_actions.extend(session['actions'])
            
        # Count action types
        action_counts = defaultdict(int)
        key_counts = defaultdict(int)
        mouse_positions = []
        timestamps = []
        
        for action in all_actions:
            action_counts[action['type']] += 1
            timestamps.append(action['timestamp'])
            
            if action['type'] in ['key_press', 'key_release']:
                key_counts[action.get('key', 'unknown')] += 1
            elif action['type'] in ['mouse_click', 'mouse_move']:
                mouse_positions.append((action.get('x', 0), action.get('y', 0)))
                
        # Print analysis
        print(f"Total actions recorded: {len(all_actions)}")
        print(f"Action type distribution:")
        for action_type, count in sorted(action_counts.items()):
            print(f"  {action_type}: {count} ({count/len(all_actions)*100:.1f}%)")
            
        print(f"\nMost used keys:")
        for key, count in sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {key}: {count}")
            
        if mouse_positions:
            mouse_positions = np.array(mouse_positions)
            print(f"\nMouse activity area:")
            print(f"  X range: {mouse_positions[:,0].min():.0f} - {mouse_positions[:,0].max():.0f}")
            print(f"  Y range: {mouse_positions[:,1].min():.0f} - {mouse_positions[:,1].max():.0f}")
            
        return {
            'total_actions': len(all_actions),
            'action_counts': dict(action_counts),
            'key_counts': dict(key_counts),
            'mouse_positions': mouse_positions
        }
        
    def load_models(self):
        """Load previously trained models"""
        # Load action predictor
        action_model_path = os.path.join(self.model_dir, "action_predictor.pkl")
        if os.path.exists(action_model_path):
            with open(action_model_path, 'rb') as f:
                self.action_predictor = pickle.load(f)
            print("✓ Loaded action predictor model")
        else:
            print("✗ Action predictor model not found")
            
        # Load neural network
        nn_model_path = os.path.join(self.model_dir, "sequence_model.h5")
        if os.path.exists(nn_model_path) and TENSORFLOW_AVAILABLE:
            self.sequence_model = keras.models.load_model(nn_model_path)
            print("✓ Loaded neural network model")
        else:
            if not TENSORFLOW_AVAILABLE:
                print("✗ Neural network model requires TensorFlow")
            else:
                print("✗ Neural network model not found")

def main():
    """Main function for the gameplay learner"""
    print("🤖 Gameplay Learner - ML Model Training")
    print("=" * 50)
    
    learner = GameplayLearner()
    
    # Load recorded sessions
    if not learner.load_all_sessions():
        print("No gameplay data found. Please record some sessions first!")
        return
        
    # Analyze patterns
    patterns = learner.analyze_gameplay_patterns()
    
    # Preprocess data
    if not learner.preprocess_data():
        print("Failed to preprocess data!")
        return
        
    # Train models
    print("\nStarting model training...")
    
    # Train action predictor
    learner.train_action_predictor()
    
    # Train neural network
    learner.train_neural_network()
    
    print("\n✅ Training complete!")
    print("Models have been saved and can be used for gameplay prediction.")

if __name__ == "__main__":
    main()