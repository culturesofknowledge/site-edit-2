function cal_max_day_of_month(year_val, month_val) {
    var max_day_of_month = 31;
    switch (month_val) {
        case 9:
        case 4:
        case 6:
        case 11:
            max_day_of_month = 30;
            break;
        case 2:
            max_day_of_month = 28;
            if (year_val % 4 === 0) {
                if (year_val % 100 > 0 || year_val % 400 === 0) {
                    max_day_of_month = 29;
                }
            }
            break;
    }
    return max_day_of_month;
}

function pad_day_month_zero(val) {
    return String(val).padStart(2, '0');
}

function to_date_str(year, month, day) {
    return `${year}-${pad_day_month_zero(month)}-${pad_day_month_zero(day)}`
}

function cal_diff_days_by_calendar_code(calendar_code, year, month, day) {
    var diffdays = 0;
    if (calendar_code == "JM" || calendar_code == "JJ") {
        diffdays = 10;
        if (year > 1700) {
            diffdays = 11;
        } else if (year == 1700 && month > 2) {
            diffdays = 11;
        } else if (year == 1700 && month == 2 && day == 29) {
            diffdays = 11;
        }
    }
    return diffdays;
}

function convert_date_by_calendar_code(calendar_code, year, month, day) {
    let new_year = parseInt(year);
    let new_month = parseInt(month);
    let day_val = parseInt(day);
    let new_day = day_val + cal_diff_days_by_calendar_code(calendar_code, new_year, new_month, day_val);
    let max_day_of_month = cal_max_day_of_month(new_year, new_month);
    if (new_day > max_day_of_month) {
        new_day = new_day - max_day_of_month;
        new_month++;
        if (new_month > 12) {
            new_month = 1;
            new_year++;
            if (new_year > 9999) {
                new_year = 9999;
            }
        }
    }
    return [new_year, new_month, new_day]
}

function AutoCalendar(year_jqe,
                      month_jqe,
                      day_jqe,
                      calendar_jqe,
                      normal_date_jqe,
                      gregorian_jqe,) {

    this.year_jqe = year_jqe;
    this.month_jqe = month_jqe;
    this.day_jqe = day_jqe;
    this.calendar_jqe = calendar_jqe;
    this.normal_date_jqe = normal_date_jqe;
    this.gregorian_jqe = gregorian_jqe;


    this.get_selected_date = function () {
        let year = this.year_jqe.val() || 9999;
        let month = this.month_jqe.val() || 1;
        let day = this.day_jqe.val() || 1;
        return [year, month, day]
    }

    this.get_selected_calendar_code = function () {
        return this.calendar_jqe.parent().find('input:checked').val();
    }


    this.update_original_calendar = function () {
        let [year, month, day] = this.get_selected_date();
        this.normal_date_jqe.val(to_date_str(year, month, day));
    }

    this.update_gregorian_calendar = function () {
        let calendar_code = this.get_selected_calendar_code()
        let [org_year, org_month, org_day] = this.get_selected_date();
        let [new_year, new_month, new_day] = convert_date_by_calendar_code(
            calendar_code, org_year, org_month, org_day,
        );
        this.gregorian_jqe.val(to_date_str(new_year, new_month, new_day));
    }


    this.setup_auto_calendar = function () {
        let self = this
        this.calendar_jqe.on('change', function (e) {
            if (e.target.checked) {
                self.update_gregorian_calendar()
            }
        });

        let update_all_calendar = function (e) {
            self.update_original_calendar()
            self.update_gregorian_calendar()
        }
        this.month_jqe.on('change', update_all_calendar);
        this.day_jqe.on('input', update_all_calendar)
        this.year_jqe.on('input', update_all_calendar)
    }


}

function maintain_is_range(autodate_div_jqe, is_range_jqe) {
    if (is_range_jqe.is(":checked")) {
        autodate_div_jqe.find('.to-div').show();
        autodate_div_jqe.find('.from-label').text('From:')
    } else {
        autodate_div_jqe.find('.to-div').hide();
        autodate_div_jqe.find('.from-label').text('Date:')
    }
}


function setup_autodate_div(autodate_div_selector) {
    let autodate_div_jqe = $(autodate_div_selector);

    // setup is_range
    let is_range_jqe = autodate_div_jqe.find('.is-range-div input');
    is_range_jqe.change(function (e) {
        maintain_is_range(autodate_div_jqe, is_range_jqe);
    });
    maintain_is_range(autodate_div_jqe, is_range_jqe);

    // setup from date
    new AutoCalendar(
        autodate_div_jqe.find('.from-div .ad-year'),
        autodate_div_jqe.find('.from-div .ad-month'),
        autodate_div_jqe.find('.from-div .ad-day'),
        autodate_div_jqe.find('.calendar-div input'),
        autodate_div_jqe.find('.original-calendar-div input'),
        autodate_div_jqe.find('.gregorian-calendar-div input'),
    ).setup_auto_calendar();


    // setup to date
    new AutoCalendar(
        autodate_div_jqe.find('.to-div .ad-year'),
        autodate_div_jqe.find('.to-div .ad-month'),
        autodate_div_jqe.find('.to-div .ad-day'),
        autodate_div_jqe.find('.calendar-div input'),
        autodate_div_jqe.find('.original-calendar-div input'),
        autodate_div_jqe.find('.gregorian-calendar-div input'),
    ).setup_auto_calendar();


}