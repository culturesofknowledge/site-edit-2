import datetime


class RecordTracker:

    def update_current_user_timestamp(self, user):
        now = datetime.datetime.now()
        if hasattr(self, 'creation_timestamp') and not self.creation_timestamp:
            self.creation_timestamp = now

        if hasattr(self, 'change_timestamp'):
            self.change_timestamp = now

        if hasattr(self, 'creation_user') and not self.creation_user:
            self.creation_user = user

        if hasattr(self, 'change_user'):
            self.change_user = user
