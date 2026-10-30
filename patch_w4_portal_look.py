# patch_w4_portal_look.py - new look for the portal rings (2.5D): a stone ring lying on the ground, a column of light,
# rising sparks, glowing floor, and a different dressing per world (starlight, crystals, roots).
# Also makes the walk-in area match the ring's oval shape. Needs patch_w3_portals first. Safe to run twice.
import sys
P = sys.argv[1] if len(sys.argv) > 1 else "src/App.jsx"
src = open(P, encoding="utf-8", newline="").read()
if "var drawPortal=" in src:
    print("Already patched. Nothing written."); sys.exit(0)
if "const PORTALS=" not in src or "/*_rings*/" not in src:
    print("ABORT: apply patch_w3_portals.py first. Nothing written."); sys.exit(1)
def once(text, s, label):
    if text.count(s) != 1:
        print(f"ABORT {label}: expected exactly 1 match, found {text.count(s)}. Nothing written."); sys.exit(1)
FUNC = r"""var drawPortal=(function () {
  var PAL = {
    malkuth: { ring: ["#15122e", "#3a3470", "#8f86d8", "#e8e4ff"], glow: [170, 160, 255], core: [235, 230, 255], spark: "#ffffff" },
    yesod:   { ring: ["#2a1f4a", "#6b55a8", "#b7a0f0", "#f4eaff"], glow: [200, 170, 255], core: [255, 240, 255], spark: "#ffffff" },
    netzach: { ring: ["#0b1c12", "#244a2c", "#5f8f45", "#d9d77a"], glow: [120, 220, 130], core: [235, 255, 190], spark: "#ffe9a0" }
  };
  function h(n) { n = Math.imul(n ^ 61, 2654435761); n ^= n >>> 15; n = Math.imul(n, 2246822519); n ^= n >>> 13; return (n >>> 0) / 4294967296; }
  function g3(v) { return Math.round(v / 3) * 3; }
  function rgba(c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a.toFixed(3) + ")"; }
  var RX = 56, RY = 28;
  return function drawPortal(ctx, x, y, t, dest) {
    var P = PAL[dest] || PAL.malkuth, i, k, a, ang;
    var pulse = 0.5 + 0.5 * Math.sin(t * 0.045);
    ctx.save();
    // 1. ground glow bands + contact shadow
    ctx.fillStyle = "rgba(0,0,0,0.38)";
    ctx.beginPath(); ctx.ellipse(x + 4, y + 5, RX + 10, RY + 5, 0, 0, 6.2832); ctx.fill();
    ctx.globalCompositeOperation = "lighter";
    for (i = 0; i < 5; i++) {
      ctx.fillStyle = rgba(P.glow, (0.05 + 0.025 * pulse) * (5 - i) / 5 + 0.015);
      ctx.beginPath(); ctx.ellipse(x, y, RX + 44 - i * 8, RY + 22 - i * 4, 0, 0, 6.2832); ctx.fill();
    }
    ctx.globalCompositeOperation = "source-over";
    // 2. back half of the ring (far side), stepped tones
    function arc(w, col, a0, a1, rx, ry, dx, dy) {
      ctx.lineWidth = w; ctx.strokeStyle = col; ctx.beginPath();
      ctx.ellipse(x + (dx || 0), y + (dy || 0), rx || RX, ry || RY, 0, a0, a1); ctx.stroke();
    }
    var PI = Math.PI;
    arc(12, P.ring[0], PI, 2 * PI, RX, RY, 0, 0);
    arc(9, P.ring[1], PI, 2 * PI, RX, RY, 0, 0);
    arc(3, P.ring[2], PI * 1.05, PI * 1.55, RX, RY, 0, -1);
    ctx.globalCompositeOperation = "lighter";
    // 3. floor of the gate (bright core inside the ring)
    for (i = 0; i < 4; i++) {
      ctx.fillStyle = rgba(P.core, 0.12 + 0.09 * i + 0.06 * pulse * (i / 3));
      ctx.beginPath(); ctx.ellipse(x, y, RX - 8 - i * 9, RY - 4 - i * 4.5, 0, 0, 6.2832); ctx.fill();
    }
    // 4. light column: stacked bands, shimmering, narrowing and fading with height
    var H = 128;
    for (k = 0; k < H; k += 6) {
      var f = k / H, hw = g3((RX - 12) * (1 - f * 0.55) + 2 * Math.sin(t * 0.03 + k * 0.12));
      a = (0.68 * (1 - f) * (1 - f) + 0.03) * (0.75 + 0.25 * Math.sin(t * 0.06 - k * 0.09));
      ctx.fillStyle = rgba(P.glow, a);
      ctx.fillRect(x - hw, y - k - 6, hw * 2, 6);
    }
    for (i = 0; i < 6; i++) {            // slow vertical streaks inside the column
      var sx = x + g3((h(i + 7) - 0.5) * 70 * (1 - ((t * 0.4 + i * 37) % 120) / 260));
      var sy = y - ((t * (0.35 + h(i) * 0.3) + i * 53) % H);
      ctx.fillStyle = rgba(P.core, 0.35 * (1 - (y - sy) / H));
      ctx.fillRect(sx, g3(sy), 3, 9);
    }
    ctx.globalCompositeOperation = "source-over";
    // 5. per-world dressing standing on the far half
    if (dest === "yesod") {
      for (i = 0; i < 7; i++) {
        ang = PI * (1.08 + 0.84 * (i / 6)); var cx = x + Math.cos(ang) * RX, cy = y + Math.sin(ang) * RY;
        var ch = 16 + h(i + 3) * 14, hue = (t * 0.6 + i * 50) % 360;
        ctx.fillStyle = "hsla(" + hue + ",70%,78%,0.85)"; ctx.beginPath();
        ctx.moveTo(cx - 5, cy); ctx.lineTo(cx, cy - ch); ctx.lineTo(cx + 5, cy); ctx.closePath(); ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.7)"; ctx.beginPath();
        ctx.moveTo(cx - 5, cy); ctx.lineTo(cx, cy - ch); ctx.lineTo(cx - 1, cy); ctx.closePath(); ctx.fill();
      }
    }
    ctx.globalCompositeOperation = "lighter";
    // 6. particles rising through the column
    for (i = 0; i < 16; i++) {
      var life = ((t * (0.5 + h(i * 3) * 0.6) + h(i * 5) * 200) % 120) / 120;
      var px = x + (h(i * 7 + 1) - 0.5) * (RX * 1.5) * (1 - life * 0.5) + Math.sin(t * 0.04 + i) * 5;
      var py = y - 6 - life * 110 + (h(i * 11) - 0.5) * 20;
      ctx.fillStyle = rgba(i % 3 === 0 ? [255, 255, 255] : P.core, 0.9 * Math.sin(life * PI));
      var s = i % 4 === 0 ? 6 : 3; ctx.fillRect(g3(px), g3(py), s, s);
    }
    ctx.globalCompositeOperation = "source-over";
    // 7. front half of the ring (near side) drawn over the column
    arc(12, P.ring[0], 0, PI, RX, RY, 0, 0);
    arc(9, P.ring[1], 0, PI, RX, RY, 0, 0);
    arc(5, P.ring[2], 0.1, PI * 0.45, RX - 1, RY - 1, 0, -1);
    arc(2, P.ring[3], 0.25, PI * 0.35, RX - 1, RY - 1, 0, -2);
    // 8. runes / lights travelling round the ring
    for (i = 0; i < 8; i++) {
      ang = t * 0.012 + i * (PI / 4);
      var rx2 = x + Math.cos(ang) * RX, ry2 = y + Math.sin(ang) * RY, near = Math.sin(ang) > 0;
      ctx.fillStyle = rgba(P.core, near ? 0.95 : 0.45);
      ctx.fillRect(g3(rx2) - 1, g3(ry2) - 1, near ? 6 : 3, near ? 6 : 3);
    }
    // 9. world-specific accents on the near side
    if (dest === "netzach") {
      ctx.lineWidth = 3; ctx.strokeStyle = P.ring[2];
      for (i = 0; i < 3; i++) {
        var ra = 0.35 + i * 1.05, bx = x + Math.cos(ra) * RX, by = y + Math.sin(ra) * RY;
        ctx.beginPath(); ctx.moveTo(bx, by);
        ctx.quadraticCurveTo(bx + 10 * (i - 1), by - 14 - i * 3, bx + 4 + 12 * Math.sin(t * 0.02 + i), by - 26 - 6 * i);
        ctx.stroke();
        ctx.fillStyle = P.ring[3]; ctx.fillRect(g3(bx + 4 + 12 * Math.sin(t * 0.02 + i)) - 1, g3(by - 26 - 6 * i) - 1, 3, 3);
      }
    } else if (dest === "malkuth") {
      for (i = 0; i < 3; i++) {
        var sa = 0.5 + i * 2.1, sxs = x + Math.cos(sa) * (RX + 3), sys = y + Math.sin(sa) * (RY + 2) - 6;
        var tw = 0.5 + 0.5 * Math.sin(t * 0.07 + i * 2);
        ctx.fillStyle = rgba([255, 255, 255], 0.4 + 0.5 * tw);
        ctx.fillRect(g3(sxs) - 1, g3(sys) - 7, 3, 15); ctx.fillRect(g3(sxs) - 7, g3(sys) - 1, 15, 3);
      }
    }
    ctx.restore();
  };
})();
"""
a = "function awayFromRing(p){"
once(src, a, "anchor")
i = src.index(a); j = src.index("}", src.index("return[", i)) + 1   # end of awayFromRing
src = src[:j] + "\n" + FUNC + "\n" + src[j:]
s0 = "/*_rings*/"; once(src, s0, "ring draw start")
e0 = 'ctx.fillText("?",_sx,_sy+74);ctx.restore();}}'; once(src, e0, "ring draw end")
i = src.index(s0); j = src.index(e0) + len(e0)
NEW = ('/*_rings*/{const _pt=PORTALS[WORLD_ID]||{};for(const _d in _pt){const _sx=_pt[_d][0]-cam.x,_sy=_pt[_d][1]-cam.y;'
       'if(_sx<-160||_sx>W+160||_sy<-200||_sy>H+100)continue;drawPortal(ctx,_sx,_sy,s.frame,_d);'
       'ctx.save();ctx.font="7px "+ff;ctx.textAlign="center";ctx.fillStyle="rgba(255,255,255,0.8)";ctx.fillText(WORLDS[_d].name,_sx,_sy-150);'
       'ctx.fillStyle="rgba(255,255,255,0.4)";ctx.fillText("?",_sx,_sy+58);ctx.restore();}}')
src = src[:i] + NEW + src[j:]
t0 = "Math.hypot(myCat.x-_pt[_d][0],myCat.y-_pt[_d][1])<60"; once(src, t0, "trigger")
src = src.replace(t0, "Math.hypot(myCat.x-_pt[_d][0],(myCat.y-_pt[_d][1])*2)<62")
open(P, "w", encoding="utf-8", newline="").write(src)
print("OK: 4 edits applied (new ring look, labels, oval walk-in area).")
