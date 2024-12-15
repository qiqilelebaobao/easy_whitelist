import argparse

def init_arg():
    '''parse parameter from command line.'''
    
    parser = argparse.ArgumentParser(prog='easy', description='This is a cloud acl auto whitelist tool.', epilog='Enjoy the tool. :) ')

    my_group = parser.add_mutually_exclusive_group(required=False)
    my_group.add_argument('-t', '-T', '--tencent', action='store_true', default=True, help='tencent cloud')
    my_group.add_argument('-a', '-A', '--alibaba', action='store_true', help='alibaba cloud')
    
    parser.add_argument('-p', '-P', '--proxy',  action='store', default=None, type=int, help ='local HTTP proxy port')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    
    parser.add_argument('target', help='template or rule_id', choices=['template', 'rule_id'])
    parser.add_argument('action', help='list', choices=['list', 'set', 'create'])
    parser.add_argument('target_id', help='template id or rule id', nargs='?')

    args = parser.parse_args()
    
    return args.tencent, args.alibaba, args.action, args.target, args.target_id, args.proxy, args.verbose
