def _rounded_rect(fb, x, y, w, h, r):
    fb.fill_rect(x + r, y, w - 2 * r, h, 1)
    fb.fill_rect(x, y + r, w, h - 2 * r, 1)
    for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                   (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
        fb.ellipse(cx, cy, r, r, 1, True)


def draw(fb):
    fb.fill(0)
    _rounded_rect(fb, 30, 30, 24, 38, 8)   # left eye
    _rounded_rect(fb, 74, 30, 24, 38, 8)   # right eye
    _rounded_rect(fb, 52, 86, 24, 6, 3)    # mouth
