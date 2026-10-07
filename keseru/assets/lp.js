// App Store の ID が決まったら APP_ID を入れる（空のあいだは「まもなく公開」）
const APP_ID = "";
if (APP_ID) {
  const a = document.getElementById('appstore');
  a.href = "https://apps.apple.com/jp/app/id" + APP_ID;
  a.classList.remove('soon');
  a.innerHTML = '<span><small>iPhone・iPad</small>App Store で入手</span>';
}
