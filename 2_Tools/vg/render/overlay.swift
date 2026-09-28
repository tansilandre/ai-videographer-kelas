// overlay.swift — renders animated captions and motion graphics as raw RGBA frames on stdout.
//
// Usage: overlay <spec.json>   (stdout: width*height*4 bytes per frame, premultiplied RGBA, top row first)
// Built and driven by `vg edit final` (vglib/finish.py). macOS only: CoreGraphics + CoreText, no packages.
//
// The spec holds absolute times in seconds. Layer types: caption, title, pin, badge, counter, map,
// callouts, card_text, endcard. Each layer has t0/t1 and animates in and out on its own.

import CoreGraphics
import CoreText
import Foundation

// MARK: - spec helpers

typealias J = [String: Any]

func num(_ j: J, _ k: String, _ d: Double) -> Double {
    if let v = j[k] as? Double { return v }
    if let v = j[k] as? Int { return Double(v) }
    return d
}
func str(_ j: J, _ k: String, _ d: String) -> String { (j[k] as? String) ?? d }

func color(_ hex: String, _ alpha: Double = 1) -> CGColor {
    var s = hex.trimmingCharacters(in: .whitespaces)
    if s.hasPrefix("#") { s.removeFirst() }
    var v: UInt64 = 0
    Scanner(string: s).scanHexInt64(&v)
    let r, g, b, a: Double
    if s.count == 8 {
        r = Double((v >> 24) & 0xff) / 255; g = Double((v >> 16) & 0xff) / 255
        b = Double((v >> 8) & 0xff) / 255; a = Double(v & 0xff) / 255
    } else {
        r = Double((v >> 16) & 0xff) / 255; g = Double((v >> 8) & 0xff) / 255
        b = Double(v & 0xff) / 255; a = 1
    }
    return CGColor(red: r, green: g, blue: b, alpha: a * alpha)
}

// MARK: - easing

func clamp(_ x: Double, _ lo: Double = 0, _ hi: Double = 1) -> Double { max(lo, min(hi, x)) }
func easeOutCubic(_ t: Double) -> Double { 1 - pow(1 - clamp(t), 3) }
func easeInOut(_ t: Double) -> Double { let x = clamp(t); return x < 0.5 ? 4 * x * x * x : 1 - pow(-2 * x + 2, 3) / 2 }
func easeOutBack(_ t: Double) -> Double {
    let c1 = 1.70158, c3 = c1 + 1, x = clamp(t)
    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)
}
func bounce(_ t: Double) -> Double {
    var x = clamp(t)
    let n1 = 7.5625, d1 = 2.75
    if x < 1 / d1 { return n1 * x * x }
    if x < 2 / d1 { x -= 1.5 / d1; return n1 * x * x + 0.75 }
    if x < 2.5 / d1 { x -= 2.25 / d1; return n1 * x * x + 0.9375 }
    x -= 2.625 / d1; return n1 * x * x + 0.984375
}

/// 0..1 envelope: in over `inDur` after t0, out over `outDur` before t1.
func envelope(_ t: Double, _ t0: Double, _ t1: Double, _ inDur: Double = 0.25, _ outDur: Double = 0.2) -> (Double, Double) {
    let pin = clamp((t - t0) / inDur)
    let pout = clamp((t1 - t) / outDur)
    return (pin, pout)
}

// MARK: - drawing

var W = 1080, H = 1920, FPS = 30.0, DURATION = 1.0
var fonts: [String: String] = ["heavy": "AvenirNext-Heavy", "bold": "AvenirNext-Bold", "demi": "AvenirNext-DemiBold",
                               "cond": "DINCondensed-Bold"]

func font(_ key: String, _ size: Double) -> CTFont {
    CTFontCreateWithName((fonts[key] ?? key) as CFString, CGFloat(size), nil)
}

func line(_ text: String, _ f: CTFont, _ fill: CGColor, stroke: CGColor? = nil, strokeWidth: Double = 0,
          kern: Double = 0) -> CTLine {
    var attrs: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): f,
        NSAttributedString.Key(kCTForegroundColorAttributeName as String): fill,
        NSAttributedString.Key(kCTKernAttributeName as String): kern,
    ]
    if let s = stroke, strokeWidth > 0 {
        attrs[NSAttributedString.Key(kCTStrokeColorAttributeName as String)] = s
        attrs[NSAttributedString.Key(kCTStrokeWidthAttributeName as String)] = -strokeWidth
    }
    return CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attrs))
}

