# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Operations Enhancement
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.osv import orm, fields


class resource_calendar(orm.Model):
    _name = "resource.calendar"
    _inherit = "resource.calendar"
    _description = "Resource Calendar"

    def interval_get_multi(self, cr, uid, date_and_hours_by_cal, resource=False, byday=True):
        def group(lst, key):
            lst.sort(key=itemgetter(key))
            grouped = groupby(lst, itemgetter(key))
            return dict([(k, [v for v in itr]) for k, itr in grouped])

        # END group

        cr.execute(
            "select calendar_id, dayofweek, hour_from, hour_to from resource_calendar_attendance order by hour_from")
        hour_res = cr.dictfetchall()
        hours_by_cal = group(hour_res, 'calendar_id')

        results = {}

        for d, hours, id in date_and_hours_by_cal:
            dt_from = datetime.strptime(d, DEFAULT_SERVER_DATETIME_FORMAT)
            if not id:
                results[(d, hours, id)] = [(dt_from, dt_from + timedelta(hours=hours))]
                continue

            dt_leave = self._get_leaves(cr, uid, id, resource)
            todo = hours
            result = []
            maxrecur = 100
            current_hour = dt_from.hour
            while (todo > 0) and maxrecur:
                for (hour_from, hour_to) in [(item['hour_from'], item['hour_to']) for item in hours_by_cal[id] if
                                             item['dayofweek'] == str(dt_from.weekday())]:
                    leave_flag = False
                    if (hour_to > current_hour) and (todo > 0):
                        m = max(hour_from, current_hour)
                        if (hour_to - m) > todo:
                            hour_to = m + todo
                        dt_check = dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        for leave in dt_leave:
                            if dt_check == leave:
                                dt_check = datetime.strptime(dt_check, DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=1)
                                leave_flag = True
                        if leave_flag:
                            break
                        else:
                            # d1 = datetime(dt_from.year, dt_from.month, dt_from.day, int(math.floor(m)), int((m%1) * 60))
                            # d2 = datetime(dt_from.year, dt_from.month, dt_from.day, int(math.floor(hour_to)), int((hour_to%1) * 60))
                            # result.append((d1, d2))
                            current_hour = hour_to
                            todo -= (hour_to - m)
                dt_from += timedelta(days=1)
                current_hour = 0
                maxrecur -= 1
            results[(d, hours, id)] = result
        return results
