// TDD contract for _new/index.html
//
// The page is a single self-contained HTML file. These tests load it in jsdom,
// run its inline script, and assert the interactive behaviour the brief asks for:
//   - a persistent talking-head presenter that never gets swapped out
//   - a cinematic background scene that switches per navigation section
//   - nav tabs + CTA buttons that drive the section/scene switch
//   - an audio toggle that (un)mutes the presenter
//
// Tests are decoupled from specific copy/filenames where possible: they assert
// internal consistency (the active scene matches the SCENES map for the current
// section) rather than hard-coding asset names, so the page stays easy to retheme.

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
      // jsdom does not implement media playback — stub it so the page script runs.
      const proto = window.HTMLMediaElement.prototype;
      proto.play = function () { this._playing = true; return Promise.resolve(); };
      proto.pause = function () { this._playing = false; };
      proto.load = function () {};
    },
  });
}

function activeSceneLayer(doc) {
  return doc.querySelector('.scene-layer.is-active');
}
function src(el) {
  return el ? (el.getAttribute('src') || '') : '';
}

let dom, window, doc;
beforeEach(() => {
  dom = makeDom();
  window = dom.window;
  doc = window.document;
});

test('exposes a SCENES map covering every section, all under assets/', () => {
  assert.ok(window.SCENES, 'window.SCENES should be defined');
  for (const id of SECTION_IDS) {
    const v = window.SCENES[id];
    assert.equal(typeof v, 'string', `SCENES.${id} should be a string path`);
    assert.match(v, /^assets\/.+\.mp4$/, `SCENES.${id} should be an mp4 under assets/`);
  }
  assert.equal(Object.keys(window.SCENES).length, SECTION_IDS.length);
});

test('exposes a global openTab(id) function', () => {
  assert.equal(typeof window.openTab, 'function');
});

test('renders one nav tab and one content section per section id', () => {
  for (const id of SECTION_IDS) {
    assert.ok(doc.querySelector(`.nav-tab[data-target="${id}"]`), `nav tab for ${id}`);
    assert.ok(doc.querySelector(`.content-section#${id}`), `section for ${id}`);
  }
});

test('initial state: overview is the only active section & tab', () => {
  const activeTabs = doc.querySelectorAll('.nav-tab.active');
  const activeSections = doc.querySelectorAll('.content-section.active');
  assert.equal(activeTabs.length, 1);
  assert.equal(activeSections.length, 1);
  assert.equal(activeTabs[0].getAttribute('data-target'), 'overview');
  assert.equal(activeSections[0].id, 'overview');
});

test('initial state: scene stage and active scene layer point at overview', () => {
  const stage = doc.querySelector('#scene-stage');
  assert.ok(stage, '#scene-stage exists');
  assert.equal(stage.getAttribute('data-scene'), 'overview');
  assert.ok(src(activeSceneLayer(doc)).endsWith(window.SCENES.overview));
});

test('there are exactly two stacked scene layers for crossfading', () => {
  const layers = doc.querySelectorAll('.scene-layer');
  assert.equal(layers.length, 2);
  assert.equal(doc.querySelectorAll('.scene-layer.is-active').length, 1);
});

for (const id of SECTION_IDS) {
  test(`openTab(${id}) activates exactly that section + matching scene`, () => {
    window.openTab(id);

    const activeTabs = [...doc.querySelectorAll('.nav-tab.active')];
    const activeSections = [...doc.querySelectorAll('.content-section.active')];
    assert.equal(activeTabs.length, 1, 'one active tab');
    assert.equal(activeSections.length, 1, 'one active section');
    assert.equal(activeTabs[0].getAttribute('data-target'), id);
    assert.equal(activeSections[0].id, id);

    const stage = doc.querySelector('#scene-stage');
    assert.equal(stage.getAttribute('data-scene'), id);
    assert.equal(doc.querySelectorAll('.scene-layer.is-active').length, 1);
    assert.ok(
      src(activeSceneLayer(doc)).endsWith(window.SCENES[id]),
      `active scene layer should show ${window.SCENES[id]}`
    );
  });
}

test('the talking head presenter persists across navigation (same node, same src)', () => {
  const before = doc.querySelector('#presenter');
  assert.ok(before, '#presenter exists');
  const beforeSrc = src(before);
  assert.ok(beforeSrc, 'presenter has a src');

  window.openTab('platform');
  window.openTab('education');
  window.openTab('products');

  const after = doc.querySelector('#presenter');
  assert.equal(after, before, 'presenter node identity is unchanged');
  assert.equal(src(after), beforeSrc, 'presenter src is never swapped');
});

test('clicking a nav tab drives the switch', () => {
  doc.querySelector('.nav-tab[data-target="employees"]').click();
  assert.equal(doc.querySelector('#scene-stage').getAttribute('data-scene'), 'employees');
  assert.ok(doc.querySelector('.content-section#employees').classList.contains('active'));
});

test('clicking any [data-target] CTA navigates (event delegation)', () => {
  const cta = doc.querySelector('[data-target="strategy"]:not(.nav-tab)');
  assert.ok(cta, 'there is at least one non-tab CTA wired to a section');
  cta.click();
  assert.equal(doc.querySelector('#scene-stage').getAttribute('data-scene'), 'strategy');
});

test('audio toggle (un)mutes the presenter and updates the indicator', () => {
  const presenter = doc.querySelector('#presenter');
  const btn = doc.querySelector('#audio-toggle');
  const icon = doc.querySelector('#audio-icon');
  const wave = doc.querySelector('#sound-wave');
  assert.ok(btn && icon && wave, 'audio controls exist');

  // starts muted
  assert.equal(presenter.muted, true);
  assert.ok(icon.classList.contains('fa-microphone-lines-slash'));
  assert.ok(wave.classList.contains('hidden'));

  btn.click(); // unmute
  assert.equal(presenter.muted, false);
  assert.ok(icon.classList.contains('fa-microphone-lines'));
  assert.ok(!wave.classList.contains('hidden'));

  btn.click(); // mute again
  assert.equal(presenter.muted, true);
  assert.ok(icon.classList.contains('fa-microphone-lines-slash'));
  assert.ok(wave.classList.contains('hidden'));
});

test('top bar: header is pointer-events-none but every interactive group re-enables them', () => {
  // Regression guard: the fixed top bar must let clicks through to the page,
  // while its own interactive groups (logo, OS button, nav) stay clickable.
  // A missing `pointer-events-auto` here silently makes nav tabs unclickable.
  const header = doc.querySelector('header');
  assert.ok(header, 'a top bar <header> exists');
  assert.ok(header.classList.contains('pointer-events-none'), 'header should be pointer-events-none');

  const groups = header.querySelectorAll(':scope > div > *');
  assert.ok(groups.length >= 3, 'top bar should hold logo + OS + nav');
  for (const g of groups) {
    assert.ok(
      g.classList.contains('pointer-events-auto'),
      `top-bar group <${g.tagName.toLowerCase()}> must have pointer-events-auto`
    );
  }
  // and the nav specifically
  assert.ok(doc.querySelector('nav').classList.contains('pointer-events-auto'));
});

test('navigation never leaves more than one active section (invariant sweep)', () => {
  for (const id of [...SECTION_IDS].reverse().concat(SECTION_IDS)) {
    window.openTab(id);
    assert.equal(doc.querySelectorAll('.content-section.active').length, 1);
    assert.equal(doc.querySelectorAll('.nav-tab.active').length, 1);
    assert.equal(doc.querySelectorAll('.scene-layer.is-active').length, 1);
  }
});
