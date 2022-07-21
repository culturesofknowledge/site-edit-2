function setup_url_checker() {
    $('.url_checker').each((idx, e) => {
        let jqe_container = $('<div class="url_checker_div"></div>');

        // input box
        let jqe_input = $(e);
        jqe_input.wrap(jqe_container);
        jqe_input.on("input", (jqe_input_e) => {
            $.ajax({
                url: jqe_input_e.target.value,
                crossDomain: true,
                dataType: 'jsonp',
            }).always(function (data) {
                const _btn = jqe_input.parent().find('button');
                if (data.status < 300) {
                    _btn.addClass('valid');
                    _btn.removeClass('invalid');
                } else {
                    _btn.removeClass('valid');
                    _btn.addClass('invalid');
                }
            });

        });

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