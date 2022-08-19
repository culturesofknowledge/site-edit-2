function setup_url_checker() {
    $('.url_checker').each((idx, e) => {
        let jqe_container = $('<div class="url_checker_div"></div>');

        // input box
        let jqe_input = $(e);
        jqe_input.wrap(jqe_container);

        // renew container
        jqe_container = jqe_input.parent()

        // button
        let jqe_btn = $('<button>');
        jqe_btn.on('click', (jqe_btn_e) => {
            jqe_btn_e.preventDefault()
            window.open($(jqe_btn_e.target).parent().find('input').val(), '_blank')
        });
        jqe_container.append(jqe_btn);

    })

}

function setup_record_delete() {
    // KTODO add dialog html if not exist

    $('.record_delete').on("click", () => {
        show_delete_dialog()
    });

}

function show_delete_dialog() {
    var retVal = confirm("Delete record?");
    console.log(retVal)

}

function setup_standtext() {
    $('.res_standtext').each((i, e) => {
        append_standtext_ele(e)
    });
}

function create_standtext_btn(text, target_id) {
    let ele = $('<div>');
    ele.text(text)
    ele.attr('target_id', target_id)
    ele.addClass('standtext_btn')

    ele.on('click', (e) => {

        let target_ele = $('#' + ele.attr('target_id'));
        let space = target_ele.val() ? ' ' : '';
        target_ele.val(
            `${target_ele.val()}${space}${ele.text()}`
        );
    });

    return ele;

}

function append_standtext_ele(target_text_ele) {

    // build list of standtext button
    const standtext_list = [
        'GeoNames', 'TGN', 'Wikidata ID', 'Wikipeda',
    ];
    const text_ele_list = standtext_list.map((t) => {
        return create_standtext_btn(t, target_text_ele.id)
    })

    //  build standtext container
    let standtext_div_jqe = $('<div>')
    standtext_div_jqe.addClass('flex')
    standtext_div_jqe.append(text_ele_list)
    $(target_text_ele).after(standtext_div_jqe)

}


function setup_checkbox_position() {
    /** django always put checkbox after the label
     *  this function reorder checkbox and label, put checkbox before label
     *  for scss "+ label" style
     */
    $('.elcheckbox').each((i, e) => {
        let checkbox_jqe = $(e)
        let label = checkbox_jqe.prev('label')
        checkbox_jqe.parent().remove(checkbox_jqe)
        label.before(
            checkbox_jqe
        )
    })

}
