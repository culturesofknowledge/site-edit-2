var emlojs = emlojs || {};
emlojs.save_on_enter = {
    setup_save_on_enter: function () {
        $('form').on('keydown', function (e) {
            if (e.key !== 'Enter') {
                return;
            }
            const $target = $(e.target);
            if ($target.is('textarea')) {
                return; // Enter in a textarea just adds a new line
            }
            if ($target.is('a')) {
                return; // e.g. tab-navigation links
            }
            if ($target.is('.sticky-btn')) {
                return; // Save/Save and close/Cancel already do the right thing
            }
            if ($target.closest('.selectfilter-root').length) {
                return; // has its own Enter handling
            }
            if ($target.is('select, input[type=file]')) {
                return; // Enter's native behaviour here varies by browser - leave it alone
            }
            e.preventDefault();
            $('#save_btn').trigger('click');
        });
    },
}
