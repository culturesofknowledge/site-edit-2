var emlojs = emlojs || {};
emlojs.leave_warning = {
    is_submit: false,
    setup_leave_warning: function () {
        function load_input_map() {
            let input_map = new Map();
            for (let ele of document.querySelectorAll('input[name],textarea[name],select[name]')) {
                if (['checkbox', 'radio'].includes(ele.type)) {
                    input_map.set(ele.name, ele.checked);
                } else {
                    input_map.set(ele.name, ele.value);
                }
            }
            return input_map
        }

        function compare_map(map_old, map_new) {
            let diff_map = new Map();
            for (let [key, new_val] of map_new) {
                let old_val = map_old.get(key);
                if (old_val !== new_val) {
                    diff_map.set(key, [old_val, new_val])
                }
            }
            return diff_map
        }

        // event beforeunload
        const org_input_map = load_input_map()
        window.addEventListener('beforeunload', function (e) {
            if (emlojs.leave_warning.is_submit) {
                return
            }
            const new_input_map = load_input_map();
            const diff_map = compare_map(org_input_map, new_input_map);
            if (diff_map.size) {
                console.log('diff_map changed:')
                console.log(diff_map)
                e.preventDefault()
                e.returnValue = 'Changes that you made may not be saved.'
            }
        });

        // event submit
        $('form').on('submit', function (event) {
            emlojs.leave_warning.is_submit = true;
        });
    },
}
