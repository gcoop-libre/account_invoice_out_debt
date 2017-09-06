# -*- coding: utf-8 -*-
# This file is part of the account_invoice_out_debt module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from trytond.model import ModelSQL, Workflow, fields, ModelView
from trytond.pool import Pool, PoolMeta

logger = logging.getLogger(__name__)

__all__ = ['Invoice']


class Invoice:
    __name__ = 'account.invoice'
    __metaclass__ = PoolMeta

    @classmethod
    @ModelView.button
    @Workflow.transition('validated')
    def validate_invoice(cls, invoices):
        super(Invoice, cls).validate_invoice(invoices)

    def _get_move_line(self, date, amount):
        line = super(Invoice, self)._get_move_line(date, amount)
        return line

    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, invoices):
        super(Invoice, cls).post(invoices)
