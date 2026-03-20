"""Generate the app icon as a PIL Image. No external files needed."""

from PIL import Image, ImageDraw


def create_icon(size=256):
    """Create a simple photo/resize icon programmatically."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = size // 8
    s = size

    # Background: rounded blue square
    bg_rect = [pad // 2, pad // 2, s - pad // 2, s - pad // 2]
    corner = size // 6
    draw.rounded_rectangle(bg_rect, radius=corner, fill="#3B82F6")

    # White photo frame (landscape rectangle)
    frame_left = pad + size // 10
    frame_top = pad + size // 6
    frame_right = s - pad - size // 10
    frame_bottom = s - pad - size // 6
    frame_corner = size // 16
    draw.rounded_rectangle(
        [frame_left, frame_top, frame_right, frame_bottom],
        radius=frame_corner, fill="#FFFFFF",
    )

    # Green mountain/landscape inside the frame
    inner_pad = size // 20
    inner_left = frame_left + inner_pad
    inner_top = frame_top + inner_pad
    inner_right = frame_right - inner_pad
    inner_bottom = frame_bottom - inner_pad

    # Sky
    draw.rectangle([inner_left, inner_top, inner_right, inner_bottom], fill="#DBEAFE")

    # Mountain 1 (big, left)
    peak1_x = inner_left + (inner_right - inner_left) * 0.35
    peak1_y = inner_top + (inner_bottom - inner_top) * 0.25
    draw.polygon(
        [(inner_left, inner_bottom), (peak1_x, peak1_y),
         (inner_left + (inner_right - inner_left) * 0.7, inner_bottom)],
        fill="#22C55E",
    )

    # Mountain 2 (smaller, right)
    peak2_x = inner_left + (inner_right - inner_left) * 0.72
    peak2_y = inner_top + (inner_bottom - inner_top) * 0.4
    draw.polygon(
        [(inner_left + (inner_right - inner_left) * 0.45, inner_bottom),
         (peak2_x, peak2_y),
         (inner_right, inner_bottom)],
        fill="#16A34A",
    )

    # Sun circle
    sun_cx = inner_right - (inner_right - inner_left) * 0.2
    sun_cy = inner_top + (inner_bottom - inner_top) * 0.25
    sun_r = size // 16
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill="#FBBF24",
    )

    # Resize arrows (bottom-right corner of the icon)
    arrow_color = "#FFFFFF"
    arrow_x = s - pad - size // 6
    arrow_y = s - pad - size // 8
    arrow_len = size // 6
    line_w = max(3, size // 40)

    # Diagonal arrow line
    draw.line(
        [(arrow_x, arrow_y), (arrow_x + arrow_len, arrow_y + arrow_len)],
        fill=arrow_color, width=line_w,
    )
    # Arrowhead
    ah = size // 14
    draw.polygon(
        [(arrow_x + arrow_len, arrow_y + arrow_len),
         (arrow_x + arrow_len - ah, arrow_y + arrow_len),
         (arrow_x + arrow_len, arrow_y + arrow_len - ah)],
        fill=arrow_color,
    )

    # Second arrow (reverse direction, slightly offset)
    draw.line(
        [(arrow_x + arrow_len, arrow_y), (arrow_x, arrow_y + arrow_len)],
        fill=arrow_color, width=line_w,
    )
    draw.polygon(
        [(arrow_x, arrow_y + arrow_len),
         (arrow_x + ah, arrow_y + arrow_len),
         (arrow_x, arrow_y + arrow_len - ah)],
        fill=arrow_color,
    )

    return img


if __name__ == "__main__":
    icon = create_icon(256)
    icon.save("app_icon.png")
    print("Saved app_icon.png")
