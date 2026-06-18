/*
 * Pulse — ambient enhancement, loaded by <Script src="/scripts/ambient.js"
 * strategy="afterInteractive" /> from the layout. It is a pure progressive
 * enhancement: the app is fully usable without it. It adds keyboard shortcuts
 * (press "?" for the cheat-sheet; "g" then s/i/r/a to jump around) and marks
 * the document ready so CSS can react. Pyxle deduplicates the script by src, so
 * even though it is referenced once per layout it loads exactly once.
 */
(function () {
  if (window.__pulseAmbient) return;
  window.__pulseAmbient = true;

  var root = document.documentElement;
  root.setAttribute('data-pulse-ready', '1');

  function panel() {
    return document.getElementById('pulse-shortcuts');
  }

  function toggle(force) {
    var el = panel();
    if (!el) return;
    var open = force != null ? force : el.classList.contains('hidden');
    el.classList.toggle('hidden', !open);
    el.setAttribute('aria-hidden', open ? 'false' : 'true');
  }

  // "g" then a letter navigates — using the real nav <a> so Pyxle's client
  // router handles it (no full reload), falling back to a hard navigation.
  var NAV = { s: '/', i: '/incidents', r: '/report', a: '/about' };
  var armed = false;
  var armedAt = 0;

  function go(key) {
    var link = document.querySelector('a[data-nav="' + key + '"]');
    if (link) {
      link.click();
    } else if (NAV[key]) {
      window.location.assign(NAV[key]);
    }
  }

  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    if (e.key === '?') {
      e.preventDefault();
      toggle();
      return;
    }
    if (e.key === 'Escape') {
      toggle(false);
      return;
    }
    if (e.key === 'g') {
      armed = true;
      armedAt = Date.now();
      return;
    }
    if (armed && Date.now() - armedAt < 1200 && NAV[e.key]) {
      e.preventDefault();
      go(e.key);
      toggle(false);
    }
    armed = false;
  });
})();