func lineWidth(_ l: CTLine) -> Double { Double(CTLineGetTypographicBounds(l, nil, nil, nil)) }

/// Draw a line centered at (cx, cy) in top-left pixel coordinates.
func drawCentered(_ ctx: CGContext, _ l: CTLine, _ cx: Double, _ cy: Double, _ f: CTFont) {
    let w = lineWidth(l)
    let ascent = Double(CTFontGetAscent(f)), descent = Double(CTFontGetDescent(f))
    let baseline = Double(H) - cy - (ascent - descent) / 2
    ctx.textPosition = CGPoint(x: cx - w / 2, y: baseline)
    CTLineDraw(l, ctx)
}

func roundedRect(_ ctx: CGContext, _ cx: Double, _ cy: Double, _ w: Double, _ h: Double, _ r: Double, _ fill: CGColor) {
    let rect = CGRect(x: cx - w / 2, y: Double(H) - cy - h / 2, width: w, height: h)
    ctx.addPath(CGPath(roundedRect: rect, cornerWidth: CGFloat(r), cornerHeight: CGFloat(r), transform: nil))
    ctx.setFillColor(fill)
    ctx.fillPath()
}

/// Run `body` with alpha and a scale around (cx, cy) (top-left coords).
func withTransform(_ ctx: CGContext, alpha: Double, scale: Double = 1, cx: Double = 0, cy: Double = 0,
                   dy: Double = 0, _ body: () -> Void) {
    guard alpha > 0.001 else { return }
    ctx.saveGState()
    ctx.setAlpha(CGFloat(clamp(alpha)))
    let px = cx, py = Double(H) - cy
    ctx.translateBy(x: CGFloat(px), y: CGFloat(py - dy))
    ctx.scaleBy(x: CGFloat(scale), y: CGFloat(scale))
    ctx.translateBy(x: CGFloat(-px), y: CGFloat(-py))
    body()
    ctx.restoreGState()
}

// MARK: - layers

func drawCaption(_ ctx: CGContext, _ j: J, _ t: Double) {
    guard let words = j["words"] as? [J], !words.isEmpty else { return }
    let chunkSize = Int(num(j, "chunk", 3))
    let size = num(j, "size", 76)
    let y = num(j, "y", 0.72) * Double(H)
    let f = font(str(j, "font", "heavy"), size)
    let fill = color(str(j, "color", "#FFFFFF")), hi = color(str(j, "highlight", "#FFD23F"))
    let strokeC = color(str(j, "stroke", "#000000"))
    // group words into chunks; a chunk is visible from its first word's t0 to the next chunk's t0.
    // "chunks" (sizes, from finish.caption_chunks) is the grouping; the loop below is the fallback.
    var chunks: [[J]] = []
    if let sizes = j["chunks"] as? [Int], sizes.reduce(0, +) == words.count {
        var start = 0
        for n in sizes { chunks.append(Array(words[start..<start + n])); start += n }
    } else {
        var cur: [J] = []
        for w in words {
            cur.append(w)
            let text = str(w, "text", "")
            if cur.count >= chunkSize || [".", "?", ",", "!", ":", "\u{2026}"].contains(where: { text.hasSuffix($0) }) {
                chunks.append(cur); cur = []
            }
        }
        if !cur.isEmpty { chunks.append(cur) }
    }
    for (i, chunk) in chunks.enumerated() {
        let c0 = num(chunk[0], "t0", 0)
        let lastEnd = num(chunk[chunk.count - 1], "t1", 0) + 0.35
        let cEnd = i + 1 < chunks.count ? min(num(chunks[i + 1][0], "t0", 0), lastEnd) : lastEnd
        guard t >= c0 && t < cEnd else { continue }
        let appear = easeOutBack((t - c0) / 0.18)
        let texts = chunk.map { str($0, "text", "").uppercased() }
        let space = lineWidth(line(" ", f, fill)) + size * 0.14  // the outline eats half of a plain space
        let lines = texts.map { line($0, f, fill, stroke: strokeC, strokeWidth: 9) }
        let widths = lines.map(lineWidth)
        let total = widths.reduce(0, +) + space * Double(max(0, texts.count - 1))
        var x = Double(W) / 2 - total / 2
        let fit = min(1, Double(W) * 0.9 / max(1, total))  // a long chunk shrinks instead of leaving the frame
        withTransform(ctx, alpha: clamp(appear * 1.4), scale: (0.85 + 0.15 * appear) * fit, cx: Double(W) / 2, cy: y) {
            ctx.setShadow(offset: CGSize(width: 0, height: -4), blur: 12, color: color("#000000", 0.55))
            for (k, w) in chunk.enumerated() {
                let active = t >= num(w, "t0", 0) && t < num(w, "t1", 0) + 0.05
                let spoken = t >= num(w, "t0", 0)
                let wf = active ? hi : (spoken ? fill : color(str(j, "color", "#FFFFFF"), 0.85))
                let l = line(texts[k], f, wf, stroke: strokeC, strokeWidth: 9)
                let pop = active ? 1 + 0.08 * (1 - clamp((t - num(w, "t0", 0)) / 0.15)) : 1
                let cx = x + widths[k] / 2
                withTransform(ctx, alpha: 1, scale: pop, cx: cx, cy: y) {
                    drawCentered(ctx, l, cx, y, f)
                }
                x += widths[k] + space
            }
        }
    }
}

