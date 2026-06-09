import re, glob

for svg_file in glob.glob('dist/github-contribution-grid-snake*.svg'):
    with open(svg_file, 'r') as f:
        content = f.read()

    # ── 1. Parse current viewBox ─────────────────────────────────────────────
    m = re.search(
        r'viewBox="(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"',
        content
    )
    if not m:
        print('No viewBox found in ' + svg_file)
        continue

    vb_x = float(m.group(1))
    vb_y = float(m.group(2))
    vb_w = float(m.group(3))
    vb_h = float(m.group(4))

    # ── 2. Clip top margin ───────────────────────────────────────────────────
    # The snake enters from y = vb_y (negative) which makes it appear ABOVE
    # the grid. Move the viewBox top to y=0 and shrink height by the same amount.
    if vb_y < 0:
        new_vb_y = 0.0
        new_vb_h = vb_h + vb_y   # vb_y is negative, so this subtracts |vb_y|
    else:
        new_vb_y = vb_y
        new_vb_h = vb_h

    # ── 3. Trim right edge to the last real grid column ──────────────────────
    all_tags = re.findall(r'<rect[^>]+class="c[^"]*"[^>]*>', content)
    xs = []
    for tag in all_tags:
        xm = re.search(r'\bx="(-?\d+(?:\.\d+)?)"', tag)
        if xm:
            xs.append(float(xm.group(1)))

    if xs:
        cell_w = 12
        grid_right = max(xs) + cell_w + 4   # last cell right edge + 4px breathing room
        new_vb_w = grid_right - vb_x         # keep left edge unchanged
        if new_vb_w >= vb_w:
            new_vb_w = vb_w                  # never enlarge beyond original
    else:
        new_vb_w = vb_w

    # ── 4. Apply new viewBox ─────────────────────────────────────────────────
    old_vb = m.group(0)
    new_vb = 'viewBox="{} {} {} {}"'.format(
        int(vb_x), int(new_vb_y), int(new_vb_w), int(new_vb_h)
    )
    content = content.replace(old_vb, new_vb, 1)

    # ── 5. Update SVG width & height to match the new viewBox exactly ────────
    # CRITICAL: if width/height don't match the viewBox ratio, browsers add
    # letterboxing — extra empty space where overflowing content stays visible.
    # By making them equal, we get a 1:1 mapping and overflow="hidden" works.
    new_svg_w = int(new_vb_w)
    new_svg_h = int(new_vb_h)

    # Replace only the first occurrence (the root <svg> element's attributes)
    content = re.sub(
        r'(<svg\b[^>]*?)\bwidth="[^"]*"',
        lambda mo: mo.group(1) + 'width="{}"'.format(new_svg_w),
        content, count=1
    )
    content = re.sub(
        r'(<svg\b[^>]*?)\bheight="[^"]*"',
        lambda mo: mo.group(1) + 'height="{}"'.format(new_svg_h),
        content, count=1
    )

    # ── 6. Ensure overflow=hidden on SVG root ────────────────────────────────
    content = re.sub(
        r'(<svg\b)(?![^>]*overflow=)',
        r'\1 overflow="hidden"',
        content
    )

    with open(svg_file, 'w') as f:
        f.write(content)

    print('Fixed {}: {} -> {}, size {}x{} -> {}x{}'.format(
        svg_file, old_vb, new_vb,
        int(vb_w), int(vb_h), new_svg_w, new_svg_h
    ))
