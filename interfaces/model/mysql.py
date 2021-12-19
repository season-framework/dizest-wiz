import season
import os
import pickle
import json
import datetime
import shutil
import pymysql
import math

# mysql model
def join(v, format='/'):
    if len(v) == 0:
        return ''
    return format.join(v)

class Model:
    def __init__(self):
        self.framework = wiz
        self.config = wiz.config('database')
        self.namespace = None
        self.tablename = None

    @classmethod
    def use(cls, tablename, namespace=None):
        model = cls()
        model.tablename = tablename
        model.namespace = namespace
        return model

    def __values__(self, values, **format):
        fields = self.fields()
        _field = []
        _format = []
        _update_format = []
        _data = []
        for key in values:
            if key not in fields.columns:
                continue
                
            _field.append('`' + key + '`')
            val = values[key]

            if val is None:
                _format.append('NULL')
                _update_format.append(f"`{key}`=NULL")
            elif key in format:
                formatstring = format[key]
                _format.append(formatstring)
                _update_format.append(f"`{key}`={formatstring}")
                if '%' in format[key]:
                    _data.append(val)
            else:
                if type(val) != dict:
                    _v = dict()
                    _v['value'] = val
                    val = _v
                fv = val['value']
                ff = val['format'] if 'format' in val else "%s"
                _format.append(ff)
                _update_format.append(f"`{key}`={ff}")
                if '%s' in ff:
                    _data.append(str(fv))

        _field = join(_field, format=',')
        _format = join(_format, format=',')
        _update_format = join(_update_format, format=',')
        return _field, _format, _update_format, _data

    def __where__(self, where):
        IGNORE_FIELDS = ['groupby', 'orderby', 'limit', 'fields', 'where', 'like', 'or']
        fields = self.fields()
        _where = []
        _data = []

        if 'where' in where:
            scope_wheres = where['where']
            if type(scope_wheres) != list:
                scope_wheres = [scope_wheres]
            for scope_where in scope_wheres:
                if type(scope_where) == dict:
                    if 'values' in scope_where:
                        if type(scope_where['values']) != list:
                            scope_where['values'] = [scope_where['values']]
                        for v in scope_where['values']:
                            _data.append(str(v))
                    _where.append(scope_where['clause'])
                elif type(scope_where) == str:
                    _where.append(scope_where)

        if 'or' in where:
            or_where = where['or']
            _or_where = []
            _or_data = []
            for key in or_where:
                if key in IGNORE_FIELDS: continue
                if key not in fields.columns: continue
                values = or_where[key]
                if type(values) != list: values = [values]
                scope_where = []
                for value in values:
                    if type(value) != dict:
                        _v = dict()
                        _v['value'] = value
                        value = _v
                    v = value['value']
                    op = value['op'] if 'op' in value else '='
                    format = value['format'] if 'format' in value else "%s"
                    if v is None: 
                        scope_where.append(f"`{key}` {op} NULL")
                    else:
                        scope_where.append(f"`{key}` {op} {format}")
                        if '%' in format: _or_data.append(str(v))
                scope_where = "( " + join(scope_where, format=' OR ') + " )"
                _or_where.append(scope_where)

            if len(_or_where) > 0:
                _or_where = '(' + join(_or_where, format=' OR ') + ')'
                _where.append(_or_where)
                _data = _data + _or_data
        
        for key in where:
            if key in IGNORE_FIELDS: continue
            if key not in fields.columns: continue
            values = where[key]
            if type(values) != list:
                values = [values]
            scope_where = []
            for value in values:
                if type(value) != dict:
                    _v = dict()
                    _v['value'] = value
                    value = _v
                v = value['value']
                op = value['op'] if 'op' in value else '='
                format = value['format'] if 'format' in value else "%s"
                
                if v is None: 
                    scope_where.append(f"`{key}` {op} NULL")
                else:
                    scope_where.append(f"`{key}` {op} {format}")
                    if '%' in format:
                        _data.append(str(v))
            scope_where = "( " + join(scope_where, format=' OR ') + " )"
            _where.append(scope_where)
            
        if len(_where) == 0: return "", None
        _where = join(_where, format=' AND ')
        return _where, _data
            
    def query(self, sql, data=None):
        coninfo = None
        if self.namespace is not None: coninfo = self.config.data[self.namespace]
        else: coninfo = self.config.data.mysql
        con = pymysql.connect(**coninfo)
        cursor = con.cursor(pymysql.cursors.DictCursor)
        status = cursor.execute(sql, data)
        rows = cursor.fetchall()
        lastrowid = cursor.lastrowid
        # print(cursor._last_executed)
        con.commit()
        con.close()
        return status, rows, lastrowid

    def fields(self):
        tablename = self.tablename
        _, columns, _ = self.query('DESC ' + tablename)
        result = season.stdClass()
        result.pk = []
        result.columns = []
        for col in columns:
            if col['Key'] == 'PRI':
                result.pk.append(col['Field'])
            result.columns.append(col['Field'])
        return result

    def insert(self, values, **format):
        try:
            tablename = self.tablename
            _field, _format, _, _data = self.__values__(values, **format)
            sql = f"INSERT INTO `{tablename}`({_field}) VALUES({_format})"
            _, _, lastrowid = self.query(sql, data=_data)
            return True, lastrowid
        except Exception as e:
            return False, e

    def upsert(self, values, **format):
        try:
            tablename = self.tablename
            _field, _format, _update_format, _data = self.__values__(values, **format)
            _data = _data + _data
            sql = f"INSERT INTO `{tablename}`({_field}) VALUES({_format}) ON DUPLICATE KEY UPDATE {_update_format}"
            status, _, lastrowid = self.query(sql, data=_data)
            if status == 0:
                return True, -1
            return True, lastrowid
        except Exception as e:
            return False, e

    def get(self, **where):
        try:
            tablename = self.tablename
            orderby = None
            if 'orderby' in where:
                orderby = where['orderby']
                del where['orderby']
            groupby = None
            if 'groupby' in where:
                groupby = where['groupby']
                del where['groupby']
            limit = None
            if 'limit' in where:
                limit = where['limit']
                del where['limit']
            
            targetfields = '*'
            if 'fields' in where:
                targetfields = where['fields']
            wherestr, wheredata = self.__where__(where)
            sql = f"SELECT {targetfields} FROM `{tablename}` WHERE {wherestr}"

            if groupby is not None:
                sql = sql + ' GROUP BY ' + groupby
            if orderby is not None:
                sql = sql + ' ORDER BY ' + orderby
            if limit is not None:
                sql = sql + ' LIMIT ' + str(limit)

            _, rows, _ = self.query(sql, wheredata)
            if len(rows) > 0:
                return rows[0]
            return None
        except Exception as e:
            print(e)
            return None

    def count(self, **where):
        try:
            tablename = self.tablename
            wherestr, wheredata = self.__where__(where)
            if len(wherestr) > 0:
                sql = 'SELECT count(*) AS cnt FROM `' + tablename + '` WHERE ' + wherestr
            else:
                sql = 'SELECT count(*) AS cnt FROM `' + tablename + '`'
            _, rows, _ = self.query(sql, wheredata)
            return rows[0]['cnt']
        except Exception as e:
            return 0
    
    def select(self, **where):
        return self.rows(**where)

    def rows(self, **where):
        try:
            tablename = self.tablename
            orderby = None
            if 'orderby' in where:
                orderby = where['orderby']
                del where['orderby']
            groupby = None
            if 'groupby' in where:
                groupby = where['groupby']
                del where['groupby']
            limit = None
            if 'limit' in where:
                limit = where['limit']
                del where['limit']

            targetfields = '*'
            if 'fields' in where:
                targetfields = where['fields']
            wherestr, wheredata = self.__where__(where)
            if len(wherestr) > 0:
                sql = f'SELECT {targetfields} FROM `{tablename}` WHERE {wherestr}'
            else:
                sql = f'SELECT {targetfields} FROM `{tablename}`'
            if groupby is not None:
                sql = sql + ' GROUP BY ' + groupby
            if orderby is not None:
                sql = sql + ' ORDER BY ' + orderby
            if limit is not None:
                sql = sql + ' LIMIT ' + str(limit)
            _, rows, _ = self.query(sql, data=wheredata)
            return rows
        except Exception as e:
            print(e)
            return []

    def delete(self, **where):
        try:
            tablename = self.tablename
            wherestr, wheredata = self.__where__(where)
            if len(wherestr) > 0:
                sql = 'DELETE FROM `' + tablename + '` WHERE ' + wherestr
            else:
                sql = 'DELETE FROM `' + tablename + '`'
            _, _, _ = self.query(sql, wheredata)
            return True
        except Exception as e:
            return False

    def update(self, values, **where):
        try:
            tablename = self.tablename
            _, _, _update_format, _data = self.__values__(values)
            wherestr, wheredata = self.__where__(where)
            sql = f"UPDATE `{tablename}` SET {_update_format} WHERE {wherestr}"
            _data = _data + wheredata
            res, _, _ = self.query(sql, data=_data)
            if res == 0: return True, "Nothing Changed"
            return True, "Success"
        except Exception as e:
            print(e)
            return False, e

    def search(self, **query):
        IGNORED_FIELDS = ['page', 'size', 'like']
        page = int(query['page']) if 'page' in query else 1
        size = int(query['size']) if 'size' in query else 20 
        likes = query['like'] if 'like' in query else []
        if type(likes) == str: likes = likes.split(',')
        for like in likes:
            if like in query:
                if type(query[like]) == dict: 
                    continue
                query[like] = {"value": "%" + str(query[like]) + "%", "op": "LIKE"}
            if 'or' in query:
                if like in query['or']:
                    if type(query['or'][like]) == dict: 
                        continue
                    query['or'][like] = {"value": "%" + str(query['or'][like]) + "%", "op": "LIKE"}
        for f in IGNORED_FIELDS:
            if f in query: del query[f]
        page = (page - 1) * size
        query['limit'] = f"{page}, {size}"
        result = dict()
        rows = self.select(**query)
        result['list'] = rows
        del query['limit']
        if 'orderby' in query: del query['orderby']
        if 'groupby' in query: del query['groupby']
        result['lastpage'] = math.ceil(self.count(**query) / size)
        result['page'] = page + 1
        result['size'] = size
        return result
