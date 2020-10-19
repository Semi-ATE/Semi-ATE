class YieldInformation:
    def __init__(self, types, site_id):
        self._site_id = site_id
        self._yield_info = {}
        self._init_yield_info(types)

    def _init_yield_info(self, types):
        for t in types:
            self._yield_info[t] = {"count": 0, "value": 0}

    def update_yield_info(self, type):
        self._yield_info[type]["count"] += 1
        self._calculate_yield()

    def max_count(self):
        return sum([values["count"] for _, values in self._yield_info.items()])

    def get_yield_info(self):
        return self._yield_info

    def _calculate_yield(self):
        max_count = self.max_count()
        for _, t in self._yield_info.items():
            t["value"] = self._calculate_value(t["count"], max_count)

    @staticmethod
    def _calculate_value(count, max):
        return (count / max) * 100

    def generate_yield_messages(self):
        messages = [self._yield_message(name, values["value"], values["count"])
                    for name, values in self._yield_info.items()]

        messages.append(self._yield_message('sum', 100.0, self.max_count()))
        return messages

    def _yield_message(self, name, value, count):
        return {"name": name, "siteid": self._site_id, "value": value, "count": count}


class YieldInformationHandler:
    def __init__(self):
        self._bin_settings = None
        self.prr_rec_information = {}
        self.sites_yield_information = {}

    def extract_yield_information(self, param_data):
        # TODO: this must be done after receiving bin settings from every site
        if not self._bin_settings:
            self.on_error("bin settings are not received yet")

        part_id = ''
        param_data = param_data[-1]
        if param_data['PART_ID']:
            part_id = param_data['PART_ID']
        else:
            default_value = -32768
            if (param_data['X_COORD'], param_data['Y_COORD']) == (default_value, default_value):
                part_id = ''
            else:
                part_id = f"{param_data['X_COORD']}x{param_data['Y_COORD']}"

        assert part_id
        if not part_id:
            self.on_error("Part id could not be extracted from PRR record")

        if not self.prr_rec_information.get(part_id):
            self.prr_rec_information[part_id] = param_data
            self._accumulate_site_bin_info(param_data)
        else:
            self.prr_rec_information.update({part_id: param_data})
            self._reaccumulate_bin_info()

    def _accumulate_site_bin_info(self, data):
        site_num = str(data['SITE_NUM'])
        soft_bin = str(data['SOFT_BIN'])
        for typ, setting in self._bin_settings.items():
            if int(soft_bin) not in setting['sbins']:
                continue

            if not self.sites_yield_information.get(site_num):
                self.sites_yield_information[site_num] = YieldInformation(list(self._bin_settings.keys()), site_num)

            self.sites_yield_information[site_num].update_yield_info(typ)
            self._accumulate_all_bin_info()
            return

        self.on_error("soft bin could not be mapped to any of the setting's bins")

    def _accumulate_all_bin_info(self):
        all_id = '-1'
        all_yield_info = YieldInformation(list(self._bin_settings.keys()), all_id)
        for site_id, info in self.sites_yield_information.items():
            if site_id == all_id:
                continue

            for typ, values in info.get_yield_info().items():
                all_yield_info._yield_info[typ]["count"] += values["count"]

        all_yield_info._calculate_yield()
        self.sites_yield_information[all_id] = all_yield_info

    def _reaccumulate_bin_info(self):
        self.sites_yield_information.clear()
        for _, prr_rec in self.prr_rec_information.items():
            self._accumulate_site_bin_info(prr_rec)

        self._accumulate_all_bin_info()

    def set_bin_settings(self, bin_settings):
        self._bin_settings = bin_settings

    def get_yield_messages(self):
        messages = []
        for _, yield_info in self.sites_yield_information.items():
            messages.extend(yield_info.generate_yield_messages())

        return messages

    def get_site_yield_info_message(self, site):
        return self.sites_yield_information[site].generate_yield_messages()
