# Program — Lekce 168: Lekce 168: Computer Vision — OpenCV

Patří k lekci [Lekce 168: Computer Vision — OpenCV](../168_computer_vision.md).

## Jak spustit

```bash
python3 programy/l168_computer_vision.py
```

## Zdrojový kód

### `l168_computer_vision.py`

```py
"""Lekce 168 — Computer Vision: OpenCV.

Spuštění:
    uv run --with opencv-python,numpy l168_computer_vision.py
"""

import numpy as np
import os

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Nainstaluj: uv add opencv-python numpy")


def vytvor_testovaci_img(w=400, h=300):
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (40, 40, 40)
    cv2.rectangle(img, (50,50), (150,150), (255,0,0), 3)
    cv2.circle(img, (250,100), 50, (0,255,0), -1)
    cv2.line(img, (0,200), (400,200), (0,0,255), 2)
    cv2.putText(img, "OpenCV Demo", (80,260), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    return img


def demo_zakladni(img):
    print("\n=== Základní operace ===")
    print(f"  Tvar: {img.shape}  (výška×šířka×kanály)")
    print(f"  dtype: {img.dtype}")
    print(f"  min/max: {img.min()}/{img.max()}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    malý = cv2.resize(img, (200, 150))
    rozostren = cv2.GaussianBlur(img, (5,5), 0)
    print(f"  Grayscale: {gray.shape}")
    print(f"  Resize 50%: {malý.shape}")
    return gray


def demo_hrany(img, gray):
    print("\n=== Detekce hran (Canny) ===")
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    hrany = cv2.Canny(blur, 50, 150)
    nenulove = np.count_nonzero(hrany)
    print(f"  Hranových pixelů: {nenulove} / {hrany.size} ({100*nenulove/hrany.size:.1f}%)")

    kontury, _ = cv2.findContours(hrany, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    velke = [k for k in kontury if cv2.contourArea(k) > 100]
    print(f"  Kontur celkem: {len(kontury)}, velkých (>100px²): {len(velke)}")
    return hrany


def demo_morphology(hrany):
    print("\n=== Morfologické operace ===")
    kernel = np.ones((5,5), np.uint8)
    dilace = cv2.dilate(hrany, kernel)
    eroze = cv2.erode(hrany, kernel)
    opening = cv2.morphologyEx(hrany, cv2.MORPH_OPEN, kernel)
    print(f"  Original:  {np.count_nonzero(hrany)} px")
    print(f"  Dilatace:  {np.count_nonzero(dilace)} px (+)")
    print(f"  Eroze:     {np.count_nonzero(eroze)} px (-)")
    print(f"  Opening:   {np.count_nonzero(opening)} px (odstraní šum)")


def demo_histogram(gray):
    print("\n=== Histogram jasu ===")
    hist = cv2.calcHist([gray], [0], None, [16], [0, 256])
    max_bin = int(np.argmax(hist))
    print(f"  Nejčastější jas: {max_bin*16}-{max_bin*16+15}")
    equalized = cv2.equalizeHist(gray)
    print(f"  Histogram equalization: {gray.std():.1f} → {equalized.std():.1f} std")


def demo_feature_detection(gray):
    print("\n=== Feature detekce (ORB) ===")
    orb = cv2.ORB_create(nfeatures=100)
    kp, desc = orb.detectAndCompute(gray, None)
    print(f"  Nalezeno {len(kp)} keypoints")
    if desc is not None:
        print(f"  Deskriptor shape: {desc.shape} (každý keypoint = 32 bytů)")


def demo_ulozeni(img, gray, hrany):
    print("\n=== Ukládání výsledků ===")
    for nazev, data in [("original.jpg", img), ("gray.jpg", gray), ("edges.jpg", hrany)]:
        cesta = f"/tmp/{nazev}"
        cv2.imwrite(cesta, data)
        size = os.path.getsize(cesta)
        print(f"  {nazev}: {size:,} B")


def main():
    print("=" * 50)
    print("  👁️  Computer Vision — OpenCV Demo")
    print("=" * 50)

    if not CV2_AVAILABLE:
        print("Nainstaluj: uv add opencv-python numpy")
        return

    img = vytvor_testovaci_img()
    gray = demo_zakladni(img)
    hrany = demo_hrany(img, gray)
    demo_morphology(hrany)
    demo_histogram(gray)
    demo_feature_detection(gray)
    demo_ulozeni(img, gray, hrany)

    print("\n✅ Demo dokončeno!")
    print("Výsledky uloženy v /tmp/original.jpg, gray.jpg, edges.jpg")
    print("\nDalší kroky:")
    print("  - Detekce tváří: cv2.CascadeClassifier (Haar Cascades)")
    print("  - Deep learning: cv2.dnn.readNet (YOLO, MobileNet)")
    print("  - Video: cv2.VideoCapture(0) — live kamera")


if __name__ == "__main__":
    main()

```
