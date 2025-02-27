import pygame
import os

class SoundManager:
    def __init__(self):
        # Make sure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 2048)
        
        self.sounds = {}
        self.current_music = None
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.background_music = pygame.mixer.Sound("assets/background-music.wav")
        print("Sound manager initialized")
    
    def load_sound(self, name, path):
        """Load a sound effect"""
        try:
            if not os.path.exists(path):
                print(f"Sound file not found: {path}")
                return False
                
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sound_volume)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"Error loading sound {path}: {str(e)}")
            return False
    
    def play_sound(self, name):
        """Play a loaded sound effect"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sound {name}: {str(e)}")
    
    def load_music(self, path):
        """Load and play background music"""
        try:
            if not os.path.exists(path):
                print(f"Music file not found: {path}")
                return False
                
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            self.current_music = path
            return True
        except Exception as e:
            print(f"Error loading music {path}: {str(e)}")
            return False
    
    def play_music(self, loop=True):
        """Start playing the loaded music"""
        if self.current_music:
            try:
                pygame.mixer.music.play(-1 if loop else 0)
            except Exception as e:
                print(f"Error playing music: {str(e)}")
    
    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)

    def play_background_music(self):
        self.background_music.play(-1)  # Loop indefinitely
