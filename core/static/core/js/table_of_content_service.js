var delayed_table_of_content_scroll_fn = null;

function isElementInViewpoint(ele) {
    let ele_jqe = $(ele);
    var elementTop = ele_jqe.offset().top;
    var elementBottom = elementTop + ele_jqe.outerHeight();

    let window_jqe = $(window)
    var viewportTop = window_jqe.scrollTop();
    var viewportBottom = viewportTop + window_jqe.height();
    viewportBottom = viewportBottom - 100;  // avoid select toc if too bottom

    return elementBottom > viewportTop && elementTop < viewportBottom;
}


function build_table_of_content_ui() {
    let container = $('<div id="toc-div">')
    container.append()


    let title = $('<h3>Table of Contents</h3>')

    let body = $('<div id="toc-body">')
    body.append(title)

    $('.toc-item, .toc-sub-item').each(function (idx, ele) {
        let link_jqe;
        if (ele.classList.contains('toc-sub-item')) {
            link_jqe = $(`<li><a href="#${ele.id}">${ele.textContent}</a></li>`)
        } else {
            link_jqe = $(`<a href="#${ele.id}">${ele.textContent}</a>`)
        }
        body.append(link_jqe)
    });

    container.append(body)

    $('.toc-host').append(container);
}


function find_new_cur_toc_item() {
    for (let toc_item_jqe of $('.toc-item, .toc-sub-item')) {
        if (isElementInViewpoint(toc_item_jqe)) {
            return toc_item_jqe
        }
    }
    return null;
}

function setup_table_of_content() {
    if (!document.querySelector('.toc-host')) {
        return
    }

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
                    history.replaceState(null, null, '#' + cur_toc_item_jqe.id)

                }


                // clean delay function for trigger again
                delayed_table_of_content_scroll_fn = null;

            }, 200)
        }
    });


}