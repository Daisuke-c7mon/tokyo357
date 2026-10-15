// リロ番 練習ストア
// 読み込んだ回数を sessionStorage（このタブだけ）で数え、4回目（3回読み込み直したあと）から在庫ありにする。
// CSP（script-src 'self'）に合わせて外部ファイルにしている。インラインの style 属性も使わない。
// ?drill=busy … 2・3回目を混雑の画面にする（4回目から在庫あり）
// ?drill=queue … 2回目を順番待ちの画面にし、6秒後に自分で読み込み直す（3回目から在庫あり）
// どちらもリロ番の「混雑ガード」を試すため。
(() => {
  "use strict";

  const drill = new URLSearchParams(location.search).get("drill");
  const KEY = "reloban-practice-loads" + (drill ? "-" + drill : "");
  const FLIP_AT = drill === "queue" ? 3 : 4;

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

  // 混雑ガードの練習：お店を隠して、混雑・順番待ちの画面だけを出す
  const showOnly = (id) => {
    Array.from(document.body.children).forEach((el) => {
      if (el.tagName !== "SCRIPT" && el.id !== id) el.hidden = true;
    });
    $(id).hidden = false;
  };
  if (drill === "busy" && (loads === 2 || loads === 3)) {
    showOnly("drillBusy");
    return;
  }
  if (drill === "queue" && loads === 2) {
    showOnly("drillQueue");
    let ahead = 3;
    setInterval(() => { ahead = Math.max(0, ahead - 1); $("ahead").textContent = String(ahead); }, 2000);
    setTimeout(() => location.reload(), 6000);
    return;
  }

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
