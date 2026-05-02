# Lekce 168: Computer Vision — OpenCV

OpenCV je nejpopulárnější knihovna pro zpracování obrazu. Detekce hran, tváří, objektů, augmented reality.

---

## 🚀 Instalace

```bash
uv add opencv-python numpy pillow
```

---

## 🖼️ Základy — načtení a zobrazení

```python
import cv2
import numpy as np
from pathlib import Path


def vytvor_testovaci_obraz(sirka: int = 400, vyska: int = 300) -> np.ndarray:
    """Vytvoří testovací obraz s geometrickými tvary."""
    img = np.zeros((vyska, sirka, 3), dtype=np.uint8)
    img[:] = (50, 50, 50)   # šedé pozadí

    # Tvary
    cv2.rectangle(img, (50, 50), (150, 150), (255, 0, 0), 3)        # modrý čtverec
    cv2.circle(img, (250, 100), 50, (0, 255, 0), -1)                # zelený kruh
    cv2.ellipse(img, (320, 200), (60, 30), 45, 0, 360, (0, 0, 255), 2)  # červená elipsa
    cv2.line(img, (0, 250), (400, 250), (255, 255, 0), 2)            # čára
    cv2.putText(img, "OpenCV Demo", (100, 280),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return img


img = vytvor_testovaci_obraz()
print(f"Obraz: {img.shape}")   # (vyska, sirka, kanaly)

# Uložení
cv2.imwrite("/tmp/demo.jpg", img)
print("Obraz uložen do /tmp/demo.jpg")

# Načtení
nacteny = cv2.imread("/tmp/demo.jpg")
print(f"Načteno: {nacteny.shape}")
```

---

## 🎨 Barevné prostory a operace

```python
# Převod barevných prostorů
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # pro matplotlib

# Kanály
b, g, r = cv2.split(img)
print(f"B kanál: {b.shape}, max={b.max()}")

# Resize
malý = cv2.resize(img, (200, 150))
vetsi = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# Crop
vyrez = img[50:150, 50:200]   # [y1:y2, x1:x2]

# Flip
horizontalni = cv2.flip(img, 1)   # 1=horizontal, 0=vertical, -1=oboje

# Rotace
stred = (img.shape[1]//2, img.shape[0]//2)
M = cv2.getRotationMatrix2D(stred, 45, 1.0)
rotovany = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
```

---

## 🔍 Detekce hran a kontur

```python
# Rozostření (odstraní šum před detekcí hran)
blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
blur_median = cv2.medianBlur(img_gray, 5)

# Canny detektor hran
hrany = cv2.Canny(blur, threshold1=50, threshold2=150)
print(f"Detekce hran: {np.count_nonzero(hrany)} hranových pixelů")

# Kontury (obrysy objektů)
kontury, hierarchy = cv2.findContours(hrany, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Nalezeno {len(kontury)} kontur")

img_kontury = img.copy()
for i, kontura in enumerate(kontury):
    plocha = cv2.contourArea(kontura)
    if plocha > 100:
        cv2.drawContours(img_kontury, [kontura], -1, (0, 255, 255), 2)
        x, y, w, h = cv2.boundingRect(kontura)
        cv2.rectangle(img_kontury, (x, y), (x+w, y+h), (255, 0, 255), 1)
```

---

## 🎭 Morfologické operace

```python
kernel = np.ones((5, 5), np.uint8)

# Dilatace — rozšíří bílé oblasti
dilace = cv2.dilate(hrany, kernel, iterations=1)

# Eroze — zmenší bílé oblasti
eroze = cv2.erode(hrany, kernel, iterations=1)

# Opening = eroze + dilatace (odstraní šum)
opening = cv2.morphologyEx(hrany, cv2.MORPH_OPEN, kernel)

# Closing = dilatace + eroze (zaplní díry)
closing = cv2.morphologyEx(hrany, cv2.MORPH_CLOSE, kernel)
```

---

## 👤 Detekce tváří (Haar Cascades)

```python
def detekuj_tvare(img: np.ndarray) -> list[tuple]:
    """Detekuje tváře pomocí Haar Cascade klasifikátoru."""
    # Stáhni cascade: cv2.data.haarcascades
    cascade_cesta = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_cesta)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tvare = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    img_out = img.copy()
    for (x, y, w, h) in tvare:
        cv2.rectangle(img_out, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(img_out, "Tvář", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return tvare, img_out


# Vytvoř testovací obraz s "tváří" (elipsa)
tvare_img = np.zeros((300, 300, 3), dtype=np.uint8)
cv2.ellipse(tvares_img, (150, 150), (60, 80), 0, 0, 360, (200, 150, 100), -1)
tvare, img_s_ramy = detekuj_tvare(tvare_img)
print(f"Detekováno tváří: {len(tvare)}")
```

---

## 🎥 Video a kamera

```python
def zpracuj_video(video_cesta: str, vystup_cesta: str):
    """Zpracuje video — aplikuje edge detection na každý snímek."""
    cap = cv2.VideoCapture(video_cesta)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    sirka = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vyska = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        vystup_cesta,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps, (sirka, vyska)
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hrany = cv2.Canny(gray, 50, 150)
        hrany_bgr = cv2.cvtColor(hrany, cv2.COLOR_GRAY2BGR)
        out.write(hrany_bgr)

    cap.release()
    out.release()


# Z kamery (0 = výchozí kamera)
def live_kamera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hrany = cv2.Canny(gray, 50, 150)
        cv2.imshow("Hrany", hrany)
        if cv2.waitKey(1) & 0xFF == ord("q"): break
    cap.release()
    cv2.destroyAllWindows()
```

---

## 🔮 Feature matching

```python
def porovnej_obrazky(img1: np.ndarray, img2: np.ndarray) -> float:
    """Porovná podobnost dvou obrázků pomocí ORB feature deskriptorů."""
    orb = cv2.ORB_create(nfeatures=500)

    kp1, desc1 = orb.detectAndCompute(img1, None)
    kp2, desc2 = orb.detectAndCompute(img2, None)

    if desc1 is None or desc2 is None:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc1, desc2)
    matches = sorted(matches, key=lambda x: x.distance)

    dobré = [m for m in matches if m.distance < 50]
    return len(dobré) / max(len(matches), 1)


score = porovnej_obrazky(img, img)   # identické obrazy
print(f"Podobnost (identické): {score:.2f}")
```

---

## ✏️ Cvičení

1. Postav **barcode scanner** — detekuj QR kódy v obrazu.
2. Implementuj **background subtraction** pro detekci pohybu ve videu.
3. Napiš **object tracking** — sleduj pohybující se objekt napříč snímky.
4. Implementuj **document scanner** — detekuj rohy dokumentu, perspektivní transformace.
5. Postav pipeline: webcam → detekce tváří → anonymizace (rozmazání) → zápis videa.
