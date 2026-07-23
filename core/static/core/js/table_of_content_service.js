var delayed_table_of_content_scroll_fn = null;

// must match the y_offset used when scrolling to a clicked toc link, so the
// "current" section lines up with whatever the click handler last scrolled to
const toc_y_offset = 130;

// short sections stacked near the bottom of the page (e.g. Earlier/Later/
// Matching letter) can all share the same clamped scroll position once
// there's no more room to scroll, so geometry alone can't tell them apart
// after a click. Lock the highlight to whatever was clicked for a bit and
// ignore scroll-driven recalculation until the click's smooth-scroll settles
const toc_click_lock_ms = 1000;
var toc_click_lock_until = 0;


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
    let toc_items = $('.toc-item:visible, .toc-sub-item:visible').toArray();
    if (toc_items.length === 0) {
        return null;
    }

    let window_jqe = $(window);

    // for organic (non-click) scrolling all the way to the end of the page,
    // the last section can't always be scrolled up to the offset line
    // (there's not enough page left below it), so treat the last toc item as
    // current instead of relying on offset math the clamped scroll position
    // can never satisfy. Clicks bypass this entirely via toc_click_lock_until,
    // since this check alone can't tell apart short sections stacked near the
    // bottom (they can all read as "at the bottom" at once)
    let scrolled_to_bottom = window_jqe.scrollTop() + window_jqe.height() >= $(document).height() - 2;
    if (scrolled_to_bottom) {
        return toc_items[toc_items.length - 1];
    }

    // pick the last section whose heading has scrolled past the offset line,
    // i.e. the section actually sitting at the top of the viewport, rather
    // than the first section that merely overlaps the viewport at all
    // (adjacent short sections can both overlap, picking the wrong one)
    let reference_line = window_jqe.scrollTop() + toc_y_offset;

    let cur_toc_item_jqe = toc_items[0];
    for (let toc_item_jqe of toc_items) {
        if ($(toc_item_jqe).offset().top <= reference_line) {
            cur_toc_item_jqe = toc_item_jqe;
        } else {
            break;
        }
    }
    return cur_toc_item_jqe;
}

function setup_table_of_content() {
    if (!document.querySelector('.toc-host')) {
        return
    }

    const cur_toc_item_class = 'toc-cur-item';
    let old_toc_id = null;

    function highlight_toc_item(toc_item_id) {
        old_toc_id = toc_item_id;

        // remove all toc-cur-item
        $(`.${cur_toc_item_class}`).removeClass(cur_toc_item_class)

        // add toc-cur-item
        $(`#toc-body a[href='#${toc_item_id}']`).addClass(cur_toc_item_class)

        // update url, add #hash to url
        history.replaceState(null, null, '#' + toc_item_id)
    }


    // build table of content UI
    build_table_of_content_ui()


    // setup scroll behavior
    $(document).on('scroll', function () {

        if (delayed_table_of_content_scroll_fn == null) {
            delayed_table_of_content_scroll_fn = setTimeout(function () {

                // a toc link was just clicked - trust that highlight rather
                // than recomputing from (possibly still-animating) scroll position
                if (Date.now() < toc_click_lock_until) {
                    delayed_table_of_content_scroll_fn = null;
                    return;
                }

                let cur_toc_item_jqe = find_new_cur_toc_item()
                if (cur_toc_item_jqe != null && old_toc_id !== cur_toc_item_jqe.id) {
                    highlight_toc_item(cur_toc_item_jqe.id)
                }


                // clean delay function for trigger again
                delayed_table_of_content_scroll_fn = null;

            }, 200)
        }
    });

    // event delegation so click handlers survive TOC rebuilds
    $('.toc-host').on('click', '#toc-body a', function (e) {
        /* scrolling to target element with offset */
        e.preventDefault();

        const target_id = e.target.getAttribute('href').substring(1);
        const element = document.getElementById(target_id);
        if (element) {
            toc_click_lock_until = Date.now() + toc_click_lock_ms;
            highlight_toc_item(target_id)

            window.scrollTo({
                top: window.scrollY + element.getBoundingClientRect().top - toc_y_offset,
                behavior: 'smooth'
            });
        }
    });


}
