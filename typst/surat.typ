// Surat Permohonan Izin Kegiatan — TPKB ITS
//
// Compiled by backend/src/services/typst_renderer.py, which passes all letter
// data as one JSON string in `sys.inputs.data`. Without that input the sample
// data is used, so this file can be edited live with:
//
//   typst watch surat.typ --root .
//
// Every value from the data is inserted as a plain string, never evaluated as
// Typst markup, so user input cannot change the layout.

// ── Tunables ────────────────────────────────────────────────────────────────
#let page-width = 21cm
#let side-margin = 3cm
#let header-gap = 0.9cm        // space between header image and first line
#let footer-gap = 0.6cm        // space between last line and footer image
#let plain-margin = 2.54cm     // top/bottom margin when there is no image
// A footer taller than this is treated as a background decoration (like the
// 7 cm wave of the 2026 letterhead): text stops this far from the bottom edge
// and may run over the empty upper part of the image.
#let footer-max-margin = 3cm

#let sign-width = 6cm          // width of the "Hormat kami" block
#let ttd-gap = 1.9cm           // empty space between the jabatan and the name
#let ttd-height = 2.7cm        // signature image; taller than the gap, so it
                               // overlaps the lines around it like real ink
#let stempel-width = 3.4cm
#let stempel-dx = -0.75cm      // from the left edge of the signature block
#let stempel-dy = 0.2cm        // from the top edge of the signature block

#let table-head-fill = rgb("#c1cebd")

// ── Data ────────────────────────────────────────────────────────────────────
#let raw-data = sys.inputs.at("data", default: none)
#let d = if raw-data != none { json(bytes(raw-data)) } else { json("sample/data.json") }

// Image paths are relative to this file (e.g. "sample/header.png").
#let assets = d.at("assets", default: (:))
#let asset(name) = {
  let path = assets.at(name, default: none)
  if path == none or path == "" { none } else { path }
}
#let header-img = asset("header")
#let footer-img = asset("footer")
#let stempel-img = asset("stempel")
#let ttd-img = asset("ttd")

#let ketua = d.at("ketua", default: (:))
#let tujuan-tempat = if d.its { "Institut Teknologi Sepuluh Nopember" } else { "Di tempat" }

// ── Page: header and footer are full-width images pinned to the page edges ──
// Liberation Serif (bundled in fonts/) has the same metrics as Times New Roman
// and is used on servers where Times New Roman is not installed.
#set text(font: ("Times New Roman", "Liberation Serif"), size: 12pt, lang: "id")

#show: body => context {
  let full(path) = image(path, width: page-width)
  let header-h = if header-img != none { measure(full(header-img)).height } else { 0pt }
  let footer-h = if footer-img != none { measure(full(footer-img)).height } else { 0pt }

  set page(
    paper: "a4",
    margin: (
      x: side-margin,
      top: if header-img != none { header-h + header-gap } else { plain-margin },
      bottom: if footer-img != none {
        calc.max(plain-margin, calc.min(footer-h + footer-gap, footer-max-margin))
      } else { plain-margin },
    ),
    background: {
      if header-img != none { place(top + center, full(header-img)) }
      if footer-img != none { place(bottom + center, full(footer-img)) }
    },
  )
  body
}

// ── Letter ──────────────────────────────────────────────────────────────────
#set par(leading: 1.05em, spacing: 1.05em)

#align(right)[Surabaya, #d.tanggal]

#v(0.5em)

#grid(
  columns: (2.6cm, 0.45cm, 1fr),
  row-gutter: 1.05em,
  [Nomor], [:], [#d.nomor_surat],
  [Lampiran], [:], [-],
  [Perihal], [:], [Permohonan Izin Kegiatan],
)

#v(0.5em)

Yth. \
#d.tujuan \
#tujuan-tempat

#v(0.5em)

Dengan hormat

#set par(first-line-indent: (amount: 1.27cm, all: true))

Berhubungan dengan akan diadakannya persiapan kegiatan
#strong(d.nama_kegiatan) pada #d.hari_tanggal, kami menyatakan bahwa mahasiswa
yang namanya terlampir dibawah ini memohon izin untuk tidak menghadiri
#strong(d.acara) pada tanggal tersebut karena kehadiran dan kontribusinya
sebagai panitia. Adapun nama mahasiswa tersebut adalah:

#v(0.3em)

#{
  set par(first-line-indent: 0pt, leading: 0.65em)
  table(
    columns: (1.2cm, 1fr, 3cm, 4.2cm),
    align: (center, left, center, center),
    stroke: 1pt + black,
    inset: (x: 6pt, y: 7pt),
    fill: (_, y) => if y == 0 { table-head-fill },
    table.header(
      ..("No.", "Nama", "NRP", "Program Studi").map(h => align(center, strong(h))),
    ),
    ..d.participants.enumerate().map(((i, p)) => (
      str(i + 1), p.nama, p.nrp, p.jurusan,
    )).flatten(),
  )
}

#v(0.3em)

Demikian permohonan surat izin keikutsertaan ini kami sampaikan. Atas perhatian
dan kerja samanya, kami ucapkan terima kasih.

#v(0.4em)

// ── Signature block ─────────────────────────────────────────────────────────
// The signature and the stempel are floating images placed after the text, so
// they are drawn in front of it: the signature over the gap above the name, the
// stempel to its left, overlapping both the signature and the jabatan line.
#align(right, block(width: sign-width, breakable: false, {
  set align(center)
  set par(first-line-indent: 0pt, leading: 0.65em, spacing: 0.65em)

  [Hormat kami,]
  linebreak()
  ketua.at("jabatan", default: "")

  block(height: ttd-gap, width: 100%, spacing: 0.3em, {
    if ttd-img != none {
      place(center + horizon, image(ttd-img, height: ttd-height, width: sign-width, fit: "contain"))
    }
  })

  strong(underline(ketua.at("nama", default: "")))
  linebreak()
  [NRP. #ketua.at("nrp", default: "")]

  if stempel-img != none {
    place(top + left, dx: stempel-dx, dy: stempel-dy, image(stempel-img, width: stempel-width))
  }
}))
