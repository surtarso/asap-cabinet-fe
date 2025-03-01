# animations.py
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

def create_fade_animation(effect, duration, start_value, end_value, easing_curve):
    """
    Create and return a QPropertyAnimation for fading an effect.
    """
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(start_value)
    animation.setEndValue(end_value)
    animation.setEasingCurve(easing_curve)
    return animation

def create_loop_fade_animation(effect, duration, key_value=1.0):
    """
    Create and start a looping fade animation (used for arrow hints).
    The animation fades from 0 to a key value and back to 0 indefinitely.
    """
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setKeyValueAt(0.5, key_value)  # Fully visible halfway through
    animation.setEndValue(0.0)
    animation.setLoopCount(-1)  # Loop indefinitely
    animation.start()
    return animation
