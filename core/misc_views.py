from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect

from core import constant
from core.helper import exporter_serv


@permission_required(constant.PM_TRIGGER_EXPORTER)
def trigger_export(request):
    exporter_serv.mark_exporter_pending()
    return redirect('login:dashboard')
