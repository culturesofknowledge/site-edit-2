function on_lang_del_click(e) {
    e.preventDefault();
    $(e.target.parentElement).remove();
}

function on_lang_select_change(e, selected_text, selected_val) {
    let selected_lang = selected_text;
    if (!selected_lang) {
        return
    }

    let lang_div_jqe = $(e.target).closest('.lang_div')
    let new_lang_div = lang_div_jqe.find('.new_lang_div');
    let new_lang = $('<div class="lang-item"></div>')
    new_lang.append(`<label class="lang-label">${selected_lang}</label>`)
    new_lang.append(`<input name="lang_name" type="hidden" value="${selected_lang}" />`)
    new_lang.append(`<input name="lang_note" type="text" />`)
    let del_btn_jqe = $('<button class="lang_del_btn">Del</button>')
    del_btn_jqe.on('click', on_lang_del_click)
    new_lang.append(del_btn_jqe)

    new_lang_div.append(new_lang)

    // cleanup selectfilter
    lang_div_jqe.find('.selectfilter-root').trigger('clean');

}

function setup_add_lang() {
    $('.lang_del_btn').on('click', on_lang_del_click)
    $('.lang_div .selectfilter-root').on('select-changed', on_lang_select_change);

}
