var emlojs = emlojs || {};
emlojs.selectfilter_service = {

    find_root_ele: function (ele) {
        if (ele) {
            return $(ele).closest('.selectfilter-root')
        } else {
            return $('.selectfilter-root')
        }
    },

    on_select_clicked: function (e) {
        emlojs.selectfilter_service.toggle_search()
    },

    on_input_change: function (e) {
        // build item list
        let root_ele = emlojs.selectfilter_service.find_root_ele(e.target)
        emlojs.selectfilter_service.define_list(root_ele)
    },
    define_list: function (root_jqe) {
        let list_jqe = root_jqe.find('.sf-list')
        list_jqe.html('')
        let selected_text = root_jqe.find('.sf-input').val()
        let selected_list = root_jqe.find('datalist option')
        selected_list = selected_list.map((i, e) => [[e.value, e.text]])
        if (selected_text !== '') {
            selected_list = selected_list.filter((i, e) => e.some((item) => item.includes(selected_text)));
        }
        for (let option_jqe of selected_list) {
            let item_jqe = $('<div class="sf-item">')
            item_jqe.html(option_jqe[0])
            item_jqe.attr('value', option_jqe[1])
            item_jqe.click(emlojs.selectfilter_service.on_item_click)
            list_jqe.append(item_jqe)
        }

    },

    on_item_click: function (e) {
        emlojs.selectfilter_service.select_choice($(e.target));
        emlojs.selectfilter_service.close_search();
    },

    select_choice: function (item_jqe) {
        let root_ele = emlojs.selectfilter_service.find_root_ele(item_jqe);
        root_ele.find('.sf-select').val(item_jqe.text())
        root_ele.find('.sf-hidden').val(item_jqe.attr('value'))

        root_ele.trigger('select-changed', [item_jqe.text(), item_jqe.attr('value')]);
    },
    select_first: function () {
        let first_item_jqe = emlojs.selectfilter_service.find_root_ele().find('.sf-list .sf-item:first')
        if (first_item_jqe.length) {
            emlojs.selectfilter_service.select_choice(first_item_jqe)
        }
    },

    close_search: function () {
        $('.sf-search-div').hide();
    },

    toggle_search: function () {
        $('.sf-search-div').toggle()
    },

    on_input_keydown: function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            emlojs.selectfilter_service.select_first();
            emlojs.selectfilter_service.close_search();
        }

    },
    on_root_clean: function (e) {
        let root_jqe = $(e.target)
        root_jqe.find('.sf-select,.sf-hidden,.sf-input').val('')
        emlojs.selectfilter_service.define_list(root_jqe)
    },


}

function setup_selectfilter() {
    $('.selectfilter-root .sf-select').click(emlojs.selectfilter_service.on_select_clicked);
    $('.selectfilter-root .sf-input')
        .keyup(emlojs.selectfilter_service.on_input_change)
        .keydown(emlojs.selectfilter_service.on_input_keydown);

    $('.selectfilter-root').on('clean', emlojs.selectfilter_service.on_root_clean);

    emlojs.selectfilter_service.define_list($('.selectfilter-root'))

}