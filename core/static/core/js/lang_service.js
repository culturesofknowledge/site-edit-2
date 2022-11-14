function on_lang_del_click(e) {
    e.preventDefault();
    $(e.target.parentElement).remove();
}

function setup_add_lang() {
    $('.lang_add_btn').on('click', function (e) {
        e.preventDefault();
        let lang_div_jqe = $(e.target.parentElement);
        let selected_lang_jqe = lang_div_jqe.find('input[type=text]');
        let selected_lang = selected_lang_jqe.val()
        if (!selected_lang) {
            return
        }

        let new_lang_div = lang_div_jqe.find('.new_lang_div');
        let new_lang = $('<div class="row-no-margin"></div>')
        new_lang.append(`<label>${selected_lang}</label>`)
        new_lang.append(`<input name="lang_name" type="hidden" value="${selected_lang}" />`)
        new_lang.append(`<input name="lang_note" type="text" />`)
        let del_btn_jqe = $('<button class="lang_del_btn">Del</button>')
        del_btn_jqe.on('click', on_lang_del_click)
        new_lang.append(del_btn_jqe)

        new_lang_div.append(new_lang)
        selected_lang_jqe.val('')
    })
    $('.lang_del_btn').on('click', on_lang_del_click)

}