func drawTitle(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (pin, pout) = envelope(t, t0, t1, 0.35, 0.25)
    let size = num(j, "size", 64)
    let f = font(str(j, "font", "heavy"), size)
    let cx = num(j, "x", 0.5) * Double(W), cy = num(j, "y", 0.2) * Double(H)
    let lines = str(j, "text", "").components(separatedBy: "\n")
    let pad = size * 0.45
    let lineH = size * 1.15
    let built = lines.map { line($0, f, color(str(j, "color", "#FFFFFF")), kern: 1.5) }
    let bw = (built.map(lineWidth).max() ?? 0) + pad * 2
    let bh = lineH * Double(lines.count) + pad * 1.1
    withTransform(ctx, alpha: min(pin * 1.5, pout), scale: 0.6 + 0.4 * easeOutBack(pin), cx: cx, cy: cy) {
        ctx.setShadow(offset: CGSize(width: 0, height: -6), blur: 18, color: color("#000000", 0.35))
        roundedRect(ctx, cx, cy, bw, bh, size * 0.28, color(str(j, "bg", "#FF5A1F")))
        ctx.setShadow(offset: .zero, blur: 0, color: nil)
        for (i, l) in built.enumerated() {
            let ly = cy - lineH * Double(lines.count - 1) / 2 + lineH * Double(i)
            drawCentered(ctx, l, cx, ly, f)
        }
    }
}

func drawPin(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (_, pout) = envelope(t, t0, t1, 0.2, 0.25)
    let cx = num(j, "x", 0.5) * Double(W), tipY = num(j, "y", 0.4) * Double(H)
    let r = num(j, "size", 58)
    let drop = bounce((t - t0) / 0.7)
    let y = tipY - (1 - drop) * num(j, "drop", 260)
    let c = color(str(j, "color", "#FF3B30"))
    // pulse rings at the tip after landing
    let since = t - t0 - 0.7
    if since > 0 {
        for k in 0..<2 {
            let p = (since + Double(k) * 0.6).truncatingRemainder(dividingBy: 1.2) / 1.2
            ctx.setStrokeColor(color(str(j, "color", "#FF3B30"), (1 - p) * 0.8 * pout))
            ctx.setLineWidth(6)
            let rr = 20 + p * 110
            ctx.strokeEllipse(in: CGRect(x: cx - rr, y: Double(H) - tipY - rr * 0.45, width: rr * 2, height: rr * 0.9))
        }
    }
    withTransform(ctx, alpha: pout, cx: cx, cy: y) {
        ctx.setShadow(offset: CGSize(width: 0, height: -8), blur: 16, color: color("#000000", 0.45))
        let tipCG = Double(H) - y
        let top = tipCG + r * 2.2          // circle centre, above the tip (CG y grows upward)
        ctx.setFillColor(c)
        ctx.fillEllipse(in: CGRect(x: cx - r, y: top - r, width: r * 2, height: r * 2))
        let path = CGMutablePath()
        path.move(to: CGPoint(x: cx - r * 0.82, y: top - r * 0.55))
        path.addLine(to: CGPoint(x: cx + r * 0.82, y: top - r * 0.55))
        path.addLine(to: CGPoint(x: cx, y: tipCG))
        path.closeSubpath()
        ctx.addPath(path)
        ctx.fillPath()
        ctx.setShadow(offset: .zero, blur: 0, color: nil)
        ctx.setFillColor(color("#FFFFFF"))
        ctx.fillEllipse(in: CGRect(x: cx - r * 0.42, y: top - r * 0.42, width: r * 0.84, height: r * 0.84))
    }
    if let label = j["label"] as? String {
        let f = font("heavy", num(j, "label_size", 40))
        let a = clamp((t - t0 - 0.6) / 0.3) * pout
        withTransform(ctx, alpha: a, cx: cx, cy: tipY - r * 2.2 - 90) {
            let l = line(label, f, color("#FFFFFF"), kern: 1)
            roundedRect(ctx, cx, tipY - r * 2.2 - 90, lineWidth(l) + 44, num(j, "label_size", 40) * 1.6, 18, c)
            drawCentered(ctx, l, cx, tipY - r * 2.2 - 90, f)
        }
    }
}

