function actionWork(action, work_id)   {
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