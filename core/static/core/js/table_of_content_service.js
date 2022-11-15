var delayed_table_of_content_scroll_fn = null;

function isElementInViewpoint(ele) {
    let ele_jqe = $(ele);
    var elementTop = ele_jqe.offset().top;
    var elementBottom = elementTop + ele_jqe.outerHeight();

    let window_jqe = $(window)
    var viewportTop = window_jqe.scrollTop();
    var viewportBottom = viewportTop + window_jqe.height();

    return elementBottom > viewportTop && elementTop < viewportBottom;
}

function toggle_table_of_content(){
    if ($('#toc-body').is(':visible')){
        $('#toc-body').hide()
        $('#toc-btn').show()
    } else {
        $('#toc-body').show()
        $('#toc-btn').hide()
    }
}


function build_table_of_content_ui() {
    let container = $('<div class="fixed-right-bottom">')
    container.append()
    let toc_btn = $('<button id="toc-btn" >Table of Content</button>')
    toc_btn.on('click', toggle_table_of_content);


    let title = $('<h3>Table of Content</h3>')
    title.on('click', toggle_table_of_content);

    let body = $('<div id="toc-body" class="flex-col">')
    body.append(title)
    body.hide()

    $('.toc-item, .toc-sub-item').each(function (idx, ele) {
        let link_jqe;
        if (ele.classList.contains('toc-sub-item')) {
            link_jqe = $(`<li><a href="#${ele.id}">${ele.textContent}</a></li>`)
        } else {
            link_jqe = $(`<a href="#${ele.id}">${ele.textContent}</a>`)
        }
        // debugger
        body.append(link_jqe)
    });

    container.append(toc_btn)
    container.append(body)
    $('body').append(container);
}


function find_new_cur_toc_item(){
    for (let toc_item_jqe of $('.toc-item, .toc-sub-item')) {
        if (isElementInViewpoint(toc_item_jqe)) {
            return toc_item_jqe
        }
    }
    return null;
}

function setup_table_of_content() {
    const cur_toc_item_class = 'toc-cur-item';
    let old_toc_id = null;


    // build table of content UI
    build_table_of_content_ui()


    // setup scroll behavior
    $(document).on('scroll', function () {

        if (delayed_table_of_content_scroll_fn == null) {
            delayed_table_of_content_scroll_fn = setTimeout(function () {



                let cur_toc_item_jqe = find_new_cur_toc_item()
                if (cur_toc_item_jqe != null && old_toc_id !== cur_toc_item_jqe.id) {
                    old_toc_id = cur_toc_item_jqe.id;

                    // remove all toc-cur-item
                    $(`.${cur_toc_item_class}`).removeClass(cur_toc_item_class)

                    // add toc-cur-item
                    $(`#toc-body a[href='#${cur_toc_item_jqe.id}']`).addClass(cur_toc_item_class)

                    // update url, add #hash to url
                    history.replaceState(null, null,  '#' + cur_toc_item_jqe.id )

                }



                // clean delay function for trigger again
                delayed_table_of_content_scroll_fn = null;

            }, 200)
        }
    });


}