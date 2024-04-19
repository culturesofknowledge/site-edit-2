from django.utils.safestring import mark_safe

from core.helper.date_serv import decode_calendar
from uploader.models import CofkCollectWork


class DisplayableCollectWork(CofkCollectWork):
    """
    Wrapper for display collect work
    """

    class Meta:
        proxy = True

    @property
    def date_of_work_std(self) -> str | None:
        date_list = []
        if self.date_of_work_std_year:
            date_list.append(str(self.date_of_work_std_year))

        if self.date_of_work_std_month:
            date_list.append(str(self.date_of_work_std_month))

        if self.date_of_work_std_day:
            date_list.append(str(self.date_of_work_std_day))

        return '-'.join(date_list)

    @property
    def date_of_work2_std(self) -> str | None:
        date_list = []
        if self.date_of_work2_std_year:
            date_list.append(str(self.date_of_work2_std_year))

        if self.date_of_work2_std_month:
            date_list.append(str(self.date_of_work2_std_month))

        if self.date_of_work2_std_day:
            date_list.append(str(self.date_of_work2_std_day))

        return '-'.join(date_list)

    @property
    def display_date(self) -> str | None:
        if self.date_of_work_std_is_range == 0:
            return self.date_of_work_std
        elif self.date_of_work_std and self.date_of_work2_std:
            return f'{self.date_of_work_std} to {self.date_of_work2_std}'
        elif self.date_of_work_std:
            return f'{self.date_of_work_std} to ????-??-??'

        return f'????-??-?? To {self.date_of_work2_std}'

    @property
    def display_original_calendar(self) -> str:
        return decode_calendar(self.original_calendar)

    @property
    def display_date_issues(self) -> str | None:
        issues = []

        if self.date_of_work_std_is_range == 1:
            issues.append('estimated or known range')

        if self.date_of_work_inferred == 1:
            issues.append('inferred')

        if self.date_of_work_uncertain == 1:
            issues.append('uncertain')

        if self.date_of_work_approx == 1:
            issues.append('approximate')

        if issues:
            return 'Issues with date of work: ' + ', '.join(issues)

    @property
    def display_origin_issues(self) -> str | None:
        issues = []

        if self.origin_inferred == 1:
            issues.append('inferred')

        if self.origin_uncertain == 1:
            issues.append('uncertain')

        if issues:
            return 'Issues with origin: ' + ', '.join(issues)

    @property
    def display_destination_issues(self) -> str | None:
        issues = []

        if self.destination_inferred == 1:
            issues.append('inferred')

        if self.destination_uncertain == 1:
            issues.append('uncertain')

        if issues:
            return 'Issues with destination: ' + ', '.join(issues)

    @property
    def display_authors_issues(self) -> str | None:
        issues = []

        if self.authors_inferred == 1:
            issues.append('inferred')

        if self.authors_uncertain == 1:
            issues.append('uncertain')

        if issues:
            return 'Issues with author/s: ' + ', '.join(issues)

    @property
    def display_addressees_issues(self) -> str | None:
        issues = []

        if self.addressees_inferred == 1:
            issues.append('inferred')

        if self.addressees_uncertain == 1:
            issues.append('uncertain')

        if issues:
            return 'Issues with addressee/s: ' + ', '.join(issues)

    @property
    def display_mentioned_issues(self) -> str | None:
        issues = []

        if self.mentioned_inferred == 1:
            issues.append('inferred')

        if self.mentioned_uncertain == 1:
            issues.append('uncertain')

        if issues:
            return 'Issues with mentioned person/people: ' + ', '.join(issues)

    @property
    def display_issues(self) -> str | None:
        display_list = [self.display_date_issues, self.display_origin_issues, self.display_destination_issues,
                        self.display_authors_issues, self.display_addressees_issues, self.display_mentioned_issues]

        return mark_safe('<br/><br/>'.join(filter(None, display_list)))
