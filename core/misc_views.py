from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect

from core import constant
from core.helper import exporter_serv


@permission_required(constant.PM_TRIGGER_EXPORTER, raise_exception=True)
def trigger_export(request):
    exporter_serv.trigger_export_tonight()
    return redirect('login:dashboard')
