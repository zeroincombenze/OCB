# -*- coding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

import datetime
import dateutil
import time
import logging
import netsvc
import base64
import sys
import pdb
from StringIO import StringIO

from urllib import quote as quote
from mako.template import Template as MakoTemplate

from openerp.osv import orm, fields
from openerp import tools
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class TelegramCommand(orm.Model):

    _name = "telegram.command"
    _order = "sequence"

    _columns = {
        'name': fields.char('Name', help='Command name. Usually starts with slash symbol, e.g. "/mycommand"',
                            required=True),
        'description': fields.text('Description', help='What command does. It will be used in /help command'),
        'sequence': fields.integer('Sequence'),
        'response_code': fields.text(help='''Code to be executed before rendering Response Template. '''),
        'response_template': fields.text(
            help='Template for the message, that user will receive immediately after sending command'),
        'post_response_code': fields.text(help='Python code to be executed after sending response'),
        'group_ids': fields.many2many('res.groups', string="Access Groups",
                                      help='Who can use this command. Set empty list for public commands (e.g. /login)', ),
        'model_id': fields.many2one('ir.model', string="Related model",
                                    help='Is used by Server Action to find commands to proceed'),
        'model': fields.related('model_id', 'model', type='char', string='Related Document model',
                                size=128, select=True, store=True, readonly=True),
        'report_name': fields.char('Report Filename', size=200,
                                   help="Name to use for the generated report file (may contain placeholders)\n"
                                        "The extension can be omitted and will then come from the report type."),
        'report_template': fields.many2one('ir.actions.report.xml', 'Optional report to print and attach'),
        'attachment_ids': fields.many2many('ir.attachment', 'telegram_template_attachment_rel', 'telegram_template_id',
                                           'attachment_id', 'Files to attach',
                                           help="You may attach files to this template, to be added to all "
                                                "emails created from this template"),
        # Fake fields used to implement the placeholder assistant
        'model_object_field': fields.many2one('ir.model.fields', string="Field",
                                              help="Select target field from the related document model.\n"
                                                   "If it is a relationship field you will be able to select "
                                                   "a target field at the destination of the relationship."),
        'sub_object': fields.many2one('ir.model', 'Sub-model', readonly=True,
                                      help="When a relationship field is selected as first field, "
                                           "this field shows the document model the relationship goes to."),
        'sub_model_object_field': fields.many2one('ir.model.fields', 'Sub-field',
                                                  help="When a relationship field is selected as first field, "
                                                       "this field lets you select the target field within the "
                                                       "destination document model (sub-model)."),
        'null_value': fields.char('Null value', help="Optional value to use if the target field is empty", size=128),
        'copyvalue': fields.char('Expression', size=256,
                                 help="Final placeholder expression, to be copy-pasted in the desired template field."),
    }

    _defaults = {
        'sequence': 16,
    }

    _sql_constraints = [
        ('command_name_uniq', 'unique (name)', 'Command name must be unique!'),
    ]

    def onchange_model_id(self, cr, uid, ids, model_id, context=None):
        mod_name = False
        if model_id:
            mod_name = self.pool['ir.model'].browse(cr, uid, model_id, context).model
        return {'value': {'model': mod_name}}

    def build_expression(self, field_name, sub_field_name, null_value):
        """Returns a placeholder expression for use in a template field,
           based on the values provided in the placeholder assistant.

          :param field_name: main field name
          :param sub_field_name: sub field name (M2O)
          :param null_value: default value if the target value is empty
          :return: final placeholder expression
        """
        expression = ''
        if field_name:
            expression = "${object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += "}"
        return expression

    def onchange_sub_model_object_value_field(self, cr, uid, ids, model_object_field, sub_model_object_field=False,
                                              null_value=None, context=None):
        result = {
            'sub_object': False,
            'copyvalue': False,
            'sub_model_object_field': False,
            'null_value': False
        }
        if model_object_field:
            fields_obj = self.pool['ir.model.fields']
            field_value = fields_obj.browse(cr, uid, model_object_field, context)
            if field_value.ttype in ['many2one', 'one2many', 'many2many']:
                res_ids = self.pool['ir.model'].search(cr, uid, [('model', '=', field_value.relation)], context=context)
                sub_field_value = False
                if sub_model_object_field:
                    sub_field_value = fields_obj.browse(cr, uid, sub_model_object_field, context)
                if res_ids:
                    result.update({
                        'sub_object': res_ids[0],
                        'copyvalue': self.build_expression(field_value.name,
                                                           sub_field_value and sub_field_value.name or False,
                                                           null_value or False),
                        'sub_model_object_field': sub_model_object_field or False,
                        'null_value': null_value or False
                    })
            else:
                result.update({
                    'copyvalue': self.build_expression(field_value.name, False, null_value or False),
                    'null_value': null_value or False
                })
        return {'value': result}

    def get_response(self, cr, uid, ids, locals_dict=None, parameters=[], context={}):
        command = self.browse(cr, uid, ids[0], context)
        locals_dict = self._eval(cr, uid, ids, command.response_code, locals_dict, context)
        return self._render(cr, uid, command, locals_dict, context)

    def eval_post_response(self, cr, uid, ids, args, context=None):
        command = self.browse(cr, uid, ids[0], context)
        if command.post_response_code:
            return self.command(cr, uid, command.post_response_code, context=context)

    def _get_globals_dict(self, cr, uid, context):
        return {
            'pool': self.pool,
            'context': context,
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            '_logger': _logger,
            'tools': tools,
            'cr': cr,
            'uid': uid,
            'pdb': pdb,
            'OrderedDict': OrderedDict,
            'sorted': sorted,
        }

    def _eval(self, cr, uid, ids, code, locals_dict=None, context={}):
        t0 = time.time()
        locals_dict = locals_dict or {}
        user = uid
        locals_dict.update({
            'data': {}})
        globals_dict = self._get_globals_dict(cr, uid, context)
        if code:
            safe_eval(code, globals_dict, locals_dict, mode="exec", nocopy=True)
            eval_time = time.time() - t0
            _logger.debug('Eval in %.2fs \nlocals_dict:\n%s\n\nCode:\n%s\n', eval_time, locals_dict, code)
        return locals_dict

    def _prepare_render_template_context(self, locals_dict):
        qcontext = {}
        qcontext['data'] = locals_dict['data']
        qcontext['subscribed'] = locals_dict.get('subscribed')
        return qcontext

    def render_template(self, cr, uid, template, model, res_id, context=None):
        """Render the given template text, replace mako expressions ``${expr}``
           with the result of evaluating these expressions with
           an evaluation context containing:

                * ``user``: browse_record of the current user
                * ``object``: browse_record of the document record this mail is
                              related to
                * ``context``: the context passed to the mail composition wizard

           :param str template: the template text to render
           :param str model: model name of the document record this mail is related to.
           :param int res_id: id of the document record this mail is related to.
        """
        if not template:
            return u""
        if context is None:
            context = {}
        try:
            template = tools.ustr(template)
            record = None
            if res_id:
                record = self.pool.get(model).browse(cr, uid, res_id, context)
            user = self.pool['res.users'].browse(cr, uid, uid, context)
            result = MakoTemplate(template).render_unicode(object=record,
                                                           user=user,
                                                           ctx=context,
                                                           quote=quote,
                                                           data=context.get('data'),
                                                           format_exceptions=True)
            if result == u'False':
                result = u''
            return result
        except Exception:
            logging.exception("failed to render mako template value %r", template)
            return u""

    def _render(self, cr, uid, template, locals_dict, context):
        t0 = time.time()
        report_xml_pool = self.pool['ir.actions.report.xml']
        model = locals_dict.get('model', template.model)
        res_id = locals_dict.get('res_id', False)
        if res_id and isinstance(res_id, (int, long)):
            res_id = [res_id]

        qcontext = self._prepare_render_template_context(locals_dict)
        html = self.render_template(cr, uid, template.response_template, model, res_id, context=qcontext)

        attachments = {}
        if res_id and template.report_template:
            report_name = self.render_template(cr, uid, template.report_name, model, res_id, context=qcontext)
            report_service = 'report.' + report_xml_pool.browse(cr, uid, template.report_template.id, context).report_name
            service = netsvc.LocalService(report_service)

            (result, format) = service.create(cr, uid, res_id, {'model': template.model}, context)
            result = base64.encodestring(result)  # todo

            if not report_name:
                report_name = report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attachments[report_name] = result

        for attach in template.attachment_ids:
            # keep the bytes as fetched from the db, base64 encoded
            attachments[attach.datas_fname] = attach.datas

        render_time = time.time() - t0
        _logger.debug('Render in %.2fs\n', render_time)
        return {
            'photos': [],
            'html': html,
            'attachments': attachments
        }

    def send(self, bot, rendered, chat_id):
        try:
            self._send(bot, rendered, chat_id)
            return True
        except Exception as error:
            _logger.error('Cannot send message {0}'.format(error))
            return False

    def _send(self, bot, rendered, chat_id):
        # https://github.com/nickoala/telepot/issues/164
        reload(sys)
        sys.setdefaultencoding('utf-8')

        if rendered.get('html'):
            _logger.debug(u'Send:\n {0}'.format(rendered['html']))
            message_to_send = rendered['html']
            while message_to_send:
                position_cuts = [pos for pos, char in enumerate(message_to_send[:400]) if char == '\n']
                if position_cuts:
                    position_cut = position_cuts[-1]
                else:
                    position_cut = 400
                try:
                    if message_to_send[:position_cut]:
                        bot.sendMessage(chat_id, message_to_send[:position_cut], parse_mode='HTML')
                except Exception as error:
                    _logger.error('Cannot send attachment: {0}'.format(str(error)))
                    bot.sendMessage(chat_id, error[:400])
                if position_cut:
                    message_to_send = message_to_send[position_cut:]
                else:
                    message_to_send = False

        if rendered.get('attachments'):
            _logger.debug('Send attachment {0}'.format(len(rendered.get('attachments'))))
            for attachment in rendered.get('attachments').keys():
                bot.sendChatAction(chat_id, 'upload_document')
                file_to_send = StringIO(base64.b64decode(rendered['attachments'][attachment]))
                try:
                    bot.sendDocument(chat_id, (attachment, file_to_send))
                except Exception as error:
                    _logger.error('Cannot send attachment: {0}'.format(error))
                finally:
                    file_to_send.close()
        return True

    def telegram_listener(self, cr, uid, messages, bot, chat_id, context):

        bot.sendChatAction(chat_id, 'typing')  # send that i'm writing replay (for give feedback)

        for message in messages:  # messages from telegram server
            user_input = message.get('text', '').split(' ')
            command_search = user_input[0]
            parameters = user_input
            del parameters[0]  # need only parameters not command
            command_ids = self.pool['telegram.command'].search(cr, uid, [('name', '=', command_search)], limit=1, context=context)
            if command_ids:
                command = self.pool['telegram.command'].browse(cr, uid, command_ids, context)[0]
                locals_dict = {
                    'user_input': parameters
                }
                try:
                    response = command.get_response(locals_dict, command_search[1:])
                except Exception as error:
                    error_message = _('Cannot get response: {0}'.format(error))
                    _logger.error(error_message)
                    response = {'html': error_message}

                self.send(bot, response, chat_id)
                try:
                    command.eval_post_response(command_search[1:])
                except Exception as error:
                    error_message = _('Cannot eval post response: {0}'.format(error))
                    _logger.error(error_message)
                    self.send(bot, {'html': error_message}, chat_id)
            elif message.get('location', False):
                location_get = {'html': _(
                    "We get your location.  \n Use /help to see all available for you commands")}
                self.send(bot, location_get, chat_id)
            else:
                not_found = {'html': _(
                    "There is no such command or you don't have access:  <b>{0}</b>.  \n Use /help to see all available for you commands").format(
                    message.get('text', 'NO TEXT'))}
                self.send(bot, not_found, chat_id)
                return

        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        command = self.browse(cr, uid, ids, context=context)
        default.update({'name': command.name + ' ' + _('Copy')})
        return super(TelegramCommand, self).copy(cr, uid, ids, default, context=context)
