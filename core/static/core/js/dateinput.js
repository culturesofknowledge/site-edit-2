

function onlySearchKeys(e){
      return e.metaKey || // cmd/ctrl
        e.which <= 0 || // arrow keys
        e.which == 8 || e.which == 46 || // delete key
        e.which == 32 || // Space
        e.which == 47 || // / key
        e.which == 58 || // : key
        /[0-9]/.test(String.fromCharCode(e.which)); // numbers
}

$('.dateinput').each(function(i, e)   {
        $(e).on('keypress', onlySearchKeys)

    }
);