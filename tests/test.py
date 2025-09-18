def _format_addres_extra_string_from_list(client_ips):
    cs = '"AddressesExtra":['
    for client_ip in client_ips:
        cs += '{{"Address":"{}","Description":"client_ip"}},'.format(client_ip)
    cs_format = cs.rstrip(',')
    cs_format += ']'

    return cs_format

import json

def _format_addres_extra_string_from_list2(client_ips):
    return json.dumps({
        "AddressesExtra": [
            {"Address": ip, "Description": "client_ip"}
            for ip in client_ips
        ]
    })

print(_format_addres_extra_string_from_list(['1.1.1.1', '1.2.3.4']))
print(_format_addres_extra_string_from_list2(['1.1.1.1', '1.2.3.4']))

print([{"aaa": x} for x in range(10)])


print(json.dumps({"a":1, "b":333}))