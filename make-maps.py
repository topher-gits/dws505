#!/usr/bin/env python3
"""Derive the mirrored battlefield map from the primary one.

bgb-map-top-right.svg is the hand-drawn source. The bottom-left variant is
generated from it so the two can never drift apart geometrically: only the
zone badges move and four refineries change hands.

  Blue  always holds the two refineries beside our Safe Zone.
  Red   keeps its Military and Hospital; its refinery moves to fill a gap.
  Green keeps its Military and Hospital; its refinery moves to fill a gap.

Regenerate the PNGs afterwards with:
  chrome --headless --screenshot=<out>.png --window-size=2160,1560 <in>.svg
"""
import re, sys

RED, BLUE, GREEN = '#c8324b', '#1f6fb8', '#1d8a4e'

# refinery -> colour it takes in the mirrored layout (keyed by path start)
REASSIGN = {
    '130,232': BLUE,   # W  : red   -> blue  (now beside the Safe Zone)
    '245,315': BLUE,   # SW : green -> blue  (now beside the Safe Zone)
    '475,149': RED,    # NE : blue  -> red   (fills what blue vacated)
    '590,232': GREEN,  # E  : blue  -> green (fills what blue vacated)
}

# badge geometry: (safe corner) <-> (enemy corner)
BADGES = [
    ('<rect x="498" y="20" width="192"', '<rect x="30" y="422" width="192"'),
    ('transform="translate(534,59)"',    'transform="translate(66,461)"'),
    ('x="560" y="65"',                   'x="92" y="467"'),
    ('<rect x="30" y="422" width="160"', '<rect x="530" y="20" width="160"'),
    ('transform="translate(66,461)"',    'transform="translate(566,59)"'),
    ('x="92" y="467"',                   'x="592" y="65"'),
]


def mirror(svg):
    for coord, colour in REASSIGN.items():
        pat = r'fill="#[0-9a-f]{6}"(\s*\n\s*d="M ' + re.escape(coord) + ')'
        svg, n = re.subn(pat, 'fill="%s"\\1' % colour, svg)
        if n != 1:
            sys.exit('refinery %s matched %d times, expected 1' % (coord, n))

    # two-pass so the safe badge landing on the enemy's old coordinates does
    # not get picked up again when the enemy badge is moved
    for i, (old, _) in enumerate(BADGES):
        svg, n = re.subn(re.escape(old), '@@%d@@' % i, svg, count=1)
        if n != 1:
            sys.exit('badge anchor %r matched %d times, expected 1' % (old, n))
    for i, (_, new) in enumerate(BADGES):
        svg = svg.replace('@@%d@@' % i, new)
    return svg


if __name__ == '__main__':
    src = open('bgb-map-top-right.svg').read()
    open('bgb-map-bottom-left.svg', 'w').write(mirror(src))
    print('wrote bgb-map-bottom-left.svg')
