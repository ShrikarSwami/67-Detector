# **67-Detector 🎉🖐️💥**
So… I accidentally made the most unhinged hand-tracking program ever.  
If you’ve ever wanted your computer to celebrate your 6-7 motion like it's a TikTok velocity edit from 2019, congratulations — this is exactly that.

Demo video 🡆 https://youtu.be/Ia8huYv7qrs  
(yes, it’s as chaotic as it looks)

---

## **✨ What This Actually Does (Friend to Friend Explanation)**

Alright, here’s the deal:

You wave your hands up and down a few times (like doing a **6-7 dance**).  
The program goes:

> “OH BET? YOU'RE LOCKED IN??”  

It starts flashing your webcam feed, blasting music, and after about 5 seconds of pure certified movement, your screen will suddenly get hit with an **avalanche of GIF popup windows**.

They move.  
They shuffle.  
They multiply.  
They behave like a virus except they’re just memes.

If you stop moving?  
Everything resets like nothing happened.

It’s essentially a **boss battle intro animation** but activated by your hands.

---

## **🔥 Features (Gently Explained)**

- Tracks your hands live using MediaPipe  
- Detects the up-down 6→7 motion  
- Flashes like a TikTok velocity edit  
- Plays **six_seven_theme.mp3**  
- After 5 seconds of hype, spams your screen with **GIF pop-ups**  
- Pop-ups move around randomly like chaotic fireworks  
- Auto resets when you stop moving  
- Works on **macOS** and **Windows**  
- Makes you question your life choices (in a fun way)  

---

## **📂 Folder Layout**

```
67-Detector/
│
├── sixty_seven_detector.py
├── six_seven_theme.mp3
├── requirements.txt
├── popups/
│   ├── popup1.gif
│   ├── popup2.gif
│   ├── popup3.gif
│   └── (put all your cursed gifs here)
└── README.md
```

---

## **🍎 macOS Install (Easy Mode)**

Open Terminal:

```bash
cd /path/to/67-Detector
```

Make a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install stuff:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Run it:

```bash
python sixty_seven_detector.py
```

If you see:

```
No module named _tkinter
```

Don’t panic — the app just uses a default resolution.

---

## **🪟 Windows Install (Also Easy Mode)**

Open CMD or PowerShell:

```cmd
cd C:\path\to\67-Detector
```

Make a virtual environment:

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

Install things:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

Run it:

```cmd
python sixty_seven_detector.py
```

---

## **🎵 Before You Run**

Make sure you have:

- You put **six_seven_theme.mp3** in the main folder  
- You put all your GIFs inside the **popups/** folder  
- Your webcam is plugged in unless you enjoy error messages  

---

## **💥 How To 67 Properly**

1. Stand in front of your webcam  
2. Lift both hands  
3. Move them **up-down-up-down**  
4. After 4 direction changes → you officially “67’ed"  
5. Music starts, screen flashes  
6. 5 seconds later → **GIF POPUP APOCALYPSE**  
7. Stop moving → everything disappears  

Keyboard shortcuts:
- **M** → turn music on/off  
- **Q** → quit if things get too real  

---

## **🧪 Troubleshooting (aka Why Is My Laptop Screaming?)**

### **❓ The GIF popups don’t show**
- Make sure your **popups/** folder exists  
- Make sure the files are actually GIF, PNG, or JPG  
- Avoid insanely large GIFs (200MB anime edits will kill your FPS)

### **❓ Music doesn’t play**
- Ensure the file is named **six_seven_theme.mp3**  
- Check your system audio output  
- On macOS, sometimes Python loses audio permissions — restart Terminal  

### **❓ Hand tracking is glitchy**
- Add more light in your room  
- Move your hands slower at first  
- macOS webcam drivers sometimes cap FPS — it’s normal  

### **❓ The program crashes randomly**
Your GIFs might be *too* high resolution.  
I wish I were joking.

### **❓ My screen got covered by popups and I can’t click anything**
Press **Q** in the webcam window.  
All popups should close.

If they don’t:
- Press **Command + Q** (macOS)  
- Press **Alt + F4** (Windows)  
- Worst case:  
  *Hold power button.*  

(This is the true 67 experience)

---

## **⭐ Final Notes**

This project is meant to be fun, chaotic, and slightly cursed.  
If you enjoyed it, laughed, or your laptop started sounding like a spaceship:

**Please star the repo ⭐ — it genuinely helps.**

Enjoy the madness, king 😎  
