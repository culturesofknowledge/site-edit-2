function actionWork(btn)   {
    const allButtons = $('#accept_all, #reject_all');
    allButtons.prop('disabled', true);
    allButtons.not(btn).addClass('btn-disabled');
    allButtons.filter(btn).addClass('btn--primary');

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
    $('#accept_all, #reject_all').prop('disabled', false).removeClass('btn-disabled btn--primary');
}