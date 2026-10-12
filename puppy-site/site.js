(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  ScrollCraft.mount(document.body);

  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  // Hero pupils follow the pointer; on touch they drift with scroll.
  var heroPupils = document.querySelectorAll('.pupils--live .pupil');
  var tx = 0, ty = 0, cx = 0, cy = 0;
  addEventListener('pointermove', function (e) {
    var r = document.querySelector('.hero__svg').getBoundingClientRect();
    var dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height * 0.34);
    var d = Math.hypot(dx, dy) || 1, k = Math.min(1, d / 300);
    tx = dx / d * 3.4 * k; ty = dy / d * 2.8 * k;
  }, { passive: true });

  var peak = document.getElementById('night'), svg = peak.querySelector('.night__svg'), zzz = peak.querySelector('.zzz');
  function frame() {
    if (!reduce) { cx += (tx - cx) * .14; cy += (ty - cy) * .14; }
    else { cx = tx; cy = ty; }
    heroPupils.forEach(function (p) { p.setAttribute('transform', 'translate(' + cx.toFixed(2) + ' ' + cy.toFixed(2) + ')'); });

    var p = parseFloat(peak.style.getPropertyValue('--sc-p')) || 0;
    var lid = clamp((p - 0.5) / 0.28, 0, 1);
    svg.style.setProperty('--lid', lid.toFixed(3));
    svg.querySelectorAll('.pupil').forEach(function (e) { e.setAttribute('transform', 'translate(0 ' + (lid * 2).toFixed(2) + ')'); });
    zzz.style.setProperty('--zzz', clamp((p - 0.74) / 0.12, 0, 1).toFixed(3));
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  // Shortlist
  var count = document.getElementById('count');
  var chips = {};
  document.querySelectorAll('.chip input').forEach(function (c) { chips[c.value] = c; });
  document.querySelectorAll('.save').forEach(function (b) {
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on);
      b.querySelector('.save__icon').textContent = on ? '♥' : '♡';
      b.querySelector('.save__txt').textContent = (on ? 'Shortlisted: ' : 'Shortlist ') + b.dataset.name;
      if (chips[b.dataset.name]) chips[b.dataset.name].checked = on;
      count.textContent = document.querySelectorAll('.save[aria-pressed="true"]').length;
    });
  });

  // Form (demo only)
  var form = document.getElementById('chatform'), out = document.getElementById('out');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var n = form.name.value.trim(), m = form.email;
    if (!n || !m.value || !m.validity.valid) { out.textContent = 'Please add your name and a valid email.'; (n ? m : form.name).focus(); return; }
    var picks = Array.prototype.map.call(form.querySelectorAll('.chip input:checked'), function (c) { return c.value; });
    out.textContent = 'Thanks, ' + n + '. ' + (picks.length ? picks.join(' and ') + ' would be told you said hi. ' : '') + '(Demo only, nothing was sent.)';
  });
})();
