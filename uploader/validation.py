import datetime
import pandas


# TODO, Establish what columns are mandatory and check for them

class CofkValueException(Exception):
    def __init__(self, msg, col):
        self.col = col
        self.msg = msg
        super().__init__(self.msg)


class CofkExcelFileError(Exception):
    def __init__(self, msg):
        self.msg = msg


class CofkValue:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.key + ": " + str(self.value)


class CofkValidateWork:

    def __init__(self, work):
        self.work = work
        self.errors = []

        self.validate_dates()

    def get_value(self, key) -> CofkValue:
        value = {'key': key, 'value': None}
        if key in self.work:
            value['value'] = self.work[key]

        return CofkValue(**value)

    def add_error(self, msg, col=None):
        self.errors.append(CofkValueException(msg, col))

    def validate_date(self, y, m, d):
        # Make sure year is early modern inclusive.
        if y.value is not None and not 1900 >= y.value >= 1500:
            self.add_error('{} is {} but must be between {} and {}'.format(y.key, y.value, 1500, 1900), y.key)

        # Make sure month is between 1-12
        if m.value is not None and not 0 < m.value < 13:
            self.add_error('{} is {} but must be between 1 and 12'.format(m.key, m.value), y.key)

        # Check day of month
        if d.value is not None:
            # If month is April, June, September or November then day must be not more than 30
            if m.value in [4, 6, 9, 11] and d.value > 30:
                self.add_error('{} is {} but must be between 1 and 30 for April, June, September or November'
                               .format(d.key, d.value), d.key)

            # For February not more than 29
            elif m.value == 2 and d.value > 29:
                self.add_error('{} is {} but must be between 1 and 29 for February'.format(d.key, d.value), d.key)

            # Otherwise
            elif d.value > 31:
                self.add_error('{} is {} but must be between 1 and 31'.format(d.key, d.value), d.key)

    def validate_dates(self):
        """
        Validating using manual string comparison because it is unclear at this time how
        use of different calendars (Gregorian, Julian, other or unknown) will affect date
        validation.
        :return:
        """
        date_of_work_std_year = self.get_value('date_of_work_std_year')
        date_of_work_std_month = self.get_value('date_of_work_std_month')
        date_of_work_std_day = self.get_value('date_of_work_std_day')
        date_of_work_std_is_range = self.get_value('date_of_work_std_is_range')

        self.validate_date(date_of_work_std_year, date_of_work_std_month, date_of_work_std_day)

        # Date is a range, switch between Julian to Gregorian calendar was around October 1582.
        # This could get sticky.
        if date_of_work_std_is_range == 1:
            date_of_work2_std_year = self.get_value('date_of_work2_std_year')
            date_of_work2_std_month = self.get_value('date_of_work2_std_month')
            date_of_work2_std_day = self.get_value('date_of_work2_std_day')

            self.validate_date(date_of_work2_std_year, date_of_work2_std_month, date_of_work2_std_day)

            first_date = datetime.datetime(date_of_work_std_year.value,
                                           date_of_work_std_month.value, date_of_work_std_day.value)
            second_date = datetime.datetime(date_of_work2_std_year.value,
                                            date_of_work2_std_month.value, date_of_work2_std_day.value)

            if first_date >= second_date:
                cols = [date_of_work_std_year.key, date_of_work_std_month.key, date_of_work_std_day.key,
                        date_of_work2_std_year.key, date_of_work2_std_month.key, date_of_work2_std_day.key]
                self.add_error("The start date in a date range can not be after the end date.", ', '.join(cols))

        notes_on_date_of_work = self.get_value('notes_on_date_of_work')

        if notes_on_date_of_work.value is not None and notes_on_date_of_work.value[0].islower():
            self.add_error("Notes with dates have to start with an upper case letter.", notes_on_date_of_work.key)

        if notes_on_date_of_work.value is not None and notes_on_date_of_work.value[-1] != '.':
            self.add_error("Notes with dates have to end with a full stop.", notes_on_date_of_work.key)

    def validate_places(self):
        destination_name = self.get_value('destination_name')
        destination_id = self.get_value('destination_id')
        origin_name = self.get_value('origin_name')
        origin_id = self.get_value('origin_id')

        if not (destination_id.value or destination_name.value):
            self.add_error("There is neither a destination_id nor a destination_name.",
                           ', '.join([destination_id.key, destination_name.key]))

        if not (origin_id or origin_name):
            self.add_error("There is neither a origin_id nor a origin_name.",
                           ', '.join([origin_id.key, origin_name.key]))

        # If place id is provided it overrides the name provided regardless if it's
        # unknown or something else.

        if destination_name.value and not destination_id.value and "unknown" == destination_name.value.strip().lower():
            self.add_error("Destination name must not be \"unknown\".", destination_name.key)

        if origin_name.value and not origin_id.value and "unknown" == origin_name.value.strip().lower():
            self.add_error("Origin name must not be \"unknown\".", origin_name.key)

    def validate_languages(self):
        lang = self.get_value('language_id')

        codes = pandas.read_csv('languages.csv').language_code.to_list()

        if not all(l in codes for l in lang.value.split(';')):
            self.add_error("Not all values in language_id are valid 3-digit ISO language codes.", lang.key)

        # Explicitly deleting language codes as it is a list of 8224 3 digit codes
        del codes

    def validate_keywords(self):
        keywords = self.get_value('keywords')

        if len(keywords.value.split('; ')) - 1 != keywords.value.count(';'):
            self.add_error("Not all keywords are properly separated with a space after the separator, ;.", keywords.key)