func drawBadge(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (pin, pout) = envelope(t, t0, t1, 0.3, 0.2)
    let size = num(j, "size", 34)
    let f = font(str(j, "font", "heavy"), size)
    let l = line(str(j, "text", ""), f, color(str(j, "color", "#FFFFFF")), kern: 2)
    let bw = lineWidth(l) + size * 1.2, bh = size * 1.7
    let corner = str(j, "corner", "top-left")
    let margin = 56.0
    let cx = corner.hasSuffix("left") ? margin + bw / 2 : Double(W) - margin - bw / 2
    let cy = corner.hasPrefix("top") ? num(j, "top", 170) + bh / 2 : Double(H) - num(j, "bottom", 320) - bh / 2
    withTransform(ctx, alpha: min(pin, pout), cx: cx, cy: cy, dy: (1 - easeOutCubic(pin)) * -20) {
        roundedRect(ctx, cx, cy, bw, bh, 12, color(str(j, "bg", "#000000B3")))
        ctx.setStrokeColor(color(str(j, "border", "#FFD23F")))
        ctx.setLineWidth(3)
        let rect = CGRect(x: cx - bw / 2, y: Double(H) - cy - bh / 2, width: bw, height: bh)
        ctx.addPath(CGPath(roundedRect: rect, cornerWidth: 12, cornerHeight: 12, transform: nil))
        ctx.strokePath()
        drawCentered(ctx, l, cx, cy, f)
    }
}

func formatNumber(_ v: Int, _ sep: String) -> String {
    let s = String(v)
    var out = ""
    for (i, ch) in s.reversed().enumerated() {
        if i > 0 && i % 3 == 0 { out.append(contentsOf: sep.reversed()) }
        out.append(ch)
    }
    return String(out.reversed())
}

func drawCounter(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (pin, pout) = envelope(t, t0, t1, 0.25, 0.25)
    let from = num(j, "from", 0), to = num(j, "to", 1000)
    let run = num(j, "run", 1.6)
    let p = easeOutCubic((t - t0) / run)
    let value = Int((from + (to - from) * p).rounded())
    let cx = Double(W) / 2, cy = num(j, "y", 0.42) * Double(H)
    let size = num(j, "size", 230)
    let f = font("heavy", size)
    let accent = color(str(j, "color", "#FFD23F"))
    withTransform(ctx, alpha: min(pin, pout), scale: 0.9 + 0.1 * easeOutBack(pin), cx: cx, cy: cy) {
        ctx.setShadow(offset: CGSize(width: 0, height: -8), blur: 24, color: color("#000000", 0.5))
        drawCentered(ctx, line(formatNumber(value, str(j, "sep", ".")), f, accent), cx, cy, f)
        let cf = font("heavy", size * 0.3)
        drawCentered(ctx, line(str(j, "caption", ""), cf, color("#FFFFFF"), kern: 3), cx, cy + size * 0.72, cf)
        let sf = font("demi", size * 0.18)
        drawCentered(ctx, line(str(j, "sub", ""), sf, color("#FFFFFF", 0.85), kern: 1), cx, cy + size * 1.08, sf)
    }
}

