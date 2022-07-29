const location_ele_id_list = [
    'id_element_1_eg_room', 'id_element_2_eg_building',
    'id_element_3_eg_parish', 'id_element_4_eg_city', 'id_element_5_eg_county',
    'id_element_6_eg_country', 'id_element_7_eg_empire',
];

function setup_location_form_listener() {
    location_ele_id_list
        .map((i) => document.getElementById(i))
        .forEach((e) => {
            e.addEventListener('input', () => {
                set_location_name();

            });
        });
}

function set_location_name() {
    const full_loc_name = location_ele_id_list
        .map((i) => document.getElementById(i))
        .map((e) => e.value)
        .filter((v) => v)
        .join(', ');

    document.getElementById('id_location_name')
        .setAttribute('value', full_loc_name);
}