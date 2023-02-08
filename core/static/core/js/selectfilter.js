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
        emlojs.selectfilter_service.toggle_search($(e.target))
    },

    on_input_change: function (event) {
        if (['ArrowUp', 'ArrowDown', 'Enter'].includes(event.key)) {
            return
        }

        // build item list
        let root_ele = emlojs.selectfilter_service.find_root_ele(event.target)
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

        // select the first items
        list_jqe.find('.sf-item:first').addClass('selected')
    },

    on_item_click: function (e) {
        let target_jqe = $(e.target);
        emlojs.selectfilter_service.select_choice(target_jqe);
        emlojs.selectfilter_service.close_search(target_jqe);
    },

    select_choice: function (item_jqe) {
        let root_ele = emlojs.selectfilter_service.find_root_ele(item_jqe);
        root_ele.find('.sf-select').val(item_jqe.text())
        root_ele.find('.sf-hidden').val(item_jqe.attr('value'))

        root_ele.trigger('select-changed', [item_jqe.text(), item_jqe.attr('value')]);
    },

    close_search: function (jqe) {
        emlojs.selectfilter_service.find_root_ele(jqe).find('.sf-search-div').hide();
    },

    toggle_search: function (jqe) {
        let search_div_jqe = emlojs.selectfilter_service.find_root_ele(jqe).find('.sf-search-div');
        search_div_jqe.toggle()
        if (search_div_jqe.is(":visible")) {
            search_div_jqe.find('.sf-input').focus()
        }

    },

    on_input_keydown: function (event) {

        function replace_other_item(get_other_fn) {
            let cur_item_ele = event.target.parentElement.querySelector('.sf-item.selected')
            let other = get_other_fn(cur_item_ele)
            if (other) {
                cur_item_ele.classList.remove(selected_class_name)
                other.classList.add(selected_class_name)
            }
        }


        const selected_class_name = 'selected'
        if (event.key === 'Enter') {
            event.preventDefault();
            let root_ele = emlojs.selectfilter_service.find_root_ele($(event.target));
            let item_jqe = root_ele.find('.sf-item.selected')
            if (!item_jqe.length) {
                item_jqe = root_ele.find('.sf-item:first')
            }
            if (item_jqe.length) {
                emlojs.selectfilter_service.select_choice(item_jqe)
            }
            emlojs.selectfilter_service.close_search($(event.target));
        } else if (event.key === 'ArrowUp') {
            replace_other_item(e => e.previousElementSibling)

        } else if (event.key === 'ArrowDown') {
            replace_other_item(e => e.nextElementSibling)
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

    let root_jqe = $('.selectfilter-root');
    root_jqe.on('clean', emlojs.selectfilter_service.on_root_clean);
    for (let root_ele of root_jqe) {
        emlojs.selectfilter_service.define_list($(root_ele))
    }

}