def validate_work(df):
    errors = []
    for i in range(1, len(df.index)):
        work_row = {k: v for k, v in df.iloc[i].to_dict().items() if v is not None}

        work = CofkValidateWork(work_row)

        if len(work.errors) > 0:
            errors.append({'sheet': 'Work', 'row': i, 'errors': work.errors})

    return errors


def validate_manifestation(df):
    errors = []
    for i in range(1, len(df.index)):
        m_errors = []
        manifestation = {k: v for k, v in df.iloc[i].to_dict().items() if v is not None}

        if 'manifestation_type' not in manifestation:
            m_errors.append(CofkValueException('manifestation_type missing from manifestation.', 'manifestation_type'))

        if 'repository_id' not in manifestation:
            m_errors.append(CofkValueException('repository_id missing from manifestation.', 'repository_id'))

        if 'id_number_or_shelfmark' not in manifestation:
            m_errors.append(CofkValueException('id_number_or_shelfmark missing from manifestation.',
                                               'id_number_or_shelfmark'))

        else:
            if manifestation['id_number_or_shelfmark'].find('-') > -1:
                m_errors.append(CofkValueException('There should be an en dash used between folio numbers,'
                                                               ' not a hyphen.', 'id_number_or_shelfmark'))

            if manifestation['id_number_or_shelfmark'][-1] != '.':
                m_errors.append(CofkValueException('There should not be a full stop at the end of'
                                                               ' a shelfmark.', 'id_number_or_shelfmark'))

        if 'printed_edition_details' in manifestation:
            if manifestation['printed_edition_details'][-1] == '.':
                m_errors.append(CofkValueException('There should not be a full stop at the end of bibliographic'
                                                   ' details of a manifestation.', 'printed_edition_details'))

            if manifestation['printed_edition_details'].find('-') > -1 and \
                    manifestation['printed_edition_details'].find('–') == -1:
                m_errors.append(CofkValueException('It seems you are using hyphens to indicate a page range when you'
                                                 ' should be using en dashes.', 'printed_edition_details'))

        if len(m_errors) > 0:
            errors.append({'sheet': 'Manifestation', 'row': i, 'errors': m_errors})

    return errors
