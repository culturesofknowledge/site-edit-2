

function switch_content(selected_content_selector){
    $('.tab-content').hide();
    $(selected_content_selector).show();
}


function setup_work_form_listener() {
    switch_content('.tc-corr')

    $('.tablinks').on('click', function (e) {
        e.preventDefault();

        let content_selector = $(e.target).attr('content-selector');
        switch_content(content_selector)
    });


}
