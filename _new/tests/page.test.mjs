// TDD contract for _new/index.html
//
// The page is the "Interactive Session" template: a talking-head video that
// fills the whole screen as the BACKGROUND, with glass content + nav on top.
// Navigating swaps the head to a short per-section "part" (a trimmed slice of
// the same head video) — the head stays, the next part speaks, the buttons
// change. These tests lock that behaviour in so it can't regress.
//
// Note: the visual swap is debounced (fade-out, then change src), so the
// authoritative "which part is showing" signal is the synchronous
// `#assistant-video[data-part]` attribute, which is what we assert.

import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { JSDOM } from 'jsdom';

const __dirname = dirname(fileURLToPath(import.meta.url));
const HTML = readFileSync(join(__dirname, '..', 'index.html'), 'utf8');

const SECTION_IDS = ['overview', 'strategy', 'platform', 'employees', 'products', 'education'];

function makeDom() {
  return new JSDOM(HTML, {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    url: 'https://andre.technology/_new/index.html',
    beforeParse(window) {
      const proto = window.HTMLMediaElement.prototype;
      proto.play = function () { this._playing = true; return Promise.resolve(); };
      proto.pause = function () { this._playing = false; };
      proto.load = function () {};
    },
  });
}

function srcAttr(el) { return el ? (el.getAttribute('src') || '') : ''; }

let dom, window, doc;
beforeEach(() => {
  dom = makeDom();
  window = dom.window;
  doc = window.document;
});

test('exposes a HEAD_PARTS map covering every section, all head clips under assets/', () => {
  assert.ok(window.HEAD_PARTS, 'window.HEAD_PARTS should be defined');
  for (const id of SECTION_IDS) {
    const v = window.HEAD_PARTS[id];
    assert.equal(typeof v, 'string', `HEAD_PARTS.${id} should be a string path`);
    assert.match(v, /^assets\/head-.+\.mp4$/, `HEAD_PARTS.${id} should be a head-*.mp4 under assets/`);
  }
  assert.equal(Object.keys(window.HEAD_PARTS).length, SECTION_IDS.length);
});

test('exposes a global openTab(id) function', () => {
  assert.equal(typeof window.openTab, 'function');
});

test('the talking head is the FULL-SCREEN BACKGROUND (not an avatar)', () => {
  const v = doc.querySelector('#assistant-video');
  assert.ok(v, '#assistant-video exists');
  // lives in a fixed, full-bleed, z-0 background container
  const bg = v.parentElement;
  const bgc = bg.className;
  assert.ok(/\bfixed\b/.test(bgc) && /\binset-0\b/.test(bgc) && /\bz-0\b/.test(bgc),
    'head video must sit in a fixed inset-0 z-0 background layer');
  // and the video itself fills the background (cover on desktop / contain on mobile)
  assert.ok(/object-(cover|contain)/.test(v.className), 'head video must fill the background');
  assert.ok(/\bw-full\b/.test(v.className) && /\bh-full\b/.test(v.className));
  // it is a looping, muted, autoplaying background video
  assert.ok(v.hasAttribute('loop') && v.hasAttribute('autoplay') && v.hasAttribute('muted'));
  // and it shows a head part
  assert.match(srcAttr(v), /assets\/head-.+\.mp4$/);
});

test('renders one nav tab and one content section per section id', () => {
  for (const id of SECTION_IDS) {
    assert.ok(doc.querySelector(`.nav-tab[data-target="${id}"]`), `nav tab for ${id}`);
    assert.ok(doc.querySelector(`.content-section#${id}`), `section for ${id}`);
  }
});

test('initial state: overview is the only active section & tab, head shows the overview part', () => {
  assert.equal(doc.querySelectorAll('.nav-tab.active').length, 1);
  assert.equal(doc.querySelectorAll('.content-section.active').length, 1);
  assert.equal(doc.querySelector('.nav-tab.active').getAttribute('data-target'), 'overview');
  assert.equal(doc.querySelector('.content-section.active').id, 'overview');

  const v = doc.querySelector('#assistant-video');
  assert.equal(v.getAttribute('data-part'), 'overview');
  assert.ok(srcAttr(v).endsWith(window.HEAD_PARTS.overview));
});

