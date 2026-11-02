#!/usr/bin/env python3
"""Synthesise the short mechanical switch sounds used by SIM CONTROL STUDIO 0.4.0.
Original, procedurally generated audio: no recordings or third-party samples."""
import wave, sys
from pathlib import Path
import numpy as np
RATE = 44100
OUT = Path(__file__).resolve().parents[1] / 'mobile_flutter/assets/sounds'
rng = np.random.default_rng(404)

def env(n, attack=0.0008, decay=0.02):
    t = np.arange(n) / RATE
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-t / decay)

def tone(freq, length, decay, amp=1.0):
    n = int(RATE * length); t = np.arange(n) / RATE
    return amp * np.sin(2 * np.pi * freq * t) * np.exp(-t / decay)

def noise(length, decay, amp=1.0, lowpass=0.0):
    n = int(RATE * length); x = rng.standard_normal(n)
    if lowpass:
        k = max(1, int(lowpass)); x = np.convolve(x, np.ones(k) / k, mode='same')
    return amp * x * env(n, decay=decay)

def place(buffer, signal, at):
    start = int(at * RATE); end = min(len(buffer), start + len(signal))
    buffer[start:end] += signal[: end - start]

def render(name, parts, length):
    buf = np.zeros(int(RATE * length))
    for sig, at in parts: place(buf, sig, at)
    fade = np.ones_like(buf); tail = int(RATE * 0.006); fade[-tail:] = np.linspace(1, 0, tail)
    buf *= fade
    buf /= max(1e-9, np.abs(buf).max()); buf *= 0.85
    data = (buf * 32767).astype('<i2').tobytes()
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(data)

def metal(base):
    return [(noise(.012, .0018, 1.0), 0), (tone(base, .09, .018, .55), 0.0005), (tone(base * 1.47, .07, .012, .35), .0005),
            (tone(base * 2.31, .05, .008, .2), .0005), (tone(180, .05, .012, .45), 0), (noise(.008, .0012, .6), .016)]
OUT.mkdir(parents=True, exist_ok=True)
render('metal_toggle_on.wav', metal(2900), .11)
render('metal_toggle_off.wav', metal(2500), .11)
render('plastic_button.wav', [(noise(.03, .004, 1.0, lowpass=6), 0), (tone(1150, .03, .006, .4), 0), (noise(.02, .003, .5, lowpass=8), .028)], .07)
render('latching_switch.wav', [(noise(.02, .002, 1.0, lowpass=3), 0), (tone(2100, .04, .006, .4), 0), (noise(.02, .002, .9, lowpass=3), .026), (tone(1700, .04, .007, .35), .026)], .09)
render('rotary_detent.wav', [(noise(.008, .0009, 1.0, lowpass=2), 0), (tone(3400, .02, .003, .5), 0)], .035)
render('safety_cover.wav', [(noise(.06, .02, .25, lowpass=20), 0), (tone(420, .06, .02, .25), .005), (noise(.015, .002, 1.0, lowpass=3), .07), (tone(1900, .05, .009, .4), .07)], .14)
render('starter_button.wav', [(noise(.03, .004, 1.0, lowpass=10), 0), (tone(95, .12, .04, .8), 0), (tone(760, .05, .01, .35), 0), (noise(.01, .0015, .7, lowpass=2), .06), (tone(2600, .03, .005, .3), .06)], .16)
print('Generated', sorted(p.name for p in OUT.glob('*.wav')))