func drawMap(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (pin, pout) = envelope(t, t0, t1, 0.3, 0.25)
    let a = min(pin, pout)
    func pt(_ p: [Double]) -> CGPoint { CGPoint(x: p[0] * Double(W), y: Double(H) - p[1] * Double(H)) }
    withTransform(ctx, alpha: a) {
        // faint grid
        ctx.setStrokeColor(color("#FFFFFF", 0.06))
        ctx.setLineWidth(2)
        for i in stride(from: 0, through: W, by: 90) {
            ctx.move(to: CGPoint(x: i, y: 0)); ctx.addLine(to: CGPoint(x: i, y: H))
        }
        for i in stride(from: 0, through: H, by: 90) {
            ctx.move(to: CGPoint(x: 0, y: i)); ctx.addLine(to: CGPoint(x: W, y: i))
        }
        ctx.strokePath()
        for road in (j["roads"] as? [J]) ?? [] {
            guard let pts = road["points"] as? [[Double]], pts.count > 1 else { continue }
            let rs = t0 + num(road, "at", 0.2), rd = num(road, "draw", 1.0)
            let p = easeInOut((t - rs) / rd)
            guard p > 0 else { continue }
            // partial polyline by length
            var segs: [Double] = []
            for i in 1..<pts.count {
                segs.append(hypot((pts[i][0] - pts[i - 1][0]) * Double(W), (pts[i][1] - pts[i - 1][1]) * Double(H)))
            }
            let total = segs.reduce(0, +)
            var remain = total * p
            let path = CGMutablePath()
            path.move(to: pt(pts[0]))
            for i in 1..<pts.count {
                if remain >= segs[i - 1] {
                    path.addLine(to: pt(pts[i])); remain -= segs[i - 1]
                } else {
                    let f = remain / segs[i - 1]
                    path.addLine(to: pt([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f,
                                         pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f]))
                    break
                }
            }
            let width = num(road, "width", 14)
            if road["glow"] as? Bool ?? false {
                ctx.addPath(path); ctx.setStrokeColor(color(str(road, "color", "#FFD23F"), 0.3))
                ctx.setLineWidth(CGFloat(width * 2.6)); ctx.setLineCap(.round); ctx.setLineJoin(.round)
                ctx.strokePath()
            }
            ctx.addPath(path); ctx.setStrokeColor(color(str(road, "color", "#FFD23F")))
            ctx.setLineWidth(CGFloat(width)); ctx.setLineCap(.round); ctx.setLineJoin(.round)
            ctx.strokePath()
            if let label = road["label"] as? String, p > 0.6, let lp = road["label_at"] as? [Double] {
                let f = font("heavy", num(road, "label_size", 34))
                withTransform(ctx, alpha: clamp((p - 0.6) / 0.3), cx: lp[0] * Double(W), cy: lp[1] * Double(H)) {
                    drawCentered(ctx, line(label, f, color(str(road, "color", "#FFD23F")), kern: 1),
                                 lp[0] * Double(W), lp[1] * Double(H), f)
                }
            }
        }
        for place in (j["places"] as? [J]) ?? [] {
            guard let p = place["at_xy"] as? [Double] else { continue }
            let ps = t0 + num(place, "at", 0.4)
            let pa = easeOutBack((t - ps) / 0.35)
            guard t >= ps else { continue }
            let cx = p[0] * Double(W), cy = p[1] * Double(H)
            let c = color(str(place, "color", "#FFFFFF"))
            withTransform(ctx, alpha: clamp(pa), scale: max(0.01, pa), cx: cx, cy: cy) {
                let r = num(place, "size", 18)
                ctx.setFillColor(c)
                ctx.fillEllipse(in: CGRect(x: cx - r, y: Double(H) - cy - r, width: r * 2, height: r * 2))
                ctx.setStrokeColor(color("#000000", 0.6)); ctx.setLineWidth(4)
                ctx.strokeEllipse(in: CGRect(x: cx - r, y: Double(H) - cy - r, width: r * 2, height: r * 2))
                let f = font(str(place, "font", "bold"), num(place, "label_size", 34))
                let off = num(place, "label_dy", -52)
                drawCentered(ctx, line(str(place, "label", ""), f, c, stroke: color("#000000", 0.9), strokeWidth: 5),
                             cx, cy + off, f)
            }
        }
        if let d = j["distance"] as? J, let pts = d["points"] as? [[Double]], pts.count == 2 {
            let ds = t0 + num(d, "at", 1.4)
            let p = easeInOut((t - ds) / 0.7)
            if p > 0 {
                let a0 = pt(pts[0]), a1 = pt(pts[1])
                ctx.setStrokeColor(color("#FFFFFF")); ctx.setLineWidth(5); ctx.setLineDash(phase: 0, lengths: [16, 12])
                ctx.move(to: a0)
                ctx.addLine(to: CGPoint(x: a0.x + (a1.x - a0.x) * CGFloat(p), y: a0.y + (a1.y - a0.y) * CGFloat(p)))
                ctx.strokePath(); ctx.setLineDash(phase: 0, lengths: [])
                if p > 0.8, let lp = d["label_at"] as? [Double] {
                    let f = font("heavy", num(d, "size", 56))
                    let l = line(str(d, "label", ""), f, color(str(d, "color", "#111111")), kern: 1)
                    let cx = lp[0] * Double(W), cy = lp[1] * Double(H)
                    withTransform(ctx, alpha: clamp((p - 0.8) / 0.2), scale: 0.7 + 0.3 * easeOutBack((p - 0.8) / 0.2), cx: cx, cy: cy) {
                        roundedRect(ctx, cx, cy, lineWidth(l) + 50, num(d, "size", 56) * 1.5, 20, color(str(d, "bg", "#FFD23F")))
                        drawCentered(ctx, l, cx, cy, f)
                    }
                }
            }
        }
    }
}

