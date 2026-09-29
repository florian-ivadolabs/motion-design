"""Synthesised score toolkit: import it from the film's audio.py.

    from synth import Score, I
    sc = Score(seconds=24, fps=30, bpm=120)
    sc.mix(sc.fs(0), I.kick(), .9); sc.sidechain(sc.fs(0))
    sc.mix(sc.fs(15), I.bass(41), .4, bus='music')
    sc.render('out/audio.wav')          # reverb, duck, tanh, fades, two-pass loudnorm -14 LUFS

Everything is placed by film frame (sc.fs(frame)) so sound and picture share one clock.
"""
import json, subprocess
import numpy as np

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FF = "ffmpeg"

SR = 44100
_rng = np.random.default_rng(11)
T = lambda d: np.arange(int(SR * d)) / SR
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
saw = lambda f, t, ph=0.0: 2 * ((f * t + ph) % 1) - 1


def lp(x, cut):
    """One-pole low-pass; cut (0..1) may vary per sample. Loop: keep it for short notes."""
    cut = np.broadcast_to(cut, x.shape); y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += cut[i] * (x[i] - s); y[i] = s
    return y


class I:
    """Instrument and SFX generators. Return mono (N,) or stereo (2, N) float arrays."""

    @staticmethod
    def kick():
        t = T(0.5); f = 50 * (1 + 3.2 * np.exp(-t * 32))
        x = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 6.5)
        x[:150] += _rng.standard_normal(150) * np.linspace(0.5, 0, 150)
        return x

    @staticmethod
    def clap():
        t = T(0.3); n = _rng.standard_normal(len(t)); n = n - lp(n, 0.06)
        env = sum(np.exp(-np.maximum(0, t - o) * 70) * (t >= o) for o in (0, 0.01, 0.02)) * 0.6 + np.exp(-t * 11) * 0.5
        return n * env

    @staticmethod
    def snare():
        t = T(0.18); n = _rng.standard_normal(len(t)); n = n - lp(n, 0.05)
        return (n * 0.8 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * np.exp(-t * 18)

    @staticmethod
    def hat(d=0.04, k=110):
        t = T(d); n = _rng.standard_normal(len(t)); return (n - lp(n, 0.5)) * np.exp(-t * k)

    @staticmethod
    def bass(m, d=0.2):
        t = T(d); f = hz(m)
        x = saw(f, t) + saw(f * 1.006, t, 0.3) + 0.6 * np.sin(np.pi * f * t)
        return lp(lp(x, 0.02 + 0.22 * np.exp(-t * 22)), 0.02 + 0.22 * np.exp(-t * 22)) * np.minimum(1, t / 0.003) * np.minimum(1, (d - t) / 0.01)

    @staticmethod
    def sub(m, d):
        t = T(d); return np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / 0.01) * np.minimum(1, np.maximum(0, d - t) / 0.05)

    @staticmethod
    def supersaw(ms, d, cut0=0.25, k=9, width=0.6):
        t = T(d); L = np.zeros_like(t); R = np.zeros_like(t)
        for m in ms:
            for v, det in enumerate(np.linspace(-0.012, 0.012, 7)):
                x = saw(hz(m) * (1 + det), t, _rng.random()); p = (v / 6 - 0.5) * width
                L += x * (0.5 - p); R += x * (0.5 + p)
        cut = 0.01 + cut0 * np.exp(-t * k)
        env = np.minimum(1, t / 0.004) * np.minimum(1, np.maximum(0, d - t) / 0.03)
        return np.stack([lp(L, cut), lp(R, cut)]) * env / (len(ms) * 7) * 2

    @staticmethod
    def pad(ms, d, cut=0.04):
        t = T(d); L = np.zeros_like(t); R = np.zeros_like(t)
        for m in ms:
            for v, det in enumerate((-0.008, -0.003, 0.003, 0.008)):
                (L if v % 2 else R)[:] += saw(hz(m) * (1 + det), t, _rng.random())
        env = np.minimum(1, t / 0.3) * np.minimum(1, np.maximum(0, d - t) / 0.3)
        return np.stack([lp(L, cut), lp(R, cut)]) * env / (len(ms) * 2)

    @staticmethod
    def pluck(m, d=0.12):
        t = T(d); f = hz(m)
        x = np.sign(np.sin(2 * np.pi * f * t)) * 0.6 + saw(f * 2.003, t) * 0.4
        return lp(x, 0.05 + 0.3 * np.exp(-t * 30)) * np.exp(-t * 14) * np.minimum(1, t / 0.002)

    @staticmethod
    def bell(m, d=2.5, k=2.2):
        t = T(d); f = hz(m)
        x = np.sin(2 * np.pi * f * t + 1.6 * np.exp(-t * 3) * np.sin(2 * np.pi * f * 3.5 * t)) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 4)
        return x * np.exp(-t * k) * np.minimum(1, t / 0.002)

    @staticmethod
    def sweep(d, lo, hi, shape=2.0, up=True):
        """Riser (up) or falling wash (down) of filtered noise."""
        t = T(d); n = _rng.standard_normal(len(t)); u = t / d
        cut = lo * (hi / lo) ** (u if up else 1 - u)
        return lp(n, cut) * (u ** shape if up else (1 - u) ** shape)

    @staticmethod
    def impact():
        t = T(2.2); f = 42 * (1 + 2.0 * np.exp(-t * 8))
        n = _rng.standard_normal(len(t))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) + (n - lp(n, 0.3)) * np.exp(-t * 3.5) * 0.35

    @staticmethod
    def swoosh(d=0.28):
        t = T(d); n = _rng.standard_normal(len(t)); u = t / d
        return lp(n, 0.02 + 0.5 * np.sin(np.pi * u) ** 2) * np.sin(np.pi * u) ** 1.5

    @staticmethod
    def blip(f0, d=0.09, up=1.8):
        t = T(d); f = f0 * (1 + (up - 1) * (1 - np.exp(-t * 60)))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)

    @staticmethod
    def thud(f0=90):
        t = T(0.25); f = f0 * (1 + 1.5 * np.exp(-t * 40))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)

    @staticmethod
    def tick(f0=2600, d=0.02):
        t = T(d); return np.sin(2 * np.pi * f0 * t) * np.exp(-t * 300)


