#!/usr/bin/env python3
"""Emit bounded review thumbnails of actual UI renders, not substitute mock-ups."""
import base64, io, sys
from pathlib import Path
from PIL import Image
for path in sorted(Path(sys.argv[1]).glob('*.png')):
    image=Image.open(path).convert('RGB'); image.thumbnail((1400,1400))
    buffer=io.BytesIO();image.save(buffer,format='JPEG',quality=90)
    print('UI_REVIEW_BASE64:'+path.stem+':'+base64.b64encode(buffer.getvalue()).decode())