for (const id of SECTION_IDS) {
  test(`openTab(${id}) activates that section and points the head at its part`, () => {
    window.openTab(id);

    const activeTabs = [...doc.querySelectorAll('.nav-tab.active')];
    const activeSections = [...doc.querySelectorAll('.content-section.active')];
    assert.equal(activeTabs.length, 1, 'one active tab');
    assert.equal(activeSections.length, 1, 'one active section');
    assert.equal(activeTabs[0].getAttribute('data-target'), id);
    assert.equal(activeSections[0].id, id);

    // the head (background) now targets this section's part
    assert.equal(doc.querySelector('#assistant-video').getAttribute('data-part'), id);
  });
}

test('the head video element is never swapped out — same node, always a head part', () => {
  const before = doc.querySelector('#assistant-video');
  assert.ok(before);
  window.openTab('platform');
  window.openTab('education');
  window.openTab('products');
  const after = doc.querySelector('#assistant-video');
  assert.equal(after, before, 'the head element keeps its identity (голова остаётся)');
  assert.match(srcAttr(after), /assets\/head-.+\.mp4$/, 'src is always one of the head parts');
});

test('clicking a nav tab drives the switch', () => {
  doc.querySelector('.nav-tab[data-target="employees"]').click();
  assert.equal(doc.querySelector('#assistant-video').getAttribute('data-part'), 'employees');
  assert.ok(doc.querySelector('.content-section#employees').classList.contains('active'));
});

test('the hero CTA (inline onclick) navigates to its section', () => {
  const cta = doc.querySelector('#overview button[onclick]');
  assert.ok(cta, 'overview has a CTA button');
  cta.click();
  assert.equal(doc.querySelector('#assistant-video').getAttribute('data-part'), 'strategy');
  assert.ok(doc.querySelector('.content-section#strategy').classList.contains('active'));
});

test('the mic toggle (un)mutes the background head and updates the indicator', () => {
  const v = doc.querySelector('#assistant-video');
  const btn = doc.querySelector('#audio-toggle');
  const icon = doc.querySelector('#audio-icon');
  const wave = doc.querySelector('#sound-wave');
  assert.ok(btn && icon && wave);

  assert.equal(v.muted, true);
  assert.ok(icon.classList.contains('fa-microphone-lines-slash'));
  assert.ok(wave.classList.contains('hidden'));

  btn.click();
  assert.equal(v.muted, false);
  assert.ok(icon.classList.contains('fa-microphone-lines'));
  assert.ok(!wave.classList.contains('hidden'));

  btn.click();
  assert.equal(v.muted, true);
  assert.ok(icon.classList.contains('fa-microphone-lines-slash'));
  assert.ok(wave.classList.contains('hidden'));
});

test('the header keeps nav and the OS button as siblings (no z-overlap nesting)', () => {
  // Regression guard: nav and the OS button must not be stacked such that one
  // covers the other (the old bug that made the last tab unclickable).
  const nav = doc.querySelector('header nav');
  const osBtn = [...doc.querySelectorAll('header button')].find(b => /AI Business OS/i.test(b.textContent));
  assert.ok(nav && osBtn, 'header has a nav and an OS button');
  assert.ok(!nav.contains(osBtn) && !osBtn.contains(nav), 'nav and OS button are not nested');
});

test('the menu button opens the section menu and navigating closes it', () => {
  const toggle = doc.querySelector('#menu-toggle');
  const nav = doc.querySelector('#main-nav');
  assert.ok(toggle && nav, 'a menu button and the nav exist');
  assert.ok(!nav.classList.contains('open'), 'menu starts closed');
  toggle.click();
  assert.ok(nav.classList.contains('open'), 'menu button opens the menu');
  window.openTab('platform');
  assert.ok(!nav.classList.contains('open'), 'choosing a section closes the menu');
});

test('navigation never leaves more than one active section (invariant sweep)', () => {
  for (const id of [...SECTION_IDS].reverse().concat(SECTION_IDS)) {
    window.openTab(id);
    assert.equal(doc.querySelectorAll('.content-section.active').length, 1);
    assert.equal(doc.querySelectorAll('.nav-tab.active').length, 1);
    assert.equal(doc.querySelector('#assistant-video').getAttribute('data-part'), id);
  }
});
