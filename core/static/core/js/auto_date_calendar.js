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

function pad_year_zero(val) {
    return String(val).padStart(4, '0');
}

function pad_day_month_zero(val) {
    return String(val).padStart(2, '0');
}

function to_date_str(year, month, day) {
    return `${pad_year_zero(year)}-${pad_day_month_zero(month)}-${pad_day_month_zero(day)}`
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
                      gregorian_jqe,
                      manual_checkbox_jqe) {

    this.year_jqe = year_jqe;
    this.month_jqe = month_jqe;
    this.day_jqe = day_jqe;
    this.calendar_jqe = calendar_jqe;
    this.normal_date_jqe = normal_date_jqe;
    this.gregorian_jqe = gregorian_jqe;
    this.manual_checkbox_jqe = manual_checkbox_jqe;

    this.is_manual = function() {
        return this.manual_checkbox_jqe && this.manual_checkbox_jqe.is(':checked');
    }


    this.get_selected_date = function () {
        let year = this.year_jqe.val() || 9999;
        let month = this.month_jqe.val() || 12;
        let day = this.day_jqe.val() || cal_max_day_of_month(parseInt(year), parseInt(month));
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
            if (self.is_manual()) return;
            self.update_original_calendar()
            self.update_gregorian_calendar()
        }
        this.month_jqe.on('change', update_all_calendar);
        this.day_jqe.on('input', update_all_calendar)
        this.year_jqe.on('input', update_all_calendar)

        if (this.manual_checkbox_jqe) {
            let update_readonly = function() {
                let is_manual = self.is_manual();
                self.normal_date_jqe.prop('readonly', !is_manual);
                self.gregorian_jqe.prop('readonly', !is_manual);
                if (!is_manual) {
                    update_all_calendar();
                }
            }
            this.manual_checkbox_jqe.on('change', update_readonly);
            update_readonly();
        }
    }


}

function maintain_is_range(autodate_div_jqe, is_range_jqe) {
    let to_div_jqe = autodate_div_jqe.find('.to-div');
    if (is_range_jqe.is(":checked")) {
        to_div_jqe.show();
        to_div_jqe.find('input, select').prop('disabled', false);
        autodate_div_jqe.find('.from-label').text('From:')
    } else {
        to_div_jqe.hide();
        to_div_jqe.find('input, select').prop('disabled', true);
        autodate_div_jqe.find('.from-label').text('Date:')
    }
}

function setup_is_range(date_div_jqe) {
    let is_range_jqe = date_div_jqe.find('.is-range-div input');
    is_range_jqe.change(function (e) {
        maintain_is_range(date_div_jqe, is_range_jqe);
    });
    maintain_is_range(date_div_jqe, is_range_jqe);
}


function setup_autodate_div(autodate_div_selector) {
    let autodate_div_jqe = $(autodate_div_selector);

    // setup is_range
    setup_is_range(autodate_div_jqe);

    let from_year_jqe = autodate_div_jqe.find('.from-div .ad-year');
    let from_month_jqe = autodate_div_jqe.find('.from-div .ad-month');
    let from_day_jqe = autodate_div_jqe.find('.from-div .ad-day');
    let to_year_jqe = autodate_div_jqe.find('.to-div .ad-year');
    let to_month_jqe = autodate_div_jqe.find('.to-div .ad-month');
    let to_day_jqe = autodate_div_jqe.find('.to-div .ad-day');
    let calendar_jqe = autodate_div_jqe.find('.calendar-div input');
    let normal_date_jqe = autodate_div_jqe.find('.original-calendar-div input');
    let gregorian_jqe = autodate_div_jqe.find('.gregorian-calendar-div input');
    let manual_checkbox_jqe = autodate_div_jqe.find('.manual-date-checkbox');
    let is_range_jqe = autodate_div_jqe.find('.is-range-div input');
    let refresh_btn_jqe = autodate_div_jqe.find('.refresh-date-btn');

    // Create AutoCalendar for "from" date fields (used for from-date computation)
    let from_auto_cal = new AutoCalendar(
        from_year_jqe, from_month_jqe, from_day_jqe,
        calendar_jqe, normal_date_jqe, gregorian_jqe,
        manual_checkbox_jqe,
    );

    // Function to update ordering date based on range state
    function update_ordering_date() {
        if (manual_checkbox_jqe.length && manual_checkbox_jqe.is(':checked')) return;

        if (is_range_jqe.is(':checked') && to_year_jqe.val()) {
            // Use "to" date for ordering, default blank month to 12, day to last day of month
            let year = to_year_jqe.val() || 9999;
            let month = to_month_jqe.val() || 12;
            let day = to_day_jqe.val() || cal_max_day_of_month(parseInt(year), parseInt(month));
            normal_date_jqe.val(to_date_str(year, month, day));

            let calendar_code = calendar_jqe.parent().find('input:checked').val();
            let [new_year, new_month, new_day] = convert_date_by_calendar_code(
                calendar_code, year, month, day
            );
            gregorian_jqe.val(to_date_str(new_year, new_month, new_day));
        } else {
            // Use "from" date (default behavior)
            from_auto_cal.update_original_calendar();
            from_auto_cal.update_gregorian_calendar();
        }
    }

    // Listen to "to" date field changes to update ordering date
    to_year_jqe.on('input', update_ordering_date);
    to_month_jqe.on('change', update_ordering_date);
    to_day_jqe.on('input', update_ordering_date);
    is_range_jqe.on('change', update_ordering_date);

    // Listen to "from" date field changes
    from_year_jqe.on('input', update_ordering_date);
    from_month_jqe.on('change', update_ordering_date);
    from_day_jqe.on('input', update_ordering_date);

    // Listen to calendar type changes
    calendar_jqe.on('change', function (e) {
        if (e.target.checked) {
            update_ordering_date();
        }
    });

    // Setup manual checkbox behavior
    if (manual_checkbox_jqe.length) {
        let update_readonly = function(trigger_update) {
            let is_manual = manual_checkbox_jqe.is(':checked');
            normal_date_jqe.prop('readonly', !is_manual);
            gregorian_jqe.prop('readonly', !is_manual);
            if (!is_manual && trigger_update) {
                update_ordering_date();
            }
        }
        manual_checkbox_jqe.on('change', function() { update_readonly(true); });
        // On initial page load, only set readonly state without overwriting
        // server-rendered values (which may have been manually entered).
        update_readonly(false);
    }

    // Refresh button: force-recompute ordering dates from date range fields,
    // overwriting any manually entered values.
    refresh_btn_jqe.on('click', function() {
        // Temporarily treat as non-manual to allow update
        let was_manual = manual_checkbox_jqe.is(':checked');
        if (was_manual) {
            manual_checkbox_jqe.prop('checked', false);
        }
        update_ordering_date();
        if (was_manual) {
            manual_checkbox_jqe.prop('checked', true);
        }
    });
}