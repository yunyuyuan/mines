#!/usr/bin/env python3
"""Integration checks for the offline packaging, not a rewrite of game rules."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SEED = '#9x9n10%2312345'
CANVAS = "document.getElementById('puzzlecanvas').toDataURL()"
SAVE = """() => {
  const pointer = Module.cwrap('get_save_file', 'number', [])();
  const text = UTF8ToString(pointer);
  Module.cwrap('free_save_file', 'void', ['number'])(pointer);
  return text;
}"""
results = []


def passed(name):
    results.append({'check': name, 'result': 'pass'})
    print('PASS:', name, flush=True)


def ready(page):
    page.wait_for_function(
        "document.getElementById('puzzle').style.display !== 'none'", timeout=20000
    )


def cell(page, column, row, button='left'):
    box = page.locator('#puzzlecanvas').bounding_box()
    assert box is not None
    # Upstream default: 20px cells, 30px border. Scale with the CSS canvas.
    x = box['x'] + (40 + 20 * column) * box['width'] / 240
    y = box['y'] + (40 + 20 * row) * box['height'] / 240
    page.mouse.click(x, y, button=button)


def reference_route(route):
    filename = route.request.url.split('/')[-1].split('#')[0]
    files = {
        'mines.html': ('text/html', ROOT / 'vendor/mines.html'),
        'mines.js': ('text/javascript', ROOT / 'vendor/mines.js'),
        'mines.wasm': ('application/wasm', ROOT / 'vendor/mines.wasm'),
    }
    if filename in files:
        content_type, path = files[filename]
        route.fulfill(status=200, content_type=content_type, body=path.read_bytes())
    else:
        route.fulfill(status=404, body='Not found')


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path='/usr/bin/chromium', headless=True,
            args=['--no-sandbox']
        )
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        offline = context.new_page()
        errors = []
        requests = []
        offline.on('pageerror', lambda error: errors.append(str(error)))
        offline.on('request', lambda request: requests.append(request.url))
        offline.goto((ROOT / 'public/index.html').as_uri() + SEED)
        ready(offline)
        assert not [url for url in requests if url.startswith(('http:', 'https:'))]
        assert not errors, errors
        passed('Direct file:// launch with zero network dependencies')
        visible = offline.locator('body').inner_text()
        assert 'Try to expose' not in visible
        assert 'Portable Puzzle' not in visible
        assert 'Link to this puzzle' not in visible
        assert offline.locator('#permalink-desc').is_hidden()
        passed('Only game controls, canvas and status are visible')

        reference = context.new_page()
        reference.route('http://reference.local/**', reference_route)
        reference.goto('http://reference.local/mines.html' + SEED)
        ready(reference)
        assert reference.evaluate(CANVAS) == offline.evaluate(CANVAS)
        passed('Default board pixel-identical to unmodified upstream')

        for page in (reference, offline):
            cell(page, 0, 0)
        assert reference.evaluate(CANVAS) == offline.evaluate(CANVAS)
        assert 'DEAD' not in offline.locator('#statusbar').inner_text()
        assert 'NSTATES :1:2' in offline.evaluate(SAVE)
        passed('Safe first click, flood reveal and digits match upstream pixels')

        for page in (reference, offline):
            cell(page, 8, 8, 'right')
        assert 'Marked: 1 / 10' in offline.locator('#statusbar').inner_text()
        assert reference.evaluate(CANVAS) == offline.evaluate(CANVAS)
        flagged = offline.evaluate(CANVAS)
        passed('Right-click flag and rendering match upstream')
        offline.locator('#undo').click()
        assert 'Marked: 0 / 10' in offline.locator('#statusbar').inner_text()
        assert not offline.locator('#redo').is_disabled()
        offline.locator('#redo').click()
        assert offline.evaluate(CANVAS) == flagged
        passed('Undo and redo restore the exact previous board')
        offline.locator('#restart').click()
        reference.locator('#restart').click()
        assert 'Marked: 0 / 10' in offline.locator('#statusbar').inner_text()
        assert offline.evaluate(CANVAS) == reference.evaluate(CANVAS)
        assert not offline.locator('#undo').is_disabled()
        passed('Restart board is pixel-identical and undoable like upstream')

        offline.locator('#solve').click()
        assert 'Marked: 10 / 10' in offline.locator('#statusbar').inner_text()
        assert 'SOLVE   :1:S' in offline.evaluate(SAVE)
        passed('Original solver and end-state feedback')
        offline.locator('#restart').click()
        lost = False
        for row in range(9):
            for column in range(9):
                cell(offline, column, row)
                if 'DEAD' in offline.locator('#statusbar').inner_text():
                    lost = True
                    break
            if lost:
                break
        assert lost, offline.locator('#statusbar').inner_text()
        offline.locator('#undo').click()
        assert 'DEAD' not in offline.locator('#statusbar').inner_text()
        passed('Mine explosion and undo from loss')

        offline.locator('#prefs').evaluate('(element) => element.click()')
        assert offline.locator('#dlgform').is_visible()
        offline.locator('#dlgform input[value="Cancel"]').click()
        offline.locator('#specific').evaluate('(element) => element.click()')
        assert offline.locator('#dlgform').is_visible()
        offline.locator('#dlgform input[value="Cancel"]').click()
        offline.locator('#save').evaluate('(element) => element.click()')
        download_url = offline.locator('#dlgform a[download]').get_attribute('href')
        assert download_url and download_url.startswith('data:')
        offline.locator('#dlgform input[value="OK"]').click()
        assert 'Honeycomb' in offline.locator('#gametype').inner_text()
        assert 'Custom...' in offline.locator('#gametype').inner_text()
        passed('Preferences, game ID, save-file export, original tiling presets')
        offline.screenshot(path=str(ROOT / 'tests/desktop.png'))

        mobile = browser.new_context(
            viewport={'width': 375, 'height': 812}, device_scale_factor=2,
            is_mobile=True, has_touch=True
        )
        touch_page = mobile.new_page()
        touch_page.on('pageerror', lambda error: errors.append(str(error)))
        touch_page.goto((ROOT / 'public/index.html').as_uri() + SEED)
        ready(touch_page)
        box = touch_page.locator('#puzzlecanvas').bounding_box()
        assert box is not None
        assert box['x'] >= 0 and box['x'] + box['width'] <= 375
        touch_page.touchscreen.tap(box['x'] + 40, box['y'] + 40)
        assert 'NSTATES :1:2' in touch_page.evaluate(SAVE)
        touch_session = mobile.new_cdp_session(touch_page)
        touch_session.send('Input.dispatchTouchEvent', {
            'type': 'touchStart',
            'touchPoints': [{'x': box['x'] + 200, 'y': box['y'] + 200, 'id': 1}]
        })
        touch_page.wait_for_timeout(550)
        touch_session.send('Input.dispatchTouchEvent', {
            'type': 'touchEnd', 'touchPoints': []
        })
        assert 'Marked: 1 / 10' in touch_page.locator('#statusbar').inner_text()
        assert not errors, errors
        touch_page.screenshot(path=str(ROOT / 'tests/mobile.png'))
        passed('Mobile tap, long-press flag, high-DPI and viewport fit')
        browser.close()
    (ROOT / 'tests/results.json').write_text(
        json.dumps({'results': results, 'page_errors': errors}, indent=2) + '\n'
    )
    print(f'{len(results)} checks passed.')


if __name__ == '__main__':
    main()
