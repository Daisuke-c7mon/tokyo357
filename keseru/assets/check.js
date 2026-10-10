(function(){
  function hidden(id){var el=document.getElementById(id);return !el||getComputedStyle(el).display==='none';}
  // 見える広告5つ。ケセルのルール（どのサイトにも効く一般のもの）で消える
  var items=[['r1','adTop'],['r2','adMid'],['r3','adFoot'],['r4','adPr'],['r5','adCookie']];
  var gone=0;
  items.forEach(function(p){var h=hidden(p[1]);if(h)gone++;mark(p[0],h,'消えました ✓','出ています ✕');});
  // 広告ブロック：広告の枠が隠れ、おとりの通信が止まっていれば効いている
  var ads=hidden('baitAd')&&!window.__keseruAdBait&&hidden('adTop')&&hidden('adMid')&&hidden('adFoot');
  // プライバシー：おとりの計測が止まり、PR枠とCookieの帯が隠れていれば効いている
  var priv=hidden('baitAnnoy')&&!window.__keseruTrackBait&&hidden('adPr')&&hidden('adCookie');
  function mark(id,on,a,b){var e=document.getElementById(id);e.textContent=on?(a||'効いています ✓'):(b||'効いていません ✕');e.className=on?'ok':'ng';}
  mark('rAds',ads); mark('rPriv',priv);
  var hero=document.getElementById('hero'),t=document.getElementById('title'),s=document.getElementById('sub'),b=document.getElementById('badge');
  document.body.classList.add(ads&&priv?'is-on':'is-off');
  if(ads&&priv){t.textContent='広告を'+gone+'つ消しました';s.textContent='ケセルはSafariで効いています。下の記事に広告が1つも出ていません。';b.textContent='✓';}
  else if(ads||priv){hero.classList.add('half');t.textContent='あと1つ、オンにしてください';s.textContent='片方の拡張機能がオフです。まだ広告が'+(5-gone)+'つ出ています。';b.textContent='!';document.getElementById('help').hidden=false;}
  else{hero.classList.add('bad');t.textContent='広告が'+(5-gone)+'つ出ています';s.textContent='ケセルがまだ効いていません。Safariの設定でオンにしてください。';b.textContent='✕';document.getElementById('help').hidden=false;}
})();
