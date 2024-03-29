function setup_url_checker() {
    $('.url_checker').each((idx, e) => {
        let jqe_container = $('<div class="url_checker_div"></div>');

        // input box
        let jqe_input = $(e);
        jqe_input.wrap(jqe_container);

        // renew container
        jqe_container = jqe_input.parent()

        // button
        let jqe_btn = $('<button class="btn">');
        jqe_btn.on('click', (jqe_btn_e) => {
            jqe_btn_e.preventDefault()
            window.open($(jqe_btn_e.target).parent().find('input').val(), '_blank')
        });
        jqe_container.append(jqe_btn);

    })

}

function setup_standtext(standtext_list) {
    $('.res_standtext').each((i, e) => {
        append_standtext_ele(e, standtext_list)
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

function append_standtext_ele(target_text_ele, standtext_list) {

    // build list of standtext button
    if (standtext_list === undefined) {
        standtext_list = [
            'GeoNames', 'TGN', 'Wikidata ID', 'Wikipeda',
        ];
    }
    const text_ele_list = standtext_list.map((t) => {
        return create_standtext_btn(t, target_text_ele.id)
    })

    //  build standtext container
    let standtext_div_jqe = $('<div>')
    standtext_div_jqe.addClass('row-no-margin')
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

function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1)
        {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return decodeURIComponent(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }