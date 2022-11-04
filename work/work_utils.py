from work.models import CofkUnionWork
import datetime
from datetime import date


def get_recref_display_name(work: CofkUnionWork):
    if not work:
        return ''
    work.date_of_work_std_day
    work.date_of_work_std_month

    work_date = date(year=work.date_of_work_std_year,
                     month=work.date_of_work_std_month,
                     day=work.date_of_work_std_day)
    work_date_str = work_date.strftime('%-d %b %Y')
    display_name = ', '.join([
        work_date_str,

    ])

    return work and work.work_id  # KTODO


def get_recref_target_id(work: CofkUnionWork):
    return work and work.work_id
