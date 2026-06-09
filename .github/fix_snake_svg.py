import re, glob, sys

for svg_file in glob.glob('dist/github-contribution-grid-snake*.svg'):
    with open(svg_file, 'r') as f:
        content = f.read()

    m = re.search(r'viewBox="(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', content)
    if not m:
        print('No viewBox found in ' + svg_file)
        continue

    vb_x = float(m.group(1))
    vb_y = float(m.group(2))
    vb_w = float(m.group(3))
    vb_h = float(m.group(4))

    # 1. Clip top: remove the negative top margin where snake appears above the grid
    if vb_y < 0:
        clip_top = -vb_y
        new_vb_y = 0
        new_vb_h = vb_h - clip_top
    else:
        new_vb_y = vb_y
        new_vb_h = vb_h

    # 2. Find rightmost grid cell and trim right edge to it
    all_tags = re.findall(r'<rect[^>]+class="c[^"]*"[^>]*>', content)
    xs = []
    for tag in all_tags:
        xm = re.search(r'\bx="(-?\d+(?:\.\d+)?)"', tag)
        if xm:
            xs.append(float(xm.group(1)))

    if xs:
        cell_w = 12
        max_cell_x = max(xs)
        grid_right = max_cell_x + cell_w + 4  # 4px breathing room
        new_vb_w = grid_right - vb_x
        if new_vb_w >= vb_w:
            new_vb_w = vb_w  # only shrink, never enlarge
    else:
        new_vb_w = vb_w

    old_vb = m.group(0)
    new_vb = 'viewBox="{} {} {} {}"'.format(int(vb_x), int(new_vb_y), int(new_vb_w), int(new_vb_h))
    content = content.replace(old_vb, new_vb, 1)

    # 3. Add overflow=hidden to SVG root to clip animation within viewBox
    content = re.sub(r'(<svg\b)(?![^>]*overflow=)', r'\1 overflow="hidden"', content)

    with open(svg_file, 'w') as f:
        f.write(content)
    print('Fixed ' + svg_file + ': ' + old_vb + ' -> ' + new_vb)
