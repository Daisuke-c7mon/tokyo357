/* Sauna Inc. — tokyo357.com
   温度計レールとスクロール表示の制御。JSが無くても内容は全て読める。 */
(function () {
  'use strict';

  document.documentElement.classList.remove('no-js');

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- スクロール表示 --- */
  var rises = document.querySelectorAll('.rise');
  if (!('IntersectionObserver' in window) || reduce) {
    Array.prototype.forEach.call(rises, function (el) { el.classList.add('in'); });
  } else {
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        revealer.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    Array.prototype.forEach.call(rises, function (el) { revealer.observe(el); });
  }

  /* --- 温度計レール --- */
  var gauge = document.querySelector('.gauge');
  if (!gauge) return;

  var read = gauge.querySelector('.gauge-read');
  var fill = gauge.querySelector('.gauge-fill');
  var note = gauge.querySelector('.gauge-note');
  var stages = document.querySelectorAll('[data-temp]');
  if (!stages.length) return;

  var current = null;

  function apply(el) {
    if (el === current) return;
    current = el;
    var temp = el.getAttribute('data-temp');
    var phase = el.getAttribute('data-phase') || 'hot';
    var label = el.getAttribute('data-stage') || '';
    var level = parseFloat(el.getAttribute('data-level') || '20');

    read.textContent = temp;
    note.textContent = label;
    fill.style.height = level + '%';
    gauge.setAttribute('data-phase', phase);
  }

  if (!('IntersectionObserver' in window)) {
    apply(stages[0]);
    return;
  }

  var tracker = new IntersectionObserver(function (entries) {
    /* 画面中央にいちばん近いステージを採用する */
    var best = null, bestRatio = 0;
    entries.forEach(function (e) {
      if (e.isIntersecting && e.intersectionRatio >= bestRatio) {
        bestRatio = e.intersectionRatio;
        best = e.target;
      }
    });
    if (best) apply(best);
  }, { rootMargin: '-45% 0px -45% 0px', threshold: [0, 0.01, 0.5, 1] });

  Array.prototype.forEach.call(stages, function (el) { tracker.observe(el); });
  apply(stages[0]);
})();
