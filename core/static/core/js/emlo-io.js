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