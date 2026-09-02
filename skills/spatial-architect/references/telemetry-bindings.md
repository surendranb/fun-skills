# Dynamic Telemetry & Living State Machine Bindings

Below are drop-in JavaScript modules to bind real-time environmental variables to SVG elements.

---

## 1. Astronomical Solar Arc & Time Engine

Calculates sun/moon coordinates along a trigonometric arc and shifts sky palettes across 4 solar phases:

```javascript
(function initSolarEngine() {
  var skyA = document.getElementById('skyA');
  var skyB = document.getElementById('skyB');
  var sun = document.getElementById('sun');
  var moon = document.getElementById('moon');
  var stars = document.getElementById('stars');
  var shaft = document.getElementById('shaft');
  
  if (!skyA || !skyB) return;

  function setOpacity(el, op) { if (el) el.setAttribute('opacity', op); }

  function updateSky() {
    var now = new Date();
    // Convert to target timezone (e.g. Asia/Kolkata UTC+5:30)
    var d = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    var h = d.getHours() + d.getMinutes() / 60;
    
    // 4 Solar Phases: Dawn (5:00-7:30), Day (7:30-17:00), Dusk (17:00-19:30), Night (19:30-5:00)
    var phase = (h >= 5 && h < 7.5) ? 'dawn' : (h >= 7.5 && h < 17) ? 'day' : (h >= 17 && h < 19.5) ? 'dusk' : 'night';

    if (phase === 'night') {
      skyA.setAttribute('stop-color', '#2B2648');
      skyB.setAttribute('stop-color', '#4C4472');
      setOpacity(moon, '1');
      setOpacity(stars, '1');
      setOpacity(sun, '0');
      if (shaft) shaft.setAttribute('opacity', '0.10');
    } else if (phase === 'dawn') {
      skyA.setAttribute('stop-color', '#FCD9A8');
      skyB.setAttribute('stop-color', '#F2B177');
      setOpacity(moon, '0');
      setOpacity(stars, '0');
      setOpacity(sun, '1');
      if (sun) sun.setAttribute('transform', 'translate(140, 345)');
    } else if (phase === 'day') {
      skyA.setAttribute('stop-color', '#EAF2E8');
      skyB.setAttribute('stop-color', '#F6EBD2');
      setOpacity(moon, '0');
      setOpacity(stars, '0');
      setOpacity(sun, '1');
      
      // Trigonometric Sun Arc across window width
      var p = (h - 7.5) / 9.5; // 0.0 to 1.0
      var x = 120 + p * 220;
      var y = 175 - Math.sin(p * Math.PI) * 55;
      if (sun) sun.setAttribute('transform', 'translate(' + x.toFixed(0) + ',' + y.toFixed(0) + ')');
    } else { // dusk
      skyA.setAttribute('stop-color', '#F7C08A');
      skyB.setAttribute('stop-color', '#E89B62');
      setOpacity(moon, '0');
      setOpacity(stars, '0');
      setOpacity(sun, '1');
      if (sun) sun.setAttribute('transform', 'translate(330, 345)');
    }
  }

  updateSky();
  setInterval(updateSky, 60000);
})();
```

---

## 2. Real-Time Open-Meteo Weather Hook (Zero Auth)

Fetches live conditions and modulates precipitation particle layers and cloud densities:

```javascript
(function initWeatherEngine(lat, lon) {
  var URL = 'https://api.open-meteo.com/v1/forecast?latitude=' + (lat || 13.0827) + '&longitude=' + (lon || 80.2707) + '&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,cloud_cover&timezone=auto';

  fetch(URL)
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (!data || !data.current) return;
      var cur = data.current;
      var temp = Math.round(cur.temperature_2m);
      var code = cur.weather_code;
      var clouds = cur.cloud_cover || 0;
      var isRaining = (cur.rain > 0 || cur.precipitation > 0 || [51,53,55,61,63,65,80,81,82,95,96,99].indexOf(code) !== -1);

      // Rain Layer
      var rainEl = document.getElementById('rain');
      if (rainEl) rainEl.setAttribute('opacity', isRaining ? '0.85' : '0');

      // Cloud Opacity Scale
      var cloudsEl = document.getElementById('clouds');
      if (cloudsEl) {
        var op = Math.max(0.18, Math.min(1.0, clouds / 100));
        cloudsEl.setAttribute('opacity', op.toFixed(2));
      }

      // HUD Text
      var hud = document.getElementById('hud-weather');
      var cond = isRaining ? 'RAIN' : (clouds > 80 ? 'OVERCAST' : (clouds > 30 ? 'PARTLY CLOUDY' : 'CLEAR'));
      if (hud) hud.textContent = temp + '°C · ' + cond;
    })
    .catch(function () {});
})();
```

---

## 3. Vector Pupil Cursor Tracking

Trigonometrically positions avatar eye pupils toward active user cursor coordinates:

```javascript
(function initGazeTracking(robotId) {
  var host = document.getElementById(robotId || 'robot');
  var pupils = document.querySelectorAll('.pupil');
  if (!host || !pupils.length) return;

  document.addEventListener('mousemove', function (e) {
    var rect = host.getBoundingClientRect();
    var centerX = rect.left + rect.width / 2;
    var centerY = rect.top + rect.height * 0.25;
    
    var dx = e.clientX - centerX;
    var dy = e.clientY - centerY;
    var dist = Math.sqrt(dx * dx + dy * dy) || 1;
    
    // Bounded maximum deflection (e.g. max 2.4px offset)
    var k = Math.min(2.4, 0.9 + dist * 0.008);
    var ox = (dx / dist * k).toFixed(1);
    var oy = (dy / dist * k).toFixed(1);

    pupils.forEach(function (p) {
      p.setAttribute('transform', 'translate(' + ox + ',' + oy + ')');
    });
  });
})();
```
