# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import json
import re
from werkzeug.exceptions import Forbidden
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape

# Amanus security hardening (DEC-VAL-044 / RG-SEC-004):
# Strict allowlist of accounting models authorized to export XLSX via /xlsx_report.
ALLOWED_XLSX_MODELS = frozenset({
    'res.partner',
    'account.common.report',
    'account.common.account.report',
    'account.common.partner.report',
    'account.common.journal.report',
    'account.aged.trial.balance',
    'account.balance.report',
    'account.bank.book.report',
    'account.cash.book.report',
    'account.day.book.report',
    'account.print.journal',
    'account.report.general.ledger',
    'account.report.partner.ledger',
    'cash.flow.report',
    'financial.report',
    'kit.account.tax.report',
})


class XLSXReportController(http.Controller):
    """ Controller for xlsx report (hardened by Amanus). """
    @http.route('/xlsx_report', type='http', auth='user', methods=['POST'],
                csrf=True)
    def get_report_xlsx(self, model, options, output_format, report_name,
                        report_action=None, **kwargs):
        """ Get xlsx report data with strict accounting RBAC and model allowlist. """
        if not request.env.user.has_group('account.group_account_user'):
            raise Forbidden("Accounting privileges are required to export financial XLSX reports.")
        if model not in ALLOWED_XLSX_MODELS or model not in request.env:
            raise Forbidden("Model not authorized for XLSX financial export.")

        report_obj = request.env[model]
        report_obj.check_access('read')
        if not hasattr(report_obj, 'get_xlsx_report'):
            raise Forbidden("Selected model does not support XLSX financial export.")

        safe_name = re.sub(r'[\r\n\\/:*?"<>|]+', '_', str(report_name or 'report')).strip() or 'report'
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None, headers=[
                        ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                        ('Content-Disposition', content_disposition(
                            safe_name + '.xlsx'))])
                report_obj.get_xlsx_report(json.loads(options), response)
                response.set_cookie('fileToken', 'dummy token')
                return response
        except Exception as event:
            serialize = http.serialize_exception(event)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': serialize
            }
            return request.make_response(html_escape(json.dumps(error)))
