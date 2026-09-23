// 右ペイン(.ds-offcanvas)を、フォーカスがペインの外にあっても Esc キーで閉じられるようにする。開閉は Bootstrap の offcanvas.js が行う
// (背景を暗くしない設定では、Bootstrap はフォーカスがペインの中にあるときしか Esc を受け付けないため)
document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') {
        return;
    }
    document.querySelectorAll('.ds-offcanvas.show').forEach(function (pane) {
        bootstrap.Offcanvas.getOrCreateInstance(pane).hide();
    });
});