func drawCallouts(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (_, pout) = envelope(t, t0, t1, 0.2, 0.25)
    let items = (j["items"] as? [J]) ?? []
    let size = num(j, "size", 58)
    let f = font("heavy", size)
    let y0 = num(j, "y", 0.3) * Double(H)
    for (i, item) in items.enumerated() {
        let at = t0 + num(item, "at", Double(i) * 0.8)
        guard t >= at else { continue }
        let p = easeOutBack((t - at) / 0.35)
        let cy = y0 + Double(i) * size * 1.9
        let l = line(str(item, "text", ""), f, color("#111111"), kern: 1.5)
        let bw = lineWidth(l) + size * 1.6
        let cx = Double(W) / 2
        withTransform(ctx, alpha: clamp(p) * pout, cx: cx, cy: cy, dy: 0) {
            ctx.saveGState()
            ctx.translateBy(x: CGFloat((1 - clamp(p)) * -300), y: 0)
            ctx.setShadow(offset: CGSize(width: 0, height: -6), blur: 14, color: color("#000000", 0.4))
            roundedRect(ctx, cx, cy, bw, size * 1.45, 16, color(str(j, "bg", "#FFFFFF")))
            ctx.setShadow(offset: .zero, blur: 0, color: nil)
            ctx.setFillColor(color(str(j, "accent", "#FF5A1F")))
            ctx.fillEllipse(in: CGRect(x: cx - bw / 2 + size * 0.35, y: Double(H) - cy - size * 0.18,
                                       width: size * 0.36, height: size * 0.36))
            drawCentered(ctx, l, cx + size * 0.2, cy, f)
            ctx.restoreGState()
        }
    }
}

func drawCardText(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let (pin, pout) = envelope(t, t0, t1, 0.3, 0.2)
    let cx = Double(W) / 2, cy = num(j, "y", 0.5) * Double(H)
    let size = num(j, "size", 40)
    let f = font(str(j, "font", "demi"), size)
    let lines = str(j, "text", "").components(separatedBy: "\n")
    withTransform(ctx, alpha: min(pin, pout) * num(j, "opacity", 1), cx: cx, cy: cy) {
        for (i, s) in lines.enumerated() {
            drawCentered(ctx, line(s, f, color(str(j, "color", "#FFFFFF")), kern: 1), cx,
                         cy + Double(i) * size * 1.35 - Double(lines.count - 1) * size * 0.67, f)
        }
    }
}

