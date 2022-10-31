// KTODO extract following javascript to js file and emlojs object
// otherwise, it will duplicate following javascript when include by django

var emlojs = emlojs || {};
emlojs.recref_service = {
    /* function for  recref_main and clean,
     * select, creat function for recref
     */
    self: this,
    fill_recref_data: function (main_ele, data) {
        main_ele = $(main_ele)
        main_ele.find('.recref_text').val(data.item_name)
        main_ele.find('.recref_id').val(data.item_id)
    },

    create_fn_fill_recref_data: function (main_ele) {
        return function (data) {
            return emlojs.recref_service.fill_recref_data(main_ele, data)
        };
    },

    find_main_ele: function (child_ele) {
        return $(child_ele).closest('.recref_main')
    },

    create_fn_open_recref: function (url) {
        return function (e) {
            e.preventDefault();
            window.open(url);
            window.on_quick_init_completed = emlojs.recref_service.create_fn_fill_recref_data(
                emlojs.recref_service.find_main_ele(e.target)
            );
        }
    },

    setup_elements: function (main_ele, urls) {
        main_ele = $(main_ele)
        main_ele.find('.recref_clean').on('click', function (e) {
            e.preventDefault();
            emlojs.recref_service.fill_recref_data(emlojs.recref_service.find_main_ele(e.target), {
                item_name: '',
                item_id: '',
            })
        });

        main_ele.find('.recref_select').on(
            'click',
            emlojs.recref_service.create_fn_open_recref(urls.select_url));


        main_ele.find('.recref_create').on(
            'click',
            emlojs.recref_service.create_fn_open_recref( urls.create_url));

    },

    setup_all: function () {
        $('.recref_main').each((i, e) => {
            let main_ele = $(e)
            let urls = {};
            const recref_type = main_ele.attr('recref_type')
            if (recref_type === 'location') {
                urls = {
                    select_url: '/location/search?recref_mode=1',
                    create_url: '/location/quick_init',
                }
            } else if(recref_type === 'person') {
                urls = {
                    select_url: '/person/search?recref_mode=1',
                    create_url: '/person/quick_init',
                }
            } else if(recref_type === 'work') {
                urls = {
                    select_url: '/work/search?recref_mode=1',
                    create_url: '/work/quick_init',
                }
            } else if(recref_type === 'manif') {
                urls = {
                    select_url: '/manif/search?recref_mode=1',
                    create_url: '/',  // manif have no create url
                }
            } else if(recref_type === 'inst') {
                urls = {
                    select_url: '/repositories/search?recref_mode=1',
                    create_url: '/repositories/quick_init',
                }
            }
            else{
                console.log(`unknown recref_type [${recref_type}]`)

            }
            emlojs.recref_service.setup_elements(main_ele, urls)
        })

    },

}

$(() => {
    emlojs.recref_service.setup_all()
})
