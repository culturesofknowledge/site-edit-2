var delayed_table_of_content_scroll_fn = null;
var TOC_SCROLL_Y_OFFSET = 130;

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
    let toc_items = $('.toc-item:visible, .toc-sub-item:visible');

    $('.toc-host').empty();

    if (toc_items.length === 0) {
        // Publications has no toc items
        return
    }

    let container = $('<div id="toc-div">')
    container.append()

    let title = $('<h3>Table of Contents</h3>')

    let body = $('<div id="toc-body">')
    body.append(title)

    toc_items.each(function (idx, ele) {
        let link_jqe;
        if (ele.classList.contains('toc-sub-item')) {
            link_jqe = $(`<a class="toc-sub-link" href="#${ele.id}">${ele.textContent}</a>`)
        } else {
            link_jqe = $(`<a href="#${ele.id}">${ele.textContent}</a>`)
        }
        body.append(link_jqe)
    });

    container.append(body)

    $('.toc-host').append(container);
}


function find_new_cur_toc_item() {
    // current item is the last heading scrolled past the reading line (just below the fixed header);
    // picking the first heading in the viewport wrongly kept short sections above the target selected
    let reading_line = $(window).scrollTop() + TOC_SCROLL_Y_OFFSET + 10;
    let cur_item = null;
    for (let toc_item_jqe of $('.toc-item:visible, .toc-sub-item:visible')) {
        if ($(toc_item_jqe).offset().top > reading_line) {
            break;
        }
        cur_item = toc_item_jqe;
    }
    if (cur_item == null) {
        // above the first heading, fall back to the first heading in view
        for (let toc_item_jqe of $('.toc-item:visible, .toc-sub-item:visible')) {
            if (isElementInViewpoint(toc_item_jqe)) {
                return toc_item_jqe
            }
        }
    }
    return cur_item;
}

function setup_table_of_content() {
    if (!document.querySelector('.toc-host')) {
        return
    }

    const cur_toc_item_class = 'toc-cur-item';
    let old_toc_id = null;


    // build table of content UI
    build_table_of_content_ui()

    // Restore scroll position after form save instead of using the URL hash
    var savedScrollPos = sessionStorage.getItem('formScrollPosition');
    if (savedScrollPos !== null) {
        sessionStorage.removeItem('formScrollPosition');
        // Clear hash to prevent browser from scrolling to the anchor
        history.replaceState(null, null, window.location.pathname + window.location.search);
        window.scrollTo(0, parseInt(savedScrollPos, 10));
    }

    // Save scroll position and clear hash on form submit
    $('form').on('submit', function () {
        sessionStorage.setItem('formScrollPosition', String(window.scrollY));
        history.replaceState(null, null, window.location.pathname + window.location.search);
    });


    function mark_cur_toc_item(toc_id) {
        if (old_toc_id === toc_id) {
            return
        }
        old_toc_id = toc_id;

        // remove all toc-cur-item
        $(`.${cur_toc_item_class}`).removeClass(cur_toc_item_class)

        // add toc-cur-item
        $(`#toc-body a[href='#${toc_id}']`).addClass(cur_toc_item_class)

        // update url, add #hash to url
        history.replaceState(null, null, '#' + toc_id)
    }

    // while a TOC link click is scrolling, keep the clicked item selected
    // (the target may not reach the top near the end of the page)
    let click_scroll_lock_timer = null;

    function lock_scroll_highlight() {
        clearTimeout(click_scroll_lock_timer);
        click_scroll_lock_timer = setTimeout(function () {
            click_scroll_lock_timer = null;
        }, 300);
    }

    // setup scroll behavior
    $(document).on('scroll', function () {
        if (click_scroll_lock_timer != null) {
            lock_scroll_highlight();  // extend lock until smooth scroll stops
            return
        }

        if (delayed_table_of_content_scroll_fn == null) {
            delayed_table_of_content_scroll_fn = setTimeout(function () {

                // clean delay function for trigger again
                delayed_table_of_content_scroll_fn = null;

                if (click_scroll_lock_timer != null) {
                    return
                }

                let cur_toc_item_jqe = find_new_cur_toc_item()
                if (cur_toc_item_jqe != null) {
                    mark_cur_toc_item(cur_toc_item_jqe.id);
                }

            }, 200)
        }
    });

    // event delegation so click handlers survive TOC rebuilds
    $('.toc-host').on('click', '#toc-body a', function (e) {
        /* scrolling to target element with offset */
        e.preventDefault();

        const element = document.getElementById(e.target.getAttribute('href').substring(1));
        if (element) {
            lock_scroll_highlight();
            mark_cur_toc_item(element.id);
            window.scrollTo({
                top: window.scrollY + element.getBoundingClientRect().top - TOC_SCROLL_Y_OFFSET,
                behavior: 'smooth'
            });
        }
    });


}
