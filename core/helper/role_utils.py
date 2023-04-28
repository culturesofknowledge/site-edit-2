import dataclasses


@dataclasses.dataclass
class PermissionData:
    app_label: str
    codename: str

    @property
    def full_name(self):
        return f'{self.app_label}.{self.codename}'

    @classmethod
    def from_full_name(cls, full_name):
        app_name, code_name = full_name.split('.')
        return cls(app_name, code_name)
