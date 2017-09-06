# -*- coding: utf-8 -*-
# This file is part of the account_invoice_out_debt module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from trytond.model import Workflow, ModelView
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
        pool = Pool()
        Move = pool.get('account.move')

        invoices_out = cls.browse([i for i in invoices if i.type == 'out'])
        moves = []
        for invoice in invoices_out:
            move = invoice.get_move()
            if move != invoice.move:
                invoice.move = move
                moves.append(move)
        if moves:
            Move.save(moves)
        cls.save(invoices_out)
