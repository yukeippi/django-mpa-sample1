// 右ペイン(.ds-offcanvas)を、フォーカスがペインの外にあっても Esc キーで閉じられるようにする。開閉は Bootstrap の offcanvas.js が行う
// (背景を暗くしない設定では、Bootstrap はフォーカスがペインの中にあるときしか Esc を受け付けないため)
document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') {
        return;
    }
    // 開く途中(.showing)のペインも閉じるため、.show で絞り込まない(閉じているペインへの hide() は何もしない)
    document.querySelectorAll('.ds-offcanvas').forEach(function (pane) {
        var instance = bootstrap.Offcanvas.getInstance(pane);
        if (instance) {
            instance.hide();
        }
    });
});
