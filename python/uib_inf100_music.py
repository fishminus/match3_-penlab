import pygame as _pygame

# For å starte lydmikseren til pygame. Mikseren kan spille av
# flere lyder samtidig.
_pygame.mixer.init()
_loopingSounds = []

# En klasse. Objekter i denne klassen representerer en enkelt lyd
# som spilles av én gang for hvert kall til play-metoden.
class _SoundEffect():
    def __init__(self, path):
        self.path = path
        self._sound = _pygame.mixer.Sound(path)

    def play(self):
        ''' Starts playing the sound. '''
        self._sound.play()

    def set_volume(self, volume):
        ''' Set the volume of the sound. The volume should be a float
        between 0.0 and 1.0, where 0.0 is silent and 1.0 is full volume.
        '''
        self._sound.set_volume(volume)

    def get_volume(self):
        ''' Returns the current volume of the sound. '''
        return self._sound.get_volume()

# En klasse. Objekter i denne klassen representerer en lyd som 
# spilles i en evig løkke helt til den stoppes.
class _LoopingSound(_SoundEffect):
    def __init__(self, path):
        global _loopingSounds
        super().__init__(path)
        self._is_playing = False
        _loopingSounds.append(self)

    def is_playing(self):
        ''' Returns True if the sound is currently playing, and False
        otherwise.
        '''
        return self._is_playing

    def play(self):
        ''' Starts playing the sound in an infinite loop. '''
        self._sound.play(loops=-1)
        self._is_playing = True
        
    def stop(self):
        ''' Stop playing the sound. '''
        self._sound.stop()
        self._is_playing = False

# I INF100 lærer vi ikke om klasser, så vi maskerer dem som funksjoner i stedet
def load_sound_effect(path):
    return _SoundEffect(path)

def load_looping_sound(path):
    return _LoopingSound(path)

def stop_all_sounds():
    ''' Stop all sounds currently playing. '''
    global _loopingSounds
    for sound in _loopingSounds:
        sound.stop()
    _pygame.mixer.stop()
