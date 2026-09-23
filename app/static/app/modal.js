// モーダル(.ds-modal)のヘッダーをドラッグして移動できるようにする。開閉は Bootstrap の modal.js が行う
document.querySelectorAll('.ds-modal').forEach(function (modal) {
    var dialog = modal.querySelector('.ds-modal-dialog');
    var header = modal.querySelector('.ds-modal-header');
    var drag = null;

    header.addEventListener('pointerdown', function (event) {
        if (event.button !== 0 || event.target.closest('button')) {
            return;
        }
        // 画面の外へ出せる範囲を、ドラッグ開始時の位置から決める(ヘッダーは常に画面内に残す)
        var rect = dialog.getBoundingClientRect();
        drag = {
            pointerX: event.clientX,
            pointerY: event.clientY,
            left: parseFloat(dialog.style.left) || 0,
            top: parseFloat(dialog.style.top) || 0,
            minX: -rect.left,
            maxX: document.documentElement.clientWidth - rect.right,
            minY: -rect.top,
            maxY: window.innerHeight - rect.top - header.offsetHeight,
        };
        header.setPointerCapture(event.pointerId);
    });

    header.addEventListener('pointermove', function (event) {
        if (!drag) {
            return;
        }
        var dx = Math.min(Math.max(event.clientX - drag.pointerX, drag.minX), drag.maxX);
        var dy = Math.min(Math.max(event.clientY - drag.pointerY, drag.minY), drag.maxY);
        dialog.style.left = drag.left + dx + 'px';
        dialog.style.top = drag.top + dy + 'px';
    });

    header.addEventListener('pointerup', function () { drag = null; });
    header.addEventListener('pointercancel', function () { drag = null; });

    // 閉じたら元の位置に戻す
    modal.addEventListener('hidden.bs.modal', function () {
        dialog.style.left = '';
        dialog.style.top = '';
    });
});