func drawEndcard(_ ctx: CGContext, _ j: J, _ t: Double) {
    let t0 = num(j, "t0", 0), t1 = num(j, "t1", 0)
    guard t >= t0 && t < t1 else { return }
    let p = easeOutCubic((t - t0) / 0.5)
    ctx.setFillColor(color(str(j, "bg", "#0F1B2D"), clamp(p * 1.2) * num(j, "bg_alpha", 1)))
    ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let cx = Double(W) / 2
    var brandSize = num(j, "brand_size", 110)
    let brandWidth = lineWidth(line(str(j, "brand", ""), font("heavy", brandSize), color("#FFFFFF"), kern: 6))
    if brandWidth > Double(W) * 0.88 { brandSize *= Double(W) * 0.88 / brandWidth }  // a long name shrinks to fit
    let brand = font("heavy", brandSize)
    withTransform(ctx, alpha: p, scale: 0.9 + 0.1 * easeOutBack((t - t0) / 0.6), cx: cx, cy: Double(H) * 0.38) {
        drawCentered(ctx, line(str(j, "brand", ""), brand, color(str(j, "brand_color", "#FFFFFF")), kern: 6),
                     cx, Double(H) * 0.38, brand)
        let tag = font("demi", 40)
        drawCentered(ctx, line(str(j, "tagline", ""), tag, color("#FFFFFF", 0.8), kern: 3), cx, Double(H) * 0.38 + 100, tag)
    }
    let ctaP = easeOutBack((t - t0 - 0.35) / 0.4)
    if t > t0 + 0.35 {
        let cf = font("heavy", 60)
        let l = line(str(j, "cta", ""), cf, color("#111111"), kern: 1)
        withTransform(ctx, alpha: clamp(ctaP), scale: 0.7 + 0.3 * ctaP, cx: cx, cy: Double(H) * 0.55) {
            roundedRect(ctx, cx, Double(H) * 0.55, lineWidth(l) + 90, 110, 55, color(str(j, "accent", "#FFD23F")))
            drawCentered(ctx, l, cx, Double(H) * 0.55, cf)
        }
        let pf = font("heavy", 64)
        withTransform(ctx, alpha: clamp((t - t0 - 0.6) / 0.3), cx: cx, cy: Double(H) * 0.64) {
            drawCentered(ctx, line(str(j, "phone", ""), pf, color("#FFFFFF"), kern: 3), cx, Double(H) * 0.64, pf)
        }
    }
    let df = font("demi", 30)
    withTransform(ctx, alpha: clamp((t - t0 - 0.5) / 0.3), cx: cx, cy: Double(H) * 0.9) {
        drawCentered(ctx, line(str(j, "disclaimer", ""), df, color("#FFFFFF", 0.75)), cx, Double(H) * 0.9, df)
    }
}

// MARK: - main

let args = CommandLine.arguments
guard args.count > 1, let data = FileManager.default.contents(atPath: args[1]),
      let spec = try? JSONSerialization.jsonObject(with: data) as? J else {
    FileHandle.standardError.write("usage: overlay <spec.json>\n".data(using: .utf8)!)
    exit(1)
}
W = Int(num(spec, "width", 1080)); H = Int(num(spec, "height", 1920))
FPS = num(spec, "fps", 30); DURATION = num(spec, "duration", 1)
if let f = spec["fonts"] as? [String: String] { for (k, v) in f { fonts[k] = v } }
let layers = (spec["layers"] as? [J]) ?? []

let bytesPerRow = W * 4
let buffer = UnsafeMutableRawPointer.allocate(byteCount: bytesPerRow * H, alignment: 64)
let ctx = CGContext(data: buffer, width: W, height: H, bitsPerComponent: 8, bytesPerRow: bytesPerRow,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setShouldAntialias(true)
ctx.setAllowsFontSmoothing(true)
let out = FileHandle.standardOutput
let frames = Int((DURATION * FPS).rounded(.up))
for i in 0..<frames {
    let t = Double(i) / FPS
    memset(buffer, 0, bytesPerRow * H)
    for layer in layers {
        let t0 = num(layer, "t0", 0), t1 = num(layer, "t1", 0)
        if layer["type"] as? String != "caption" && (t < t0 || t >= t1) { continue }
        switch layer["type"] as? String ?? "" {
        case "caption": drawCaption(ctx, layer, t)
        case "title": drawTitle(ctx, layer, t)
        case "pin": drawPin(ctx, layer, t)
        case "badge": drawBadge(ctx, layer, t)
        case "counter": drawCounter(ctx, layer, t)
        case "map": drawMap(ctx, layer, t)
        case "callouts": drawCallouts(ctx, layer, t)
        case "card_text": drawCardText(ctx, layer, t)
        case "endcard": drawEndcard(ctx, layer, t)
        default: break
        }
    }
    out.write(Data(bytesNoCopy: buffer, count: bytesPerRow * H, deallocator: .none))
}
