from django.template.loader import render_to_string


def record_tracker_label_fn_factory(subject='Entry'):
    def _fn(_self):
        context = {k: _self[k].value() for k in
                   ['creation_timestamp', 'creation_user', 'change_timestamp', 'change_user', ]}

        context = context | {'subject': subject}
        return render_to_string('core/component/record_tracker_label.html', context)

    return _fn