class Score:
    def __init__(self, seconds, fps=30, bpm=120, tail=3.0):
        self.fps, self.bpm, self.len = fps, bpm, int(SR * seconds)
        self.N = self.len + int(SR * tail)
        self.dry = np.zeros((2, self.N)); self.music = np.zeros((2, self.N)); self.send = np.zeros((2, self.N))
        self.duck = np.ones(self.N)
        self.beat_frames = 60 * fps / bpm

    fs = lambda self, frame: frame / self.fps                     # film frame -> seconds
    beat = lambda self, b: self.fs(b * self.beat_frames)           # beat index -> seconds

    def mix(self, t, x, g=1.0, pan=0.0, rev=0.1, bus="dry"):
        i = int(t * SR)
        if i >= self.N or i < 0: return
        x = x[..., :self.N - i]
        if x.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4); x = np.stack([x * l, x * r])
        tgt = self.music if bus == "music" else self.dry
        tgt[:, i:i + x.shape[1]] += x * g; self.send[:, i:i + x.shape[1]] += x * g * rev

    def place_peak(self, t, x, g=1.0, pan=0.0, rev=0.1, bus="dry"):
        """Place a sample so its loudest point lands exactly on t (for stock SFX)."""
        pk = int(np.abs(x if x.ndim == 1 else x.sum(0)).argmax())
        self.mix(t - pk / SR, x, g, pan, rev, bus)

    def sidechain(self, t, depth=0.7, release=11):
        i = int(t * SR); L = min(int(0.4 * SR), self.N - i)
        if L <= 0: return
        e = 1 - depth * np.exp(-np.arange(L) / SR * release)
        self.duck[i:i + L] = np.minimum(self.duck[i:i + L], e)

    def voice(self, t, x, g=0.92):
        """Voice-over on the dry bus; call duck_under_voice() after placing all lines."""
        self.mix(t, x, g, 0, 0.03)
        self._voice = getattr(self, "_voice", np.zeros(self.N)); i = int(t * SR); n = min(len(x), self.N - i)
        self._voice[i:i + n] = np.maximum(self._voice[i:i + n], (np.abs(x[:n]) > 0.02).astype(float))

    def duck_under_voice(self, amount=0.65):
        if not hasattr(self, "_voice"): return
        k = np.ones(int(0.25 * SR)) / int(0.25 * SR)
        m = np.convolve(np.convolve(self._voice, k, "same"), k, "same")
        self.duck *= 1 - amount * np.clip(m, 0, 1)

    def render(self, path, reverb=0.3, drive=2.0, fade_out=0.6, lufs=-14):
        bus = self.dry + self.music * self.duck
        L = int(2.2 * SR); t = np.arange(L) / SR
        ir = lp(_rng.standard_normal(L) * np.exp(-t * 3.0), 0.3); ir /= np.sqrt(np.sum(ir ** 2))
        n = 1 << int(np.ceil(np.log2(self.N + L)))
        for c in range(2):
            bus[c] += np.fft.irfft(np.fft.rfft(self.send[c], n) * np.fft.rfft(ir, n), n)[:self.N] * reverb
        bus = bus[:, :self.len]; bus /= np.max(np.abs(bus)) + 1e-9
        bus = np.tanh(bus * drive) / np.tanh(drive)
        k = np.arange(self.len)
        bus *= np.minimum(1, k / (0.01 * SR)) * np.minimum(1, (self.len - k) / (fade_out * SR)) * 0.9
        raw = str(path) + ".raw.wav"
        subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw],
                       input=bus.T.astype(np.float32).tobytes(), check=True)
        m = subprocess.run([FF, "-hide_banner", "-i", raw, "-af", f"loudnorm=I={lufs}:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
        af = (f"loudnorm=I={lufs}:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
              f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.891:level=false")  # loudnorm can overshoot: cap at -1 dBTP
        subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), str(path)], check=True)
        return path

    def energy(self):
        """RMS per 2 s of the pre-master mix: check the arc (intro not silent, drop higher, breakdown dips)."""
        x = (self.dry + self.music * self.duck)[0, :self.len]; s = 2 * SR
        return [round(float(np.sqrt(np.mean(x[i:i + s] ** 2))), 3) for i in range(0, len(x), s)]


if __name__ == "__main__":  # smoke test: 8 s of four-on-the-floor with a drop at 4 s
    sc = Score(8, fps=30, bpm=120)
    for b in range(16):
        t = sc.beat(b)
        if b >= 8: sc.mix(t, I.kick(), .9); sc.sidechain(t); sc.mix(t + sc.beat(.5), I.bass(41), .4, bus="music")
        sc.mix(t, I.hat(), .1, .3)
    sc.mix(0, I.pad([65, 68, 72], 4.0), .5, bus="music"); sc.mix(4 - 2, I.sweep(2, .003, .4), .3); sc.mix(4, I.impact(), .8)
    print(sc.energy()); print(sc.render("synth_test.wav"))
