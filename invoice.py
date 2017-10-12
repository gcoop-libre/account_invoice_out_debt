# This file is part of the account_invoice_out_debt module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from trytond.model import Workflow, ModelView
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.modules.account_invoice.invoice import _ZERO

logger = logging.getLogger(__name__)

__all__ = ['Invoice']


class Invoice:
    __name__ = 'account.invoice'
    __metaclass__ = PoolMeta

    @classmethod
    def get_amount_to_pay(cls, invoices, name):
        pool = Pool()
        Currency = pool.get('currency.currency')
        Date = pool.get('ir.date')

        today = Date.today()
        res = dict((x.id, _ZERO) for x in invoices)
        for invoice in invoices:
            if invoice.state in ['draft', 'cancel', 'paid']:
                continue
            amount = _ZERO
            amount_currency = _ZERO
            for line in invoice.lines_to_pay:
                if line.reconciliation:
                    continue
                if (name == 'amount_to_pay_today'
                        and line.maturity_date > today):
                    continue
                if (line.second_currency
                        and line.second_currency == invoice.currency):
                    amount_currency += line.amount_second_currency
                else:
                    amount += line.debit - line.credit
            for line in invoice.payment_lines:
                if line.reconciliation:
                    continue
                if (line.second_currency
                        and line.second_currency == invoice.currency):
                    amount_currency += line.amount_second_currency
                else:
                    amount += line.debit - line.credit
            if amount != _ZERO:
                with Transaction().set_context(date=invoice.currency_date):
                    amount_currency += Currency.compute(
                        invoice.company.currency, amount, invoice.currency)
            if invoice.type == 'in':
                amount_currency *= -1
            res[invoice.id] = amount_currency
        return res

    @classmethod
    @ModelView.button
    @Workflow.transition('validated')
    def validate_invoice(cls, invoices):
        super(Invoice, cls).validate_invoice(invoices)
        pool = Pool()
        Move = pool.get('account.move')
        Date = pool.get('ir.date')

        invoices_out = cls.browse([i for i in invoices if i.type == 'out'])
        moves = []
        for invoice in invoices_out:
            invoice.invoice_date = invoice.invoice_date or Date.today()
            move = invoice.get_move()
            if move != invoice.move:
                invoice.move = move
                moves.append(move)
        if moves:
            Move.save(moves)
        cls.save(invoices_out)
