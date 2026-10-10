// リロ番 練習ストア
// 読み込んだ回数を sessionStorage（このタブだけ）で数え、4回目（3回読み込み直したあと）から在庫ありにする。
// CSP（script-src 'self'）に合わせて外部ファイルにしている。インラインの style 属性も使わない。
(() => {
  "use strict";

  const KEY = "reloban-practice-loads";
  const FLIP_AT = 4;

  let loads = 1;
  try {
    loads = (parseInt(sessionStorage.getItem(KEY) || "0", 10) || 0) + 1;
    sessionStorage.setItem(KEY, String(loads));
  } catch (e) {
    // sessionStorage が使えない環境では数えられないので、毎回1回目として表示する
    loads = 1;
  }

  const $ = (id) => document.getElementById(id);
  const stock = $("stock");
  const cart = $("cart");
  const done = $("done");

  $("loads").textContent = String(loads);

  if (loads >= FLIP_AT) {
    stock.textContent = "在庫状況：在庫あり";
    stock.classList.remove("is-out");
    stock.classList.add("is-in");
    cart.disabled = false;
    cart.textContent = "カートに入れる";
    cart.addEventListener("click", () => {
      done.hidden = false;
    });
  }

  // 閲覧中の人数は読み込むたびに変える（「変化したら」の誤報を体験するため）
  $("viewers").textContent = String(80 + Math.floor(Math.random() * 160));

  // 時計は毎秒進める
  const clock = $("clock");
  const pad = (n) => String(n).padStart(2, "0");
  const tick = () => {
    const d = new Date();
    clock.textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  };
  tick();
  setInterval(tick, 1000);

  $("reset").addEventListener("click", (ev) => {
    ev.preventDefault();
    try { sessionStorage.removeItem(KEY); } catch (e) { /* noop */ }
    location.reload();
  });
})();
