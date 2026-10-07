(function(){
  function hidden(id){var el=document.getElementById(id);return !el||getComputedStyle(el).display==='none';}
  // 広告ブロック：おとりの要素が隠れ、おとりの通信が止まっていれば効いている
  var ads = hidden('baitAd') && !window.__keseruAdBait;
  // プライバシー：おとりの計測が止まり、Cookieバナー型のおとりが隠れていれば効いている
  var priv = !window.__keseruTrackBait && hidden('baitAnnoy');
  function mark(id,on){var e=document.getElementById(id);e.textContent=on?'効いています ✓':'効いていません ✕';e.className=on?'ok':'ng';}
  mark('rAds',ads); mark('rPriv',priv);
  var hero=document.getElementById('hero'),t=document.getElementById('title'),s=document.getElementById('sub'),b=document.getElementById('badge');
  if(ads&&priv){t.textContent='消えています';s.textContent='ケセルはSafariで効いています。';b.textContent='✓';}
  else if(ads||priv){hero.classList.add('half');t.textContent='あと1つ、オンにしてください';s.textContent='片方の拡張機能がオフです。';b.textContent='!';document.getElementById('help').hidden=false;}
  else{hero.classList.add('bad');t.textContent='まだ効いていません';s.textContent='Safariの設定でケセルをオンにしてください。';b.textContent='✕';document.getElementById('help').hidden=false;}
})();
