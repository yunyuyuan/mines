/* Touch-only bridge. Original mouse, keyboard and game logic are unchanged. */
(function () {
  'use strict';
  const canvas = document.getElementById('puzzlecanvas');
  let gesture = null;

  function clearGesture() {
    if (gesture) window.clearTimeout(gesture.timer);
    gesture = null;
  }

  function clickAt(point, button) {
    if (typeof canvas.onmousedown !== 'function') return;
    const options = {
      bubbles: true,
      cancelable: true,
      clientX: point.x,
      clientY: point.y,
      button: button,
      buttons: button === 2 ? 2 : 1,
      view: window
    };
    canvas.dispatchEvent(new MouseEvent('mousedown', options));
    canvas.dispatchEvent(new MouseEvent('mouseup', {
      ...options,
      buttons: 0
    }));
  }

  canvas.addEventListener('pointerdown', function (event) {
    if (event.pointerType !== 'touch') return;
    event.preventDefault();
    clearGesture();
    canvas.focus({ preventScroll: true });
    const point = {
      id: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      held: false,
      timer: 0
    };
    point.timer = window.setTimeout(function () {
      if (gesture !== point) return;
      point.held = true;
      clickAt(point, 2);
    }, 450);
    gesture = point;
  }, { passive: false });

  canvas.addEventListener('pointermove', function (event) {
    if (!gesture || event.pointerId !== gesture.id) return;
    if (Math.hypot(event.clientX - gesture.x, event.clientY - gesture.y) > 12) {
      clearGesture();
    }
  });

  canvas.addEventListener('pointerup', function (event) {
    if (!gesture || event.pointerId !== gesture.id) return;
    event.preventDefault();
    const point = gesture;
    clearGesture();
    if (!point.held) clickAt(point, 0);
  }, { passive: false });

  canvas.addEventListener('pointercancel', clearGesture);
  window.addEventListener('blur', clearGesture);
}());
