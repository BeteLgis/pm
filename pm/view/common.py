from pm.models import Record


class Data:
    def __init__(self):
        self.href = Href()
        self.redirect = None

    def to_dict(self):
        dict = getattr(self, '__dict__')
        res = {}
        for key in dict:
            if dict[key] is not None:
                res[key[1:] if key[0] == '_' else key] = dict[key]
        return res

    def update(self, value):
        b = value.to_dict()
        for key in b:
            if key != 'href':
                self.__setattr__(key, b[key])


class CommonData(Data):
    def __init__(self, view):
        super().__init__()
        self.href.update(view=view)
        self.view = view
        self._header = None
        self.error = None

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        if self._header is None:
            self._header = {}
        if isinstance(value, dict) and 'id' not in value:
            for key in value:
                self.header = value[key]
        else:
            self._header[value['id']] = value


class View:
    RECORD = 0
    RECORD_LOADED = 1
    INDICT = 2

    def __init__(self, request, view):
        self._request = request
        self._data = CommonData(view)

    def header(self):
        pass

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data.update(value)

    def load(self, *_args):
        return self._data

    def _request_get(self, val, type, *default):
        return self.__request_switch(self._request.GET.get(val, default[0]), type, *default)

    def _request_post(self, val, type, *default):
        return self.__request_switch(self._request.POST.get(val, default[0]), type, *default)

    def __request_switch(self, val, type, *default):
        type = str(type)
        if type == "<class 'int'>":
            val = int(val) if View.is_int(val) else default[0]
            if len(default) > 1:
                if default[1] == self.RECORD:
                    val = val if Record.objects.filter(user=self._request.user, id=val).exists() else default[0]
                elif default[1] == self.RECORD_LOADED:
                    val = val if Record.objects.filter(user=self._request.user, id=val).exists() \
                                 and Record.objects.get(user=self._request.user, id=val).isloaded else default[0]
                elif default[1] == self.INDICT:
                    val = val if val in default[2] else default[0]
        elif type == "<class 'bool'>":
            val = False if val is False else True

        return val

    @staticmethod
    def is_int(s):
        if s is None or isinstance(s, bool):
            return False
        else:
            try:
                int(s)
                return True
            except ValueError:
                return False

    def _switch(self, val):
        if val == -1:
            return '<'
        elif val == 1:
            return '>'
        elif val == 2:
            return '||'
        else:
            return '#'


class IUpdate:
    def update(self, items):
        for key, val in items:
            if key != 'self' and val is not None:
                self.__setattr__(key, val)
        return self


class Button(IUpdate):
    def __init__(self, value=None, label=None, href=None):
        self.value = value
        self.label = label
        self.href = href

    def update(self, href=None, label=None, value=None):
        return super(Button, self).update(locals().items())


class Href(IUpdate):
    def __init__(self, view=None, record=None, record2=None, step=None, clean=None, delete=None):
        self.view = view
        self.record = record
        self.record2 = record2
        self.step = step
        self.clean = clean
        self.delete = delete

    def update(self, view=None, record=None, record2=None, step=None, clean=None, delete=None):
        return super(Href, self).update(locals().items())

    def copy(self, view=None, record=None, record2=None, step=None, clean=None, delete=None):
        copy = Href(self.view, self.record, self.record2, self.step, self.clean, self.delete)
        return copy.update(view, record, record2, step, clean, delete)

    @staticmethod
    def clone(href):
        if href is not None:
            return href.copy(href.view, href.record, href.record2, href.step, href.clean, href.delete)
        return Href()

    def __str__(self):
        ref = ''
        params = []
        for key, value in getattr(self, '__dict__').items():
            if value is not None:
                params.append((key, value))
        if len(params):
            ref = '?'
            for param in params:
                if isinstance(param[1], bool):
                    if param[1]:
                        ref += f"{param[0]}&"
                else:
                    ref += f"{param[0]}={param[1]}&"
            ref = ref[:-1]
        return ref
