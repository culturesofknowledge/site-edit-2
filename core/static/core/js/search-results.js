
if(localStorage.getItem('fieldset-toggle') == 'false')  {
   $('#query-fieldset').toggle();
   $('#query-result').toggleClass('col--3of4');
}

if(localStorage.getItem('advanced-search-toggle') == 'true')  {
    $('.advanced_search').toggle();
    $('.search_input').toggleClass('col--3of4');
    $('.search_input').toggleClass('col--4of4');
    $( "#advanced_search" ).prop( "checked", true);
}


var emlojs = emlojs || {};
emlojs.selectable_service = {
    _mode_change_listener_fn_list: [],
    is_selectable_mode_on: function () {
        return $('.selectable_mode_btn').hasClass('selectable_mode_on');
    },
    setup_toggle_selectable_mode: function () {
        $('.selectable_mode_btn').on('click', (e) => {
            e.preventDefault();
            $(e.target).toggleClass('selectable_mode_on')


            let is_mode_on = this.is_selectable_mode_on()
            this._mode_change_listener_fn_list.forEach((fn) => {
                fn(is_mode_on)
            });
        })
    },
    setup_selectable_entry: function () {
        $('.selectable_entry').on('click', (e) => {
            if (this.is_selectable_mode_on()) {
                $(e.target).closest('.selectable_entry').toggleClass('selected')
            }
        })
    },
    setup_all: function () {
        this.setup_toggle_selectable_mode();
        this.setup_selectable_entry();
    },
    on_mode_change: function (fn) {
        this._mode_change_listener_fn_list.push(fn);
    },
    get_entry_id: function (selectable_entry_ele) {
        return $(selectable_entry_ele).attr('entry_id');
    }

}

emlojs.recref_select_service = {

    setup_all: function () {

        if(return_quick_init_vname) {

            $('.selectable_entry').on('click', (e) => {
                let entry_id = emlojs.selectable_service.get_entry_id(
                    $(e.target).closest('.selectable_entry')
                );

                let form = $('<form action="' + vname_action_url + '">');
                form.attr(
                    'action',
                    form.attr('action').replace('__entry_id__', entry_id)
                )
                $('body').append(form)
                form.submit()
            })

        }

    },

}


function submit_page(target_page_num) {
    if (target_page_num) {
        let page_ele = document.getElementById('id_page')
        page_ele.setAttribute('value', target_page_num)
    }

    document.getElementById('search_form').submit()
}

function setup_merge_btn() {
    $('#merge_btn').hide()
    emlojs.selectable_service.on_mode_change((is_on) => {
        if (is_on) {
            $('#merge_btn').show()
        } else {
            $('#merge_btn').hide()

            // cancel all selected entry
            $('.selectable_entry.selected').removeClass('selected');
        }
    });

    $('#merge_btn').on('click', (e) => {
        e.preventDefault();

        // clean up old merge_id if any
        $('#merge_form input[name=__merge_id]').remove();

        let form = $('#merge_form');
        $('.selectable_entry.selected').map((i, v) => {
            let entry_id = emlojs.selectable_service.get_entry_id(v);
            return $(`<input type="hidden" name="__merge_id" value="${entry_id}" />`);
        }).each((i, v) => {
            form.append(v);
        });

        // debugger
        form.submit()
    })

}

['id_next_page', 'id_previous_page'].forEach((target_id) => {
    let ele = document.getElementById(target_id);
    if (ele) {
        ele.addEventListener('click', () => {
            submit_page(ele.getAttribute('page'))
        });
    }
});

['id_sort_by', 'id_num_record', 'id_order_0', 'id_order_1',
    'display-as-grid', 'display-as-list'].forEach((target_id) => {
    if(document.getElementById(target_id)) {
            document.getElementById(target_id).addEventListener('change', () => {
            submit_page();

        });
    }
});

function setup_fieldset_toggle() {
    $('#fieldset-toggle-btn').click(function () {
        $('#query-fieldset').toggle();
        $('#query-result').toggleClass('col--3of4');
        localStorage.setItem('fieldset-toggle', $('#query-fieldset').is(':visible'));
    });
}

function setup_advanced_search_toggle() {
    $('#advanced_search').on('click', function () {
        $('.advanced_search').toggle();
        $('.search_input').toggleClass('col--3of4');
        $('.search_input').toggleClass('col--4of4');
        localStorage.setItem('advanced-search-toggle', $('#advanced_search').prop('checked'));
    });

}

function show_column(show_tag, column_index) {
    show_tag.remove();
    $('#results_table tr > *:nth-child(' + column_index + ')').show();
}

function hide_column(column_index, column_name) {
    $('#results_table tr > *:nth-child(' + column_index + ')').hide();
    $('#hidden_columns').append('<span onclick="show_column(this, ' + column_index + ');">'+ feather.icons['eye'].toSvg() + '&nbsp;' + column_name + '</span>');
}

function isEmpty(column) {
    for(var i = 0; i < column.length; i++) {
        if($(column[i]).text().trim() != '' || $(column[i]).children().length > 0)
                return false;

    }
 return true;
}

function add_hide_buttons_to_columns() {
    var columns = $('#results_table thead')[0].children[1].cells;
    for (var i = 0; i < columns.length; i++) {
        var header = columns[i].innerText;

        if(header == '')
            header = '[Uncertainties]';

        columns[i].innerHTML += '&nbsp;<a href="#" onclick="hide_column(' + (i + 1) + ', \'' + header.replace("'", "\\'") + '\');">' + feather.icons['eye-off'].toSvg() + '</span></a>';

        if(isEmpty($('#results_table tr > *:nth-child(' + (i + 1) + ')').filter('td')))    {
            hide_column(i + 1, header);
        }
    }
}

$(function () {
    setup_record_delete();
    emlojs.selectable_service.setup_all()
    setup_merge_btn();
    setup_fieldset_toggle();
    setup_advanced_search_toggle();

    if($('#results_table thead').length)   {
        add_hide_buttons_to_columns();
    }

    if(recref_mode == '1')  {
        emlojs.recref_select_service.setup_all()
    }
})