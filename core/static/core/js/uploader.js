function actionWork(btn)   {
    $('#accept_all').prop('disabled', true);
    $('#accept_all').addClass('btn-disabled');
    $('#reject_all').prop('disabled', true);
    $('#reject_all').addClass('btn-disabled');

    let action = btn.name.split('_')[0];
    let work_id = btn.name.split('_')[1];

    $('#review').hide(400);
    $('#confirm').show(400);
    $('#action').val(action);
    $('#work_id').val(work_id);

    action = action.charAt(0).toUpperCase() + action.slice(1);

    if(parseInt(work_id)) {
        $('#confirm_title').text(action + ' the following work (Collect ID: ' + work_id + ')?');
        location.href = '#confirm';
    }
    else {
        $('#confirm_title').text(action + ' the following ' + work_count + ' works?');
    }
}

function cancelActionWork() {
    $('#confirm').hide(400);
    $('#review').show(400);
    $('#accept_all').prop('disabled', false);
    $('#accept_all').removeClass('btn-disabled');
    $('#reject_all').prop('disabled', false);
    $('#reject_all').removeClass('btn-disabled');
}