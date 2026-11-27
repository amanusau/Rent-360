# -*- coding: utf-8 -*-
from . import test_asset
# Amanus hardening (DEC-VAL-044): test_credit_limit disabled (depends on sale.order)
from . import test_recurring
from . import test_recurring_invoice
from . import test_followup
from . import test_payment_pdc
from . import test_bank_reconcile
from . import test_bulk_payment
from . import test_fx_revaluation
from . import test_reports
from . import test_report_xlsx
from . import test_partner_statement
from . import test_misc
