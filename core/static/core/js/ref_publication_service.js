function create_fn_open_ref_pub(url) {
    return function (e) {
        e.preventDefault();
        window.open(url);
        window.on_quick_init_completed = function (data) {
            let textbox_id = $(e.target).closest('.ref-publication-row').attr('textbox_id')
            let target_ta = $('#' + textbox_id)
            target_ta.text(target_ta.text() + ' ' + data.item_name)
        }
    }
}


$(() => {
    $('.ref-publication-row').each((idx, e)=>{
        let target_div = $(e)
        target_div.append( $('<span>Refer publication:</span>') )
        target_div.append( $('<button class="btn inline_btn create_pub"> Create</button>') )
        target_div.append( $('<button class="btn inline_btn copy_pub"> Copy</button>') )

    });
    $('.create_pub').mousedown(create_fn_open_ref_pub('/publication/quick_init'));
    $('.copy_pub').mousedown(create_fn_open_ref_pub('/publication/search?recref_mode=1'));
});
