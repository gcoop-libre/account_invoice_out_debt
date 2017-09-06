try:
    from trytond.modules.account_invoice_out_debt.tests.tests import suite
except ImportError:
    from .tests import suite

__all__ = ['suite']
